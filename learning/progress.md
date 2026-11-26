# Progress

## Pointers
- 2026-11-18 FOCUS CHANGE: interview in ~2 weeks (AVP backend/frontend: core Java, Spring, React hooks). Data engineering PARKED (see parked/data-engineering.md; his B1-B3 history below stays for reference). Daily: java x2, react x1, ai x1, evening drill (java or react).
- java: J1 equals/hashCode, String pool, immutable class done. J2 HashMap internals + ConcurrentHashMap vs synchronizedMap done. Fail-fast iterators done. ArrayList vs LinkedList done. TreeMap/LinkedHashMap/PriorityQueue done. Next: J6 Spring IoC/DI (constructor vs field injection); J1 exceptions/generics later.
- react: R2 re-render triggers + keys/reconciliation done. R3 started: useState updater/stale closures, useEffect deps + cleanup done. Next: fetch race conditions in useEffect.
- ai: A1-A4 seen; A5 seen (agent vs workflow, memory, multi-agent; standalone planning lesson trimmed for the sprint). A6 MCP done. Next: A6 harnesses and hooks. One lesson a day.

## Module levels
Levels: new | seen | solid | mastered

### AI development
- A1 LLM fundamentals: seen
- A2 Structured outputs and tool calling: seen (structured outputs done; tool calling next)
- A3 Embeddings and vector search: seen
- A4 RAG in depth: seen (pipeline + chunking done)
- A5 Agents: seen (agent vs workflow, memory)
- A6 Harnesses, hooks, MCP: seen (MCP)
- A7 Evals and observability: new
- A8 Safety, security and cost: new
- A9 LLM system design: new
- A10 Python (differences from JS only): new

### Java and Spring (new 2026-11-18)
- J1 Core Java: seen (equals/hashCode)
- J2 Collections: seen (HashMap internals)
- J3 Java 8+ functional: new
- J4 Concurrency: new
- J5 JVM and memory: new
- J6 Spring and Spring Boot: new
- J7 Backend design and APIs: new

### React and frontend (new 2026-11-18)
- R1 JS/TS for React: new
- R2 React fundamentals: seen (re-render triggers)
- R3 Hooks: seen (useState updater/stale closures, useEffect deps/cleanup)
- R4 State, data, architecture: new
- R5 Web fundamentals: new
- R6 Frontend/full-stack design: new

### Data engineering (PARKED)
- B1 SQL for interviews: seen
- B2 Data modelling: seen (star schema, facts/dims, grain done)
- B3 Pipelines: seen (ETL/ELT, idempotency done)
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
- B1: gaps and islands (date minus ROW_NUMBER constant, dedupe days first, per-user partition) — 2026-11-16
- A3: embedding = vector of meaning, cosine similarity, same model for query+docs, misses exact codes — 2026-11-16
- B2: star schema, fact vs dimension, grain, denormalised dims — 2026-11-16
- A3: vector DB, ANN vs exact search, HNSW, recall vs speed trade-off, hybrid search (BM25 + vector) — 2026-11-16
- B2: SCD Type 1 vs 2 (surrogate key, valid_from/to, is_current), Type 3 mention — 2026-11-17
- A4: RAG pipeline overview, chunking size trade-off, structure-aware splits, overlap, metadata/heading context — 2026-11-17
- B2: normalisation vs denormalisation, update anomalies, OLTP vs analytics, 3NF rule of thumb — 2026-11-17
- A4: reranking (wide top-k then cross-encoder, latency cost, shortlist limit), query rewriting, metadata filters — 2026-11-17
- B3: ETL vs ELT, idempotency (upsert/MERGE vs partition overwrite) — 2026-11-18
- A4: RAG eval (retrieval vs generation split, golden set, recall@k, faithfulness, answer relevance, LLM-judge) — 2026-11-18
- J1: equals vs ==, equals/hashCode contract, HashSet bucket lookup failure, mutable keys — 2026-11-18
- R2: re-render triggers (state, parent, context), Object.is/mutation trap, render vs DOM commit — 2026-11-18
- J1: String immutability (why), string pool, new String vs literal ==, += in loops vs StringBuilder/StringBuffer — 2026-11-19
- J1: immutable class recipe, final ref vs object, defensive copies in/out, List.copyOf, records shallow — 2026-11-20
- J2: HashMap buckets, power-of-two mask, collisions + equals, load 0.75 resize, pre-sizing, treeify at 8 (table>=64) — 2026-11-23
- J2: fail-fast iterators, modCount, CME on remove in for-each, Iterator.remove/removeIf, best effort, CopyOnWriteArrayList — 2026-11-24
- A5: agent vs workflow, who controls steps, turn cap/budget, compounding errors, approval on risky tools — 2026-11-23
- J2: ConcurrentHashMap vs synchronizedMap (one lock vs lock-free reads/per-bucket writes), no nulls, weakly consistent iterators, check-then-act race, merge/computeIfAbsent — 2026-11-23
- J2: ArrayList vs LinkedList (array/cache locality, LinkedList O(1) insert needs node, ArrayDeque for queues) — 2026-11-24
- A5: agent memory (short-term = context + compaction; long-term external store; stale/poisoned notes) — 2026-11-24
- A5: single vs multi-agent (context isolation, parallelism, permissions vs tokens, debugging, lossy handoffs) — 2026-11-25
- A6: MCP (host/client/server, tool discovery, resources/prompts, local vs HTTP, tool bloat, untrusted servers, vs plain tool calling) — 2026-11-26
- R2: keys, reconciliation, index-key bug (state stuck to position), random keys remount, key to reset state — 2026-11-23
- R3: render = snapshot, setCount(count+1) x3 adds 1, updater form c=>c+1, stale timers — 2026-11-24
- SQL coding challenges written (also cohort retention, 11-16): HAVING/aggregation (11-05), top 2 per customer (11-06), month-over-month LAG + running total (11-09), longest login streak / gaps and islands (11-11), latest status per order + dedupe/tiebreak (11-12)

- J2: TreeMap (sorted, compareTo decides key identity, floor/ceiling), LinkedHashMap (insertion/access order, LRU), PriorityQueue (heap, iteration unsorted, top K) — 2026-11-26
- R3: useEffect deps (Object.is), cleanup order/unmount, object deps rerun every render, Strict Mode double setup — 2026-11-26

## Drills
- 2026-11-26 java: TreeSet with score-only comparator drops tied player (why, fix, mutable score + update cost) — awaiting grade
- 2026-11-25 react: overlapping async uploads, setFiles([...files, saved]) loses a file (why, fix, pick-order trade-off) — awaiting grade
- 2026-11-05 ai: context window overflow — 3/5 (knew causes/fixes, missed trade-offs and reply-token budget)
- 2026-11-06 data: window AVG OVER vs GROUP BY/CTE — awaiting grade
- 2026-11-09 ai: injection in email-reading refund agent (fixes + trade-offs) — awaiting grade
- 2026-11-11 ai: support bot invented refund policy (hallucination causes, fixes + trade-offs) — 3/5 (good fixes, no root cause, no trade-offs)
- 2026-11-12 data: LOWER(email) non-sargable on 50M-row table (root cause, 2 fixes, costs) — awaiting grade
- 2026-11-17 ai: RAG wrong chunks (paternity vs maternity; chunking/reranking, root cause + costs) — 3/5 (found both failure points; said embeddings are "3-D", treated 250-300 tokens as a rule, reranking costs not stated)
- 2026-11-18 java: mutable HashMap key lost after mutation (why + 2 fixes with costs) — awaiting grade
- 2026-11-23 react: mutate todo + setTodos(same array), stale UI (why + 2 fixes with costs) — awaiting grade (react not drilled before)
- 2026-11-24 java: ConcurrentHashMap containsKey/get/put counter loses counts (why + fixes with costs) — awaiting grade
- 2026-11-16 data: B2 grain/fan-out, SUM(order_total) doubled after join to items — awaiting grade (next normal lesson still data B2 SCDs)

## Pacing notes
- 2026-11-26: Spring (J6) pulled ahead of J3-J5 and the rest of J1: interview is about a week away and no Spring is covered yet. No new questions or reactions in recent logs.
- 2026-W45: only one drill graded (3/5), so nothing is marked solid. A1 and B1 stay `seen`. Revisit trade-off framing in answers. No curriculum changes.
- 2026-11-12: second drill 3/5 with same gap (trade-offs). 👍 on lessons 13, 17, 18 (injection, hallucination, indexes) but no 4/5 drill yet, so still `seen`. Lesson 18 👍 → indexes can go deeper later (composite indexes).
