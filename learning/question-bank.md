# Question bank

Interview questions already asked or taught, so none repeat. Format: `- <question> (track, module) — <date> — grade if drill`

## Java
- What happens if you override equals but not hashCode? (J1) — 11-18
- Drill: key mutated after HashMap put, get returns null; why, 2 fixes with costs? (J1) — 11-18 — awaiting grade
- Why is String immutable, what does new String("hi") == "hi" give, StringBuilder vs += in loops? (J1) — 11-19
- How do you create an immutable class? Is `final` enough? Are records immutable? (J1) — 11-20
- How does HashMap work internally, including collision and resize? (J2) — 11-23
- ConcurrentHashMap vs synchronizedMap; why is containsKey+put still a race? (J2) — 11-23
- Why does removing inside a for-each throw ConcurrentModificationException, and how do you fix it? (J2) — 11-24
- ArrayList vs LinkedList; is LinkedList insert really O(1)? (J2) — 11-24
- Drill: ConcurrentHashMap containsKey/get/put counter loses counts; why, fixes with costs? (J2) — 11-24 — awaiting grade
- TreeMap vs LinkedHashMap vs PriorityQueue; LRU cache and top K? (J2) — 11-26
- Drill: TreeSet with score-only comparator drops a tied player; why, fix, cost if score mutates? (J2) — 11-26 — awaiting grade
- What is IoC/DI, why constructor injection, what if two beans match or depend on each other? (J6) — 11-27

## React
- What causes a re-render, and why doesn't mutating state work? (R2) — 11-18
- Why not use array index as key (inputs show wrong values after delete)? (R2) — 11-23
- Drill: todo mutated in place + setTodos(same array), stale UI; why, 2 fixes with costs? (R2) — 11-23 — awaiting grade
- Why does setCount(count + 1) twice add only 1, and why do timers see old values? (R3) — 11-24
- Drill: overlapping uploads with setFiles([...files, saved]) lose a file; why, fix, keeping pick order? (R3) — 11-25 — awaiting grade
- Why does useEffect run twice or every render, and when does cleanup run? (R3) — 11-26
- Why does a page show stale fetch results, and abort vs ignore flag? (R3) — 11-27
- Drill: chat effect with [roomId, theme] reconnects on theme toggle; why, what if theme is removed, fix + cost? (R3) — 11-27 — awaiting grade

## AI
- What's a token and why does it matter? (A1) — 11-04
- What does temperature do; settings for extraction vs creative? (A1) — 11-05
- Drill: "context length exceeded" after ~30 messages; why, fixes with trade-offs? (A1) — 11-05 — 3/5
- Few-shot vs a better instruction? (A1) — 11-06
- How would you improve an LLM that gets multi-step problems wrong (chain-of-thought)? (A1) — 11-06
- System vs user prompt; can you rely on the system prompt for security? (A1) — 11-09
- How do you protect an agent from direct and indirect prompt injection? (A8) — 11-09
- Drill: refund agent obeys instructions in a customer email; cause, fixes with costs? (A8) — 11-09 — awaiting grade
- How do you reduce hallucinations in production? (A1) — 11-11
- Drill: support bot invented a 90-day refund policy; why, fixes with costs? (A1) — 11-11 — 3/5
- How do you get reliable JSON from an LLM? (A2) — 11-12
- How does tool calling work, and what can go wrong in the loop? (A2) — 11-12
- What is an embedding and how does semantic search work? (A3) — 11-16
- How does a vector DB search fast, and what's the trade-off (ANN/HNSW, hybrid)? (A3) — 11-16
- RAG retrieves wrong chunks; how do you debug and improve it (chunking, reranking, rewriting, filters)? (A4) — 11-17
- Drill: HR RAG answers paternity question from maternity/partial chunk; root cause, fixes with costs? (A4) — 11-17 — 3/5
- How do you evaluate a RAG system? (A4) — 11-18
- Agent vs workflow: when would you pick each? (A5) — 11-23
- How would you give an agent memory or handle a very long task? (A5) — 11-24
- When would you use multiple agents, and what does it cost? (A5) — 11-25
- What is MCP, how does it differ from tool calling, what are the risks? (A6) — 11-26
- What is an agent harness; how do you guarantee an agent never does something (hooks vs prompts)? (A6) — 11-27

## Data (parked)
- Why did my LEFT JOIN drop rows / how do you find customers with no orders? (B1) — 11-05
- WHERE vs HAVING, including filtering customers by order count and spend (B1) — 11-05
- CTE vs subquery; what's a correlated subquery? (B1) — 11-06
- Latest order or top N per group, including ties (B1) — 11-06
- Drill: orders above the customer's own average; why window over GROUP BY? (B1) — 11-06 — awaiting grade
- RANK vs DENSE_RANK vs ROW_NUMBER; second highest salary per department (B1) — 11-09
- Running totals with duplicate dates: RANGE vs ROWS (B1) — 11-09
- LAG/LEAD: gaps between orders, first-row value, month-over-month growth (B1) — 11-09
- How do you investigate a slow query (indexes, EXPLAIN)? (B1) — 11-11
- Drill: LOWER(email) filter slow on indexed 50M rows; why, 2 fixes with costs? (B1) — 11-12 — awaiting grade
- Dedupe keeping the latest row per key (tied timestamps); why not DISTINCT? (B1) — 11-12
- Longest login streak (gaps and islands) (B1) — 11-16
- Monthly cohort retention (B1) — 11-16
- Star schema: fact vs dimension, grain (B2) — 11-16
- Drill: SUM(order_total) doubles after joining items; why, 2 fixes with costs? (B2) — 11-16 — awaiting grade
- SCD Type 1 vs 2 (B2) — 11-17
- Normalised vs denormalised: when each? (B2) — 11-17
- ETL vs ELT; how do you make a pipeline safe to retry? (B3) — 11-18
