# Runtime lab — SD-BEG-050-T01

## Question this lab answers

After PostgreSQL is force-stopped, why does an open user/profile transaction recover as `0/0`, while the same pair committed before the stop recovers as `1/1`?

## Tool-selection justification

- Selected profile: `postgres-root` semantics with a task-local crash-isolation override.
- Why a real runtime is needed: the instructor explicitly asks the learner to interrupt execution and inspect database recovery. A paper schedule cannot prove PostgreSQL process-crash behavior or the retained on-disk state.
- Why a smaller simulation is insufficient: a Python model could assert rollback, but it would not exercise PostgreSQL transaction visibility, WAL recovery, health transition, or durability settings.
- Version and primary source checked on: PostgreSQL `18.6`, checked 2026-09-01 against the [PostgreSQL 18.6 release notes](https://www.postgresql.org/docs/release/18.6/) and Docker Official Image [version registry](https://github.com/docker-library/postgres/blob/master/versions.json). The image [documents](https://github.com/docker-library/docs/blob/master/postgres/README.md) the PostgreSQL 18 `PGDATA=/var/lib/postgresql/18/docker` and `/var/lib/postgresql` volume layout used here.

The root PostgreSQL service is appropriate for ordinary SQL, but this task intentionally crashes the server. Therefore the lab uses its own exact Compose project, database, loopback port, and volume.

## Resource budget

| Resource | Estimate |
|---|---|
| CPU | About 0.5 CPU while active; brief extra work during startup/recovery |
| Memory | Approximately 256–512 MB for one PostgreSQL container |
| Disk/images | Less than 20 MB task data; allow roughly 150–250 MB image download and several hundred MB unpacked, platform-dependent |
| Startup | Usually 5–30 seconds once the image is present; initial download is network-dependent |
| Data generation | Under one second for five small tables and synthetic rows |

## Safety preflight

From this `lab/` directory, run the read-only check before starting or killing anything:

```bash
python3 preflight.py
docker compose -f compose.yaml --project-name sd-beg-050-t01 --profile lab config
```

It must print/verify:

- a local `unix://` Docker endpoint;
- project `sd-beg-050-t01` and service `postgres`;
- image `postgres:18.6`;
- loopback port `127.0.0.1:55450` only;
- task label `SD-BEG-050-T01` on any pre-existing project container/volume;
- database and reset schema `sd_beg_050_t01`;
- volume `sd-beg-050-t01-postgres-18`;
- recovery by restarting only this project/service.

Abort if any identity differs. Do not redirect these commands to an existing service, database, or volume.

## Start and health check

```bash
docker compose -f compose.yaml --project-name sd-beg-050-t01 --profile lab up -d postgres
docker compose -f compose.yaml --project-name sd-beg-050-t01 --profile lab ps postgres
docker compose -f compose.yaml --project-name sd-beg-050-t01 --profile lab exec -T postgres \
  sh -lc 'pg_isready -U "$POSTGRES_USER" -d "$POSTGRES_DB"'
```

Expected identity is task database/user `sd_beg_050_t01`. The reference verifier checks the live container labels, binding, mount, database, schema, `fsync`, and `synchronous_commit` before drawing conclusions.

## Deterministic setup

Rahul should complete `../starter/schema.sql` and load it only after the database guard passes. The verified reference uses its physically separate `../reference/00_schema.sql`.

To run the reference path after making a learner prediction:

```bash
python3 verify_reference.py --confirm-task-local-crash
```

The flag is a deliberate acknowledgement: the script observes an open transaction, verifies every task identity, then sends `SIGKILL` only to service `postgres` in project `sd-beg-050-t01`. It restarts the same service with the retained labeled volume.

## Predict before running

Record in `../ATTEMPT.md`:

1. counts after the first insert is interrupted before commit;
2. why those counts follow from the transaction boundary;
3. counts after both inserts commit before the same interruption;
4. evidence that would falsify each prediction.

The generated `evidence.md` records the course/reference prediction, not Rahul's future personal prediction.

## Run

The reference verifier performs this order:

```text
read-only preflight
-> start and verify exact task service
-> load reference schema
-> check foreign key and owned-child cascade
-> open transaction and insert one user
-> prove that transaction is active and uncommitted
-> force-stop only the verified task service
-> restart and assert users=0, profiles=0
-> commit a matching pair
-> apply the same scoped stop
-> restart and assert users=1, profiles=1
```

For Rahul's own implementation, reproduce the same states with the learner SQL and place only genuine output in `ATTEMPT.md`.

## Inspect what happened

Use narrow queries from a separate session. Always set an explicit schema:

```bash
docker compose -f compose.yaml --project-name sd-beg-050-t01 --profile lab exec -T postgres \
  psql -X -At -U sd_beg_050_t01 -d sd_beg_050_t01 -c \
  "SET search_path TO sd_beg_050_t01,pg_catalog; SELECT (SELECT count(*) FROM app_user),(SELECT count(*) FROM profile);"
```

For an open transaction, inspect only the task marker:

```bash
docker compose -f compose.yaml --project-name sd-beg-050-t01 --profile lab exec -T postgres \
  psql -X -At -U sd_beg_050_t01 -d sd_beg_050_t01 -c \
  "SELECT application_name,state,xact_start IS NOT NULL FROM pg_stat_activity WHERE application_name='sd_beg_050_open_transaction';"
```

Do not classify a predicted count as observed until the query actually returns it after recovery.

## Vary one condition

Baseline: interrupt after the user insert while the transaction is open. Variation: insert both rows and receive successful commit before applying the same task-local process failure. Predict `0/0` versus `1/1` before running and explain that commit status—not crash presence—is the changed deciding condition.

A second learner-only variation is to terminate just the client session before commit. It should also leave no committed pair, but it tests disconnect cleanup rather than server crash recovery.

## Reset and cleanup

Reset only after verifying the database identity:

```bash
docker compose -f compose.yaml --project-name sd-beg-050-t01 --profile lab exec -T postgres \
  psql -X -U sd_beg_050_t01 -d sd_beg_050_t01 -f /dev/stdin < 05_reset.sql
```

The SQL prints its target and refuses a different database. Stop only this service:

```bash
docker compose -f compose.yaml --project-name sd-beg-050-t01 --profile lab stop postgres
```

This retains volume `sd-beg-050-t01-postgres-18`, so the last state is recoverable by starting the task again. To remove the stopped container/network while still retaining the volume, use:

```bash
docker compose -f compose.yaml --project-name sd-beg-050-t01 --profile lab down
```

Never run broad Docker cleanup for this task. Do not delete any volume unless its exact name and task label have been inspected and Rahul explicitly chooses to discard the recoverable state.

## Troubleshooting

| Symptom | Check | Likely cause | Safe repair |
|---|---|---|---|
| Docker permission error | `docker context show` and `docker version` | Current shell cannot access the local daemon | Fix local Docker access; do not select a remote daemon as a shortcut |
| Port 55450 already used | Inspect the listener and Compose project before mutation | Another process or stale task instance owns the port | Stop only the verified owner or choose no action and report the conflict |
| Preflight reports a remote endpoint | Inspect `docker context inspect` | Active context targets a remote host | Abort; switch only with Rahul's explicit knowledge |
| Existing volume lacks task label | `docker volume inspect sd-beg-050-t01-postgres-18` | Name collision or unrelated state | Abort; never relabel or delete it automatically |
| Service never becomes healthy | Task `ps`, narrow service logs, disk free space | Image startup, stale task data, or resource pressure | Preserve evidence; restart only this service after diagnosis |
| Open transaction not observed | Query the exact application name | Session failed or never reached the pause | Do not inject failure; repair the learner command and retry |
| Counts are `1/0` after recovery | Confirm both statements and commit boundary | Writes did not share one transaction or evidence points at wrong schema | Stop, preserve evidence, inspect connection/transaction usage |
| Commit variation loses rows | Inspect `fsync`, `synchronous_commit`, mount, and server logs | Wrong configuration/storage or wrong observation target | Stop and report; do not claim durability passed |

Record genuine results in [`evidence.md`](evidence.md).
