# Local lab safety and reproducibility

## Scope

Labs use disposable, synthetic local resources. They must never target a production host, employer system, existing personal database, real cloud account, or shared Docker environment without explicit authorization.

## Required preflight

Before mutation or failure injection, print and verify:

- current Docker context;
- exact Compose project name;
- exact service/container identity;
- bound loopback ports;
- exact database and schema/queue/bucket/topic;
- exact disposable volume labels;
- recoverability/reset method.

If identity differs, stop.

## Network safety

Published ports bind to `127.0.0.1`. Do not publish databases, brokers, admin UIs, telemetry endpoints, or debug servers on all interfaces.

Use synthetic local credentials in `.env.example`; never use real tokens or cloud secrets.

## Data and reset

- Seed data is deterministic and synthetic.
- Reset targets one exact allowlisted schema, queue, topic, bucket, cache namespace, or task-local volume.
- Show the target before deletion.
- Prefer reloading a schema or task-local volume over broad service cleanup.

Forbidden commands include:

```text
docker system prune
docker compose down --volumes
docker-compose down -v
unscoped docker volume prune
unverified DROP DATABASE
recursive deletion of a workspace, home directory, or broad path
```

## Failure injection

State:

1. the failure being simulated;
2. why it is safe and recoverable;
3. exact scope;
4. expected evidence;
5. abort condition;
6. recovery command;
7. post-recovery invariant.

## Resource budget

Every task-local stack documents approximate CPU, memory, disk, image download, startup time, and data generation time. Prefer simulation when a heavy cluster adds little learning value.

## Versions

At task creation, resolve service/library versions from primary sources and record them in `task.json` or the lab README. Pin explicit supported tags; never use `latest`. When a historical course behavior differs from a current release, either pin the historical version safely or explain and demonstrate the current behavior boundary.

The reusable root database baseline was checked on 2026-08-31. PostgreSQL's [18.6 release notes](https://www.postgresql.org/docs/release/18.6/) and the Docker Official Image [version registry](https://github.com/docker-library/postgres/blob/master/versions.json) support the exact `postgres:18.6` pin. The official image [documents](https://github.com/docker-library/docs/blob/master/postgres/README.md) the PostgreSQL 18 `PGDATA=/var/lib/postgresql/18/docker` layout and `/var/lib/postgresql` volume target used here.

## Cleanup

Stop and remove only task-owned services. Delete a volume only after verifying exact name and Compose labels. Report whether cleanup ran and whether data is recoverable.
