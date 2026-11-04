# Weekly synthesis task

You are running the weekly synthesis, not writing a lesson. Do NOT write `outbox/lesson.md`.

Goal: compress everything stored so Claude reads less on every future run, without losing what matters.

Do the following, in this folder only:

1. Read this week's files in `logs/` (Ayush's questions, bot answers, drill grades), plus `progress.md`, `weak-spots.md`, `question-bank.md`, `curriculum.md`.
2. **Rewrite `progress.md` compactly.** One short line per concept or module, for example "RAG: chunking, retrieval, eval covered — solid". Drop wording that only repeats earlier lines. Keep the pointers and module levels up to date. Stay under about 150 lines.
3. **Tidy `weak-spots.md`.** Remove concepts he has since shown he understands. Keep open ones with a one-line reason.
4. **Tidy `question-bank.md`.** Keep one line per question; merge near-duplicates.
5. **Write the week's digest** to `archive/YYYY-Www.md` (use this week's ISO week): one short paragraph covering what was covered, drill scores, and recurring struggles or interests.
6. **Apply pacing decisions** to `curriculum.md`: skip modules he has shown he knows, deepen where he is strong, reorder where useful. Note each reason in `progress.md` under "Pacing notes".
7. Do NOT delete anything. You have no shell; the script removes the digested raw logs itself once `archive/YYYY-Www.md` exists. Do not touch anything outside this folder.

Finish by printing one line: `weekly synthesis done`.
