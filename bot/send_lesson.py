"""Send the lesson Claude wrote to Telegram and record it in SQLite.

Run:  python -m bot.send_lesson --slot 2026-11-05T11:30
      python -m bot.send_lesson --check-slot 2026-11-05T11:30   (exit 3 if already sent)

Exit codes: 0 sent, 1 failed, 2 config problem, 3 slot already sent.
If sending fails the outbox file is kept so a retry can resend it.
"""
from __future__ import annotations

import argparse
import re
import sys
import time
from pathlib import Path

import httpx

from . import db
from .config import ROOT, ConfigError, load_config
from .telegram_api import TelegramClient, TelegramError

OUTBOX_FILE = ROOT / "learning" / "outbox" / "lesson.md"
TRACK_LABELS = {"ai": "🤖 AI development", "data": "🗄️ Data engineering"}
VALID_KINDS = {"lesson", "drill"}
MAX_BODY_CHARS = 3000  # lessons are meant to be a minute or two on a phone

EXIT_OK, EXIT_FAIL, EXIT_CONFIG, EXIT_ALREADY_SENT = 0, 1, 2, 3


class LessonFormatError(Exception):
    """lesson.md doesn't follow the output contract in learning/CLAUDE.md."""


def parse_lesson_file(path: Path) -> dict:
    raw = Path(path).read_text(encoding="utf-8-sig")
    m = re.match(r"\A\s*---\s*\n(.*?)\n---\s*\n(.*)\Z", raw, re.S)
    if not m:
        raise LessonFormatError("missing --- front-matter block")
    meta: dict[str, str] = {}
    for line in m.group(1).splitlines():
        if ":" in line:
            key, value = line.split(":", 1)
            meta[key.strip().lower()] = value.strip()

    track, topic, kind = meta.get("track", ""), meta.get("topic", ""), meta.get("kind", "lesson")
    body = m.group(2).strip()
    if track not in TRACK_LABELS:
        raise LessonFormatError(f"track must be 'ai' or 'data', got {track!r}")
    if kind not in VALID_KINDS:
        raise LessonFormatError(f"kind must be 'lesson' or 'drill', got {kind!r}")
    if not topic:
        raise LessonFormatError("topic is empty")
    if not body:
        raise LessonFormatError("lesson body is empty")
    if len(body) > MAX_BODY_CHARS:
        raise LessonFormatError(f"lesson body is {len(body)} characters (max {MAX_BODY_CHARS})")
    return {"track": track, "topic": topic, "kind": kind, "text": body}


def format_for_telegram(lesson: dict) -> str:
    if lesson["kind"] == "drill":
        return (
            f"🎤 **Interview drill: {lesson['topic']}**\n\n{lesson['text']}\n\n"
            "Reply to this message with your answer."
        )
    return f"{TRACK_LABELS[lesson['track']]} · **{lesson['topic']}**\n\n{lesson['text']}"


def _send_with_retry(tg, chat_id: int, text: str, attempts: int = 3) -> list[int]:
    for attempt in range(1, attempts + 1):
        try:
            return tg.send_message(chat_id, text)
        except (httpx.HTTPError, TelegramError) as e:
            retryable = isinstance(e, httpx.HTTPError) or e.retryable
            if not retryable or attempt == attempts:
                raise
            time.sleep(2 * attempt)
    raise AssertionError("unreachable")


def send_lesson(conn, tg, owner_chat_id: int, path: Path, slot: str | None) -> int:
    """Parse, send, record, then remove the outbox file. Returns the lesson id."""
    lesson = parse_lesson_file(path)
    message_ids = _send_with_retry(tg, owner_chat_id, format_for_telegram(lesson))
    lesson_id = db.add_lesson(
        conn,
        track=lesson["track"],
        topic=lesson["topic"],
        text=lesson["text"],
        telegram_message_ids=message_ids,
        kind=lesson["kind"],
        slot=slot,
    )
    Path(path).unlink(missing_ok=True)
    return lesson_id


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--file", default=str(OUTBOX_FILE))
    parser.add_argument("--slot", help="slot id like 2026-11-05T11:30 (prevents double-sending)")
    parser.add_argument("--check-slot", help="only check whether this slot was already sent")
    args = parser.parse_args(argv)

    try:
        if args.check_slot:
            conn = db.connect(load_config().db_path)
            return EXIT_ALREADY_SENT if db.lesson_exists_for_slot(conn, args.check_slot) else EXIT_OK

        cfg = load_config(need=("telegram_bot_token", "owner_chat_id"))
        conn = db.connect(cfg.db_path)
        if args.slot and db.lesson_exists_for_slot(conn, args.slot):
            print(f"slot {args.slot} was already sent; skipping")
            return EXIT_ALREADY_SENT
        lesson_id = send_lesson(conn, TelegramClient(cfg.telegram_bot_token), cfg.owner_chat_id, Path(args.file), args.slot)
        print(f"sent lesson {lesson_id}")
        return EXIT_OK
    except ConfigError as e:
        print(f"Config problem: {e}", file=sys.stderr)
        return EXIT_CONFIG
    except LessonFormatError as e:
        print(f"Bad lesson file: {e}", file=sys.stderr)
        return EXIT_FAIL
    except (httpx.HTTPError, TelegramError) as e:
        print(f"Could not send to Telegram: {type(e).__name__}", file=sys.stderr)
        return EXIT_FAIL


if __name__ == "__main__":
    sys.exit(main())
