# Runtime evidence — SD-BEG-070-T01

## Execution status

- Status: Passed
- Date/time: completed 2026-09-01T16:35:04+05:30
- Environment: Linux 7.0.0-30-generic x86_64; Docker Engine client/server 29.7.2; Docker Compose v5.5.0; MySQL 8.4.11; Node.js v24.19.0; npm 11.17.0; `mysql2` 3.24.2
- Image: `mysql:8.4.11`, observed digest `mysql@sha256:b3b90af2a6552ae30c266fdb7d5dd55f3afb72404bb78d37fe8a23eb857fd3fb`
- Reason if skipped/failed: Not applicable

## Prediction

This is the course/reference prediction, not Rahul’s future learner prediction:

- With both replica threads running, a primary write should become visible on the replica after catch-up.
- With only the replica SQL/applier thread paused, strong GET through the primary should return the new row while eventual GET through the replica should return `404`.
- After the applier resumes and reaches the saved source position, eventual GET should return the row.
- An application-user write on the read-only replica should be rejected.

## Expected behavior

The primary commits and acknowledges independently of asynchronous replica apply. Pausing the applier holds query-visible state at the earlier applied position even though the receiver can remain connected. The API’s strong path chooses server `701`, while the eventual path chooses server `702`. Read-only controls protect the replica from application mutations. Catch-up makes the delayed row query-visible without rewriting it through the API.

## Actual run

From the task directory, the following commands genuinely ran:

```text
python3 lab/preflight.py
npm ci --prefix reference --ignore-scripts --no-audit --no-fund
python3 lab/verify_reference.py
docker version --format 'client={{.Client.Version}} server={{.Server.Version}}'
docker compose version
docker ps -a --filter label=com.rahulyadav.learning-task=SD-BEG-070-T01
docker volume inspect sd-beg-070-t01-source-mysql-8-4 sd-beg-070-t01-replica-mysql-8-4
```

The verifier itself executed the scoped Compose start/stop, MySQL configuration/status/DDL/DML queries, source-position waits, reference API requests, and direct physical-state assertions.

## Observed evidence

```text
PREFLIGHT status=passed context=default endpoint=unix:///var/run/docker.sock existing_project_containers=0 volumes=absent
HEALTH source=healthy replica=healthy
RUNTIME_IDENTITY source port=127.0.0.1:55701 server_id=701 volume=sd-beg-070-t01-source-mysql-8-4 labels=verified
RUNTIME_IDENTITY replica port=127.0.0.1:55702 server_id=702 volume=sd-beg-070-t01-replica-mysql-8-4 labels=verified
VERSIONS source=8.4.11 replica=8.4.11 node=v24.19.0 mysql2=3.24.2
REPLICATION_CONFIGURED file=mysql-bin.000003 position=158
REPLICA_STATE io=Yes sql=Yes source=source exec_pos=158
REPLICA_GUARDS read_only=1 super_read_only=1
SCHEMA_REPLICATION table=items source=present replica=present
BASELINE_ROUTING post_server=701 eventual_get_server=702 rows=source:1,replica:1 source_position=1087 replica_exec_position=1087
REPLICA_WRITE_REJECTED returncode=1 error=MySQL server is running with the --read-only option
REPLICA_STATE io=Yes sql=No exec_pos=1087
STALE_READ applier=paused strong=200@701 eventual=404@702 rows=source:1,replica:0
REPLICA_STATE io=Yes sql=Yes
REPLICA_CAUGHT_UP source_position=1424 replica_exec_position=1424
CATCH_UP applier=resumed eventual=200@702 rows=source:1,replica:1
CLEANUP source=exited replica=exited volumes=retained-and-labeled recoverable=true
SD-BEG-070-T01_REFERENCE_VERIFIED
```

## Explanation

The server IDs and direct counts independently confirm the API’s labels. The baseline proves source DDL/DML reached query-visible replica state. In the variation, only the applier was paused: the primary accepted item `202`, server `701` returned it, server `702` did not, and direct counts were `1/0`. Resuming and waiting for the exact source file/position advanced the replica to the write and changed the same eventual read to `200`, with counts `1/1`. The rejected replica insert proves the application user could not turn the read copy into a second writer.

## Variation

- Changed condition: replica SQL/applier thread paused while the receiver remained running.
- Prediction: primary/strong read present; replica/eventual read missing until apply catches up.
- Actual result: `strong=200@701`, `eventual=404@702`, direct rows `source=1/replica=0`; after resume and position `1424`, `eventual=200@702`, direct rows `1/1`.
- Explanation: asynchronous acknowledgment preceded replica apply. Query visibility changed only when the applier replayed the retained log entry.

## Remaining proof gap

The run proves the deterministic reference path for one local MySQL 8.4.11 source and one replica. It does not prove behavior under source crash/promotion, network partition, host/disk loss, semisynchronous or fully synchronous acknowledgment, TLS/auth rotation, backup restore, multiple replicas, production load, or remote-region latency. Both containers were stopped cleanly; the exact task-labeled volumes were retained and remain recoverable.
