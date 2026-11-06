"""Telegram long-polling bot. Run with:  python -m bot.bot

The laptop asks Telegram "any new messages?" over outbound HTTPS, so no server,
domain or open port is needed.
"""
from __future__ import annotations

import argparse
import logging
import sys
import time
from datetime import datetime, timezone
from logging.handlers import RotatingFileHandler

import httpx

from . import db, qa, reactions
from .config import Config, ConfigError, ROOT, load_config
from .telegram_api import TelegramClient, TelegramError

log = logging.getLogger("bot")

HELP_TEXT = (
    "I'm your interview-prep tutor. Just message me to ask about the latest lesson, "
    "or reply to any lesson (or any of my answers) to ask about that specific one. "
    "If the lesson is an interview drill, reply with your answer and I'll grade it."
)


def local_day_start_utc() -> str:
    """Start of today (laptop's local time) as a UTC ISO string."""
    start = datetime.now().astimezone().replace(hour=0, minute=0, second=0, microsecond=0)
    return start.astimezone(timezone.utc).isoformat(timespec="seconds")


def resolve_lesson(conn, message: dict):
    """The lesson a message is about: the one replied to, else the latest."""
    reply = message.get("reply_to_message")
    if reply:
        lesson_id = db.find_lesson_id_by_message(conn, reply["message_id"])
        if lesson_id:
            return db.get_lesson(conn, lesson_id)
    return db.latest_lesson(conn)


def handle_reaction(reaction: dict, cfg: Config, conn) -> None:
    """Store a 👍/👎-style reaction against the lesson the reacted-to message belongs to."""
    if reaction.get("chat", {}).get("id") != cfg.owner_chat_id:
        log.warning("ignored a reaction from a non-owner chat")
        return
    lesson_id = db.find_lesson_id_by_message(conn, reaction.get("message_id"))
    if lesson_id is None:
        return  # a message that isn't part of any lesson
    db.set_feedback(conn, lesson_id, reactions.pick_reaction(reaction.get("new_reaction", [])))


def handle_update(update: dict, cfg: Config, conn, tg: TelegramClient, answer_fn) -> None:
    if "message_reaction" in update:
        handle_reaction(update["message_reaction"], cfg, conn)
        return

    message = update.get("message")
    if not message:
        return

    chat_id = message.get("chat", {}).get("id")
    if chat_id != cfg.owner_chat_id:
        # Silently ignore everyone else. Never log their content.
        log.warning("ignored a message from a non-owner chat")
        return

    text = message.get("text")
    if not text:
        tg.send_message(chat_id, "I can only read text messages.")
        return

    if text.startswith("/"):
        tg.send_message(chat_id, HELP_TEXT)
        return

    lesson = resolve_lesson(conn, message)
    if lesson is None:
        tg.send_message(chat_id, "No lesson yet. The first one arrives at the next scheduled time.")
        return

    if db.count_user_messages_since(conn, local_day_start_utc()) >= cfg.daily_question_limit:
        tg.send_message(chat_id, f"Daily question limit ({cfg.daily_question_limit}) reached. Try again tomorrow.")
        return

    history = db.messages_for_lesson(conn, lesson["id"])
    try:
        raw = answer_fn(lesson, history, text)
        if lesson["kind"] == "drill":
            answer, grade = qa.parse_grade(raw)
        else:
            answer, grade = raw.strip(), None
        if not answer:
            raise qa.AnswerError("empty reply after parsing")
    except Exception as e:  # OpenAI down, bad model name, empty reply...
        log.error("could not get an answer: %s", type(e).__name__)
        tg.send_message(chat_id, "Sorry, I couldn't get an answer just now. Try again in a minute.")
        return

    # Store only after a successful answer, so a failed attempt can simply be re-sent.
    reply_ids = tg.send_message(chat_id, answer, reply_to_message_id=message["message_id"])
    db.add_message(conn, lesson["id"], "user", text, [message["message_id"]], grade=grade)
    db.add_message(conn, lesson["id"], "assistant", answer, reply_ids)


def process_updates(updates: list[dict], cfg: Config, conn, tg, answer_fn) -> None:
    """Handle updates in order, saving the offset after each one.

    Temporary failures (Telegram/network) stop processing without advancing the
    offset, so the update is retried. Anything else is logged and skipped so one
    bad message can never block the queue.
    """
    for update in updates:
        try:
            handle_update(update, cfg, conn, tg, answer_fn)
        except TelegramError as e:
            if e.retryable:
                raise
            log.error("skipping update after Telegram error: %s", e)
        except httpx.HTTPError:
            raise
        except Exception:
            log.exception("unexpected error handling an update; skipping it")
        db.set_state(conn, "tg_offset", str(update["update_id"] + 1))


def run(cfg: Config) -> None:
    conn = db.connect(cfg.db_path)
    tg = TelegramClient(cfg.telegram_bot_token)
    answer_fn = qa.make_answerer(cfg)
    backoff = 5
    log.info("bot started")
    while True:
        try:
            offset = int(db.get_state(conn, "tg_offset", "0"))
            updates = tg.get_updates(offset)
            process_updates(updates, cfg, conn, tg, answer_fn)
            backoff = 5
        except (TelegramError, httpx.HTTPError) as e:
            # Log the type only: some messages can contain the request URL, which holds the token.
            log.warning("temporary problem (%s); retrying in %ss", type(e).__name__, backoff)
            time.sleep(backoff)
            backoff = min(backoff * 2, 60)


def whoami(cfg: Config) -> None:
    """Print the chat ID of the first message received, to fill TELEGRAM_OWNER_CHAT_ID."""
    tg = TelegramClient(cfg.telegram_bot_token)
    print("Send any message to your bot in Telegram now (Ctrl+C to cancel)...")
    while True:
        for update in tg.get_updates():
            message = update.get("message")
            if message:
                chat = message["chat"]
                print(f"Your chat ID is: {chat['id']}  (name: {chat.get('first_name', '?')})")
                print("Put it in .env as TELEGRAM_OWNER_CHAT_ID")
                tg.get_updates(offset=update["update_id"] + 1, timeout=0)  # mark as read
                return


def setup_logging() -> None:
    (ROOT / "data").mkdir(exist_ok=True)
    fmt = logging.Formatter("%(asctime)s %(levelname)s %(message)s")
    file_handler = RotatingFileHandler(ROOT / "data" / "bot.log", maxBytes=1_000_000, backupCount=3, encoding="utf-8")
    file_handler.setFormatter(fmt)
    console = logging.StreamHandler()
    console.setFormatter(fmt)
    logging.basicConfig(level=logging.INFO, handlers=[file_handler, console])
    logging.getLogger("httpx").setLevel(logging.WARNING)  # httpx logs full URLs, which hold the token


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Interview-prep Telegram bot")
    parser.add_argument("--whoami", action="store_true", help="print your Telegram chat ID and exit")
    args = parser.parse_args(argv)

    setup_logging()
    try:
        if args.whoami:
            whoami(load_config(need=("telegram_bot_token",)))
        else:
            run(load_config(need=("telegram_bot_token", "owner_chat_id", "openai_api_key", "openai_model")))
    except ConfigError as e:
        print(f"Config problem: {e}", file=sys.stderr)
        return 2
    except KeyboardInterrupt:
        log.info("stopped")
    return 0


if __name__ == "__main__":
    sys.exit(main())
