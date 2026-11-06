import pytest

from bot import alerts, db, export_logs, send_lesson, weekly
from bot.telegram_api import TelegramError

GOOD = """---
track: ai
topic: Tokens and context window
kind: lesson
---
Tokens are chunks of text.

🎯 Interview angle: what is a token?
"""


class FakeTelegram:
    def __init__(self, fail_times=0, code=502):
        self.sent = []
        self.fail_times = fail_times
        self.code = code

    def send_message(self, chat_id, text, reply_to_message_id=None):
        if self.fail_times:
            self.fail_times -= 1
            raise TelegramError("boom", self.code)
        self.sent.append(text)
        return [500 + len(self.sent)]


@pytest.fixture(autouse=True)
def no_sleep(monkeypatch):
    monkeypatch.setattr(send_lesson.time, "sleep", lambda s: None)


def write(tmp_path, content):
    p = tmp_path / "lesson.md"
    p.write_text(content, encoding="utf-8")
    return p


# ---- parsing ---------------------------------------------------------------

def test_parse_valid_lesson(tmp_path):
    lesson = send_lesson.parse_lesson_file(write(tmp_path, GOOD))
    assert lesson["track"] == "ai" and lesson["kind"] == "lesson"
    assert lesson["topic"] == "Tokens and context window"
    assert lesson["text"].startswith("Tokens are chunks")


def test_parse_tolerates_bom(tmp_path):
    p = tmp_path / "l.md"
    p.write_bytes(b"\xef\xbb\xbf" + GOOD.encode("utf-8"))
    assert send_lesson.parse_lesson_file(p)["track"] == "ai"


@pytest.mark.parametrize(
    "content",
    [
        "no front matter at all",
        GOOD.replace("track: ai", "track: music"),
        GOOD.replace("kind: lesson", "kind: essay"),
        GOOD.replace("topic: Tokens and context window", "topic:"),
        "---\ntrack: ai\ntopic: x\nkind: lesson\n---\n",
        GOOD + ("word " * 800),
    ],
)
def test_parse_rejects_bad_files(tmp_path, content):
    with pytest.raises(send_lesson.LessonFormatError):
        send_lesson.parse_lesson_file(write(tmp_path, content))


# ---- sending ---------------------------------------------------------------

def test_send_records_lesson_and_removes_file(tmp_path):
    conn = db.connect(tmp_path / "t.db")
    path = write(tmp_path, GOOD)
    tg = FakeTelegram()
    lesson_id = send_lesson.send_lesson(conn, tg, 1, path, "2026-11-05T09:00")

    assert not path.exists()
    assert "AI development" in tg.sent[0] and "**Tokens and context window**" in tg.sent[0]
    row = db.get_lesson(conn, lesson_id)
    assert row["slot"] == "2026-11-05T09:00" and row["telegram_message_id"] == 501
    assert db.find_lesson_id_by_message(conn, 501) == lesson_id  # replies will find it


def test_drill_is_formatted_as_a_question(tmp_path):
    conn = db.connect(tmp_path / "t.db")
    path = write(tmp_path, GOOD.replace("kind: lesson", "kind: drill"))
    tg = FakeTelegram()
    send_lesson.send_lesson(conn, tg, 1, path, None)
    assert "Interview drill" in tg.sent[0] and "Reply to this message" in tg.sent[0]


def test_temporary_telegram_error_is_retried(tmp_path):
    conn = db.connect(tmp_path / "t.db")
    tg = FakeTelegram(fail_times=2, code=502)
    send_lesson.send_lesson(conn, tg, 1, write(tmp_path, GOOD), None)
    assert len(tg.sent) == 1


def test_failed_send_keeps_file_and_records_nothing(tmp_path):
    conn = db.connect(tmp_path / "t.db")
    path = write(tmp_path, GOOD)
    with pytest.raises(TelegramError):
        send_lesson.send_lesson(conn, FakeTelegram(fail_times=5, code=400), 1, path, "slot")
    assert path.exists()
    assert db.latest_lesson(conn) is None


# ---- export ----------------------------------------------------------------

def test_export_is_incremental_and_includes_grades(tmp_path):
    conn = db.connect(tmp_path / "t.db")
    logs = tmp_path / "logs"
    drill = db.add_lesson(conn, track="data", topic="RANK vs DENSE_RANK", text="Q?", telegram_message_ids=[1], kind="drill")
    quiet = db.add_lesson(conn, track="ai", topic="Quiet lesson", text="t", telegram_message_ids=[2])
    db.add_message(conn, drill, "user", "RANK skips after ties", [3], grade=4)
    db.add_message(conn, drill, "assistant", "Good.", [4])

    path = export_logs.export(conn, logs)
    text = path.read_text(encoding="utf-8")
    assert "drill grade: 4/5" in text and "RANK skips after ties" in text
    assert "Quiet lesson" in text and "0 question(s)" in text

    assert export_logs.export(conn, logs) is None  # nothing new

    db.add_message(conn, quiet, "user", "what is a token?", [5])
    db.add_message(conn, quiet, "assistant", "a chunk", [6])
    second = export_logs.export(conn, logs).read_text(encoding="utf-8")
    assert "what is a token?" in second
    assert "RANK skips after ties" not in second.split("# Export")[-1]  # old content not repeated


def test_export_includes_reactions_once_and_null_means_no_signal(tmp_path):
    conn = db.connect(tmp_path / "t.db")
    logs = tmp_path / "logs"
    lesson = db.add_lesson(conn, track="data", topic="Window functions", text="t", telegram_message_ids=[1])
    db.set_feedback(conn, lesson, "👍")
    text = export_logs.export(conn, logs).read_text(encoding="utf-8")
    assert "Window functions" in text and "👍 = got it" in text

    assert export_logs.export(conn, logs) is None  # reaction already exported

    db.set_feedback(conn, lesson, None)  # reaction removed
    second = export_logs.export(conn, logs).read_text(encoding="utf-8").split("# Export")[-1]
    assert "reaction removed" in second and "👍" not in second


# ---- alerts ----------------------------------------------------------------

def test_expired_login_gets_a_helpful_message():
    msg = alerts.failure_message("Lesson run failed", "Failed to authenticate: OAuth session expired")
    assert "claude auth login" in msg


def test_usage_limit_message():
    assert "usage limit" in alerts.failure_message("x", "Claude AI usage limit reached").lower()


def test_unknown_failure_includes_output_tail():
    msg = alerts.failure_message("Lesson run failed", "something weird happened")
    assert "something weird happened" in msg


def test_alert_without_config_does_not_raise(monkeypatch):
    monkeypatch.delenv("TELEGRAM_BOT_TOKEN", raising=False)
    monkeypatch.setattr("bot.config.load_dotenv", lambda *a, **k: None)
    assert alerts.send_alert("hi") is False


# ---- weekly marker ---------------------------------------------------------

def test_iso_week_format():
    from datetime import date
    assert weekly.current_week(date(2026, 11, 4)) == "2026-W45"
    assert weekly.current_week(date(2026, 1, 1)) == "2026-W01"


def test_challenge_ping_names_the_dated_file():
    assert "coding-challenges/2026-11-06.md" in alerts.challenge_message("coding-challenges/2026-11-06.md")


def test_lessons_are_numbered_in_order_and_number_is_shown(tmp_path):
    conn = db.connect(tmp_path / "t.db")
    tg = FakeTelegram()
    ids = [send_lesson.send_lesson(conn, tg, 1, write(tmp_path, GOOD), None) for _ in range(2)]
    drill = send_lesson.send_lesson(conn, tg, 1, write(tmp_path, GOOD.replace("kind: lesson", "kind: drill")), None)
    assert ids == [1, 2] and drill == 3
    assert tg.sent[0].startswith("#1 · ") and tg.sent[1].startswith("#2 · ")
    assert "#3 · Interview drill" in tg.sent[2]


def test_numbering_continues_after_existing_lessons(tmp_path):
    conn = db.connect(tmp_path / "t.db")
    for _ in range(10):
        db.add_lesson(conn, track="ai", topic="t", text="t", telegram_message_ids=[])
    tg = FakeTelegram()
    assert send_lesson.send_lesson(conn, tg, 1, write(tmp_path, GOOD), None) == 11
    assert tg.sent[0].startswith("#11 · ")


def test_failed_send_does_not_use_up_a_number(tmp_path):
    conn = db.connect(tmp_path / "t.db")
    with pytest.raises(TelegramError):
        send_lesson.send_lesson(conn, FakeTelegram(fail_times=5, code=400), 1, write(tmp_path, GOOD), None)
    assert send_lesson.send_lesson(conn, FakeTelegram(), 1, write(tmp_path, GOOD), None) == 1
