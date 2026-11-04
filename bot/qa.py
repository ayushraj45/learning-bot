"""Follow-up Q&A: build the OpenAI prompt from one lesson and its conversation."""
from __future__ import annotations

import re
from typing import Callable, Sequence

from .config import Config

# Sanity cap only. Smarter trimming of long threads is deliberately deferred.
MAX_HISTORY_MESSAGES = 40

SYSTEM_PROMPT = """You are Ayush's interview-prep tutor. He is a software engineer (strong in \
JavaScript/TypeScript, knows OOP and general programming) preparing for mid-level AI engineer and \
data engineer interviews in the UK. He reads on his phone in Telegram.

Rules:
- Answer the question about the lesson below. Be accurate, direct and concise: a few short paragraphs at most, \
unless he asks for depth.
- Plain language first. One everyday analogy or small example is welcome. Explain jargon the first time.
- Never teach programming basics. Use JavaScript/TypeScript comparisons for Python or code where helpful.
- Tie the answer back to how it is asked in interviews when natural.
- If you are not sure about something, say so rather than guess.
- No behavioural-interview coaching. If a question drifts off topic, answer briefly and steer back.
- Light formatting only: **bold** for key terms, `code` for code. No headings or tables."""

DRILL_ADDENDUM = """

This lesson is an INTERVIEW DRILL: the lesson text below is the question he was asked.
- If his message is an attempt at answering it, give concise, honest feedback: what was good, what was \
missing, and a stronger model answer in one or two sentences. Then, on the very last line by itself, write \
GRADE: n/5 (n is 1-5; 3 = acceptable mid-level answer, 5 = excellent).
- If his message is instead a follow-up question or asks for the answer, answer it normally and do NOT \
write a GRADE line."""

GRADE_RE = re.compile(r"^\s*GRADE:\s*([1-5])\s*/\s*5\s*$", re.I | re.M)

AnswerFn = Callable[[dict, Sequence, str], str]


class AnswerError(Exception):
    """The model returned nothing usable."""


def parse_grade(text: str) -> tuple[str, int | None]:
    """Split a trailing 'GRADE: n/5' line off the reply. Returns (clean_text, grade)."""
    matches = list(GRADE_RE.finditer(text))
    if not matches:
        return text.strip(), None
    m = matches[-1]
    cleaned = (text[: m.start()] + text[m.end():]).strip()
    return cleaned, int(m.group(1))


def build_messages(lesson, history: Sequence, question: str) -> list[dict]:
    """System prompt + the lesson + that lesson's conversation + the new question."""
    is_drill = lesson["kind"] == "drill"
    label = "INTERVIEW DRILL QUESTION" if is_drill else "LESSON"
    system = (
        SYSTEM_PROMPT
        + (DRILL_ADDENDUM if is_drill else "")
        + f"\n\n--- {label} (track: {lesson['track']}, topic: {lesson['topic']}) ---\n"
        + f"{lesson['text']}\n--- END {label} ---"
    )
    messages = [{"role": "system", "content": system}]
    for row in list(history)[-MAX_HISTORY_MESSAGES:]:
        messages.append({"role": row["role"], "content": row["text"]})
    messages.append({"role": "user", "content": question})
    return messages


def make_answerer(cfg: Config) -> AnswerFn:
    """Return a function (lesson, history, question) -> reply text using OpenAI."""
    from openai import OpenAI  # imported here so tests don't need a key

    client = OpenAI(api_key=cfg.openai_api_key, timeout=60)

    def answer(lesson, history, question: str) -> str:
        resp = client.chat.completions.create(
            model=cfg.openai_model,
            messages=build_messages(lesson, history, question),
        )
        text = (resp.choices[0].message.content or "").strip()
        if not text:
            raise AnswerError("empty reply from model")
        return text

    return answer
