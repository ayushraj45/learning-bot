import pytest

from bot import bot, db
from bot.config import Config
from bot.telegram_api import TelegramError

OWNER = 111
STRANGER = 999


class FakeTelegram:
    def __init__(self):
        self.sent = []  # (chat_id, text, reply_to)
        self._next_id = 1000

    def send_message(self, chat_id, text, reply_to_message_id=None):
        self.sent.append((chat_id, text, reply_to_message_id))
        self._next_id += 1
        return [self._next_id]


@pytest.fixture
def env(tmp_path):
    cfg = Config(
        telegram_bot_token="x",
        owner_chat_id=OWNER,
        openai_api_key="x",
        openai_model="m",
        daily_question_limit=60,
        db_path=tmp_path / "t.db",
    )
    conn = db.connect(cfg.db_path)
    tg = FakeTelegram()
    calls = []

    def answer_fn(lesson, history, question):
        calls.append((lesson["id"], len(history), question))
        return f"answer to: {question}"

    return cfg, conn, tg, answer_fn, calls


def msg(text, chat=OWNER, message_id=1, reply_to=None, update_id=1):
    m = {"message_id": message_id, "chat": {"id": chat}, "text": text}
    if reply_to:
        m["reply_to_message"] = {"message_id": reply_to}
    return {"update_id": update_id, "message": m}


def test_stranger_is_ignored_and_openai_never_called(env):
    cfg, conn, tg, answer_fn, calls = env
    db.add_lesson(conn, track="ai", topic="A", text="a", telegram_message_ids=[50])
    bot.handle_update(msg("hi", chat=STRANGER), cfg, conn, tg, answer_fn)
    assert tg.sent == [] and calls == []


def test_plain_message_goes_to_latest_lesson(env):
    cfg, conn, tg, answer_fn, calls = env
    db.add_lesson(conn, track="ai", topic="old", text="old", telegram_message_ids=[50])
    newest = db.add_lesson(conn, track="data", topic="new", text="new", telegram_message_ids=[51])
    bot.handle_update(msg("what is x?"), cfg, conn, tg, answer_fn)
    assert calls[0][0] == newest
    assert tg.sent[0][1] == "answer to: what is x?"
    assert [m["role"] for m in db.messages_for_lesson(conn, newest)] == ["user", "assistant"]


def test_reply_to_old_lesson_uses_that_lesson(env):
    cfg, conn, tg, answer_fn, calls = env
    old = db.add_lesson(conn, track="ai", topic="old", text="old", telegram_message_ids=[50])
    db.add_lesson(conn, track="data", topic="new", text="new", telegram_message_ids=[51])
    bot.handle_update(msg("explain more", reply_to=50), cfg, conn, tg, answer_fn)
    assert calls[0][0] == old


def test_reply_to_a_bot_answer_continues_that_lesson(env):
    cfg, conn, tg, answer_fn, calls = env
    old = db.add_lesson(conn, track="ai", topic="old", text="old", telegram_message_ids=[50])
    db.add_lesson(conn, track="data", topic="new", text="new", telegram_message_ids=[51])
    bot.handle_update(msg("first q", message_id=2, reply_to=50), cfg, conn, tg, answer_fn)
    bot_answer_id = db.messages_for_lesson(conn, old)[-1]["telegram_message_id"]
    bot.handle_update(msg("follow up", message_id=3, reply_to=bot_answer_id, update_id=2), cfg, conn, tg, answer_fn)
    assert calls[1][0] == old
    assert calls[1][1] == 2  # it saw the earlier question and answer


def test_no_lessons_yet(env):
    cfg, conn, tg, answer_fn, calls = env
    bot.handle_update(msg("hello"), cfg, conn, tg, answer_fn)
    assert "No lesson yet" in tg.sent[0][1] and calls == []


def test_daily_limit(env):
    cfg, conn, tg, answer_fn, calls = env
    limited = Config(**{**cfg.__dict__, "daily_question_limit": 1})
    db.add_lesson(conn, track="ai", topic="A", text="a", telegram_message_ids=[50])
    bot.handle_update(msg("one"), limited, conn, tg, answer_fn)
    bot.handle_update(msg("two", message_id=2, update_id=2), limited, conn, tg, answer_fn)
    assert len(calls) == 1
    assert "limit" in tg.sent[-1][1]


def test_failed_answer_is_not_stored(env):
    cfg, conn, tg, _, _ = env
    lesson = db.add_lesson(conn, track="ai", topic="A", text="a", telegram_message_ids=[50])

    def broken(lesson, history, question):
        raise RuntimeError("openai down")

    bot.handle_update(msg("q"), cfg, conn, tg, broken)
    assert "couldn't get an answer" in tg.sent[0][1]
    assert db.messages_for_lesson(conn, lesson) == []


def test_drill_answer_is_graded_and_grade_line_hidden(env):
    cfg, conn, tg, _, _ = env
    drill = db.add_lesson(conn, track="data", topic="D", text="Q?", telegram_message_ids=[50], kind="drill")

    def grader(lesson, history, question):
        return "Decent, but missed ties.\nGRADE: 3/5"

    bot.handle_update(msg("my answer"), cfg, conn, tg, grader)
    assert tg.sent[0][1] == "Decent, but missed ties."
    rows = db.messages_for_lesson(conn, drill)
    assert rows[0]["role"] == "user" and rows[0]["grade"] == 3
    assert rows[1]["grade"] is None


def test_retryable_error_does_not_advance_offset(env):
    cfg, conn, tg, answer_fn, _ = env
    db.add_lesson(conn, track="ai", topic="A", text="a", telegram_message_ids=[50])

    class Flaky(FakeTelegram):
        def send_message(self, *a, **k):
            raise TelegramError("boom", 502)

    with pytest.raises(TelegramError):
        bot.process_updates([msg("q", update_id=7)], cfg, conn, Flaky(), answer_fn)
    assert db.get_state(conn, "tg_offset") is None


def test_bad_update_is_skipped_and_offset_advances(env):
    cfg, conn, tg, _, _ = env
    db.add_lesson(conn, track="ai", topic="A", text="a", telegram_message_ids=[50])

    class Exploding(FakeTelegram):
        def send_message(self, *a, **k):
            raise ValueError("bug")

    bot.process_updates([msg("q", update_id=7)], cfg, conn, Exploding(), lambda *a: "x")
    assert db.get_state(conn, "tg_offset") == "8"
