# Curriculum (living document)

Claude may reorder, trim or extend this based on Ayush's progress. Note reasons in `progress.md`. Each bullet is lesson-sized or a small cluster of lessons. Every concept must connect to how it gets asked in an interview.

## Track A: AI development

**A1. LLM fundamentals**
- Tokens and tokenisation; context window; why long context costs more
- Sampling: temperature, top-p, determinism
- Prompting patterns that matter in interviews (few-shot, chain-of-thought, system vs user)
- Hallucination: causes and mitigations

**A2. Structured outputs and tool calling**
- JSON mode, schema-constrained output, validation and retries
- Function/tool calling loop, parallel tool calls, error handling

**A3. Embeddings and vector search**
- What an embedding is; cosine similarity
- Vector databases, ANN indexes (HNSW, IVF), trade-offs
- Hybrid search (BM25 + vectors)

**A4. RAG in depth**
- The basic pipeline end to end
- Chunking strategies and why they matter
- Retrieval quality: reranking, query rewriting, metadata filters
- Evaluating RAG: retrieval metrics vs answer metrics; faithfulness
- Common failure modes and how to debug them

**A5. Agents**
- Agent loop, planning, reflection
- Memory (short term, long term, summarisation)
- Multi-agent patterns and when not to use them
- Agent SDKs and frameworks: what they abstract

**A6. Modern tooling: harnesses, hooks, MCP**
- Agent harness: what it is and what it controls
- Hooks and lifecycle events
- Model Context Protocol: servers, tools, resources, why it exists
- Skills, subagents, permissions

**A7. Evals and observability**
- Offline evals, golden sets, LLM-as-judge and its pitfalls
- Tracing, logging, cost and latency monitoring

**A8. Safety, security and cost**
- Prompt injection and tool-use risks; guardrails
- Caching, batching, model routing, cost control
- Fine-tuning vs RAG vs prompting: when to pick which

**A9. LLM system-design interviews**
- Designing a support bot, a doc-QA system, a coding assistant
- Latency, scale, failure handling, privacy, evaluation plan

**A10. Python for this role (only what's different from JS)**
- asyncio and concurrency, generators, decorators, context managers
- Type hints and pydantic, packaging with uv, virtual environments
- The GIL and what it means for AI workloads
- Common Python coding-interview idioms

## Track B: Data engineering

**B1. SQL for interviews**
- Joins, aggregation, subqueries vs CTEs
- Window functions (ranking, running totals, lag/lead)
- Query plans, indexes, why a query is slow
- Classic interview problems (dedupe, top-N per group, gaps and islands)

**B2. Data modelling**
- Normalisation vs denormalisation
- Star and snowflake schemas, facts and dimensions
- Slowly changing dimensions
- Data vault and modern lakehouse modelling at a glance

**B3. Pipelines**
- ETL vs ELT; batch vs streaming; idempotency and backfills
- Incremental loads, late-arriving data, exactly-once vs at-least-once

**B4. Spark**
- Architecture: driver, executors, partitions
- Transformations vs actions, lazy evaluation
- Shuffles, joins, skew, broadcast joins
- Tuning and debugging slow jobs; file formats (Parquet)

**B5. Streaming and CDC**
- Kafka: topics, partitions, consumer groups, offsets
- Change data capture; stream processing basics

**B6. Orchestration and transformation**
- Airflow: DAGs, scheduling, retries, sensors
- dbt: models, tests, incremental models, lineage

**B7. Warehouses and lakehouse**
- Snowflake / BigQuery concepts; partitioning and clustering
- Delta / Iceberg: table formats, ACID on object storage

**B8. Data quality and governance**
- Testing data, contracts, lineage, observability
- Handling PII and regulated data (finance flavour)

**B9. Data system-design interviews**
- Designing a pipeline for transactions, clickstream, or reporting
- Scale, cost, failure recovery, monitoring

## Cross-cutting
- Periodic interview drills drawn from any covered module.
- Weak spots from `weak-spots.md` are revisited before moving on.
