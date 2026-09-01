# SD-BEG-110-T01 — Measure Redis and relational-database operations

> Instructor-assigned task from `SD-BEG-110`. Write a prediction in `ATTEMPT.md`, complete your own first run, and only then open `reference/SOLUTION.md`.

## Source and fidelity

- Source timestamp: `00:10:23-00:11:12`; the final supplied slide shows the same four-part exercise.
- Faithful paraphrase: run Redis locally, practice storing and retrieving data with its basic commands, measure how long the operations take (the instructor suggests a small Python script), perform equivalent storage and retrieval against a relational database, and compare the timings.
- Short exact excerpt: Not needed; the spoken and slide requirements agree.
- Source ambiguity: the instructor does not choose a relational database, payload, schema, operation count, client library, warm-up, connection strategy, concurrency, durability configuration, statistical summary, or definition of “same operation.”

## Exact requirement checklist

- [ ] Set up Redis locally.
- [ ] Put data into Redis and retrieve it with basic commands.
- [ ] Measure the Redis operation time.
- [ ] Store and retrieve equivalent data through a relational database.
- [ ] Measure and compare the two paths.
- [ ] Explain the behavior you observed.

## Codex-added safety or verification

These controls make the exercise repeatable; they are not instructor wording:

- Use only the task-local Compose project `sd-beg-110-t01`.
- Bind Redis and PostgreSQL to loopback ports `55110` and `55111`.
- Use pinned Redis `8.10.1`, PostgreSQL `18.6`, redis-py `8.1.0`, and Psycopg `3.3.4`.
- Use synthetic credentials, one namespaced Redis key, one task-owned table, and a deterministic payload.
- Check exact returned values before trusting latency samples.
- Keep clients connected during measurement, warm both paths, record multiple samples and units, and disclose sequential concurrency.
- Do not assert that Redis must be faster; report the observed ordering and semantic differences.
- Reset only the exact key and table rows, then stop only the two task services.

## Inputs, constraints, and expected artifact

| Item | Contract |
|---|---|
| Input | One deterministic synthetic profile payload stored under logical key `profile:42` |
| Redis identity | Task-local `redis:8.10.1`, key namespace `sd-beg-110:t01:*`, persistence disabled for this cache experiment |
| Relational identity | Task-local `postgres:18.6`, database `sd_beg_110_t01`, table `public.cache_benchmark` |
| Baseline operations | Redis `SET`/`GET`; PostgreSQL autocommit upsert/primary-key `SELECT` |
| Measurement boundary | Persistent clients, sequential operations, warm-up disclosed, at least 50 recorded samples per operation |
| Output | Rahul's code or exact method, command, versions, correctness proof, latency summaries with units, explanation, and one variation |
| Completion evidence | Rahul-owned entries in `ATTEMPT.md`; the supplied reference run does not count as Rahul's attempt |

“Equivalent data” does not mean equivalent guarantees. A Redis write with persistence disabled and a PostgreSQL autocommit transaction do different work. The comparison is useful only when that boundary is stated.

## Before you start: predict

Record in `ATTEMPT.md`:

1. the order you expect for Redis `SET`, Redis `GET`, PostgreSQL upsert, and PostgreSQL primary-key read;
2. whether you expect the first sample to differ from later samples;
3. the exact payload invariant both systems must preserve;
4. what connection setup, network, parsing, query, and commit work each timer includes;
5. one result that would make you reject your first explanation.

Do not read `lab/evidence.md` before committing to this prediction.

## Setup

This task needs a real runtime because the instructor explicitly asks Rahul to operate Redis, operate a relational database, and measure both. Use the isolated instructions in [`lab/README.md`](lab/README.md).

Expected local budget: Docker Engine and Compose, Python 3.10 or newer, about 0.5 CPU during the tiny run, roughly 350–600 MiB of active memory, up to about 800 MiB of cold image/client downloads, and 30–120 seconds for a first start plus dependency installation.

## Learner steps

1. Run the read-only preflight and verify every identity before starting services.
2. Start only `redis` and `postgres` in project `sd-beg-110-t01`; wait for both health checks.
3. Use `redis-cli` to set and get one namespaced synthetic key. Record the exact returned value.
4. Use `psql` to create/use only `public.cache_benchmark`, upsert the same logical key and payload, and select it by primary key.
5. Complete [`starter/benchmark.py`](starter/benchmark.py) or write an equivalent benchmark. Use persistent clients and correctness assertions.
6. Warm each path, then record multiple latency samples with units and a distribution such as mean, p50, and p95.
7. Explain observed differences without treating different durability/query semantics as identical work.
8. Change one condition, predict first, rerun, and explain the changed distribution.
9. Reset the exact task state and stop only the task services.

## Progressive hints

<details><summary>Hint 1 — requirement</summary><p>The deliverable is not “Redis is fast.” It is a correct, repeatable put/get experiment plus a bounded relational comparison.</p></details>

<details><summary>Hint 2 — invariant</summary><p>Every timed read must return the exact deterministic payload for the same logical key. A fast wrong answer is a failed sample.</p></details>

<details><summary>Hint 3 — mechanism</summary><p>Keep connections open and warm both systems. Otherwise connection and initialization cost can dominate the operation you intended to study.</p></details>

<details><summary>Hint 4 — evidence</summary><p>Report a distribution, not only one elapsed time. First-run initialization and host scheduling often create outliers.</p></details>

<details><summary>Hint 5 — interpretation</summary><p>Ask what Redis skipped and what PostgreSQL guaranteed. Do not erase persistence, transaction, query, and protocol differences just because both returned bytes.</p></details>

## Acceptance criteria

- [ ] All six source requirements are represented in Rahul's own attempt.
- [ ] Preflight proves a local Unix Docker endpoint, exact project/services/images/labels, loopback ports, namespace, database, table, and volume.
- [ ] Redis and PostgreSQL each return the exact payload before any timing conclusion.
- [ ] Both clients remain persistent during the recorded loop, or connection-per-operation is explicitly the intended changed condition.
- [ ] Warm-up count, sample count, concurrency, payload bytes, units, and summary statistics are recorded.
- [ ] The explanation distinguishes latency evidence from production throughput/capacity.
- [ ] The explanation identifies the Redis persistence setting and PostgreSQL transaction boundary.
- [ ] One condition changes after a fresh prediction.
- [ ] Reset and cleanup touch only the exact task key, table rows, services, and labeled PostgreSQL volume boundary.
- [ ] Rahul can explain the result naturally without reading the reference.

## Cleanup/reset

Follow the exact commands in [`lab/README.md`](lab/README.md). The allowed reset targets are Redis key `sd-beg-110:t01:profile:42` and rows in `sd_beg_110_t01.public.cache_benchmark`. Stop services `redis` and `postgres` only. The labeled PostgreSQL volume is retained; no broad Docker cleanup is part of this task.

## Reference answer boundary

After writing a prediction and completing a first measurement, compare with [`reference/SOLUTION.md`](reference/SOLUTION.md). The reference uses [`reference/benchmark.py`](reference/benchmark.py) and the verifier; its verification status does not imply learner completion.
