from bot import qa
from bot.telegram_api import split_text, to_html


LESSON = {"kind": "lesson", "track": "ai", "topic": "Tokens", "text": "Tokens are chunks."}
DRILL = {"kind": "drill", "track": "data", "topic": "Window functions", "text": "Explain RANK vs DENSE_RANK."}


def test_parse_grade_strips_the_grade_line():
    text, grade = qa.parse_grade("Good start, missed ties.\n\nGRADE: 3/5")
    assert text == "Good start, missed ties."
    assert grade == 3


def test_parse_grade_absent_or_out_of_range():
    assert qa.parse_grade("Just an answer.") == ("Just an answer.", None)
    assert qa.parse_grade("Hmm.\nGRADE: 9/5")[1] is None


def test_build_messages_contains_lesson_history_and_question():
    history = [{"role": "user", "text": "what is a token?"}, {"role": "assistant", "text": "a chunk"}]
    msgs = qa.build_messages(LESSON, history, "and a context window?")
    assert msgs[0]["role"] == "system" and "Tokens are chunks." in msgs[0]["content"]
    assert "GRADE" not in msgs[0]["content"]
    assert [m["role"] for m in msgs[1:]] == ["user", "assistant", "user"]
    assert msgs[-1]["content"] == "and a context window?"


def test_drill_prompt_asks_for_a_grade():
    msgs = qa.build_messages(DRILL, [], "RANK skips numbers after ties")
    assert "GRADE: n/5" in msgs[0]["content"]
    assert "INTERVIEW DRILL QUESTION" in msgs[0]["content"]


def test_history_is_capped():
    history = [{"role": "user", "text": str(i)} for i in range(100)]
    msgs = qa.build_messages(LESSON, history, "q")
    assert len(msgs) == 1 + qa.MAX_HISTORY_MESSAGES + 1


def test_split_text_respects_limit_and_loses_nothing():
    text = "\n\n".join(["word " * 200] * 10)
    parts = split_text(text, limit=1000)
    assert all(len(p) <= 1000 for p in parts)
    assert "".join(parts).replace(" ", "").replace("\n", "") == text.replace(" ", "").replace("\n", "")


def test_short_text_is_one_part():
    assert split_text("hello") == ["hello"]


def test_to_html_escapes_and_formats():
    assert to_html("**bold** and `code` <b>") == "<b>bold</b> and <code>code</code> &lt;b&gt;"
    assert to_html("```py\nx = 1\n```") == "<pre>x = 1\n</pre>"
