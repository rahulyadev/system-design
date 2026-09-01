# Runtime evidence — SD-BEG-050-T01

## Execution status

- Status: Passed
- Date/time: 2026-09-01T15:10:15+05:30 to 2026-09-01T15:11:31+05:30
- Environment: Linux x86_64; Docker Engine client/server 29.7.2; Docker Compose v5.5.0; PostgreSQL 18.6 (Debian 18.6-1.pgdg13+2); `postgres:18.6` image digest `sha256:4ef4dbc939d61acea57712655ddb4b4ab27419c913f94cca0cd57cb3ea3c2280`
- Reason if skipped/failed: Not applicable

## Prediction

This is the course/reference prediction, not Rahul's future learner prediction:

- Open transaction interrupted before commit: `users=0`, `profiles=0`.
- Changed condition, successful commit before interruption: `users=1`, `profiles=1`.

## Expected behavior

The first user insert belongs to an uncommitted transaction, so crash recovery must not expose it as committed. In the variation, both rows share one successfully committed transaction; with normal PostgreSQL durability settings and the retained task-owned volume, both should be present after restart.

## Actual run

```text
python3 preflight.py
python3 verify_reference.py --confirm-task-local-crash
docker compose -f compose.yaml --project-name sd-beg-050-t01 --profile lab logs --no-color --tail 80 postgres
docker compose -f compose.yaml --project-name sd-beg-050-t01 --profile lab stop postgres
```

## Observed evidence

```text
PREFLIGHT status=passed context=default endpoint=unix:///var/run/docker.sock
RUNTIME_IDENTITY project=sd-beg-050-t01 service=postgres port=127.0.0.1:55450 database=sd_beg_050_t01 schema=sd_beg_050_t01 volume=sd-beg-050-t01-postgres-18 labels=verified
SERVER version=18.6 fsync=on synchronous_commit=on
SCHEMA_CHECK tables=5 status=passed
CONSTRAINT_CHECK foreign_key=passed cascade=passed
OPEN_TRANSACTION_CONFIRMED active=1 commit_not_sent=true
OPEN_TRANSACTION_RECOVERY users=0 profiles=0 status=passed
COMMITTED_BASELINE users=1 profiles=1
COMMITTED_RECOVERY users=1 profiles=1 status=passed
RECOVERY_LOG automatic recovery in progress; redo completed; database system ready for connections
SD-BEG-050-T01_REFERENCE_VERIFIED
CLEANUP service=postgres status=exited(0) volume=sd-beg-050-t01-postgres-18 task_label=SD-BEG-050-T01 retained=true
```

## Explanation

The first failure arrived after one insert while the transaction was provably active and before commit was sent. Recovery exposed neither row, matching atomic rollback. The variation changed only commit status: both inserts committed, the same service received `SIGKILL`, recovery replayed the retained volume, and both rows remained. The logs independently showed automatic crash recovery and readiness after redo.

## Variation

- Changed condition: commit succeeds before the same scoped PostgreSQL process failure.
- Prediction: the complete pair should recover as `1/1`.
- Actual result: `users=1`, `profiles=1` after restart.
- Explanation: PostgreSQL returned commit under `fsync=on` and `synchronous_commit=on`; the required WAL survived in the labeled task volume and recovery preserved both effects.

## Remaining proof gap

The run proves the deterministic reference path for PostgreSQL process crashes with one retained local volume. It does not prove behavior under disk/host loss, power-loss hardware semantics, replica or region failure, malicious deletion, backup restore, or a client connection lost during commit. The service was stopped cleanly after verification; the labeled volume was retained, so the final committed reference state is recoverable by restarting this exact task service.
