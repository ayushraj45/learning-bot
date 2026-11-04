"""Telegram alerts for the scripts: run failures and "challenge ready".

Run:
  python -m bot.alerts failure --reason "Lesson run failed" [--output-file path]
  python -m bot.alerts challenge
Alerts never raise: a broken alert must not hide the original problem.
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

from .config import ConfigError, load_config
from .telegram_api import TelegramClient

CHALLENGE_TEXT = (
    "💻 Today's coding challenge is ready. Open learning/coding-challenge.md "
    "in Claude Code whenever you have time."
)


def classify_claude_failure(output: str) -> str | None:
    """Turn raw `claude -p` output into a friendly cause, if it's a known one."""
    low = output.lower()
    if any(s in low for s in ("oauth", "failed to authenticate", "not logged in", "please log in", "invalid api key")):
        return "Claude sign-in has expired. Open a normal terminal and run: claude auth login (or claude setup-token)."
    if any(s in low for s in ("usage limit", "limit reached", "rate limit", "too many requests")):
        return "Claude usage limit reached. The next scheduled run will try again."
    return None


def failure_message(reason: str, output: str = "") -> str:
    cause = classify_claude_failure(output) if output else None
    if cause:
        return f"⚠️ {reason}\n{cause}"
    tail = output.strip()[-300:]
    return f"⚠️ {reason}" + (f"\n\nLast output:\n{tail}" if tail else "")


def send_alert(text: str) -> bool:
    """Send a message to the owner. Returns False (never raises) if it can't."""
    try:
        cfg = load_config(need=("telegram_bot_token", "owner_chat_id"))
        TelegramClient(cfg.telegram_bot_token).send_message(cfg.owner_chat_id, text)
        return True
    except ConfigError as e:
        print(f"alert not sent: {e}", file=sys.stderr)
    except Exception as e:  # network, Telegram error...
        print(f"alert not sent: {type(e).__name__}", file=sys.stderr)
    return False


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    sub = parser.add_subparsers(dest="cmd", required=True)
    fail = sub.add_parser("failure")
    fail.add_argument("--reason", required=True)
    fail.add_argument("--output-file")
    sub.add_parser("challenge")
    args = parser.parse_args(argv)

    if args.cmd == "challenge":
        ok = send_alert(CHALLENGE_TEXT)
    else:
        output = ""
        if args.output_file and Path(args.output_file).exists():
            output = Path(args.output_file).read_text(encoding="utf-8-sig", errors="replace")
        ok = send_alert(failure_message(args.reason, output))
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
