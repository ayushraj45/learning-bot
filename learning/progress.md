# Progress

## Pointers
- Last track taught: data drill (indexes/sargability, 11-12; drill doesn't change the lesson order). Next normal lesson: data (B1 gaps and islands lesson or move to B2)
- AI development: A1 complete (hallucination done), A2 structured outputs + tool loop done; next tool-design/parallel calls or A3. Prompt injection intro done early (A8) after 👍 on lesson 11; later A8 can go deeper (guardrails, tool risks)
- Data engineering: up to B1 (indexes/EXPLAIN done; next: dedupe, gaps and islands). Lesson 12 (RANK) got 👍, so went deeper into frames
- NEXT track to teach: data

## Module levels
Levels: new | seen | solid | mastered

### AI development
- A1 LLM fundamentals: seen
- A2 Structured outputs and tool calling: seen (structured outputs done; tool calling next)
- A3 Embeddings and vector search: new
- A4 RAG in depth: new
- A5 Agents: new
- A6 Harnesses, hooks, MCP: new
- A7 Evals and observability: new
- A8 Safety, security and cost: new
- A9 LLM system design: new
- A10 Python (differences from JS only): new

### Data engineering
- B1 SQL for interviews: seen
- B2 Data modelling: new
- B3 Pipelines: new
- B4 Spark: new
- B5 Streaming and CDC: new
- B6 Orchestration and transformation: new
- B7 Warehouses and lakehouse: new
- B8 Data quality and governance: new
- B9 Data system design: new

## Covered so far
- A1: tokens/context window/params vs tokens (asked what "parameters" means); temperature, top-p, greedy, temp 0 not fully deterministic; few-shot (zero vs few, token cost, varied examples); chain-of-thought (cost, reasoning models); system vs user prompts (roles, caching, not a security boundary) — 2026-11-09
- B1: LEFT vs INNER JOIN + WHERE-vs-ON trap; GROUP BY, WHERE vs HAVING, COUNT variants; subqueries vs CTEs, correlated subqueries; window intro (ROW_NUMBER, PARTITION BY, top-N per group)
- B1: ROW_NUMBER vs RANK vs DENSE_RANK, ties, Nth highest distinct — 2026-11-09
- A8: prompt injection, direct vs indirect, blast-radius mitigations (lethal trifecta) — 2026-11-09 (pulled forward on 👍 reaction)
- B1: running totals, default RANGE frame vs ROWS, moving average — 2026-11-09
- B1: LAG/LEAD, partition/order, NULL first row + default, filter via CTE — 2026-11-11
- A1: hallucination causes (autocomplete, missing facts, sycophancy), mitigations (grounding, cite, low temp, verify) and their costs — 2026-11-11
- B1: indexes (B-tree), seq scan vs seek, non-sargable functions/leading wildcard, EXPLAIN ANALYZE, write cost — 2026-11-11
- A2: JSON mode vs schema-constrained output vs validate+retry; shape ≠ correct values; reasoning field first — 2026-11-12
- B1: dedupe with ROW_NUMBER (partition by key, order by updated_at desc + tiebreaker), vs DISTINCT, find dupes via HAVING — 2026-11-12
- A2: tool calling loop (model requests, code runs, result appended, loop; max-turn cap, validate args, errors as text, token growth) — 2026-11-12
- SQL coding challenges written: HAVING/aggregation (11-05), top 2 per customer (11-06), month-over-month LAG + running total (11-09), longest login streak / gaps and islands (11-11), latest status per order + dedupe/tiebreak (11-12)

## Drills
- 2026-11-05 ai: context window overflow — 3/5 (knew causes/fixes, missed trade-offs and reply-token budget)
- 2026-11-06 data: window AVG OVER vs GROUP BY/CTE — awaiting grade
- 2026-11-09 ai: injection in email-reading refund agent (fixes + trade-offs) — awaiting grade
- 2026-11-11 ai: support bot invented refund policy (hallucination causes, fixes + trade-offs) — 3/5 (good fixes, no root cause, no trade-offs)
- 2026-11-12 data: LOWER(email) non-sargable on 50M-row table (root cause, 2 fixes, costs) — awaiting grade

## Pacing notes
- 2026-W45: only one drill graded (3/5), so nothing is marked solid. A1 and B1 stay `seen`. Revisit trade-off framing in answers. No curriculum changes.
- 2026-11-12: second drill 3/5 with same gap (trade-offs). 👍 on lessons 13, 17, 18 (injection, hallucination, indexes) but no 4/5 drill yet, so still `seen`. Lesson 18 👍 → indexes can go deeper later (composite indexes).
