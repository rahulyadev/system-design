# Runtime evidence — SD-BEG-110-T01

## Execution status

- Status: Passed
- Date/time: completed 2026-09-01T21:32:13+05:30
- Environment: Linux 7.0.0-30-generic x86_64; Docker Engine client/server 29.7.2; Docker Compose v5.5.0; isolated Python 3.12.13; redis-py 8.1.0; Psycopg 3.3.4; psycopg-binary 3.3.4
- Servers: Redis 8.10.1; PostgreSQL `18.6 (Debian 18.6-1.pgdg13+2)`
- Images: `redis:8.10.1` observed digest `redis@sha256:298e5b3bc566bade82f46ad5511777a4a07a294097ce16ada2f6a42be5239df5`; `postgres:18.6` observed digest `postgres@sha256:4ef4dbc939d61acea57712655ddb4b4ab27419c913f94cca0cd57cb3ea3c2280`
- Method: persistent clients, concurrency one, 40 warm-up operations, 250 measured baseline operations per path, 125 variation operations per path, 255-byte deterministic payload, `time.perf_counter_ns` clock
- Reason if skipped/failed: Not applicable to the final run. The host system Python 3.14.4 lacked `ensurepip`, so the run used an isolated Python 3.12.13 runtime without changing global packages.

## Prediction

This is the course/reference prediction, not Rahul's future learner prediction:

- Both systems should return the exact deterministic payload for the same logical key.
- Redis will likely have lower local sequential latency for this configuration because persistence is disabled and the key path avoids PostgreSQL statement/index/transaction work.
- PostgreSQL autocommit upsert is likely to cost more than its warmed primary-key read because each write commits a transaction.
- The final verifier should not assert a universal Redis/PostgreSQL latency ordering because the semantics and local host conditions differ.
- Adding a fixed 4 ms database delay should shift the delayed PostgreSQL read distribution by approximately that controlled work.

## Expected behavior

Persistent clients remove connection establishment from each sample. Warm-up reduces one-time import, connection, server, and allocation effects. Redis `SET`/`GET` and PostgreSQL autocommit upsert/primary-key `SELECT` must preserve the same JSON string before their latency samples are trusted. Redis `save` must be empty and `appendonly` must be `no`; the PostgreSQL upsert still commits independently. The controlled `pg_sleep(0.004)` variation should be visible in PostgreSQL p50 but does not model every production query.

## Actual run

The following commands genuinely ran from the task directory. The dependency install targeted only an isolated temporary Python environment.

```text
python3 lab/preflight.py
isolated-python -m pip install --requirement reference/requirements.txt
isolated-python lab/verify_reference.py
docker version --format 'client={{.Client.Version}} server={{.Server.Version}}'
docker compose version
```

Inside the verifier, genuine commands performed:

```text
read-only preflight
docker compose ... up -d redis postgres
Docker health and container/image/label/port/mount inspection
redis-cli INFO server
psql SHOW server_version
redis-cli CONFIG GET save
redis-cli CONFIG GET appendonly
reference/benchmark.py --iterations 250 --warmup 40
redis-cli UNLINK sd-beg-110:t01:profile:42
DELETE FROM public.cache_benchmark
zero-state assertions
docker compose ... stop redis postgres
container-state and retained-volume-label assertions
```

An earlier pre-measurement verifier run stopped because PostgreSQL returned its correct full package string while the verifier expected only `18.6`. It reset the exact state and stopped both services. The parser was narrowed to the semantic-version token while preserving the full build string, and the final run below passed. No latency claim was taken from the failed pre-measurement run.

## Observed evidence

```text
PREFLIGHT context=default endpoint=unix:///var/run/docker.sock services=redis,postgres ports=55110,55111 labels=verified volume=present-and-labeled
CLIENT_VERSIONS redis=8.1.0 psycopg=3.3.4 psycopg-binary=3.3.4 python=3.12.13
HEALTH service=redis status=healthy
HEALTH service=postgres status=healthy
RUNTIME_IDENTITY service=redis image=redis:8.10.1 port=127.0.0.1:55110
RUNTIME_IDENTITY service=postgres image=postgres:18.6 port=127.0.0.1:55111 volume=sd-beg-110-t01-postgres-18
SERVER_VERSIONS redis=8.10.1 postgres=18.6 postgres_build="18.6 (Debian 18.6-1.pgdg13+2)" redis_save=empty redis_appendonly=no
CORRECTNESS redis=exact postgres=exact rows=1 payload_bytes=255
BASELINE operation=redis_set count=250 p50_us=75.565 p95_us=217.455 mean_us=109.028
BASELINE operation=redis_get count=250 p50_us=95.323 p95_us=224.070 mean_us=123.121
BASELINE operation=postgres_upsert_autocommit count=250 p50_us=2112.231 p95_us=2586.320 mean_us=2176.748
BASELINE operation=postgres_primary_key_select count=250 p50_us=159.318 p95_us=311.554 mean_us=155.787
VARIATION redis_get_p50_us=104.924 postgres_plus_4ms_p50_us=4591.202
SEMANTICS redis_persistence=disabled postgres_upsert=autocommit comparison=not-equivalent-durability
RESET redis_key=absent postgres_rows=0 targets=exact-task-key-and-table
CLEANUP redis=exited postgres=exited postgres_volume=retained-and-labeled recoverable=true redis_persistence=disabled
RESULT_BOUNDARY ordering=redis-lower claim=local-sequential-measurement-not-production-capacity
SD-BEG-110-T01_REFERENCE_VERIFIED
```

Full measured ranges retained from the final benchmark:

| Operation | Min µs | Mean µs | p50 µs | p95 µs | Max µs | Samples |
|---|---:|---:|---:|---:|---:|---:|
| Redis `SET` | 40.278 | 109.028 | 75.565 | 217.455 | 492.584 | 250 |
| Redis `GET` | 81.570 | 123.121 | 95.323 | 224.070 | 403.491 | 250 |
| PostgreSQL autocommit upsert | 1,841.256 | 2,176.748 | 2,112.231 | 2,586.320 | 2,822.583 | 250 |
| PostgreSQL primary-key `SELECT` | 71.392 | 155.787 | 159.318 | 311.554 | 567.114 | 250 |
| Redis cached `GET` variation | 86.996 | 134.178 | 104.924 | 255.835 | 488.202 | 125 |
| PostgreSQL `SELECT` + 4 ms work | 4,292.191 | 4,635.656 | 4,591.202 | 5,000.337 | 5,099.194 | 125 |

## Explanation

The exact payload and one-row assertions establish correctness before timing interpretation. In this local sequential run, Redis had the lower observed read p50 (`95.323 µs` versus PostgreSQL `159.318 µs`) and much lower write p50 (`75.565 µs` versus PostgreSQL autocommit upsert `2,112.231 µs`). The write difference is not an apples-to-apples durability comparison: Redis persistence was intentionally disabled, while each PostgreSQL upsert was an autocommit transaction.

The PostgreSQL primary-key read was already fast because the table had one row, the connection stayed open, and the path was warm. That is useful: caching is not justified by slogans; avoided work must be measured. The injected 4 ms work moved the PostgreSQL read p50 to `4,591.202 µs`, while the unchanged Redis hit measured `104.924 µs`. This demonstrates avoided work under a controlled changed condition, not a universal product ranking.

## Variation

- Changed condition: add fixed 4 ms `pg_sleep` work to the PostgreSQL read projection while keeping key, payload, clients, concurrency, and Redis hit unchanged.
- Prediction: the delayed PostgreSQL p50 should expose at least roughly the injected delay; the Redis hit distribution should remain in its earlier local range.
- Actual result: PostgreSQL delayed-read p50 was `4,591.202 µs`; Redis cached-GET p50 was `104.924 µs`.
- Explanation: the measured database path now includes explicit extra work. The cache hit reuses the existing value and avoids that work. Scheduling/protocol overhead explains why the measured database p50 is not exactly 4,000 µs.

## Remaining proof gap

This run proves the deterministic reference path for one local Redis 8.10.1 process, one PostgreSQL 18.6 process, persistent sequential Python clients, one 255-byte value, and the exact configurations recorded above. It does not establish production throughput, concurrent/tail behavior, remote/TLS latency, larger values, realistic query plans/data size, pipelining/batching, connection-pool behavior, eviction/max-memory pressure, cache miss/hit-rate distributions, persistence-enabled Redis, replication/failover, database crash recovery, multi-region behavior, cost, or a universal product ranking. Both task containers are stopped; the exact key and table rows are empty; the labeled PostgreSQL volume is retained.
