# Interview-prep learning bot

Five short lessons each weekday on Telegram (AI engineering and data engineering), written by Claude Code on this laptop. Reply to any lesson to ask follow-ups, answered by OpenAI. Claude's memory lives in `learning/`.

Full design and step list: `plan-telegram-learning-bot.md`.

## One-time setup

1. **Python env** (already done if `.venv` exists):
   ```powershell
   python -m venv .venv
   .\.venv\Scripts\python.exe -m pip install -r requirements.txt
   ```
2. **Create the bot:** in Telegram talk to @BotFather, send `/newbot`, copy the token.
3. **Fill in `.env`:** copy `.env.example` to `.env`, then set `TELEGRAM_BOT_TOKEN`, `OPENAI_API_KEY`, `OPENAI_MODEL` (check the model name exists on your account).
4. **Find your chat ID:** run `.\.venv\Scripts\python.exe -m bot.bot --whoami`, message your bot, and put the number it prints in `.env` as `TELEGRAM_OWNER_CHAT_ID`.
5. **Lock down `.env`** so only your Windows user can read it:
   ```powershell
   icacls .env /inheritance:r /grant:r "$($env:USERNAME):(R,W)"
   ```
6. **Claude sign-in:** `claude auth status` must say `loggedIn: true`. If the desktop app keeps clearing the login, run `claude setup-token` once and store the result in a user environment variable named `CLAUDE_CODE_OAUTH_TOKEN`.
7. **Windows power settings:** in Power Options, enable "Allow wake timers" so scheduled runs can wake the laptop. Modern Standby on Windows 11 Home can ignore wake timers: test it, or stop the laptop sleeping while plugged in.
8. **Preview, then create the scheduled tasks:**
   ```powershell
   .\scripts\register-tasks.ps1 -DryRun
   .\scripts\register-tasks.ps1
   ```

## Daily operation

| What | Where |
|---|---|
| Times of the five lessons | `scripts/schedule.ps1` (re-run `register-tasks.ps1` after editing) |
| Run history and errors | `data/runs.log` |
| Bot log (no message text, no secrets) | `data/bot.log` |
| Last Claude output | `data/last-claude-output.txt` |
| Database and backups | `data/learning.db`, `data/backups/` (newest 14) |
| Today's coding challenge | `learning/coding-challenge.md` (you get a Telegram ping) |
| Remove everything scheduled | `.\scripts\register-tasks.ps1 -Unregister` |

Manual runs for testing: `.\scripts\run-lesson.ps1 -Slot 11:30 -Force`, `.\scripts\run-weekly.ps1 -Force`. Add `-SkipClaude` to send whatever is already in `learning/outbox/lesson.md`.

## Security checklist

- [ ] No inbound ports. The bot uses long polling, which is outbound HTTPS only, so nothing on the internet can reach the laptop. Docker is not needed.
- [ ] `.env` is gitignored and locked down with `icacls` (setup step 5). Never paste tokens into chats or commit them.
- [ ] The bot answers **only** `TELEGRAM_OWNER_CHAT_ID`. Anyone else is ignored without any OpenAI call.
- [ ] `DAILY_QUESTION_LIMIT` caps OpenAI use. Use a dedicated OpenAI project key with a monthly spending cap in the OpenAI dashboard.
- [ ] The OpenAI call has no tools, so a prompt-injection can only change the text of a reply.
- [ ] `claude -p` runs inside `learning/` with only Read, Write, Edit, Glob and Grep. No shell, no web.
- [ ] Logs never contain the bot token or message text. If the token ever leaks, regenerate it in BotFather (`/revoke`) and update `.env`.
- [ ] GitHub repo is **private** (it holds your learning history).
- [ ] The database is backed up on this laptop only. For an off-machine copy, copy `data/backups/` somewhere safe now and then.

## Troubleshooting

- **"Claude sign-in has expired" alert:** run `claude auth login` in a normal terminal, or use `claude setup-token` (setup step 6).
- **Lesson didn't arrive:** check `data/runs.log`. A slot that starts more than 60 minutes late is skipped on purpose.
- **Bot silent:** check `data/bot.log`; confirm the `Bot` task is running in Task Scheduler (folder LearningBot). Messages sent while the laptop was off are delivered for about 24 hours after it wakes.
- **Task window flashes briefly** when a run starts. That is the hidden PowerShell window opening.
