"""Tests the real TelegramClient against a fake HTTP server (no network)."""
import json

import httpx
import pytest

from bot.telegram_api import TelegramClient, TelegramError


def client_with(handler):
    return TelegramClient("TOKEN", http=httpx.Client(transport=httpx.MockTransport(handler)))


def test_get_updates_sends_long_poll_timeout_and_offset():
    seen = {}

    def handler(request):
        seen["url"] = str(request.url)
        seen["body"] = json.loads(request.content)
        return httpx.Response(200, json={"ok": True, "result": [{"update_id": 5}]})

    result = client_with(handler).get_updates(offset=5, timeout=30)
    assert result == [{"update_id": 5}]
    assert seen["body"]["timeout"] == 30 and seen["body"]["offset"] == 5
    assert seen["url"].endswith("/botTOKEN/getUpdates")


def test_send_message_returns_ids_and_replies_to_first_part_only():
    bodies = []

    def handler(request):
        bodies.append(json.loads(request.content))
        return httpx.Response(200, json={"ok": True, "result": {"message_id": 100 + len(bodies)}})

    ids = client_with(handler).send_message(1, ("para " * 300 + "\n\n") * 5, reply_to_message_id=9)
    assert len(ids) == len(bodies) > 1
    assert bodies[0]["reply_to_message_id"] == 9
    assert "reply_to_message_id" not in bodies[1]
    assert bodies[0]["parse_mode"] == "HTML"


def test_formatting_error_falls_back_to_plain_text():
    calls = []

    def handler(request):
        body = json.loads(request.content)
        calls.append(body)
        if body.get("parse_mode"):
            return httpx.Response(400, json={"ok": False, "error_code": 400, "description": "Bad Request: can't parse entities"})
        return httpx.Response(200, json={"ok": True, "result": {"message_id": 7}})

    assert client_with(handler).send_message(1, "hello **x**") == [7]
    assert "parse_mode" not in calls[1]


def test_api_error_carries_code_and_hides_token():
    def handler(request):
        return httpx.Response(429, json={"ok": False, "error_code": 429, "description": "Too Many Requests"})

    with pytest.raises(TelegramError) as e:
        client_with(handler).get_updates()
    assert e.value.code == 429 and e.value.retryable
    assert "TOKEN" not in str(e.value)
