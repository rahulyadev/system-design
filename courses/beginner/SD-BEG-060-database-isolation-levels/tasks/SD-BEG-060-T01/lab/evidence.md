# Runtime evidence — SD-BEG-060-T01

## Execution status

- Status: Passed
- Date/time: 2026-09-01T16:47:43+05:30
- Environment: Docker 29.7.2, Docker Compose 5.5.0, local `default` Unix-socket context, `postgres:18.6`, server `18.6 (Debian 18.6-1.pgdg13+2)`, database `sd_learning`, user `sd_learner`, loopback `127.0.0.1:55434`
- Reason if skipped/failed: Not applicable

## Prediction

This is the reference-path prediction, not Rahul's learner prediction:

- Read Committed: `A → B` after the concurrent commit.
- Repeatable Read: `A → A` inside the original transaction; a new transaction sees `B`.
- PostgreSQL Read Uncommitted request: the reader sees committed `A`, not the writer's uncommitted `B`; rollback leaves `A`.
- Serializable stale-snapshot update: the old attempt fails with SQLSTATE `40001`; a whole-transaction retry succeeds from current state.
- Variation: a plain Serializable read returns its snapshot-visible committed version, while `SELECT ... FOR UPDATE` waits behind the uncommitted writer, exposes a blocker relationship, and is predicted to fail with `40001` after that writer commits.

## Expected behavior

PostgreSQL uses a new snapshot per Read Committed statement and a stable transaction snapshot for Repeatable Read. It treats Read Uncommitted as Read Committed. Serializable adds conflict/dependency protection and can abort an unsafe attempt. A plain Serializable read is not automatically a row-locking read; an explicit locking clause can create an incompatible wait.

## Actual run

```text
python courses/beginner/SD-BEG-060-database-isolation-levels/tasks/SD-BEG-060-T01/lab/verify_reference.py
```

## Observed evidence

```text
RUNTIME_IDENTITY context=default endpoint=local-unix project=system-design-learning service=postgres image=postgres:18.6 port=127.0.0.1:55434 database=sd_learning user=sd_learner schema=sd_beg_060_t01 volume=system-design-learning-postgres-18 labels=verified
SERVER version=18.6 (Debian 18.6-1.pgdg13+2) database=sd_learning user=sd_learner default_isolation=read_committed
SCHEMA_CHECK schema=sd_beg_060_t01 rows=1 initial=A status=passed
READ_COMMITTED isolation=read_committed first=A writer=commit:B_RC second=B_RC status=passed
REPEATABLE_READ isolation=repeatable_read first=A writer=commit:B_RR second=A fresh_transaction=B_RR status=passed
READ_UNCOMMITTED_REQUEST reported=read_uncommitted writer_uncommitted=B_DIRTY reader=A writer=rollback reader_after_rollback=A mapping=read_committed status=passed
SERIALIZABLE_CONFLICT first=A concurrent_commit=B_SER stale_attempt_sqlstate=40001 stale_write_committed=false retry_read=B_SER retry_commit=T1_RETRY status=passed
LOCK_WAIT blocked_pid=560 blocker_pid=546 wait_event_type=Lock wait_event=transactionid pg_blocking_pids=546 status=observed
PLAIN_VS_LOCKING_READ plain_first=A plain_wait=false plain_elapsed_ms=0.7 locking_read_wait=true locking_read_sqlstate=40001 plain_second=A fresh_transaction=B_PENDING status=passed
CLEANUP database=sd_learning user=sd_learner schema=sd_beg_060_t01 removed=true shared_volume=retained status=passed
SD-BEG-060-T01_REFERENCE_VERIFIED
```

## Explanation

Read Committed used a new statement snapshot, so the second read included `B_RC`. Repeatable Read retained the snapshot established by the first read, so it returned `A` until a fresh transaction saw `B_RR`. PostgreSQL reported the requested Read Uncommitted name but hid the writer's uncommitted `B_DIRTY`, matching its documented Read Committed mapping. The stale Serializable writer was rejected with `40001`; a complete retry read current `B_SER` and committed `T1_RETRY`.

## Variation

- Changed condition: Serializable plain `SELECT` → `SELECT ... FOR UPDATE` behind the same uncommitted writer
- Prediction: plain read returns a committed snapshot without waiting; locking read waits, lists the writer as blocker, and then fails with `40001` after the writer commits
- Actual result: the plain read returned `A` in 0.7 ms without a lock wait. The locking reader showed `wait_event_type=Lock`, `wait_event=transactionid`, and writer PID `546` as its blocker; after that writer committed, the locking attempt failed with SQLSTATE `40001`. The plain reader's second read remained `A`, while a fresh transaction saw `B_PENDING`.
- Explanation: the plain read used its Serializable snapshot. `FOR UPDATE` requested conflicting access and waited; once the newer row committed, the old Serializable snapshot could not lock it, so PostgreSQL aborted that attempt rather than silently switching snapshots.

## Cleanup

- Status: Passed
- Target: schema `sd_beg_060_t01` only
- Recoverability: the shared volume was retained; the scoped task schema was removed and is not recoverable from this reset

## Remaining proof gap

The one-row reference path does not test predicate phantoms, multi-row write skew, sustained throughput, retry storms, replicas, failover, or application-driver pool behavior.
