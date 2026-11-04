from bot import db


def make(tmp_path):
    return db.connect(tmp_path / "test.db")


def test_reply_to_any_message_finds_the_lesson(tmp_path):
    conn = make(tmp_path)
    lesson = db.add_lesson(conn, track="ai", topic="Tokens", text="t", telegram_message_ids=[100])
    db.add_message(conn, lesson, "user", "q", [101])
    db.add_message(conn, lesson, "assistant", "a", [102, 103])  # long answer sent in 2 parts

    for mid in (100, 101, 102, 103):
        assert db.find_lesson_id_by_message(conn, mid) == lesson
    assert db.find_lesson_id_by_message(conn, 999) is None


def test_latest_lesson_and_messages_are_ordered(tmp_path):
    conn = make(tmp_path)
    first = db.add_lesson(conn, track="ai", topic="A", text="a", telegram_message_ids=[1])
    second = db.add_lesson(conn, track="data", topic="B", text="b", telegram_message_ids=[2])
    assert db.latest_lesson(conn)["id"] == second

    db.add_message(conn, first, "user", "one", [3])
    db.add_message(conn, first, "assistant", "two", [4])
    texts = [m["text"] for m in db.messages_for_lesson(conn, first)]
    assert texts == ["one", "two"]
    assert db.messages_for_lesson(conn, second) == []


def test_slot_is_unique(tmp_path):
    conn = make(tmp_path)
    db.add_lesson(conn, track="ai", topic="A", text="a", telegram_message_ids=[1], slot="2026-11-05T09:00")
    assert db.lesson_exists_for_slot(conn, "2026-11-05T09:00")
    assert not db.lesson_exists_for_slot(conn, "2026-11-05T11:30")


def test_question_count_only_counts_user_messages_since(tmp_path):
    conn = make(tmp_path)
    lesson = db.add_lesson(conn, track="ai", topic="A", text="a", telegram_message_ids=[1])
    db.add_message(conn, lesson, "user", "q1", [2])
    db.add_message(conn, lesson, "assistant", "a1", [3])
    assert db.count_user_messages_since(conn, "2000-01-01T00:00:00+00:00") == 1
    assert db.count_user_messages_since(conn, "2999-01-01T00:00:00+00:00") == 0


def test_state_roundtrip(tmp_path):
    conn = make(tmp_path)
    assert db.get_state(conn, "tg_offset", "0") == "0"
    db.set_state(conn, "tg_offset", "42")
    db.set_state(conn, "tg_offset", "43")
    assert db.get_state(conn, "tg_offset") == "43"
