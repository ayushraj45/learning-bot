# Plan: Telegram Interview-Prep Learning Bot (laptop-only)

## Overview

A personal interview-prep system. Five times each weekday, Windows Task Scheduler runs a script that asks Claude Code (`claude -p`, signed in with the Claude Pro account, no API key) to write one small lesson. The lesson is sent to Telegram and stored in a local SQLite file. A small Python bot running on the laptop listens to Telegram via **long polling** (the laptop makes outbound requests only, so no server, domain, HTTPS or open ports are needed). When the user asks a question, the bot sends the relevant lesson and its Q&A history to OpenAI and replies. Claude keeps its memory in markdown files, which are backed up to a private GitHub repo.

**Everything serves one goal: passing interviews for a new job.** Every lesson ends with an interview angle, and one lesson a day is an interview drill that the bot grades.

**Decisions locked in**
- Laptop-only. No Lightsail, Docker, Caddy, domain or GitHub Action. A move to the cloud is an optional Phase 5.
- Python for the bot (so the user can read and learn it). The user reads code, AI writes it.
- Telegram Bot API used directly over `httpx` (simple, readable) rather than a big bot framework.
- Q&A model is set by `OPENAI_MODEL` in `.env`. Verify the name before first use (the old plan said `gpt-6.1-sol`).
- Replying to **any** lesson message or bot answer loads that lesson's full conversation. A non-reply message goes to the latest lesson. No open/closed state and no "Done" button.
- Schedule (UK time, weekdays), configurable in `scripts/register-tasks.ps1`: **09:00, 11:30, 14:00, 16:30, 19:00**. The coding challenge is generated on the 16:30 run and announced by a Telegram ping.
- Lessons alternate between two tracks: **AI development** and **data engineering**. Each track continues where it left off.

- **Weekly synthesis:** a weekly scheduled run compresses logs, conversations and progress into short digest lines (for example "RAG: covered") so Claude reads less every run and uses less of the Pro allowance. See Step 3.5.
- **Adaptive pacing:** Claude decides the pace from drill grades and the user's questions. It deepens, skips ahead or revisits topics. See Step 1.2.
- **Claude channels evaluated, not used for v1.** The Telegram channel plugin is a real, official feature (research preview). It pushes Telegram messages into an already-open interactive Claude Code session, and Claude replies through it. It would not remove overhead here: it needs a permanently open terminal session and Bun, every question would use the Pro allowance that lessons also need, and all questions would share one growing session instead of one isolated lesson conversation. It also can't share a bot token with our own polling bot. Kept as a later option (Phase 5).
- **OpenAI context trimming** (for conversations over about 20 messages) is deferred until usage shows it matters.

**Confirmed goals**
- Roles: **AI engineer and data engineer**, mid-level (not entry level), UK market, targeting roughly £50–55k+.
- Interview types: concepts, system design, SQL/Python coding. **No behavioural questions.**
- Timeline: no interview date; expected in a couple of months, so the curriculum can go deep and wide.

## Repo layout (target)

```
learning-bot/
├── bot/
│   ├── __init__.py
│   ├── config.py          # load + validate .env
│   ├── db.py              # SQLite schema and queries
│   ├── telegram_api.py    # send_message, get_updates (httpx)
│   ├── qa.py              # build OpenAI context, call model, drill grading
│   ├── bot.py             # long-polling loop (entrypoint)
│   ├── send_lesson.py     # CLI: read outbox/lesson.md, send, record
│   ├── export_logs.py     # CLI: new Q&A -> learning/logs/*.md
│   └── alerts.py          # failure + "challenge ready" messages
├── scripts/
│   ├── run-lesson.ps1     # what Task Scheduler runs
│   ├── start-bot.ps1      # runs the bot (hidden window)
│   └── register-tasks.ps1 # creates the scheduled tasks
├── learning/              # Claude's working folder and memory
│   ├── CLAUDE.md
│   ├── curriculum.md
│   ├── progress.md
│   ├── weak-spots.md
│   ├── question-bank.md
│   ├── coding-challenge.md
│   ├── outbox/            # Claude writes lesson.md here
│   └── logs/              # exported Q&A
├── data/                  # learning.db, backups, run.lock (gitignored)
├── tests/
├── requirements.txt
├── .env.example
└── .gitignore
```

---

## Phase 1: Repo and Claude's Teaching Brain

### Step 1.1: Create the repo skeleton, `.gitignore`, `.env.example`, `requirements.txt`
Run `git init` locally (do not create the GitHub repo yet). `.gitignore` must exclude `.env`, `data/`, `__pycache__/`, `.venv/`. `.env.example` lists `TELEGRAM_BOT_TOKEN`, `TELEGRAM_OWNER_CHAT_ID`, `OPENAI_API_KEY`, `OPENAI_MODEL`, `DAILY_QUESTION_LIMIT`. `requirements.txt`: `httpx`, `openai`, `python-dotenv`, `pytest`. Create a `.venv` and install.

### Step 1.2: Write the teaching rules — `learning/CLAUDE.md`
Contains: who the user is (software engineer, strong in JS/TS, knows OOP, understands RAG conceptually but has not built it, knows agent SDKs and model orchestration, wants Python only where it differs from what they know); the goal (interview prep); the lesson format (one concept, max 2–3 short paragraphs, plain language, one analogy, no unexplained jargon); a mandatory final line `🎯 Interview angle:` with how it's asked and a one-sentence model answer; the rule that the 5th lesson of the day is an **interview drill** (a question for the user to answer in their own words, `kind: drill`); the output contract (write `outbox/lesson.md` with front-matter `track`, `topic`, `kind`, nothing else printed); the memory-update rules (update `progress.md`, `weak-spots.md`, `question-bank.md` every run); the compaction rule (keep `progress.md` under about 150 lines, summarise old entries); **no behavioural-interview content**; and an **Adaptive pacing** section: each module has a level in `progress.md` (`new`, `seen`, `solid`, `mastered`). When the user has few questions on a module and drills in it are graded 4+ out of 5 twice, Claude marks it `solid`, skips the remaining basic lessons and moves to harder material or the next module. When questions pile up or a drill scores 2 or below, Claude adds the concept to `weak-spots.md` and revisits it in a later lesson. Claude may reorder `curriculum.md` and must note the reason in `progress.md`. The curriculum is a living document, never a fixed list.

### Step 1.3: Write the curriculum — `learning/curriculum.md`
Two tracks, ordered modules, each module a list of lesson-sized concepts that Claude expands. Interview-weighted. Starting point:
- **AI development:** LLM fundamentals (tokens, context, sampling) → structured outputs and tool calling → embeddings and vector search → **RAG in depth** (chunking, retrieval, reranking, hybrid search, evaluation, failure modes) → agents beyond the SDK (loops, planning, memory, multi-agent) → harnesses, hooks, MCP → evals and observability → guardrails and prompt-injection security → cost/latency/caching → fine-tuning vs RAG vs prompting → LLM system-design interviews. Python-only items: asyncio, generators, decorators, context managers, typing/pydantic, packaging with uv, the GIL. No OOP or syntax basics.
- **Data engineering:** SQL for interviews (window functions, CTEs, query plans) → data modelling (star schema, SCD, normalisation trade-offs) → ETL vs ELT, batch vs streaming → **Spark** (architecture, partitions, shuffles, joins, skew, tuning) → Kafka and CDC → orchestration (Airflow) → dbt → warehouses and lakehouse (Snowflake/BigQuery, Delta/Iceberg) → data quality and lineage → data system-design interviews, with finance-domain examples.

### Step 1.4: Seed the memory files — `learning/progress.md`, `weak-spots.md`, `question-bank.md`
Empty templates with headings only (per-track "up to" pointer; one line per module with its level, `new`/`seen`/`solid`/`mastered`; weak concepts with date and reason; interview questions already asked, to avoid repeats). Also create `learning/archive/` for weekly digests (Step 3.5).

**Test after this phase:**
- `git status` shows no `.env` or `data/` tracked.
- Running `claude -p` manually in `learning/` produces a valid `outbox/lesson.md` in the agreed format.
- The lesson reads in 1–2 minutes and ends with the interview angle.

**Warnings:**
- Check `claude --help` for the exact flags that restrict tools to Read/Write/Edit in the working folder before relying on them (see Step 3.1).

---

## Phase 2: Bot and Storage

### Step 2.1: Configuration loader — `bot/config.py`
Load `.env`, fail with a clear message if a required value is missing. Never print secret values.

### Step 2.2: SQLite schema and queries — `bot/db.py`
Tables: `lessons(id, slot, track, topic, kind, text, telegram_message_id, sent_at)`, `messages(id, lesson_id, role, text, telegram_message_id, created_at, grade)` (`grade` is a nullable 1–5 score, set only on graded drill answers), `state(key, value)` for the Telegram update offset and the log-export cursor. Also a `telegram_refs(telegram_message_id, lesson_id)` table: every message id we send or receive is stored there, so replying to any part of a long answer still finds the lesson. The `grade` goes on the user's answer row, and the role values are `user`/`assistant`. Functions: add lesson, add message, find lesson by Telegram message id (looks in both tables), latest lesson, messages for lesson, count questions today. Turn on WAL mode so the bot and the lesson script can use the file at once.

### Step 2.3: Telegram wrapper — `bot/telegram_api.py`
`send_message(text, reply_markup=None)` and `get_updates(offset, timeout=30)` over `httpx`. Split messages over 4096 characters. Handle network errors with a short backoff.

### Step 2.4: Q&A logic — `bot/qa.py`
Build the prompt: system prompt + the lesson + that lesson's messages so far + the new question. For `kind: drill` lessons, treat the user's reply as an answer attempt and give concise feedback (what was good, what was missing, a better one-line answer) and end with a machine-readable `GRADE: n/5` line. The bot strips that line from the Telegram reply and stores `n` in `messages.grade`, which feeds adaptive pacing. Call the model named in `OPENAI_MODEL`. No tools are given to this model. Cap the context size.

### Step 2.5: Polling loop with owner check — `bot/bot.py`
Loop on `get_updates`. **Ignore every update whose chat ID isn't `TELEGRAM_OWNER_CHAT_ID`.** Add a `--whoami` flag that prints the chat ID of the first message received, so the user can find theirs. For each owner message: if it's a reply, look up the lesson by the replied-to message id; otherwise use the latest lesson. Save the question, call `qa.py`, send the answer, save the answer with its Telegram message id (so replies to answers also map). Enforce `DAILY_QUESTION_LIMIT`. Save the offset only after handling an update.

**Test after this phase:**
- Insert a fake lesson with a script, send yourself the message, reply to it, and get an answer.
- Reply to a lesson from two lessons ago and to a bot answer; both pick the right lesson.
- A message from a second Telegram account is ignored and nothing is sent to OpenAI.
- Kill and restart the bot mid-conversation; no message is answered twice or lost.

**Warnings:**
- Without the owner check, anyone who finds the bot's username can run up the OpenAI bill.
- Telegram only keeps pending updates for about 24 hours. If the laptop is off longer, older messages are lost.

---

## Phase 3: Lesson Generation Pipeline

### Step 3.1: Export new Q&A — `bot/export_logs.py`
Write messages since the last cursor into `learning/logs/YYYY-MM-DD.md` grouped by lesson (include drill grades), then advance the cursor. Raw log files stay until the next weekly synthesis (Step 3.5) digests and deletes them. The full history always remains in SQLite.

### Step 3.2: Lesson runner — `scripts/run-lesson.ps1`
Takes the slot name as a parameter. Order:
1. **Guards:** skip if a lesson for this slot already exists in the DB, skip if more than 60 minutes past the slot time (missed-run catch-up rule), skip if `data/run.lock` is younger than 20 minutes. Create and always remove the lock.
2. Run `export_logs.py`.
3. Run `claude -p "<lesson prompt>"` with the working directory set to `learning/`, allowed only to Read/Write/Edit there. The 5th slot of the day passes "this is a drill". The 16:30 slot also asks for `coding-challenge.md`.
4. Run `send_lesson.py`.
5. Commit and push `learning/` (skip the push quietly if no remote is set yet).
6. On any failure, call `alerts.py` with the reason.

### Step 3.3: Send and record — `bot/send_lesson.py`
Parse the front-matter and body of `learning/outbox/lesson.md`, validate length and format, send it to Telegram, store the lesson with the returned message id, then delete the outbox file. If Telegram fails, keep the file so a retry can resend it.

### Step 3.4: Alerts and challenge ping — `bot/alerts.py`
Functions: `send_failure(reason)` and `send_challenge_ready()`. Detect the "usage limit reached" and "not signed in" cases from `claude` output and give a specific message.

> **Built in Phase 3, beyond the file list above:** `scripts/common.ps1` (shared helpers: lock, logging, alerts, git backup), `scripts/schedule.ps1` (the one place the times live), `bot/weekly.py` (once-a-week marker), and testing switches `-Force` and `-SkipClaude` on `run-lesson.ps1`. Run history is written to `data/runs.log`. Claude has no shell, so the weekly script, not Claude, deletes the digested raw logs.

### Step 3.5: Weekly synthesis — `scripts/run-weekly.ps1`, `learning/weekly-prompt.md`
Once a week the script runs `export_logs.py`, then `claude -p` with `weekly-prompt.md`, which tells Claude to:
- Read the week's `logs/*.md` plus `progress.md`, `weak-spots.md` and `question-bank.md`.
- Compress `progress.md` into one short line per concept or module (for example "RAG: chunking, retrieval, eval covered — solid"), and drop wording that only repeats earlier lines.
- Remove resolved items from `weak-spots.md` and keep only open ones, with the reason.
- Write one short paragraph for the week to `learning/archive/YYYY-Www.md` (what was covered, drill scores, recurring struggles), then delete that week's raw logs.
- Apply pacing decisions to `curriculum.md` (skip, deepen, reorder) and state each reason in `progress.md`.
- Never touch the SQLite data; reply context for old lessons still comes from there.

Guards: skip if a synthesis already ran this ISO week, and use the same `data/run.lock` as the lesson runner. Commit and push `learning/` afterwards.

**Test after this phase:**
- Run `run-lesson.ps1` by hand for each slot type, including the drill and the 16:30 challenge slot.
- Run it twice for the same slot; the second run does nothing.
- Break the Claude sign-in or Wi-Fi on purpose and confirm a Telegram failure alert arrives.
- Questions asked in Telegram show up in `learning/logs/` and are reflected in the next lesson.
- After a test week, run `run-weekly.ps1`: `progress.md` gets noticeably shorter, raw logs are replaced by one archive paragraph, and the next lesson still builds on the right topic.

**Warnings:**
- Claude writing to a file is more reliable than parsing its printed output; keep that contract strict.
- `claude -p` counts against the same Pro usage limits as the rest of the account. Five short runs a day should be fine, but check after the first week.

---

## Phase 4: Scheduling, Reliability and Security

### Step 4.1: Register scheduled tasks — `scripts/register-tasks.ps1`
Create five weekday tasks (Mon–Fri) calling `run-lesson.ps1 -Slot <time>`, with wake-to-run, start-when-available, run on battery, and a 15-minute time limit. The script has the five times as one editable list. Also create one **weekly task** for `run-weekly.ps1` (Friday 20:30, after the last lesson), with start-when-available so it still runs the next time the laptop is on if it was off.

### Step 4.2: Keep the bot running — `scripts/start-bot.ps1`
Starts `python -m bot.bot` hidden from the virtual environment. Register it as a task at logon with automatic restart on failure (every minute, many retries). Log to `data/bot.log` with rotation, and never log tokens.

### Step 4.3: Backups and memory hygiene
Nightly copy of `data/learning.db` to `data/backups/` (keep 14). Check after the first weekly synthesis that `progress.md` stays small.

### Step 4.4: Security checklist (done once, documented in `README.md`)
- `.env` readable only by the user (`icacls`), never committed.
- OpenAI key scoped to a dedicated project with a monthly spending cap.
- Bot answers only the owner chat ID and has a daily question limit.
- The OpenAI call has no tools, so prompt injection can't act on the laptop.
- `claude -p` restricted to the `learning/` folder, with no shell or web tools.
- Private GitHub repo only. If the bot token ever leaks, regenerate it in BotFather.
- No inbound ports; long polling is outbound only. Docker is not required.

**Test after this phase:**
- Reboot, log in, and confirm the bot is listening without opening a terminal.
- Let the laptop sleep and confirm a scheduled lesson wakes it and arrives.
- Leave the laptop off through a slot and confirm the missed slot is skipped, not delivered late.
- Leave the laptop off through Friday 20:30 and confirm the weekly synthesis runs when it next wakes, without colliding with a lesson run.

**Warnings:**
- Windows 11 Home may use Modern Standby, where wake-to-run can be unreliable. Test it. Fallback: set the laptop not to sleep on AC power.
- Make sure the laptop is awake and online when the 09:00 task fires.

---

## Phase 5 (optional, later): Backlog

Not planned now. Revisit once the system has run for a few weeks.
- **Trim long OpenAI conversations:** summarise the oldest messages once a lesson thread passes about 20 messages. Only if OpenAI usage turns out to matter.
- **Claude channels as the Q&A engine:** swap `bot/qa.py` for the Telegram channel plugin (needs Bun, an always-open `claude --channels` session and a second bot token). Only worth it if answer quality from OpenAI disappoints and Pro usage allows it. It is a research preview, so the flag may change.
- **Move the bot to the cloud:** for evening or weekend Q&A with the laptop off. Containerise `bot/` with Docker on a separate small instance (not the BizMitra box) and give the lesson script a way to post lessons to it.
