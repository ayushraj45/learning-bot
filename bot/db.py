"""SQLite storage: lessons, messages, Telegram message-id references, small state."""
from __future__ import annotations

import sqlite3
from datetime import datetime, timezone
from pathlib import Path

SCHEMA = """
CREATE TABLE IF NOT EXISTS lessons (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    slot TEXT UNIQUE,                 -- e.g. '2026-11-05T11:30'; NULL allowed for manual lessons
    track TEXT NOT NULL,              -- 'ai' | 'data'
    topic TEXT NOT NULL,
    kind TEXT NOT NULL DEFAULT 'lesson',   -- 'lesson' | 'drill'
    text TEXT NOT NULL,
    telegram_message_id INTEGER,      -- first Telegram message of the lesson
    sent_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS messages (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    lesson_id INTEGER NOT NULL REFERENCES lessons(id),
    role TEXT NOT NULL CHECK (role IN ('user', 'assistant')),
    text TEXT NOT NULL,
    telegram_message_id INTEGER,      -- first Telegram message of this entry
    created_at TEXT NOT NULL,
    grade INTEGER CHECK (grade BETWEEN 1 AND 5)  -- only on graded drill answers (user rows)
);
CREATE INDEX IF NOT EXISTS idx_messages_lesson ON messages(lesson_id, id);

-- Every Telegram message id we send or receive maps to its lesson, so a reply
-- to ANY of them (even one chunk of a long answer) finds the right lesson.
CREATE TABLE IF NOT EXISTS telegram_refs (
    telegram_message_id INTEGER PRIMARY KEY,
    lesson_id INTEGER NOT NULL REFERENCES lessons(id)
);

CREATE TABLE IF NOT EXISTS state (
    key TEXT PRIMARY KEY,
    value TEXT NOT NULL
);
"""


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def connect(path: Path | str) -> sqlite3.Connection:
    """Open (and create if needed) the database. WAL lets the bot and the
    lesson script use the file at the same time."""
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(path, timeout=30)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode=WAL")
    conn.execute("PRAGMA foreign_keys=ON")
    conn.executescript(SCHEMA)
    return conn


# ---- lessons ---------------------------------------------------------------

def add_lesson(
    conn: sqlite3.Connection,
    *,
    track: str,
    topic: str,
    text: str,
    telegram_message_ids: list[int],
    kind: str = "lesson",
    slot: str | None = None,
    sent_at: str | None = None,
) -> int:
    with conn:
        cur = conn.execute(
            "INSERT INTO lessons (slot, track, topic, kind, text, telegram_message_id, sent_at) "
            "VALUES (?, ?, ?, ?, ?, ?, ?)",
            (
                slot,
                track,
                topic,
                kind,
                text,
                telegram_message_ids[0] if telegram_message_ids else None,
                sent_at or utc_now(),
            ),
        )
        lesson_id = cur.lastrowid
        _add_refs(conn, lesson_id, telegram_message_ids)
    return lesson_id


def lesson_exists_for_slot(conn: sqlite3.Connection, slot: str) -> bool:
    row = conn.execute("SELECT 1 FROM lessons WHERE slot = ?", (slot,)).fetchone()
    return row is not None


def get_lesson(conn: sqlite3.Connection, lesson_id: int) -> sqlite3.Row | None:
    return conn.execute("SELECT * FROM lessons WHERE id = ?", (lesson_id,)).fetchone()


def latest_lesson(conn: sqlite3.Connection) -> sqlite3.Row | None:
    return conn.execute("SELECT * FROM lessons ORDER BY id DESC LIMIT 1").fetchone()


# ---- messages --------------------------------------------------------------

def add_message(
    conn: sqlite3.Connection,
    lesson_id: int,
    role: str,
    text: str,
    telegram_message_ids: list[int] | None = None,
    grade: int | None = None,
) -> int:
    ids = telegram_message_ids or []
    with conn:
        cur = conn.execute(
            "INSERT INTO messages (lesson_id, role, text, telegram_message_id, created_at, grade) "
            "VALUES (?, ?, ?, ?, ?, ?)",
            (lesson_id, role, text, ids[0] if ids else None, utc_now(), grade),
        )
        _add_refs(conn, lesson_id, ids)
    return cur.lastrowid


def messages_for_lesson(conn: sqlite3.Connection, lesson_id: int) -> list[sqlite3.Row]:
    return conn.execute(
        "SELECT * FROM messages WHERE lesson_id = ? ORDER BY id", (lesson_id,)
    ).fetchall()


def count_user_messages_since(conn: sqlite3.Connection, since_utc_iso: str) -> int:
    row = conn.execute(
        "SELECT COUNT(*) AS n FROM messages WHERE role = 'user' AND created_at >= ?",
        (since_utc_iso,),
    ).fetchone()
    return row["n"]


# ---- Telegram message-id references -----------------------------------------

def _add_refs(conn: sqlite3.Connection, lesson_id: int, message_ids: list[int]) -> None:
    for mid in message_ids:
        conn.execute(
            "INSERT OR REPLACE INTO telegram_refs (telegram_message_id, lesson_id) VALUES (?, ?)",
            (mid, lesson_id),
        )


def find_lesson_id_by_message(conn: sqlite3.Connection, telegram_message_id: int) -> int | None:
    row = conn.execute(
        "SELECT lesson_id FROM telegram_refs WHERE telegram_message_id = ?",
        (telegram_message_id,),
    ).fetchone()
    return row["lesson_id"] if row else None


# ---- small key/value state --------------------------------------------------

def get_state(conn: sqlite3.Connection, key: str, default: str | None = None) -> str | None:
    row = conn.execute("SELECT value FROM state WHERE key = ?", (key,)).fetchone()
    return row["value"] if row else default


def set_state(conn: sqlite3.Connection, key: str, value: str) -> None:
    with conn:
        conn.execute(
            "INSERT INTO state (key, value) VALUES (?, ?) "
            "ON CONFLICT(key) DO UPDATE SET value = excluded.value",
            (key, value),
        )
