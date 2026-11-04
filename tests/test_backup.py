from datetime import date, timedelta

from bot import backup, db


def test_backup_is_a_readable_copy(tmp_path):
    conn = db.connect(tmp_path / "live.db")
    db.add_lesson(conn, track="ai", topic="Tokens", text="t", telegram_message_ids=[1])

    dest = backup.backup(tmp_path / "live.db", tmp_path / "backups", today=date(2026, 11, 4))
    assert dest.name == "learning-2026-11-04.db"

    copy = db.connect(dest)
    assert db.latest_lesson(copy)["topic"] == "Tokens"


def test_only_newest_backups_are_kept(tmp_path):
    db.connect(tmp_path / "live.db").close()
    start = date(2026, 11, 1)
    for i in range(20):
        backup.backup(tmp_path / "live.db", tmp_path / "backups", keep=14, today=start + timedelta(days=i))
    names = sorted(p.name for p in (tmp_path / "backups").glob("*.db"))
    assert len(names) == 14
    assert names[0] == "learning-2026-11-07.db" and names[-1] == "learning-2026-11-20.db"


def test_second_backup_same_day_replaces_first(tmp_path):
    db.connect(tmp_path / "live.db").close()
    for _ in range(2):
        backup.backup(tmp_path / "live.db", tmp_path / "backups", today=date(2026, 11, 4))
    assert len(list((tmp_path / "backups").glob("*.db"))) == 1
