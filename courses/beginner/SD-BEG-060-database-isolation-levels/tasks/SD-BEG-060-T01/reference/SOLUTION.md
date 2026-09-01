# Reference solution — SD-BEG-060-T01

> **Spoiler:** Open only after writing a committed attempt. This is one verified PostgreSQL solution, not proof that every database or alternative schedule must produce the same trace.

## Clarifications and assumptions

- Runtime: the repository's loopback-only `postgres:18.6` root profile.
- Identity: Compose project `system-design-learning`, service `postgres`, database `sd_learning`, user `sd_learner`, and task schema `sd_beg_060_t01`.
- Data: exactly one synthetic row begins as `(1, 'A')`; every schedule resets that value.
- Sessions: separate PostgreSQL backends with task-specific `application_name` values.
- Reads are plain `SELECT` unless the variation explicitly says `FOR UPDATE`.
- Isolation is set in `BEGIN ISOLATION LEVEL ...` before the first table statement.
- The course's MySQL trace is preserved as course evidence; this reference predicts and tests PostgreSQL's documented behavior.

## Prediction

| Schedule | Prediction | Deciding reason |
|---|---|---|
| Read Committed | `T1` reads `A`, `T2` commits `B`, `T1` reads `B` | PostgreSQL takes a fresh committed snapshot for each statement |
| Repeatable Read | `T1` reads `A`, `T2` commits `B`, `T1` still reads `A`; a fresh transaction sees `B` | `T1` keeps the snapshot established by its first data statement |
| Read Uncommitted request | While `T2` holds uncommitted `B`, `T1` reads `A`; after `T2` rolls back, committed state remains `A` | PostgreSQL treats the requested level as Read Committed behavior |
| Serializable stale update | After `T1` reads `A` and `T2` commits `B`, `T1`'s update attempt aborts with `40001`; retry succeeds | The original serializable snapshot cannot update a row changed after it began |
| Plain/locking variation | Plain Serializable read returns committed `A`; `FOR UPDATE` waits behind the same writer and then fails with `40001` after the writer commits | Plain MVCC visibility and incompatible locking access are different mechanisms; the locking attempt cannot adopt a row newer than its Serializable snapshot |

## Approach and why it fits

The assignment asks for the smallest practical demonstration, so the reference keeps one table, one row, and two active sessions. It changes only the isolation level or locking clause, resets deterministically, and asserts values instead of relying on visual timing.

The standard-library verifier starts persistent `psql` processes for transactions that must stay open, places the concurrent commit/rollback at a known marker, and uses a third query to prove the locking wait. It checks SQLSTATE `40001`, retries the entire serializable transaction, and performs a guarded final schema reset.

## Step-by-step solution

### 1. Read Committed

Initial committed row: `A`.

```text
T1: BEGIN ISOLATION LEVEL READ COMMITTED
T1: SELECT name → A
T2: BEGIN; UPDATE name='B'; COMMIT
T1: SELECT name → B
T1: COMMIT
```

`T1` did not read dirty data: `B` was committed before the second statement began. The result is non-repeatable because two statements inside one transaction used different committed snapshots.

### 2. Repeatable Read

Reset to `A`.

```text
T1: BEGIN ISOLATION LEVEL REPEATABLE READ
T1: SELECT name → A       # establishes the snapshot
T2: BEGIN; UPDATE name='B'; COMMIT
T1: SELECT name → A       # same transaction snapshot
T1: COMMIT
T3: SELECT name → B       # fresh transaction
```

The old result is intentional snapshot visibility, not replica lag and not a dirty read. `T1`'s own writes would still be visible to `T1`.

### 3. Read Uncommitted request on PostgreSQL

Reset to `A`.

```text
T2: BEGIN ISOLATION LEVEL READ COMMITTED
T2: UPDATE name='B'       # remain uncommitted
T1: BEGIN ISOLATION LEVEL READ UNCOMMITTED
T1: SHOW transaction_isolation → read uncommitted
T1: SELECT name → A
T2: ROLLBACK
T1: SELECT name → A
T1: COMMIT
```

PostgreSQL accepts and reports the requested name but implements its visibility like Read Committed. Therefore the experiment correctly differs from MySQL InnoDB's dirty-read demonstration.

### 4. Serializable stale-snapshot update and retry

Reset to `A`.

```text
T1: BEGIN ISOLATION LEVEL SERIALIZABLE
T1: SELECT name → A
T2: BEGIN ISOLATION LEVEL SERIALIZABLE
T2: UPDATE name='B'; COMMIT
T1: UPDATE name='T1' → ERROR SQLSTATE 40001
```

The failed attempt is over. Do not keep its earlier read and retry only the `UPDATE`.

```text
T1 retry: BEGIN ISOLATION LEVEL SERIALIZABLE
T1 retry: SELECT current name → B
T1 retry: UPDATE name='T1_RETRY'
T1 retry: COMMIT
Final committed name → T1_RETRY
```

The retry starts from a fresh snapshot and may make a different decision from the aborted attempt.

### 5. Changed condition: plain read versus locking read

Reset to `A`.

```text
Writer: BEGIN; UPDATE name='B'       # uncommitted, holds write conflict
Plain reader: BEGIN SERIALIZABLE
Plain reader: SELECT name → A        # committed snapshot, no row-lock wait
Locking reader: BEGIN SERIALIZABLE
Locking reader: SELECT name FOR UPDATE → waits
Inspector: wait_event_type=Lock, blocking_pids includes writer PID
Writer: COMMIT
Locking reader: ERROR 40001, concurrent update
Plain reader: second SELECT → A; COMMIT
Fresh transaction: SELECT name → B
```

This trace corrects a common overgeneralization. PostgreSQL Serializable does not transform every plain read into a locking read. The explicit `FOR UPDATE` request must wait for the uncommitted updater; once that writer commits, PostgreSQL rejects the locking reader because its Serializable snapshot cannot lock the newer row version. The plain read selects the previously committed MVCC version and remains read-only.

### Question this visual answers

Which proof belongs to visibility, and which proof belongs to locking?

| Observation | Evidence | Meaning |
|---|---|---|
| Plain reader returns `A` while writer holds `B` | returned row value plus open writer | snapshot hides the uncommitted version without waiting |
| Locking reader is blocked | `wait_event_type='Lock'` and writer PID in `pg_blocking_pids` | an incompatible lock/transaction dependency is unresolved |
| Locking reader fails after writer commits | verbose error contains SQLSTATE `40001` | the stale Serializable snapshot cannot lock the newly committed row version |
| Plain Serializable reader still returns `A` | second value in the same transaction | its transaction snapshot remains stable |

### How to read this visual

Do not use one kind of evidence to claim the other mechanism. A returned old value proves visibility behavior for that schedule. A wait event and blocker relationship prove blocking.

### Key insight

The database can preserve a snapshot without blocking, and it can block a locking statement at any isolation level when incompatible access exists.

### Simplification or limitation

The table does not show PostgreSQL predicate-lock dependency structures or a multi-row serialization anomaly. It proves only the exact one-row schedules asserted by the verifier.

## Correctness invariant

For each observation:

1. schema and initial row are reset;
2. isolation is set before the first data statement;
3. the writer's commit/rollback position is known;
4. values come from the intended persistent backend session;
5. a wait claim requires database wait/blocker evidence;
6. an aborted serializable attempt contributes no committed application result;
7. the retry begins again from `BEGIN` and commits before its output is trusted.

The global Serializable invariant is stronger: every group of successfully committed Serializable transactions has an outcome equivalent to at least one serial order.

## Complexity, capacity, or resource reasoning

The experiment uses constant data and a constant number of statements: `O(1)` rows, two long-lived session processes, and one inspector. Complexity notation is not the production decision.

For a hot row, approximate serialized capacity is `1 / lock_hold_time`. At an 8 ms incompatible-lock hold, that is about `125 updates/s`. At `200/s`, offered utilization is `160%`, so queue growth is expected even if the rest of the database is idle.

For independent serialization-abort probability `p`, expected attempts per success are approximately `1/(1-p)`. At `p=0.15`, that is about `1.176`, or roughly 176 extra attempts per 1,000 successful transactions/s before feedback effects.

## Verification status

- Status: passed
- Evidence: [`lab/evidence.md`](../lab/evidence.md)
- Limitation: The verified run covers the exact one-row schedules only; it does not prove predicate phantoms, multi-row write skew, sustained load, replicas, or driver/pool behavior.

## Failure modes and recovery

| Failure | Symptom | Response | Remaining risk |
|---|---|---|---|
| Isolation set after first data statement | PostgreSQL rejects the change or schedule uses the prior level | Roll back, reset, and set level in `BEGIN` | Pool/session defaults can still surprise another code path |
| Unexpected open transaction | Verifier timeout or task session visible in `pg_stat_activity` | Roll back only the task-named backend; scoped reset | Killing a PID without identity proof could affect unrelated work |
| Serialization failure | SQLSTATE `40001`; transaction is aborted | Retry the whole transaction with bounded jitter | External effects may duplicate without idempotency/outbox |
| Deadlock | SQLSTATE `40P01` | Roll back victim, retry, and fix lock order | Retries alone do not remove the cycle |
| Lock wait | `wait_event_type='Lock'`, non-empty blocker list, rising latency | End verified blocker, shorten transaction, order locks | Hot-key queue may recur at load |
| Ambiguous commit response | Client loses connection around commit | Query by stable operation ID; make retry idempotent | External system may have its own ambiguous outcome |
| Broad cleanup | Other lecture schemas disappear | Prevented by database/user guard and exact schema target | Human must still inspect context before running commands |

## Alternatives

| Alternative | Prefer when | Why not selected here |
|---|---|---|
| MySQL task-local lab | Exact reproduction of the course terminal is the learning goal | The instructor allows the learner's database; the repository already provides a safe PostgreSQL profile and the divergence is high-value |
| Paper schedule only | The question tests terminology or ordering | It cannot prove PostgreSQL's RU mapping, SQLSTATE, or real wait graph |
| One atomic conditional update | A narrow business invariant fits one statement | It would skip the instructor's isolation-level observation |
| `SELECT FOR UPDATE` for every case | Known-row pessimistic coordination is the design | It would hide snapshot differences and conflate locking with isolation |
| Multi-row write-skew lab | The goal is to prove Serializable beyond row conflicts | It expands beyond the instructor's one-row recommendation; use it as later practice |

## Interview follow-ups

### SDE-2

- Why does Read Committed return `B` on the second read without permitting a dirty read?
- Why is PostgreSQL's Read Uncommitted result not a failed experiment?
- Which query proves the locking reader is blocked and who blocks it?
- Why must `40001` rerun the earlier reads?
- Replace a stock read-then-write with one conditional update and state its success condition.

### SDE-3

- A hot SKU receives 1,500 requests/s. Quantify why a single row cannot sustain the current lock hold and propose an ownership/admission design.
- Serializable retries jump after a deploy. Separate conflict skew, longer transactions, plan changes, pool pressure, and a retry feedback loop using evidence.
- A payment call occurs inside the retried function. Redesign with idempotency, state transitions, and an outbox.
- The system becomes multi-region. Define write ownership and explain why isolation on one primary does not solve replica freshness or cross-region atomicity.
- Product relaxes exact inventory to bounded oversell. Explain which invariant, user impact, reconciliation, and cost change before selecting a weaker mechanism.

## Compare with Rahul's attempt

Complete only after Rahul attempts:

- Correct predictions:
- Correct engine-specific explanation:
- Missing schedule or evidence:
- Different but valid choices:
- One thing to retry closed-book:
