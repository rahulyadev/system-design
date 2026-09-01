# Runtime lab — SD-BEG-070-T01

## Question this lab answers

Can an API prove that writes use a MySQL primary, eligible reads use a replica, and a committed write remains temporarily invisible on that replica while its applier is paused?

## Tool-selection justification

- Selected profile: `source-required task-local MySQL topology` (a narrow extension because the instructor explicitly assigns MySQL replication).
- Why a real runtime is needed: separate receiver/applier state, binary-log positions, read-only enforcement, and query visibility are product semantics; a dictionary copy would not prove them.
- Why a smaller simulation is insufficient: a simulation could illustrate lag but could not validate MySQL configuration, server identity, replication status, or write rejection.
- Versions checked on 2026-09-01: `mysql:8.4.11` from the [Docker Official Image source](https://raw.githubusercontent.com/docker-library/mysql/master/versions.json), MySQL [replication documentation](https://dev.mysql.com/doc/refman/8.4/en/replication.html), and `mysql2@3.24.2` from the npm registry.

## Resource budget

| Resource | Estimate |
|---|---|
| CPU | 1–1.5 cores peak during startup; usually below one core during the tiny run |
| Memory | about 1.2 GiB for two MySQL servers plus the host API/verifier |
| Disk/images | roughly 750 MiB shared image download plus two labeled volumes under 100 MiB each for this fixture |
| Startup | 30–90 seconds from a cold image; commonly under 30 seconds when cached |
| Data generation | under 10 seconds and fewer than ten rows |

Run this task separately from T02 so its port, memory, and evidence boundaries stay obvious.

## Safety preflight

From the task directory:

```bash
python3 lab/preflight.py
```

The read-only preflight must report:

- a local Unix Docker endpoint;
- project `sd-beg-070-t01`;
- services `source` and `replica`, both pinned to `mysql:8.4.11`;
- ports `127.0.0.1:55701:3306` and `127.0.0.1:55702:3306`;
- task label `SD-BEG-070-T01` on any existing project container or volume;
- exact volumes `sd-beg-070-t01-source-mysql-8-4` and `sd-beg-070-t01-replica-mysql-8-4`;
- database `sd_beg_070_t01` and the scoped table reset target `sd_beg_070_t01.items`.

Stop on any mismatch. Never relabel, reuse, or delete an unrelated container or volume.

## Start and health check

```bash
docker compose -f lab/compose.yaml --project-name sd-beg-070-t01 --profile lab up -d source replica
docker compose -f lab/compose.yaml --project-name sd-beg-070-t01 --profile lab ps
docker compose -f lab/compose.yaml --project-name sd-beg-070-t01 --profile lab exec -T source mysqladmin ping -h 127.0.0.1 -uroot -psd_beg_070_t01_root_local
docker compose -f lab/compose.yaml --project-name sd-beg-070-t01 --profile lab exec -T replica mysqladmin ping -h 127.0.0.1 -uroot -psd_beg_070_t01_root_local
```

## Deterministic setup

The source starts with binary logging and server ID `701`; the replica uses server ID `702`. Configure file/position replication only after both independent Docker initialization sequences finish. The application schema is loaded on the source after replication is running, so its DDL and later rows are copied rather than created independently.

Install only the pinned reference dependency when verifying the supplied answer:

```bash
npm ci --prefix reference --ignore-scripts
python3 lab/verify_reference.py
```

For the learner path, use `npm ci --prefix starter --ignore-scripts`, implement `starter/server.mjs`, configure replication, and collect your own evidence. The reference verifier does not execute or grade the starter.

## Predict before running

Record in `../ATTEMPT.md`:

- primary and replica server IDs;
- the route for POST, eventual GET, and strong GET;
- the result of each GET while the SQL/applier thread is paused;
- the source position/catch-up evidence you expect;
- the error expected from an application-user write on the replica.

## Run

Reference-path command:

```bash
python3 lab/preflight.py
npm ci --prefix reference --ignore-scripts
python3 lab/verify_reference.py
```

The verifier re-runs preflight, starts only this Compose project, verifies every runtime identity, configures/resumes the replica, loads deterministic schema, starts the loopback reference API, runs the baseline and variation, then stops the two services while retaining labeled volumes.

## Inspect what happened

Useful narrow learner commands:

```bash
docker compose -f lab/compose.yaml --project-name sd-beg-070-t01 --profile lab exec -T source mysql -uroot -psd_beg_070_t01_root_local -NBe "SELECT @@server_id, VERSION(); SHOW BINARY LOG STATUS;"
docker compose -f lab/compose.yaml --project-name sd-beg-070-t01 --profile lab exec -T replica mysql -uroot -psd_beg_070_t01_root_local -e "SHOW REPLICA STATUS\G"
docker compose -f lab/compose.yaml --project-name sd-beg-070-t01 --profile lab exec -T source mysql -uapp -psd_beg_070_t01_app_local -D sd_beg_070_t01 -e "SELECT id,name FROM items ORDER BY id;"
docker compose -f lab/compose.yaml --project-name sd-beg-070-t01 --profile lab exec -T replica mysql -uapp -psd_beg_070_t01_app_local -D sd_beg_070_t01 -e "SELECT id,name FROM items ORDER BY id;"
```

Do not treat `served_by` alone as proof. Compare it with `@@server_id`, the physical row, and replication position.

## Vary one condition

Simulate only **apply delay**:

1. verify `Replica_IO_Running=Yes` and `Replica_SQL_Running=Yes`;
2. execute `STOP REPLICA SQL_THREAD` on `replica`;
3. POST one new item through the API;
4. predict and compare strong versus eventual GET;
5. inspect the row directly on both servers;
6. execute `START REPLICA SQL_THREAD`;
7. wait for the replica to reach the recorded source file/position;
8. repeat the eventual GET.

Abort if service identity, task labels, receiver state, or source host differs from the contract. The failure is safe and recoverable because only one task-local applier thread is paused; the source and retained logs remain available.

## Reset and cleanup

First re-run `python3 lab/preflight.py`. Delete only the task table’s rows on the primary, allowing the deletion to replicate:

```bash
docker compose -f lab/compose.yaml --project-name sd-beg-070-t01 --profile lab exec -T source mysql -uapp -psd_beg_070_t01_app_local -D sd_beg_070_t01 -e "DELETE FROM items;"
```

Stop only the task services:

```bash
docker compose -f lab/compose.yaml --project-name sd-beg-070-t01 --profile lab stop source replica
```

The two exact labeled volumes are retained, so this cleanup is recoverable by restarting the same services. Do not remove them through a broad Compose or Docker cleanup command.

## Troubleshooting

| Symptom | Check | Likely cause | Safe repair |
|---|---|---|---|
| Preflight rejects Docker endpoint | `docker context inspect` output | remote/non-Unix context | switch deliberately to the intended local context; do not continue automatically |
| Port already used | preflight’s conflicting container identity | unrelated process/project owns `55701` or `55702` | stop and choose with Rahul; never kill or relabel it automatically |
| Source/replica unhealthy | task `ps` and narrow service logs | cold image, initialization, disk, or option error | inspect only these services; preserve evidence; restart only the failed task service |
| `Replica_IO_Running=No` | `Last_IO_Error`, source host, user, network | authentication, source connectivity, or purged log | repair channel or rebuild only this replica; do not skip missing history silently |
| `Replica_SQL_Running=No` | `Last_SQL_Error`, relay/source positions | apply error or intentionally paused thread | confirm whether the pause is expected; repair the exact error before resume |
| Eventual read never catches up | source file/position and `SOURCE_POS_WAIT` result | applier stopped/failed or source position unavailable | stop the claim, inspect status/logs, and retain task state for diagnosis |
| Replica accepts app write | `@@read_only`, `@@super_read_only`, grants | guard not enabled or overly privileged user | enable both guards and remove excess application privilege before testing |
| Node cannot load `mysql2` | `reference/package-lock.json`, `npm ci` result | dependency not installed in that boundary | run the exact pinned `npm ci --prefix ... --ignore-scripts`; do not use a global package |

Record genuine results in [`evidence.md`](evidence.md).
