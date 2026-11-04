"""Thin Telegram Bot API wrapper over httpx.

Never put the bot token in log lines or error messages: it is part of the URL.
"""
from __future__ import annotations

import html
import re

import httpx

API = "https://api.telegram.org"
# Telegram's hard limit is 4096 characters. Split lower to leave room for HTML tags.
SPLIT_AT = 3500


class TelegramError(Exception):
    def __init__(self, message: str, code: int | None = None):
        super().__init__(message)
        self.code = code

    @property
    def retryable(self) -> bool:
        """Worth retrying later (rate limit or Telegram-side failure)?"""
        return self.code is None or self.code == 429 or self.code >= 500


def split_text(text: str, limit: int = SPLIT_AT) -> list[str]:
    """Split on paragraph, then line, then space boundaries."""
    chunks: list[str] = []
    text = text.strip()
    while len(text) > limit:
        cut = text.rfind("\n\n", 0, limit)
        if cut < limit // 2:
            cut = text.rfind("\n", 0, limit)
        if cut < limit // 2:
            cut = text.rfind(" ", 0, limit)
        if cut <= 0:
            cut = limit
        chunks.append(text[:cut].rstrip())
        text = text[cut:].lstrip()
    if text:
        chunks.append(text)
    return chunks


def to_html(text: str) -> str:
    """Turn light markdown (**bold**, `code`, ``` fences) into Telegram HTML."""
    out = html.escape(text, quote=False)
    out = re.sub(r"```(?:\w+)?\n?(.*?)```", r"<pre>\1</pre>", out, flags=re.S)
    out = re.sub(r"\*\*(.+?)\*\*", r"<b>\1</b>", out, flags=re.S)
    out = re.sub(r"`([^`\n]+)`", r"<code>\1</code>", out)
    return out


class TelegramClient:
    def __init__(self, token: str, http: httpx.Client | None = None):
        self._base = f"{API}/bot{token}"
        self._http = http or httpx.Client(timeout=httpx.Timeout(10.0))

    def _call(self, method: str, timeout: float | None = None, **params):
        kwargs = {"json": params}
        if timeout is not None:
            kwargs["timeout"] = timeout
        resp = self._http.post(f"{self._base}/{method}", **kwargs)
        try:
            data = resp.json()
        except ValueError:
            raise TelegramError(f"{method}: HTTP {resp.status_code}", resp.status_code) from None
        if not data.get("ok"):
            raise TelegramError(
                f"{method}: {data.get('description', 'unknown error')}",
                data.get("error_code", resp.status_code),
            )
        return data["result"]

    def get_updates(self, offset: int | None = None, timeout: int = 30) -> list[dict]:
        """Long poll: Telegram holds the request open until a message arrives
        or `timeout` seconds pass."""
        params: dict = {"timeout": timeout, "allowed_updates": ["message"]}
        if offset:
            params["offset"] = offset
        return self._call("getUpdates", timeout=timeout + 15, **params)

    def send_message(
        self, chat_id: int, text: str, reply_to_message_id: int | None = None
    ) -> list[int]:
        """Send text (split if long). Returns the Telegram message id of each part."""
        ids: list[int] = []
        for i, chunk in enumerate(split_text(text)):
            params = {"chat_id": chat_id}
            if i == 0 and reply_to_message_id:
                params["reply_to_message_id"] = reply_to_message_id
                params["allow_sending_without_reply"] = True
            try:
                result = self._call("sendMessage", text=to_html(chunk), parse_mode="HTML", **params)
            except TelegramError as e:
                if "parse entities" not in str(e).lower():
                    raise
                result = self._call("sendMessage", text=chunk, **params)  # plain-text fallback
            ids.append(result["message_id"])
        return ids
