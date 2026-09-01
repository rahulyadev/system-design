# PostgreSQL lab — SD-BEG-050-T01

## Question this lab answers

How does PostgreSQL enforce a local parent/child relationship, and what observable error appears for an orphan?

## Tool-selection justification

- Selected profile: `postgres-root`
- A real runtime is needed because constraint enforcement is PostgreSQL behavior.
- A Python simulation would not prove the database rejected the write.
- Version baseline: PostgreSQL 18.6 pinned by the repository; re-verify before real execution.

## Resource budget

One local container, roughly 0.5 CPU while active, 256–512 MB memory, under 100 KB task data, plus the PostgreSQL image and volume.

## Safety preflight

Run `python scripts/lab_preflight.py`. Confirm local Docker context, project `system-design-learning`, service `postgres`, loopback port, database `sd_learning`, and schema `sd_beg_050_t01`.

## Start and health check

```bash
docker compose --profile postgres up -d postgres
docker compose exec -T postgres sh -lc \
  'pg_isready -U "$POSTGRES_USER" -d "$POSTGRES_DB"'
```

## Deterministic setup

```bash
docker compose exec -T postgres sh -lc \
  'psql -v ON_ERROR_STOP=1 -U "$POSTGRES_USER" -d "$POSTGRES_DB"' < 00_schema.sql
docker compose exec -T postgres sh -lc \
  'psql -v ON_ERROR_STOP=1 -U "$POSTGRES_USER" -d "$POSTGRES_DB"' < 01_seed.sql
```

## Predict before running

Write the result rows and orphan-failure prediction in `../ATTEMPT.md`.

## Run and inspect

Run Rahul's query, then the assertion command generated with the real task. Record only genuine output in `evidence.md`.

## Vary one condition

Predict deletion behavior before attempting to delete a customer with orders. Do not change the constraint until you explain the new business semantics.

## Reset and cleanup

Verify the exact database and run `05_reset.sql`. It drops only schema `sd_beg_050_t01`. Stopping the shared Postgres service is optional; never delete its volume as part of this task.

## Troubleshooting

| Symptom | Check | Likely cause | Safe repair |
|---|---|---|---|
| Connection refused | `docker compose ps postgres` | Service is not healthy | Inspect narrow service logs and retry health check |
| Schema exists | Query current schema names | Prior task run | Run the exact task reset, then reload |
| Unexpected rows | Count each seed table | Residual or edited data | Reset and load deterministic seed |
