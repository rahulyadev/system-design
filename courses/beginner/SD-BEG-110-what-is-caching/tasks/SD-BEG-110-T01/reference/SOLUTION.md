# Reference solution — SD-BEG-110-T01

> **Spoiler:** Open only after writing a committed prediction and completing a first learner measurement. This is one defensible local experiment, not proof that Redis is always faster or PostgreSQL is the wrong cache.

## Clarifications and assumptions

- “Put and get” becomes Redis `SET`/`GET` and PostgreSQL autocommit upsert/primary-key `SELECT` for one logical key.
- Both systems store the same deterministic JSON string, and every read must return it byte-for-byte.
- Clients connect once, then execute sequential operations at concurrency one. Connection setup is excluded from per-operation samples.
- Forty warm-up operations run before 250 measured operations per baseline path.
- Timings use `time.perf_counter_ns` and are reported in microseconds as min, mean, p50, p95, and max.
- Redis RDB and AOF persistence are disabled to model an intentionally disposable cache. PostgreSQL uses one autocommit transaction per upsert. Therefore write semantics are not equivalent.
- The task proves behavior only for the exact local host, versions, payload, and low-concurrency path.

## Prediction

Both paths should preserve the exact payload. Redis will probably show lower p50 latency because the selected path is a direct in-memory key lookup/write without the relational statement/transaction work performed by PostgreSQL. The first/warm-up samples may be slower. PostgreSQL may show a wider write tail due to commit/storage scheduling.

That ordering is a prediction, not a test assertion. A valid run can observe PostgreSQL equal to or below Redis because the local scheduler, client implementations, caches, virtualization, or sample method can dominate small operations. Correctness and a complete measurement are the invariant; a universal speed ranking is not.

## Approach and why it fits

The reference uses the smallest real topology that satisfies every source requirement:

1. one task-local Redis process;
2. one task-local PostgreSQL process;
3. one Python process with persistent redis-py and Psycopg clients;
4. one namespaced key and one table row;
5. one correctness assertion around every timed read/write path;
6. one controlled variation that injects 4 ms of database work;
7. exact scoped reset and service stop.

It avoids a simulated dictionary because the instructor asks Rahul to set up and measure Redis. It avoids a distributed cluster because replication, sharding, failover, and production load are not part of this exercise.

## Step-by-step solution

### 1. Prove identity before mutation

Run `lab/preflight.py`. It rejects non-Unix Docker endpoints, mismatched projects/images/labels/ports, unrelated port owners, a wrongly labeled volume, the wrong database, and an unexpected Redis persistence command.

### 2. Start and verify services

Start only `redis` and `postgres`. Wait for Docker health, inspect actual container image/label/project/port/mount identity, query Redis `INFO server`, query PostgreSQL `SHOW server_version`, and verify Redis `save` is empty and `appendonly` is `no`.

### 3. Reset the exact logical state

Delete only Redis key `sd-beg-110:t01:profile:42`. Create `public.cache_benchmark` if absent, then delete only its rows. Never flush Redis, drop a database, or remove broad Docker state.

### 4. Establish correctness

Write the deterministic payload through Redis and PostgreSQL. Read it back from both. Reject the run immediately if either value differs or the PostgreSQL key has anything other than one row.

### 5. Warm and measure

Warm all four paths with persistent clients. Then time each operation separately for 250 sequential samples. A timer surrounds only the client operation, so it includes serialization, loopback protocol, server execution, reply parsing, and—on the PostgreSQL write—an autocommit transaction.

### 6. Summarize without hiding tails

Sort each sample list and report min, arithmetic mean, p50, p95, and max. Preserve the observed ordering rather than converting the prediction into a forced assertion.

### 7. Vary one condition

Add `pg_sleep(0.004)` to the PostgreSQL read projection while leaving the Redis hit unchanged. The verifier requires the delayed PostgreSQL p50 to expose at least 3.5 ms, proving the controlled work entered the measured boundary. It does not claim every database query costs 4 ms.

### 8. Reset and stop

`UNLINK` only the exact Redis key and delete only task-table rows. Assert zero remaining task data. Stop the two services, verify both containers are exited, and retain the correctly labeled PostgreSQL volume.

## Correctness invariant

For logical key `profile:42`, every successful timed read must return the exact deterministic payload most recently written by that same path. The Redis namespace, PostgreSQL database/table, Compose project, ports, labels, and volume must remain inside `SD-BEG-110-T01`. Timing evidence is invalid if identity or payload correctness fails.

The benchmark also preserves an interpretation invariant: measured latency describes this method and environment; it does not silently become a claim about durability, throughput under concurrency, remote latency, arbitrary queries, cache hit rate, or production cost.

## Complexity, capacity, or resource reasoning

- Redis `GET` and `SET` are constant-time for this simple string-key use in the course-level model; the hidden constant includes hashing, network/protocol, allocation, and server work.
- PostgreSQL primary-key lookup is index-based and typically logarithmic in index size, but the one-row local table makes algorithmic growth irrelevant to this microbenchmark.
- At 250 sequential samples, the run estimates a local distribution; it cannot saturate either service or establish maximum throughput.
- A 300-byte payload at 10,000 cached profiles is roughly 3 MB of payload alone. Real cache memory is higher because keys, object metadata, allocator fragmentation, expiry structures, replication buffers, and client overhead also consume memory.
- A cache decision needs hit rate and miss penalty. If a hit costs 1 ms, a miss path costs 22 ms, and hit rate is 90%, expected latency is `0.90 × 1 + 0.10 × 22 = 3.1 ms`; this task's direct-operation timing is only one input to that larger model.

## Verification status

- Status: passed
- Evidence: [`../lab/evidence.md`](../lab/evidence.md)
- Observed baseline p50: Redis `SET` 75.565 µs; Redis `GET` 95.323 µs; PostgreSQL autocommit upsert 2,112.231 µs; PostgreSQL primary-key read 159.318 µs.
- Observed variation p50: Redis cached `GET` 104.924 µs; PostgreSQL read plus controlled 4 ms work 4,591.202 µs.
- Correctness: both systems returned the exact 255-byte payload; PostgreSQL contained exactly one keyed row before scoped reset.
- Limitation: this remains one local, sequential, synthetic microbenchmark with non-equivalent write durability.

## Failure modes and recovery

| Failure | Symptom | Response | Remaining risk |
|---|---|---|---|
| Wrong Docker context | preflight reports non-Unix endpoint | stop before mutation and deliberately select the intended local context | a local endpoint is still not proof of an idle/safe host without identity checks |
| Port collision | unrelated container owns `55110` or `55111` | stop and choose with Rahul; do not kill or relabel it | a non-container process can still bind between checks and start |
| Payload mismatch | a timed read returns missing/different JSON | fail the run and inspect key/table/client encoding | earlier timing samples are unusable correctness evidence |
| Redis restart | key disappears because persistence is disabled | repopulate from the source of truth; treat this as expected cache loss | simultaneous fallback traffic can overload PostgreSQL |
| PostgreSQL commit/storage tail | high write p95/max | inspect host load/storage and repeat under a stated condition | local volume behavior differs from managed/remote storage |
| Client warm-up | early samples much slower | disclose warm-up and keep the raw reasoning boundary | arbitrary sample deletion can hide real cold-start behavior |
| Misleading comparison | conclusion says Redis replaces PostgreSQL because p50 is lower | restate guarantees, access patterns, query needs, and failure model | organizational decisions can still misuse a microbenchmark |
| Cleanup interruption | service remains running or task data remains | re-run preflight, reset exact targets, stop exact services | retained PostgreSQL state remains until verified reset |

## Alternatives

| Alternative | Prefer when | Why not selected here |
|---|---|---|
| Python dictionary simulation | teaching hit/miss or eviction policy without product semantics | does not satisfy the instructor's Redis setup/command requirement |
| Redis `redis-benchmark` and PostgreSQL `pgbench` | exploring each product's throughput with mature load tools | defaults and operation models are not equivalent and can hide the beginner mechanism |
| Connection-per-operation benchmark | studying connection/TLS/pool setup | would measure a different boundary and overwhelm the basic data-operation lesson |
| Pipelined/batched operations | studying throughput and round-trip amortization | changes concurrency/batching semantics and obscures the one-operation baseline |
| SQLite comparison | a relational library is needed without a server | avoids PostgreSQL protocol/commit behavior and weakens the assigned server comparison |
| Production-like load generator | SLO/capacity planning under concurrency | requires workload models, isolation, monitoring, and resources far beyond this exercise |

## Interview follow-ups

### SDE-2

- Why is one timing sample invalid? Discuss warm-up, host noise, correctness, and distributions.
- Why can a cache hit reduce database load but a cache outage increase it catastrophically? Trace fallback and saturation.
- What metrics separate a low hit ratio from a slow cache? Use outcome-tagged latency, hits/misses, errors, evictions, and database QPS.
- How would you invalidate a cached profile after an update? State the stale-data window and failure behavior.

### SDE-3

- At 50,000 requests/s and 95% hit ratio, what database QPS remains? What happens if the cache fleet fails at once?
- How would you prevent a hot key or miss storm from concentrating load? Compare request coalescing, jittered TTL, stale-while-revalidate, replication, and admission control.
- When is Redis allowed to become authoritative rather than a rebuildable cache? Define persistence, replication, backup, recovery-point, and recovery-time requirements.
- How would you design a benchmark that informs a production decision? Define workload distribution, payloads, concurrency, duration, network, durability, failure injection, confidence, and cost.

## Compare with Rahul's attempt

Complete only after Rahul attempts:

- Correct decisions:
- Missing reasoning:
- Different but valid choices:
- Evidence that changes the reference interpretation:
- One thing to retry closed-book:
