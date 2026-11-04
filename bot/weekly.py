"""Tracks which ISO week the weekly synthesis last ran, so it runs once a week.

  python -m bot.weekly week    -> prints this ISO week, e.g. 2026-W45
  python -m bot.weekly check   -> exit 3 if this week's synthesis is already done, else 0
  python -m bot.weekly mark    -> record this week as done
"""
from __future__ import annotations

import sys
from datetime import date

from . import db
from .config import load_config

STATE_KEY = "weekly_done"


def current_week(today: date | None = None) -> str:
    year, week, _ = (today or date.today()).isocalendar()
    return f"{year}-W{week:02d}"


def main(argv: list[str] | None = None) -> int:
    args = argv if argv is not None else sys.argv[1:]
    cmd = args[0] if args else ""
    if cmd == "week":
        print(current_week())
        return 0
    conn = db.connect(load_config().db_path)
    if cmd == "check":
        return 3 if db.get_state(conn, STATE_KEY) == current_week() else 0
    if cmd == "mark":
        db.set_state(conn, STATE_KEY, current_week())
        return 0
    print("usage: python -m bot.weekly week|check|mark", file=sys.stderr)
    return 1


if __name__ == "__main__":
    sys.exit(main())
