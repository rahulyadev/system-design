# Quick review — SD-BEG-060 Database Isolation Levels

> Answer before opening `notes.md`. Keep this review usable in 10–20 minutes.

## Closed-book recall

1. Define isolation without saying that transactions literally run alone.
2. Draw `T1: read A ... read again` and place `T2: write B, commit` between the reads. Predict both Read Committed and Repeatable Read.
3. What makes a read **dirty** rather than merely old or stale?
4. Give a one-row dirty-read schedule and explain what happens if the writer rolls back.
5. Distinguish a non-repeatable read, phantom read, and serialization anomaly.
6. Why can stable Repeatable Read snapshots still permit write skew?
7. Define Serializable by the outcome of successful commits.
8. Why is “Serializable means every read blocks every other transaction” wrong?
9. What does PostgreSQL do when `READ UNCOMMITTED` is requested?
10. How do MySQL InnoDB and PostgreSQL differ in the Serializable examples from this pack?
11. Why must SQLSTATE `40001` retry the entire transaction rather than only the final statement?
12. Name evidence that separates row-lock contention, a deadlock, a serialization failure, and pool saturation.

## Draw from memory

- Components/states: two sessions, `BEGIN`, snapshot, old row version `A`, new version `B`, `COMMIT`/`ROLLBACK`, compatible/incompatible lock, retry.
- Arrows/order: `T1 read A → T2 write B → T2 commit → T1 read ?`.
- Failure boundary: an attempt can read a valid snapshot and still be aborted at update/commit to preserve serializability.
- Key invariant: every **successfully committed** Serializable history must match at least one serial order.
- Engine boundary: identical level names specify a minimum/contract, not an identical trace.

Then compare with [Big picture](notes.md#big-picture) and [Ordering, concurrency, and stale state](notes.md#ordering-concurrency-and-stale-state).

## Instructor-task recall

Without opening the task README:

1. Restate the one-table, one-row, two-session assignment.
2. Predict the second read at PostgreSQL Read Committed and Repeatable Read.
3. Predict whether PostgreSQL exposes another session's uncommitted update when Read Uncommitted is requested.
4. Explain why the PostgreSQL result can faithfully differ from the MySQL course demo.
5. Predict the result of changing a PostgreSQL Serializable plain read to `SELECT ... FOR UPDATE` behind an uncommitted writer.
6. Name the evidence that proves a real lock wait rather than a slow query.

Attempt [`SD-BEG-060-T01`](tasks/SD-BEG-060-T01/README.md) before opening its reference solution.

## Answer cues

- **Isolation contract:** allowed observations and committed outcomes; see [Isolation](notes.md#isolation-the-concurrency-contract).
- **Dirty:** the writer has not committed; see [Read Uncommitted](notes.md#read-uncommitted).
- **Fresh versus stable:** statement snapshot versus transaction snapshot; see [Read Committed](notes.md#read-committed) and [Repeatable Read](notes.md#repeatable-read).
- **Strongest level:** serial-equivalent successful commits, with possible full retry; see [Serializable](notes.md#serializable).
- **Mechanism boundary:** snapshots, locks, and dependency tracking are tools; see [Isolation is not locking](notes.md#isolation-is-not-locking).
- **Database boundary:** PostgreSQL maps Read Uncommitted and can abort Serializable attempts; see [Engine details](notes.md#engine-and-transaction-boundary-details).

## Two-minute teach-back

1. State one business invariant and draw the smallest schedule that can violate it.
2. Explain dirty, non-repeatable, phantom, and serialization anomalies in that order.
3. Compare statement and transaction snapshots.
4. Define Serializable without equating it to global locking.
5. Explain the course's MySQL lock wait and PostgreSQL's different behavior.
6. Choose atomic SQL, explicit locking, Repeatable Read, or Serializable retry and defend the choice.
7. Close with blocker, retry, transaction-age, and tail-latency evidence.

## Interview follow-ups

1. Two Read Committed requests oversell one unit. Show the schedule and replace it with one atomic conditional update.
2. A Repeatable Read workflow checks two rows and updates a third. What anomaly can remain?
3. A Serializable endpoint has a 15% `40001` rate after a traffic shift. What do you inspect before lowering isolation?
4. A `SELECT FOR UPDATE` request is slow. Which PostgreSQL views/functions prove who blocks whom?
5. A connection times out during commit. Why is rollback not a safe assumption, and how does an operation key help?
6. Payment cannot join the database transaction. Where do idempotency and an outbox fit?

## Flashcards

| Front | Back | Type |
|---|---|---|
| Dirty read deciding condition? | The observed write belongs to another transaction that has not committed. | invariant |
| Read Committed snapshot scope in PostgreSQL? | One committed snapshot per statement. | mechanism |
| Repeatable Read snapshot scope in PostgreSQL? | One snapshot from the first non-control statement for the transaction. | mechanism |
| Does PostgreSQL implement distinct Read Uncommitted behavior? | No; it treats the request as Read Committed behavior. | engine boundary |
| Serializable guarantee? | Successful commits have an effect equivalent to some serial order. | invariant |
| PostgreSQL serialization-failure SQLSTATE? | `40001`; retry the whole transaction. | failure |
| PostgreSQL deadlock SQLSTATE? | `40P01`; the victim transaction is aborted and normally retried as a whole. | failure |
| Why can Repeatable Read allow write skew? | Stable snapshots do not alone reject every non-serializable read/write dependency. | anomaly |
| MySQL course Serializable wait cause? | T1's exclusive row lock conflicts with T2's implicit shared locking read when autocommit is off. | mechanism |
| Are MySQL shared row locks mutually blocking? | No; shared locks are compatible with shared locks. | misconception |
| Best narrow stock decrement? | Often one conditional atomic `UPDATE ... WHERE available > 0 RETURNING`. | decision |
| Lock-contention evidence? | Waiting activity, `wait_event_type='Lock'`, blocker PIDs, relevant `pg_locks`, and rising tail latency. | observability |
| Retry amplification at 15% independent abort probability? | About `1 / 0.85 = 1.176` attempts per success. | estimate |

## English speaking check

- Use `snapshot` naturally without calling it a backup.
- Explain `anomaly` with one two-session schedule.
- Say naturally: “Transactions contend for the same row lock.”
- Define `serializable` without saying “the database runs only one transaction.”
- Correct this weak phrase: “Read Committed gives consistent data throughout my transaction.”

## Weakness log

No demonstrated gaps are recorded yet. Add a row only after Rahul predicts, explains, draws, or runs the task.

| Date | Exact gap | Type | Repair | Retest |
|---|---|---|---|---|

## Next review

- Suggested date: after the first task attempt, then one day later for closed-book reconstruction.
- Highest-value thing to retest: predict the same schedule on MySQL InnoDB and PostgreSQL without confusing the isolation contract with its locking/MVCC implementation.
