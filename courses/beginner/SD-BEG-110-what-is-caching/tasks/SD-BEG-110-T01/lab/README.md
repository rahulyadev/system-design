# Runtime lab — SD-BEG-110-T01

## Question this lab answers

What do correct, repeated Redis `SET`/`GET` and PostgreSQL autocommit upsert/primary-key-read latency distributions look like on the same local host, and which semantic differences prevent that microbenchmark from being a universal database choice rule?

## Tool-selection justification

- Selected profile: `redis-task-local`, extended with one PostgreSQL service because the instructor explicitly assigns a relational comparison.
- Why a real runtime is needed: the exercise requires actual Redis commands, actual relational writes/reads, client/server round trips, transaction behavior, and observed timings.
- Why a smaller simulation is insufficient: a dictionary and SQLite timing could illustrate caching but would not satisfy the assigned Redis setup or demonstrate the two pinned server protocols.
- Redis image: `redis:8.10.1`, checked 2026-09-01 in the [Docker Official Images Redis registry](https://raw.githubusercontent.com/docker-library/official-images/master/library/redis). The task uses only stable `SET`, `GET`, `UNLINK`, `EXISTS`, `INFO`, and `CONFIG GET` behavior.
- PostgreSQL image: `postgres:18.6`, checked 2026-09-01 in the [Docker Official Image version registry](https://raw.githubusercontent.com/docker-library/postgres/master/versions.json) and [PostgreSQL 18.6 release notes](https://www.postgresql.org/docs/release/18.6/).
- Python clients: `redis==8.1.0` and `psycopg[binary]==3.3.4`, checked 2026-09-01 in their PyPI project registries.
- Redis persistence is explicitly disabled here. Redis documents “no persistence” as an option sometimes used for caching; PostgreSQL remains a durable relational system. This difference is part of the explanation, not an accidental benchmark detail.

## Resource budget

| Resource | Estimate |
|---|---|
| CPU | usually below 0.5 core after startup; brief cold-start/dependency peaks can be higher |
| Memory | approximately 350–600 MiB for Redis, PostgreSQL, Docker overhead, and the Python client |
| Disk/images | up to roughly 800 MiB on a cold host; PostgreSQL task data should remain below 50 MiB |
| Startup | commonly 10–60 seconds with cached images; up to 2 minutes on a cold host |
| Data generation | one Redis key, one PostgreSQL row, and under 1 KiB of logical payload |
| Benchmark | about 3–20 seconds for the supplied sequential reference, depending on local storage/host load |

## Safety preflight

From this task directory, run the read-only identity check:

```bash
python3 lab/preflight.py
```

It must report:

- a local Unix Docker endpoint;
- Compose project `sd-beg-110-t01`;
- services `redis` and `postgres` only;
- images `redis:8.10.1` and `postgres:18.6`;
- ports `127.0.0.1:55110:6379` and `127.0.0.1:55111:5432`;
- task label `SD-BEG-110-T01` on every existing project container/volume;
- Redis namespace `sd-beg-110:t01:*`;
- PostgreSQL database `sd_beg_110_t01` and table reset target `public.cache_benchmark`;
- exact volume `sd-beg-110-t01-postgres-18` as absent or present-and-labeled.

Stop on any mismatch. Never relabel, reuse, stop, or delete an unrelated container or volume.

## Start and health check

Start only the two task services:

```bash
docker compose -f lab/compose.yaml --project-name sd-beg-110-t01 --profile lab up -d redis postgres
docker compose -f lab/compose.yaml --project-name sd-beg-110-t01 --profile lab ps
docker compose -f lab/compose.yaml --project-name sd-beg-110-t01 --profile lab exec -T redis redis-cli ping
docker compose -f lab/compose.yaml --project-name sd-beg-110-t01 --profile lab exec -T postgres pg_isready -U benchmark -d sd_beg_110_t01
```

Expected health evidence is `PONG` and an accepting-connections result for the exact database. Health alone does not prove payload correctness.

## Deterministic setup

Create a task-specific virtual environment outside the Worktree. This keeps generated interpreter symlinks out of the repository validator's scan:

```bash
python3 -m venv /tmp/sd-beg-110-t01-venv
/tmp/sd-beg-110-t01-venv/bin/python -m pip install --requirement starter/requirements.txt
```

If `python3 -m venv` reports that `ensurepip` is unavailable, install the matching operating-system `python3-venv` package or deliberately use another isolated Python 3.10+ runtime. Do not install the task clients globally. The verified reference run used isolated Python 3.12.13 because this host's system Python 3.14.4 lacked `ensurepip`.

For a manual Redis smoke check, use only the namespaced key:

```bash
docker compose -f lab/compose.yaml --project-name sd-beg-110-t01 --profile lab exec -T redis redis-cli SET sd-beg-110:t01:profile:42 '{"id":42,"name":"synthetic-profile"}'
docker compose -f lab/compose.yaml --project-name sd-beg-110-t01 --profile lab exec -T redis redis-cli GET sd-beg-110:t01:profile:42
```

For a manual relational smoke check, create/use only the task table:

```bash
docker compose -f lab/compose.yaml --project-name sd-beg-110-t01 --profile lab exec -T postgres psql -v ON_ERROR_STOP=1 -U benchmark -d sd_beg_110_t01 -c "CREATE TABLE IF NOT EXISTS public.cache_benchmark (item_key text PRIMARY KEY, payload text NOT NULL, updated_at timestamptz NOT NULL DEFAULT clock_timestamp());"
docker compose -f lab/compose.yaml --project-name sd-beg-110-t01 --profile lab exec -T postgres psql -v ON_ERROR_STOP=1 -U benchmark -d sd_beg_110_t01 -c "INSERT INTO public.cache_benchmark(item_key,payload) VALUES ('sd-beg-110:t01:profile:42','{\"id\":42,\"name\":\"synthetic-profile\"}') ON CONFLICT (item_key) DO UPDATE SET payload=EXCLUDED.payload, updated_at=clock_timestamp();"
docker compose -f lab/compose.yaml --project-name sd-beg-110-t01 --profile lab exec -T postgres psql -v ON_ERROR_STOP=1 -U benchmark -d sd_beg_110_t01 -c "SELECT item_key,payload FROM public.cache_benchmark WHERE item_key='sd-beg-110:t01:profile:42';"
```

These commands prove basic put/get behavior. They do not yet provide a fair latency distribution.

## Predict before running

Before completing `starter/benchmark.py`, record:

- the four expected latency orderings and why;
- which one-time work warm-up should remove;
- whether Redis persistence is enabled;
- which PostgreSQL transaction boundary the write uses;
- why a Redis `SET` and PostgreSQL autocommit upsert are not identical guarantees;
- what result would falsify your explanation.

## Run

Learner path:

```bash
/tmp/sd-beg-110-t01-venv/bin/python starter/benchmark.py
```

The starter intentionally stops at marked sections until Rahul implements the comparison. A valid replacement is allowed if it preserves the safety, correctness, and evidence contracts.

Reference path, only after Rahul's attempt:

```bash
python3 -m venv /tmp/sd-beg-110-t01-venv
/tmp/sd-beg-110-t01-venv/bin/python -m pip install --requirement reference/requirements.txt
/tmp/sd-beg-110-t01-venv/bin/python lab/verify_reference.py
```

The verifier re-runs preflight, verifies exact client versions, starts only this project, waits for health, validates runtime images/labels/ports/volume/server versions/persistence settings, performs correctness-checked measurements, exercises one controlled variation, resets the exact key/table rows, stops both services, confirms the retained labeled volume, and emits a unique success marker only after every assertion passes.

## Inspect what happened

Use narrow commands:

```bash
docker compose -f lab/compose.yaml --project-name sd-beg-110-t01 --profile lab exec -T redis redis-cli INFO stats
docker compose -f lab/compose.yaml --project-name sd-beg-110-t01 --profile lab exec -T redis redis-cli INFO memory
docker compose -f lab/compose.yaml --project-name sd-beg-110-t01 --profile lab exec -T redis redis-cli CONFIG GET save
docker compose -f lab/compose.yaml --project-name sd-beg-110-t01 --profile lab exec -T redis redis-cli CONFIG GET appendonly
docker compose -f lab/compose.yaml --project-name sd-beg-110-t01 --profile lab exec -T postgres psql -U benchmark -d sd_beg_110_t01 -c "SELECT count(*), min(length(payload)), max(length(payload)) FROM public.cache_benchmark;"
```

Read a latency summary as a distribution:

| Field | Meaning | Useful warning |
|---|---|---|
| `mean_us` | arithmetic average in microseconds | sensitive to large outliers |
| `p50_us` | half the samples are at or below this value | does not describe the tail |
| `p95_us` | 95% are at or below this value | still not a production SLO under concurrency |
| `max_us` | slowest observed sample | one host pause can dominate it |

## Vary one condition

The supplied reference adds a fixed 4 ms `pg_sleep` to the PostgreSQL read while leaving the Redis cached hit unchanged.

Prediction contract:

1. baseline both exact read paths;
2. predict the delayed database p50 shift before running it;
3. keep key, payload, clients, and concurrency unchanged;
4. measure the delayed query and Redis hit again;
5. attribute the shift to the injected work, not to a universal Redis speed law.

Rahul may instead choose connection-per-operation, a larger payload, pipeline/batching, concurrent clients, a cache miss, or enabled Redis persistence—but change only one principal condition and disclose the changed semantics.

## Reset and cleanup

Run preflight again before mutation. Reset exactly one Redis key and task-table rows:

```bash
docker compose -f lab/compose.yaml --project-name sd-beg-110-t01 --profile lab exec -T redis redis-cli UNLINK sd-beg-110:t01:profile:42
docker compose -f lab/compose.yaml --project-name sd-beg-110-t01 --profile lab exec -T postgres psql -v ON_ERROR_STOP=1 -U benchmark -d sd_beg_110_t01 -c "DELETE FROM public.cache_benchmark;"
```

Verify zero task data, then stop only these services:

```bash
docker compose -f lab/compose.yaml --project-name sd-beg-110-t01 --profile lab exec -T redis redis-cli EXISTS sd-beg-110:t01:profile:42
docker compose -f lab/compose.yaml --project-name sd-beg-110-t01 --profile lab exec -T postgres psql -U benchmark -d sd_beg_110_t01 -Atc "SELECT count(*) FROM public.cache_benchmark;"
docker compose -f lab/compose.yaml --project-name sd-beg-110-t01 --profile lab stop redis postgres
```

The PostgreSQL volume remains labeled and recoverable; its synthetic table is empty after reset. Redis persistence is disabled, so its in-memory state is not recoverable after process restart. Do not use a broad Compose or Docker cleanup command.

## Troubleshooting

| Symptom | Check | Likely cause | Safe repair |
|---|---|---|---|
| Preflight refuses endpoint | `docker context inspect` | remote or non-Unix Docker context | deliberately select the intended local context; do not continue automatically |
| Preflight reports port conflict | conflicting container ID from output | another project reserves `55110` or `55111` | stop and choose with Rahul; never kill or relabel it automatically |
| Redis is unhealthy | task `ps` and `logs redis` | cold image, command/config error, host pressure | inspect/restart only this task's Redis service |
| PostgreSQL is unhealthy | task `ps` and `logs postgres` | initialization, disk, volume, or credential issue | inspect the exact labeled volume and task service; preserve state |
| Python import fails | `/tmp/sd-beg-110-t01-venv/bin/python -m pip show redis psycopg psycopg-binary` | wrong interpreter or dependencies not installed | install the exact task requirements into the task-specific virtual environment; do not depend on globals |
| Virtual environment creation reports missing `ensurepip` | `python3 -m venv /tmp/sd-beg-110-t01-venv` output and OS Python packaging | matching `python3-venv` support is absent | install the matching OS venv package or deliberately use another isolated Python 3.10+ runtime; do not install globally |
| First samples are slow | compare warm-up and measured ranges | connection, import, allocation, or server initialization | keep clients persistent and disclose warm-up rather than deleting inconvenient samples |
| Redis is not faster | correctness, payload, persistence, operation, host load | measurement noise or non-equivalent path | report the observation; inspect semantics and method instead of forcing the expected story |
| High p95/max | rerun with host load and per-operation samples | scheduling, storage flush, background work, insufficient samples | preserve the outliers, repeat under a stated condition, and avoid production extrapolation |
| Reset fails | exact key/table and service health | wrong scope or stopped service | stop mutation, re-run preflight, and repair only the exact task service |

Record genuine results in [`evidence.md`](evidence.md).
