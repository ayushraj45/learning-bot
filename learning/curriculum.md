# Curriculum (living document)

Claude may reorder, trim or extend this based on Ayush's progress. Note reasons in `progress.md`. Each bullet is lesson-sized or a small cluster of lessons. Every concept must connect to how it gets asked in an interview.

**Interview sprint (from 2026-11-18, interview about 2 weeks away):** backend and frontend development at assistant-vice-president level (mid-senior, not junior): core Java, Spring, React with hooks. Java and React get the focus; AI gets one lesson a day. Data engineering is parked in `parked/data-engineering.md`.

Level to aim at: a mid-senior interviewer asks "why" and "what goes wrong", not definitions. Expect trade-offs, internals (how HashMap works, how the JVM manages memory), concurrency, debugging scenarios and small design questions.

## Track J: Java and Spring (backend)

**J1. Core Java language**
- OOP in Java: abstract class vs interface (default/static methods), composition over inheritance, overloading vs overriding, `static`, `final`, initialisation order
- `equals`/`hashCode` contract, immutability and how to write an immutable class, records, String pool vs `StringBuilder`, `==` vs `equals`
- Exceptions: checked vs unchecked, try-with-resources, custom exceptions, `finally` traps
- Generics: type erasure, wildcards (`? extends` / `? super`, PECS)
- Enums, `Optional` (and its misuse), sealed classes, pattern matching, text blocks (Java 17/21)
- Pass by value, object references, shallow vs deep copy, `Comparable` vs `Comparator`

**J2. Collections**
- ArrayList vs LinkedList, HashSet, TreeSet, LinkedHashMap, PriorityQueue, ArrayDeque; choosing the right one
- HashMap internals: hashing, buckets, collisions, treeification, resizing, why keys must be immutable
- ConcurrentHashMap vs synchronized map; fail-fast vs fail-safe iterators; `List.of` vs unmodifiable views

**J3. Java 8+ functional style**
- Lambdas, functional interfaces, method references
- Streams: map/filter/reduce, `collect`, `groupingBy`, `flatMap`, laziness, parallel streams and why they bite
- `Optional` chaining, `CompletableFuture` composition

**J4. Concurrency**
- Threads, `Runnable`/`Callable`, `ExecutorService`, pool sizing, virtual threads (Java 21)
- `synchronized`, `volatile`, happens-before, race conditions, deadlock, atomics, locks
- `ThreadLocal`, producer-consumer, common concurrency interview questions

**J5. JVM and memory**
- Heap vs stack, generations, garbage collection basics (G1), memory leaks in Java, `OutOfMemoryError` debugging
- Class loading, JIT, common performance pitfalls

**J6. Spring and Spring Boot**
- IoC and dependency injection (constructor vs field injection), bean scopes and lifecycle, component scanning
- Boot: auto-configuration, starters, `application.yml`, profiles, `@ConfigurationProperties`
- MVC/REST: `@RestController`, validation, `@ControllerAdvice` error handling, DTOs vs entities, status codes
- Spring Data JPA/Hibernate: lazy vs eager, the N+1 problem, `@Transactional` (propagation, isolation, self-invocation trap), optimistic locking
- Spring Security basics: authentication vs authorisation, JWT, filter chain
- AOP and proxies (why `@Transactional` sometimes does nothing), `@Async`, caching, scheduling
- Testing: JUnit 5, Mockito, `@WebMvcTest`/`@SpringBootTest`

**J7. Backend design and APIs**
- REST design: idempotency, pagination, versioning, error format
- Databases for app developers: transactions, isolation levels, indexes, connection pooling
- Microservices vs monolith, messaging at a glance (Kafka/RabbitMQ), resilience (timeouts, retries, circuit breaker), caching (Redis)
- Small design questions: rate limiter, URL shortener, notification service
- Patterns that get asked: singleton, factory, builder, strategy, observer, SOLID

## Track R: React and frontend

**R1. JS/TS that React interviews lean on**
- Closures, `this`, event loop, promises/async-await, immutability and spread, destructuring
- TypeScript in React: props typing, generics, `useState<T>`, union types

**R2. React fundamentals**
- Props vs state, keys and why they matter, controlled vs uncontrolled inputs, lifting state up
- Virtual DOM and reconciliation, what triggers a re-render, batching, Strict Mode double render

**R3. Hooks (the core of the interview)**
- `useState` (functional updates, stale state)
- `useEffect`: dependency array, cleanup, race conditions in fetches, infinite-loop bugs
- `useRef`, `useMemo`, `useCallback` (when they help, when they don't), `React.memo`
- `useReducer`, `useContext` and its re-render cost, custom hooks, rules of hooks and why
- `useLayoutEffect`, `useTransition`/`useDeferredValue`, React 18/19 notes (Suspense, `use`, Server Components at a glance)

**R4. State, data and architecture**
- Context vs Redux/Zustand; server state with TanStack Query
- Forms and validation, error boundaries, code splitting and lazy loading
- Performance: memoisation, list virtualisation, profiling
- Routing, auth flow in a SPA, accessibility basics, React Testing Library

**R5. Web fundamentals**
- HTTP, CORS, cookies vs localStorage, JWT storage trade-offs, XSS/CSRF
- Browser rendering, Core Web Vitals, flexbox/grid quick fire

**R6. Frontend and full-stack design**
- Designing autocomplete, infinite scroll, a data table, a form wizard
- How a React app talks to a Spring Boot backend: contracts, errors, auth, pagination

## Track A: AI development (one lesson a day)

**A1. LLM fundamentals** (tokens, context window, sampling, prompting patterns, hallucination)
**A2. Structured outputs and tool calling**
**A3. Embeddings and vector search** (ANN/HNSW, hybrid search)
**A4. RAG in depth** (pipeline, chunking, reranking, query rewriting, evaluation, failure modes)
**A5. Agents** (loop, planning, memory, multi-agent trade-offs, SDKs)
**A6. Modern tooling** (harnesses, hooks, MCP, skills, subagents, permissions)
**A7. Evals and observability** (golden sets, LLM-as-judge, tracing, cost and latency)
**A8. Safety, security and cost** (prompt injection, guardrails, caching, routing, fine-tuning vs RAG)
**A9. LLM system design** (support bot, doc-QA, coding assistant)
**A10. Python only where it differs from JS** (asyncio, generators, decorators, pydantic, GIL)

(Where it fits, link AI to Java/React: calling an LLM from Spring Boot, streaming tokens into a React UI.)

## Cross-cutting
- Daily interview drill (Java or React) drawn from any covered module.
- Weak spots from `weak-spots.md` are revisited before moving on.
- Suggested sprint pacing: J1, J2, R2, R3 first (most commonly asked), then J6, J3, J4, R4, then J5, J7, R5, R6. Reorder using his reactions and drill grades.
