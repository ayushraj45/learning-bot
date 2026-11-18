# PARKED: Data engineering track

Parked on 2026-11-18 so Ayush can focus on the Java/React interview (about 2 weeks away). Do NOT teach from this file until Ayush asks to resume it. Normal runs must not read it.

Where he stopped: B1 SQL (windows, indexes, dedupe, gaps and islands) seen; B2 data modelling (star schema, SCD, normalisation) seen; B3 pipelines (ETL/ELT, idempotency) seen. Next on resume: B3 backfills and incremental loads, then B4 Spark. His drills and question history stay in `question-bank.md` so nothing repeats.

To resume: move this track back into `curriculum.md` and set the slots in `scripts/schedule.ps1` (`$SlotTracks`) back to `data`.

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

