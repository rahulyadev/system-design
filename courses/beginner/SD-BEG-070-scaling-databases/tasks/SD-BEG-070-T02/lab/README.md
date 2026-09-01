# Runtime lab — SD-BEG-070-T02

## Question this lab answers

Can one API mapping rule place every valid a–z key on exactly one of two MySQL shards, prove absence from the wrong shard, and expose how range skew defeats nominal aggregate capacity?

## Tool-selection justification

- Selected profile: `source-required task-local MySQL shards` (a narrow extension because the exercise requires two real databases and follows the MySQL task).
- Why a real runtime is needed: the assignment asks Rahul to spin up two databases and route API requests. Physical placement, wrong-shard absence, server identity, and independent failure domains are the evidence.
- Why a smaller simulation is insufficient: a dictionary map would teach the comparison but would not prove two connection pools or two database owners.
- Versions checked on 2026-09-01: `mysql:8.4.11` from the [Docker Official Image source](https://raw.githubusercontent.com/docker-library/mysql/master/versions.json) and `mysql2@3.24.2` from the npm registry.

## Resource budget

| Resource | Estimate |
|---|---|
| CPU | 1–1.5 cores peak during startup; usually below one core during the tiny run |
| Memory | about 1.2 GiB for two MySQL servers plus the host API/verifier |
| Disk/images | roughly 750 MiB shared image download plus two labeled volumes under 100 MiB each |
| Startup | 30–90 seconds from a cold image; commonly under 30 seconds when cached |
| Data generation | under 15 seconds for 27 stored synthetic rows plus one rejected input |

Run T01 and T02 separately; they intentionally use different project names, ports, volumes, databases, and labels.

## Safety preflight

From the task directory:

```bash
python3 lab/preflight.py
```

Require a local Unix Docker endpoint, project `sd-beg-070-t02`, services `shard_am`/`shard_nz`, image `mysql:8.4.11`, loopback ports `55711`/`55712`, exact task labels, database `sd_beg_070_t02`, and exact volumes `sd-beg-070-t02-am-mysql-8-4`/`sd-beg-070-t02-nz-mysql-8-4`. Stop on a mismatch or unrelated port/volume owner.

## Start and health check

```bash
docker compose -f lab/compose.yaml --project-name sd-beg-070-t02 --profile lab up -d shard_am shard_nz
docker compose -f lab/compose.yaml --project-name sd-beg-070-t02 --profile lab ps
docker compose -f lab/compose.yaml --project-name sd-beg-070-t02 --profile lab exec -T shard_am mysqladmin ping -h 127.0.0.1 -uroot -psd_beg_070_t02_root_local
docker compose -f lab/compose.yaml --project-name sd-beg-070-t02 --profile lab exec -T shard_nz mysqladmin ping -h 127.0.0.1 -uroot -psd_beg_070_t02_root_local
```

## Deterministic setup

Both shards receive the same [reference schema](../reference/schema.sql) independently. No replication connects them. Server ID `711` is the a–m owner and `712` is the n–z owner. The reference API normalizes one key and calls one centralized owner function before selecting one of two actual pools.

Reference path:

```bash
npm ci --prefix reference --ignore-scripts
python3 lab/verify_reference.py
```

Learner path: use `npm ci --prefix starter --ignore-scripts`, implement `starter/server.mjs`, and collect separate evidence in `../ATTEMPT.md`.

## Predict before running

Record owners/server IDs for `apple`, `mango`, `nectar`, and `zebra`; state the invalid-key result; and predict counts for 20 `a-hot-*` plus two `z-cold-*` keys. The expected skew ratio is a hypothesis until direct queries run.

## Run

```bash
python3 lab/preflight.py
npm ci --prefix reference --ignore-scripts
python3 lab/verify_reference.py
```

The verifier re-runs preflight, starts only this project, checks container/port/volume identity, loads each schema, starts the loopback reference API, proves boundary placement and wrong-shard absence, rejects a digit-prefixed key, runs the skew variation, then stops the two services and retains the labeled volumes.

## Inspect what happened

```bash
docker compose -f lab/compose.yaml --project-name sd-beg-070-t02 --profile lab exec -T shard_am mysql -uapp -psd_beg_070_t02_app_local -D sd_beg_070_t02 -e "SELECT @@server_id; SELECT key_name,value_text FROM records ORDER BY key_name;"
docker compose -f lab/compose.yaml --project-name sd-beg-070-t02 --profile lab exec -T shard_nz mysql -uapp -psd_beg_070_t02_app_local -D sd_beg_070_t02 -e "SELECT @@server_id; SELECT key_name,value_text FROM records ORDER BY key_name;"
```

For each key, require count `1` on its expected owner and count `0` on the other shard. This is stronger evidence than an API-provided shard name.

## Vary one condition

Keep the mapping fixed but skew the input distribution:

1. POST 20 distinct keys beginning `a-hot-`.
2. POST two distinct keys beginning `z-cold-`.
3. Count only those prefixes on each physical owner.
4. Confirm `20/2`, a `10:1` ownership ratio.
5. Explain why two equally sized servers do not provide evenly usable capacity under this workload.

This is a deterministic placement experiment, not a latency/throughput benchmark. A production mitigation might move a hot range, add sub-shards, isolate a tenant, or change the mapping, but each requires a migration and mapping-version plan.

## Reset and cleanup

First re-run `python3 lab/preflight.py`. Delete only `sd_beg_070_t02.records` on each exact shard:

```bash
docker compose -f lab/compose.yaml --project-name sd-beg-070-t02 --profile lab exec -T shard_am mysql -uapp -psd_beg_070_t02_app_local -D sd_beg_070_t02 -e "DELETE FROM records;"
docker compose -f lab/compose.yaml --project-name sd-beg-070-t02 --profile lab exec -T shard_nz mysql -uapp -psd_beg_070_t02_app_local -D sd_beg_070_t02 -e "DELETE FROM records;"
```

Stop only these services:

```bash
docker compose -f lab/compose.yaml --project-name sd-beg-070-t02 --profile lab stop shard_am shard_nz
```

The exact labeled volumes remain and are recoverable by restarting this project. Do not use a broad Docker cleanup or delete another task’s state.

## Troubleshooting

| Symptom | Check | Likely cause | Safe repair |
|---|---|---|---|
| Preflight rejects context | Docker context endpoint | remote/non-Unix context | switch deliberately to intended local context; do not continue automatically |
| Port collision | preflight conflicting container ID/project | unrelated owner of `55711`/`55712` | stop and ask; never kill or relabel automatically |
| One shard unhealthy | task `ps`, narrow service log, disk | cold image, initialization, resource pressure | preserve evidence; restart only that exact task service after diagnosis |
| API reports wrong server ID | pool port/config and `@@server_id` | connections swapped or stale environment | stop writes, repair central configuration, rerun physical-placement assertions |
| Key exists on both shards | direct count and router code/version | dual write, divergent rules, manual wrong-shard write | stop traffic for affected key, determine authoritative owner, reconcile with an audited migration |
| API misses an existing row | normalized key, selected shard, direct rows | GET and POST use different mapping or case rule | centralize normalization/routing and add boundary tests |
| One shard grows much faster | per-shard rows/bytes/writes and hot-key trace | input/range skew | plan a versioned split/move; do not change boundaries in one process only |
| Node cannot load `mysql2` | package lock and `npm ci` output | dependency missing from chosen boundary | run exact pinned install; do not rely on a global package |

Record genuine results in [`evidence.md`](evidence.md).
