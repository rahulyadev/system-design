# Runtime lab - SD-BEG-090-T01

## Question this lab answers

What capability becomes directly observable when the same tiny domain is exercised through a document update, exact-key commands, and a relationship path query?

## Tool-selection justification

- Selected profile: `task-local-mongodb-redis-neo4j`, a narrow extension of the repository’s task-local service pattern because the instructor explicitly requires all three products.
- Why real runtimes are needed: the assignment is to run and use MongoDB, Redis, and Neo4j locally. A simulation would not demonstrate their actual clients, commands, query syntax, atomic operators, or runtime identities.
- Why one combined heavy cluster is unnecessary: sharding, replication, and failover are not assigned. Each product runs as one task-local node and can be started, verified, and stopped before the next.
- Versions and primary sources checked on 2026-09-01:
  - MongoDB `mongo:8.0.29-noble`: [Docker Official Image supported tags](https://hub.docker.com/_/mongo) and [MongoDB 8.0.29 release notes](https://www.mongodb.com/docs/manual/release-notes/8.0/). MongoDB 8.0 is a major release with a predictable lifecycle; `8.0.29` was the latest published patch, while `8.0.30` was still marked upcoming.
  - Redis `redis:8.10.1-alpine3.23`: [Docker Official Image supported tags](https://hub.docker.com/_/redis) and [Redis Open Source version management](https://redis.io/docs/latest/operate/oss_and_stack/install/version-mgmt/). The exact Alpine tag keeps the image small and avoids a moving alias.
  - Neo4j `neo4j:2026.07.1`: [official Docker guide](https://neo4j.com/docs/operations-manual/current/docker/introduction/) and [release notes](https://neo4j.com/release-notes/). The guide names this exact Community Edition tag, and the release notes identify it as the current release checked on that date.

Runtime compatibility boundary observed on 2026-09-01: MongoDB’s 8.0 release notes warn that Linux kernels `6.19` through `7.0.13` are incompatible. This host is `7.0.0-30-generic`, and `mongod` exited with that exact safety diagnosis before accepting data. The verifier therefore skips MongoDB on this host, does not bypass the guard, and runs the applicable Redis/Neo4j checks. Use a compatible host kernel, including `7.0.14` or later for this documented boundary, to complete the MongoDB sub-requirement.

## Resource budget

The verifier runs the services sequentially.

| Resource | Estimate |
|---|---|
| CPU | usually below 1 core after startup; brief startup/query spikes up to about 2 cores |
| Memory | Redis under 128 MiB; MongoDB roughly 300-700 MiB; Neo4j roughly 700 MiB-1.2 GiB with the configured heap/page cache; sequential peak about 1.2 GiB |
| Disk/images | roughly 1-1.5 GiB of downloaded/unpacked images in total; deterministic task data under 100 MiB; three retained labeled volumes |
| Startup | warm: roughly 5-60 seconds per service; cold pulls may take several minutes depending on network |
| Data generation | normally under 5 seconds per service |

These are planning estimates, not measured guarantees. Docker Desktop/VM overhead and image cache state can dominate.

## Safety preflight

Run:

```bash
python3 preflight.py
```

The read-only script prints and verifies:

- a local Docker Unix-socket context;
- exact Compose project `sd-beg-090-t01`;
- exact service images and task labels;
- only `127.0.0.1:55901`, `55902`, `55903`, and `55904` bindings;
- exact volumes `sd-beg-090-t01-mongo-8-0-data`, `sd-beg-090-t01-redis-8-10-data`, and `sd-beg-090-t01-neo4j-2026-07-data`;
- absence of an unrelated container on any task port;
- narrow reset targets for the MongoDB database/collection filter, Redis keys, and Neo4j label/property.

Stop on any mismatch. Do not relabel, reuse, overwrite, or delete an unrelated container or volume.

## Start and health check

Use one profile at a time:

```bash
docker compose -f compose.yaml --project-name sd-beg-090-t01 --profile mongo up -d mongo
docker compose -f compose.yaml --project-name sd-beg-090-t01 --profile mongo ps

docker compose -f compose.yaml --project-name sd-beg-090-t01 --profile redis up -d redis
docker compose -f compose.yaml --project-name sd-beg-090-t01 --profile redis ps

docker compose -f compose.yaml --project-name sd-beg-090-t01 --profile neo4j up -d neo4j
docker compose -f compose.yaml --project-name sd-beg-090-t01 --profile neo4j ps
```

The image health checks use `mongosh` ping, authenticated `redis-cli PING`, and authenticated `cypher-shell RETURN 1`. Do not treat health as completion evidence.

## Deterministic setup

The supplied reference verifier owns these exact fixtures:

| Service | Namespace | Deterministic state |
|---|---|---|
| MongoDB | `sd_beg_090_t01.products`, filtered by `lab_id=SD-BEG-090-T01` | two products; only the shirt has `size`; book stock begins at `2` |
| Redis | prefix `sd:beg:090:t01:` | one JSON string, one integer counter beginning at `270`, one temporary key |
| Neo4j | `LabPerson` nodes with `lab_id=SD-BEG-090-T01` | `Asha -> Ben -> Chen` through two directed `FOLLOWS` relationships |

To verify only the physically separate reference path:

```bash
python3 verify_reference.py
```

The verifier re-runs preflight and checks the host kernel before starting MongoDB. On a compatible kernel it tests all three products. On a kernel in MongoDB’s documented incompatible range it records a MongoDB skip, stops any task MongoDB container, tests Redis and Neo4j, and reports only the applicable-check marker. It never converts that partial result into full verification and never reads or grades `ATTEMPT.md`.

## Predict before running

Record in `../ATTEMPT.md`:

- MongoDB stock before/after, flexible-field count, and atomicity boundary;
- Redis exact GET value, counter result, deletion result, and command boundary;
- Neo4j node/relationship counts, baseline hop count, and changed hop count after one direct relationship;
- identity/version evidence and what the single-node setup cannot prove.

## Run

Reference path:

```bash
python3 preflight.py
python3 verify_reference.py
```

Learner path: follow `../README.md`, use each database’s container-local client, and capture your own commands and output. Do not copy the reference commands before attempting the query shapes yourself.

## Inspect what happened

Useful identity-only checks:

```bash
docker compose -f compose.yaml --project-name sd-beg-090-t01 --profile lab ps -a
docker inspect --format '{{json .Config.Labels}}' sd-beg-090-t01-mongo-1
docker inspect --format '{{json .Config.Labels}}' sd-beg-090-t01-redis-1
docker inspect --format '{{json .Config.Labels}}' sd-beg-090-t01-neo4j-1
```

Container names can differ if Compose changes its naming implementation; `preflight.py` and the verifier resolve containers by project/service labels and are the authoritative checks.

The useful data evidence is:

- MongoDB: two documents, exactly one `size=M`, stock `2 -> 3`, `matchedCount=1`, `modifiedCount=1`, and one product in each category;
- Redis: exact profile bytes, counter `270 -> 271`, delete count `1`, and post-delete existence `0`;
- Neo4j: three nodes, two baseline relationships, shortest path `2`, then three relationships and shortest path `1`.

## Vary one condition

Baseline graph:

```text
Asha --FOLLOWS--> Ben --FOLLOWS--> Chen
```

Changed condition: add only `Asha --FOLLOWS--> Chen` inside the task namespace.

Make the prediction before executing. Expected evidence is a relationship count change from `2` to `3` and a shortest-hop change from `2` to `1`. This demonstrates path semantics on a tiny graph; it does not benchmark traversal performance.

## Reset and cleanup

First re-run `python3 preflight.py` and stop if identity differs.

Reset only the MongoDB task documents:

```bash
docker compose -f compose.yaml --project-name sd-beg-090-t01 --profile mongo exec -T mongo mongosh --quiet --username sd_beg_090_t01_root --password sd_beg_090_t01_mongo_local --authenticationDatabase admin --eval "db.getSiblingDB('sd_beg_090_t01').products.deleteMany({lab_id: 'SD-BEG-090-T01'})"
```

Reset only the three Redis task keys:

```bash
docker compose -f compose.yaml --project-name sd-beg-090-t01 --profile redis exec -T -e REDISCLI_AUTH=sd_beg_090_t01_redis_local redis redis-cli --no-auth-warning DEL sd:beg:090:t01:profile:42 sd:beg:090:t01:counter sd:beg:090:t01:temporary
```

Reset only the Neo4j task nodes and their attached task relationships:

```bash
docker compose -f compose.yaml --project-name sd-beg-090-t01 --profile neo4j exec -T neo4j cypher-shell -a bolt://127.0.0.1:7687 -u neo4j -p sd_beg_090_t01_neo4j_local "MATCH (n:LabPerson {lab_id: 'SD-BEG-090-T01'}) DETACH DELETE n;"
```

Stop only the task services:

```bash
docker compose -f compose.yaml --project-name sd-beg-090-t01 --profile lab stop --timeout 60 mongo redis neo4j
```

The exact labeled volumes are retained, so stopping is recoverable by starting the same service. This task never needs to remove a volume.

## Troubleshooting

| Symptom | Check | Likely cause | Safe repair |
|---|---|---|---|
| Preflight refuses endpoint | `docker context inspect` output from preflight | remote/TCP Docker context | deliberately switch to the intended local context; do not continue automatically |
| Port already owned | preflight’s conflicting container ID and project label | unrelated service uses `55901-55904` | stop and choose with Rahul; never kill or relabel it automatically |
| Image pull fails | exact image name and Docker daemon/network output | restricted network, registry outage, or unsupported architecture | preserve skipped evidence; retry only the exact image after access is available |
| MongoDB exits with kernel incompatibility | host `uname -r` plus the narrow task log | kernel is in MongoDB’s documented `6.19` through `7.0.13` range | do not bypass; use a compatible host kernel and rerun preflight |
| MongoDB remains unhealthy | task `ps` and narrow `mongo` logs | initialization, credentials, disk, or image issue | inspect/restart only `mongo`; keep its labeled volume |
| Redis returns `NOAUTH` | `REDISCLI_AUTH` and service identity | client omitted synthetic password | pass the documented local credential; do not disable auth globally |
| Neo4j rejects login at first start | task `neo4j` logs and exact volume label | initialization incomplete or an older task-local password in retained volume | inspect only this labeled volume; use its known task credential or ask before any reset |
| Cypher path returns no row | node names, `lab_id`, relationship direction/type | fixture or predicate mismatch | inspect the three task nodes/relationships; do not broaden the match to unrelated nodes |
| Verifier stops after one service | last unique marker and task `ps -a` | assertion or health failure | retain evidence and volumes; repair only the named service, rerun preflight, then retry |

Record genuine results in [`evidence.md`](evidence.md).
