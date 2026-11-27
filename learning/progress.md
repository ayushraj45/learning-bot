# Progress

## Pointers
- 2026-11-18 FOCUS CHANGE: interview ~2 weeks from then (about 12-02). AVP backend/frontend: core Java, Spring, React hooks. Data engineering PARKED (parked/data-engineering.md). Daily: java x2, react x1, ai x1, evening drill (java or react). Sprint order is at the bottom of curriculum.md.
- java: J1, J2 basics and J6 IoC/DI done. Next: J6 bean scopes and lifecycle, then proxies/@Transactional.
- react: R2 re-renders + keys, R3 useState + useEffect + fetch races done. Next: useRef, then useMemo/useCallback/React.memo.
- ai: A1-A6 done for the sprint. Next: A7 evals and observability.

## Module levels
Levels: new | seen | solid | mastered
- AI seen: A1, A2, A3, A4, A5, A6, A8 (injection only)
- AI new: A7, A9, A10
- Java seen: J1, J2, J6 (IoC/DI only)
- Java new: J3, J4, J5, J7
- React seen: R2, R3
- React new: R1, R4, R5, R6
- Data (parked): B1-B3 seen, B4-B9 new

## Covered
- A1: tokens/context/params, sampling, few-shot, chain-of-thought, system vs user prompts, hallucination
- A2: schema-constrained output + validate/retry; tool calling loop
- A3: embeddings + cosine; vector DB, ANN/HNSW, hybrid search
- A4: chunking, reranking, query rewriting, filters, RAG eval
- A5: agent vs workflow, memory, single vs multi-agent (planning lesson trimmed for sprint)
- A6: MCP; harness and hooks
- A8: prompt injection, direct/indirect, blast radius
- J1: equals/hashCode + mutable keys; String immutability/pool/StringBuilder; immutable class, defensive copies, records
- J2: HashMap internals; ConcurrentHashMap vs synchronizedMap + check-then-act; fail-fast iterators
- J2: ArrayList vs LinkedList/ArrayDeque; TreeMap/LinkedHashMap (LRU)/PriorityQueue (top K)
- J6: IoC/beans, scanning, constructor injection, @Primary/@Qualifier, circular dependencies
- R2: re-render triggers, mutation/Object.is, render vs commit; keys and reconciliation
- R3: render snapshot, updater form, stale closures; useEffect deps/cleanup/Strict Mode; fetch races (abort/ignore)
- B1 (parked): joins, GROUP BY/HAVING, CTEs, window functions, RANK family, running totals, LAG/LEAD, indexes, dedupe, gaps and islands
- B2-B3 (parked): star schema/grain, SCD 1/2, normalisation, ETL/ELT + idempotency

## Drills
Graded:
- 11-05 ai: context window overflow — 3/5 (no trade-offs, forgot reply-token budget)
- 11-11 ai: invented refund policy — 3/5 (good fixes, no root cause or trade-offs)
- 11-17 ai: RAG wrong chunks — 3/5 ("3-D" embeddings, chunk size as a rule, reranking costs missing)
Awaiting grade:
- java: 11-18 mutable HashMap key; 11-24 ConcurrentHashMap counter race; 11-26 TreeSet score-only comparator
- react: 11-23 mutated todo state; 11-25 overlapping uploads; 11-27 chat reconnects on theme change
- ai/data (older): 11-06 window vs GROUP BY; 11-09 refund agent injection; 11-12 LOWER(email) index; 11-16 grain/fan-out

## Pacing notes
- W45 and 11-12: graded drills 3/5 with a trade-off gap, so nothing solid. 👍 on indexes → go deeper (composite indexes).
- 11-26: J6 pulled ahead of J3-J5 and the rest of J1; interview close and no Spring covered yet.
- 11-27 weekly: no module skipped or marked solid (no drill at 4/5+; no questions, grades or reactions logged for Java/React).
- 11-27 weekly: Java reordered to finish high-yield J6 first, then J4, J3, J7 transactions/indexes, since only a few days remain. Exceptions/generics, J5 and rest of J1 move behind these.
- 11-27 weekly: React goes useRef/memoisation → useContext/useReducer/custom hooks → Context vs Redux/Zustand; these are core hooks and state trade-offs.
- 11-27 weekly: AI goes A7 → A9; rest of A8 after, A10 last (Python is outside the Java/React interview).
- 11-27 weekly: J7 databases includes composite indexes because of the indexes 👍 (strongest area to deepen on the backend).
