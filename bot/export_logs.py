"""Export new Q&A from SQLite to learning/logs/YYYY-MM-DD.md for Claude to read.

Run:  python -m bot.export_logs
Only messages and lessons newer than the saved cursors are exported, so each
run is incremental. The full history always stays in SQLite.
"""
from __future__ import annotations

import sqlite3
import sys
from datetime import datetime
from pathlib import Path

from . import db
from .config import ROOT, load_config

LOGS_DIR = ROOT / "learning" / "logs"
MSG_CURSOR = "export_msg_cursor"
LESSON_CURSOR = "export_lesson_cursor"


def _local(iso_utc: str) -> str:
    return datetime.fromisoformat(iso_utc).astimezone().strftime("%Y-%m-%d %H:%M")


def render_export(conn: sqlite3.Connection) -> tuple[str, int, int] | None:
    """Build the markdown for everything new. Returns (text, msg_cursor, lesson_cursor)
    or None if there is nothing new."""
    msg_cursor = int(db.get_state(conn, MSG_CURSOR, "0"))
    lesson_cursor = int(db.get_state(conn, LESSON_CURSOR, "0"))

    new_lessons = conn.execute("SELECT * FROM lessons WHERE id > ? ORDER BY id", (lesson_cursor,)).fetchall()
    new_messages = conn.execute(
        "SELECT m.*, l.topic, l.track, l.kind, l.sent_at AS lesson_sent_at "
        "FROM messages m JOIN lessons l ON l.id = m.lesson_id "
        "WHERE m.id > ? ORDER BY m.lesson_id, m.id",
        (msg_cursor,),
    ).fetchall()
    if not new_lessons and not new_messages:
        return None

    lines: list[str] = [f"# Export {datetime.now().astimezone().strftime('%Y-%m-%d %H:%M')}", ""]

    if new_lessons:
        lines.append("## Lessons sent since last export")
        for les in new_lessons:
            questions = conn.execute(
                "SELECT COUNT(*) AS n FROM messages WHERE lesson_id = ? AND role = 'user'", (les["id"],)
            ).fetchone()["n"]
            lines.append(
                f"- Lesson {les['id']} [{les['track']}, {les['kind']}] {les['topic']} "
                f"(sent {_local(les['sent_at'])}) — {questions} question(s) so far"
            )
        lines.append("")

    if new_messages:
        lines.append("## Conversations")
        current = None
        for m in new_messages:
            if m["lesson_id"] != current:
                current = m["lesson_id"]
                lines += [
                    "",
                    f"### Lesson {m['lesson_id']} [{m['track']}, {m['kind']}]: {m['topic']}",
                ]
            who = "Ayush" if m["role"] == "user" else "Tutor"
            grade = f" (drill grade: {m['grade']}/5)" if m["grade"] else ""
            lines.append(f"**{who}** ({_local(m['created_at'])}){grade}: {m['text']}")
        lines.append("")

    max_msg = max([msg_cursor] + [m["id"] for m in new_messages])
    max_lesson = max([lesson_cursor] + [l["id"] for l in new_lessons])
    return "\n".join(lines), max_msg, max_lesson


def export(conn: sqlite3.Connection, logs_dir: Path = LOGS_DIR) -> Path | None:
    """Append the new export to today's log file, then advance the cursors."""
    result = render_export(conn)
    if result is None:
        return None
    text, msg_cursor, lesson_cursor = result
    logs_dir.mkdir(parents=True, exist_ok=True)
    path = logs_dir / f"{datetime.now().astimezone().strftime('%Y-%m-%d')}.md"
    with path.open("a", encoding="utf-8") as f:
        f.write(text + "\n")
    # Cursors move only after the file is safely written.
    db.set_state(conn, MSG_CURSOR, str(msg_cursor))
    db.set_state(conn, LESSON_CURSOR, str(lesson_cursor))
    return path


def main() -> int:
    cfg = load_config()
    conn = db.connect(cfg.db_path)
    path = export(conn)
    print(f"exported to {path}" if path else "nothing new to export")
    return 0


if __name__ == "__main__":
    sys.exit(main())
