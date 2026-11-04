"""Consistent daily copy of the SQLite database, keeping the newest 14.

Run:  python -m bot.backup
Uses SQLite's own backup API, which is safe while the bot is writing
(copying the .db file directly is not, because of WAL mode).
"""
from __future__ import annotations

import sqlite3
import sys
from datetime import date
from pathlib import Path

from .config import ROOT, load_config

BACKUP_DIR = ROOT / "data" / "backups"
KEEP = 14


def backup(db_path: Path, backup_dir: Path = BACKUP_DIR, keep: int = KEEP, today: date | None = None) -> Path:
    backup_dir.mkdir(parents=True, exist_ok=True)
    dest = backup_dir / f"learning-{(today or date.today()).isoformat()}.db"
    dest.unlink(missing_ok=True)  # a second run on the same day replaces the first

    src = sqlite3.connect(db_path)
    dst = sqlite3.connect(dest)
    try:
        src.backup(dst)
    finally:
        dst.close()
        src.close()

    for old in sorted(backup_dir.glob("learning-*.db"))[:-keep]:
        old.unlink()
    return dest


def main() -> int:
    cfg = load_config()
    if not cfg.db_path.exists():
        print("no database yet; nothing to back up")
        return 0
    print(f"backed up to {backup(cfg.db_path)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
