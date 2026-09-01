# SD-BEG-060 — Database Isolation Levels

> **Track:** Beginner
>
> **Artifact state:** Ready
>
> **Learning state:** Not started
>
> **Last updated:** 2026-09-01

## Source and coverage check

- Inspected: the complete timestamped transcript, both slide pages rendered and visually checked, the 18:21 video sampled across its full duration, the terminal states for every demonstration, and the complete ending.
- Coverage: complete. The transcript covers `00:00:00.640-00:18:13.160`; the remaining video is closing material without an additional technical section or assignment.
- Resolved source points: the course demo uses MySQL, two sessions, autocommit disabled, one `users` row, and plain `SELECT` statements. Exact behavior therefore belongs to that engine and setup. The final slide and narration explicitly warn that engines can differ.
- Unclear source points: none remain unresolved.
- Instructor-task scan: complete. One experiment was found at `00:17:02-00:17:24`; see [`SD-BEG-060-T01`](tasks/SD-BEG-060-T01/README.md).

## What I should be able to do

- Explain isolation as a contract about the outcomes and observations allowed when transactions overlap.
- Predict dirty reads, non-repeatable reads, phantoms, lock waits, and serialization failures from a two-session schedule.
- Compare Read Uncommitted, Read Committed, Repeatable Read, and Serializable without assuming that identical names imply identical engine behavior.
- Distinguish an isolation guarantee from a mechanism such as MVCC, row locks, or dependency tracking.
- Choose an isolation strategy for a backend invariant, build a safe retry boundary, and diagnose contention from database evidence.

## Small bridge from earlier ideas

A **transaction** begins, executes one or more statements on one connection, and ends with `COMMIT` or `ROLLBACK`. A commit makes the transaction's outcome eligible to become visible to other transactions. A rollback discards its uncommitted database effects.

Two requests can use two database connections at the same time. Their statements may interleave like this:

```text
T1: BEGIN → read A ─────────────→ read again → COMMIT
T2:          BEGIN → write B → COMMIT
```

The isolation level decides which outcomes are legal for that overlap. A database may enforce the contract with **multiversion concurrency control (MVCC)**, locks, conflict checks, aborts, or a mixture. This compact bridge is enough to study the lecture independently.

## The 60-second story

Isolation is the `I` in ACID. It does not mean that transactions literally run alone. It means the database defines how concurrent transactions may observe and affect one another.

The course builds the idea with one row and two MySQL sessions. Under Repeatable Read, a transaction keeps seeing the snapshot established by its first consistent read. Under Read Committed, its next statement may see a value committed after its previous statement. Under Read Uncommitted, MySQL may expose another transaction's uncommitted value—a dirty read. Under the demonstrated MySQL Serializable setup, a plain read becomes a locking read and waits behind a conflicting uncommitted update.

The portable lesson is the anomaly contract, not one universal implementation. PostgreSQL 18 maps Read Uncommitted to Read Committed, gives Repeatable Read a transaction snapshot, and implements Serializable by detecting executions that cannot match any serial order; it may abort work with SQLSTATE `40001` instead of making every plain read wait.

## Why the terms matter

| Term | Simple meaning | Why it matters here | Common confusion |
|---|---|---|---|
| Concurrent transactions | Transactions whose lifetimes overlap | Their statement order creates the behavior being studied | Concurrent does not require simultaneous CPU execution |
| Visibility | Which row version a statement is allowed to observe | It explains dirty and non-repeatable reads | Visibility is not the same as lock ownership |
| Snapshot | A rule selecting a consistent set of visible row versions | Statement versus transaction snapshots separate Read Committed from Repeatable Read | A snapshot is not necessarily a physical copy of the database |
| Dirty read | Reading a value another transaction has not committed | The value may later disappear on rollback | A stale committed value is not a dirty value |
| Non-repeatable read | Re-reading one row and seeing a later committed version | It can make a multi-statement decision internally inconsistent | It is different from a phantom, which changes a matching row set |
| Phantom read | Re-running a predicate and seeing a changed set of matching rows | Range checks such as “no active booking exists” can be affected | Updating an already-read row is a non-repeatable read, not a phantom |
| Serialization anomaly | A committed result that matches no one-at-a-time ordering | Serializable must prevent such committed outcomes | It is broader than dirty/non-repeatable/phantom reads |
| Lock wait | A statement pauses until an incompatible lock is released | It is one possible correctness mechanism and latency source | A wait does not prove Serializable, and Serializable need not always wait |
| Serialization failure | The database aborts a transaction to preserve a serial outcome | The application must retry the whole transaction | Retrying only the failed statement can reuse invalid earlier reads |

## Big picture

### Question this visual answers

Where does an isolation-level decision change what transaction `T1` can observe after `T2` commits?

```mermaid
sequenceDiagram
    participant T1 as Transaction T1
    participant DB as Database versions/locks
    participant T2 as Transaction T2

    T1->>DB: BEGIN and read user 1 = A
    DB-->>T1: Snapshot-visible value A
    T2->>DB: BEGIN, update user 1 = B
    Note over T2,DB: B is uncommitted
    T2->>DB: COMMIT B
    Note over DB: A and B versions exist; visibility rules choose one
    T1->>DB: Read user 1 again
    alt Read Committed
        DB-->>T1: B from a fresh statement snapshot
    else Repeatable Read
        DB-->>T1: A from T1's established transaction snapshot
    else Serializable
        DB-->>T1: Engine-specific wait, snapshot result, or later abort
    end
```

### How to read this visual

Read from top to bottom. Both levels initially return committed value `A`. `T2` creates `B`, but it becomes committed only at its commit boundary. The final branch shows that `T1`'s second read is chosen by the isolation contract and database implementation.

### Key insight

The meaningful question is not “Did another transaction write?” It is “Was that write committed, which snapshot applies to this statement, and can the complete outcome be placed in a valid serial order?”

### Simplification or limitation

The visual shows one row and omits write-write conflicts, predicate/range reads, deadlock detection, replicas, sequence objects, and engine-specific lock types. Serializable correctness often becomes visible only after considering the entire transaction and its commit outcome.

## Core concepts

### Isolation: the concurrency contract

**Course:** Isolation describes how much one running transaction can observe about another. Isolation levels let the developer tune that boundary.

**Simple meaning:** Choose which concurrent effects may become visible and which outcomes the database must prevent.

**Formal meaning:** The SQL isolation levels prohibit defined phenomena at increasing strengths. Serializable additionally requires every set of successfully committed transactions to have an effect equivalent to some serial, one-at-a-time order.

**Why it exists:** Without a concurrency contract, a correct single-request algorithm can fail when two requests read and write overlapping state.

**How it works:**

1. Each transaction declares or inherits an isolation level.
2. The engine chooses visible row versions for each statement.
3. Locking statements acquire compatible or incompatible locks as needed.
4. The engine tracks conflicts that matter to its isolation implementation.
5. A statement may return a version, wait, fail, or cause the transaction to be aborted.
6. Only successfully committed transactions count when evaluating a Serializable history.

**Invariant or deciding condition:** Every observation and committed outcome must be allowed by the selected level as implemented by that database version and storage engine.

**Small example:** Two checkout requests read stock `1`. If both independently write stock `0` and both report success, the system sold two units from one. Preventing dirty reads alone does not protect that invariant; use an atomic conditional update, an explicit lock, or a serializable transaction with full retry.

**Trade-off:** Stronger isolation can simplify correctness reasoning, but conflict detection, retained versions, waits, and retries consume resources. Lower isolation may reduce some overhead but moves invariant protection into statement design and application logic.

**Failure/observability:** Watch SQLSTATEs, rollback and retry rates, lock waits, transaction age, and tail latency. A level name in configuration is not evidence that the application handles its abort path correctly.

**When not to use it:** Do not choose the strongest name reflexively. A single atomic `UPDATE ... WHERE ... RETURNING` may protect a narrow invariant more simply than a wide serializable transaction.

### The anomaly vocabulary

| Phenomenon | Minimal schedule | What goes wrong | Prevented by SQL minimum |
|---|---|---|---|
| Dirty read | `T2` writes `B` but does not commit; `T1` reads `B`; `T2` rolls back | `T1` acted on a value that never became committed | Read Committed and above |
| Non-repeatable read | `T1` reads row=`A`; `T2` commits row=`B`; `T1` re-reads row=`B` | One transaction gets two committed versions of the same row | Repeatable Read and above |
| Phantom read | `T1` counts matching rows; `T2` inserts and commits another match; `T1` recounts | A repeated predicate returns a different set | Serializable; some engines prevent it at Repeatable Read too |
| Serialization anomaly | Two transactions read related state and commit writes that no serial order could produce | Every local read may look valid, but the combined committed result breaks the rule | Serializable |

**Invariant or deciding condition:** Name the exact forbidden outcome. “I need consistency” is too vague to choose a level.

**Small example:** Two doctors are on call. Each transaction sees the other doctor on call and takes its own doctor off call. Snapshot isolation can let both commit, leaving zero doctors. There was no dirty read and each row may have been repeatable; the combined result is still not serializable.

**Failure/observability:** Anomalies are often silent business-state failures. Add invariant queries, operation IDs, and concurrency tests. Database waits and aborts are visible; an allowed wrong application outcome may not emit an error.

**When not to use it:** Do not label every stale read a dirty read. Replica lag, cached data, and an old but committed snapshot have different mechanisms and repairs.

### Read Uncommitted

**Course:** In the MySQL demonstration, `T2` changes `A` to `A_T2` without committing. `T1` reads `A_T2`. If `T2` rolls back, `T1` has processed a value that never committed; this is a dirty read.

**Simple meaning:** The SQL level may allow a transaction to see another transaction's unfinished write.

**Why it exists:** Some engines expose a very weak visibility option where exact transactional consistency is intentionally relaxed.

**How it works in the demonstrated MySQL case:**

1. Both sessions disable autocommit and begin transactions.
2. `T1` reads committed value `A`.
3. `T2` updates the row to `A_T2` but remains open.
4. `T1` reads again and may see `A_T2`.
5. `T2` rolls back; committed state is still `A`.

**Invariant or deciding condition:** If a consumer must never act on a value that can disappear on another transaction's rollback, dirty reads are unacceptable.

**Trade-off:** The course notes a possible throughput benefit, but that is not a universal or sufficient reason to choose this level. Measure the actual engine and workload; correctness loss can dominate a small overhead reduction.

**Failure/observability:** Dirty reads usually do not produce a database error. Reconcile business outcomes against committed records and capture the exact transaction schedule in tests.

**When not to use it:** Avoid it for balances, inventory, permissions, billing, workflows, or any decision that triggers an external side effect.

**Verified PostgreSQL boundary:** PostgreSQL accepts the name but treats Read Uncommitted as Read Committed, so the dirty-read trace does not occur there. This is an implementation guarantee, not proof that the SQL level universally forbids dirty reads.

### Read Committed

**Course:** A transaction reads `A`; another transaction updates and commits `A_T2`; the first transaction's second read returns `A_T2`. The two reads happen inside one still-open transaction.

**Simple meaning:** Each statement reads committed data, but successive statements may use different snapshots.

**Formal meaning in PostgreSQL 18:** A plain `SELECT` sees rows committed before that query began, plus the transaction's own earlier writes. A later statement obtains a new snapshot.

**Why it exists:** Many request transactions need committed data but do not require every statement to share one historical view. PostgreSQL uses it as the default.

**How it works:**

1. `T1`'s first `SELECT` starts with committed value `A` and returns `A`.
2. `T2` updates to `B` and commits.
3. `T1`'s second `SELECT` begins after that commit.
4. The new statement snapshot includes `B`, so `T1` returns `B`.

**Invariant or deciding condition:** Statements may be individually committed-consistent while the transaction as a whole does not use one stable snapshot.

**Small example:** A report reads an order total, then separately reads line items. A concurrent commit between statements can make those two answers describe different database moments.

**Trade-off:** It avoids long-lived transaction snapshots for ordinary reads and works well for many short operations. Multi-statement read-then-write logic may need an atomic statement, explicit lock, version check, or stronger isolation.

**Failure/observability:** Look for decisions built from separate reads, rows affected unexpectedly equal to zero, or invariant drift without database errors. Test with controlled commits between statements.

**When not to use it:** Avoid an unprotected read-compute-write sequence when correctness depends on the value remaining unchanged until the write.

### Repeatable Read

**Course:** `T1` reads `A`. `T2` updates the row and commits `A_T2`. While `T1` remains open, its second plain read still returns `A`. After `T1` commits and begins a new transaction, it sees `A_T2`.

**Simple meaning:** Repeated reads in one transaction use a stable view for the covered data.

**Formal meaning:** The SQL minimum prevents dirty and non-repeatable reads but can permit phantoms. MySQL InnoDB and PostgreSQL both provide engine-specific guarantees beyond that minimum. PostgreSQL 18 Repeatable Read uses snapshot isolation and also prevents phantoms, while serialization anomalies can remain.

**Why it exists:** A multi-query calculation or report may need a coherent historical view even while other transactions commit.

**How it works:**

1. The transaction establishes a snapshot at the engine-defined point.
2. Plain reads select row versions visible in that snapshot.
3. Other transactions can commit newer versions.
4. The original transaction continues to read versions allowed by its snapshot.
5. Its own writes remain visible to itself.
6. A new transaction establishes a new view and can see later commits.

**Invariant or deciding condition:** A stable snapshot does not by itself prove that the combined outcome of multiple concurrent writers matches a serial order.

**Small example:** An export reads customers, orders, and totals in several queries. Repeatable Read can keep the export internally stable, but a business rule spanning concurrent writes may still require Serializable or explicit coordination.

**Trade-off:** Stable reads simplify reporting. Long transactions retain old row versions, can increase storage cleanup pressure, and may encounter update conflicts or stale decisions.

**Failure/observability:** Track long `xact_start`, old snapshot age, vacuum pressure, and update failures. A transaction left “idle in transaction” is operationally dangerous even if its reads are repeatable.

**When not to use it:** Do not hold a Repeatable Read transaction open across user think time or slow network calls. Read Committed may be enough for independent statements; Serializable may be required for cross-row invariants.

### Serializable

**Course:** Serializable is presented as the strictest level. In the shown MySQL setup, `T1` updates the row and holds an exclusive lock. `T2` issues a plain `SELECT`; with autocommit disabled, InnoDB treats it as a shared locking read, so it waits. After `T1` commits, `T2` returns the committed value. The source explicitly says storage engines may change behavior.

**Simple meaning:** Every set of transactions that successfully commits must have the same effect as some one-at-a-time order.

**Formal meaning:** Serializability is an outcome guarantee. The implementation may block conflicts, detect dependency cycles and abort a transaction, or combine techniques.

**Why it exists:** Some invariants span rows or predicates and are difficult to protect with one atomic statement or a small explicit lock set.

**How PostgreSQL 18 works at a high level:**

1. It gives the transaction a stable snapshot like Repeatable Read.
2. It records read/write dependencies that could form a non-serializable outcome.
3. Predicate locks (`SIReadLock`) help track what was read; these tracking locks do not themselves block writers.
4. If concurrent dependencies create a dangerous structure, PostgreSQL aborts a transaction.
5. The application discards everything derived from that aborted attempt and retries the whole transaction from a fresh snapshot.

**Invariant or deciding condition:** A result is safe only after the serializable transaction commits successfully. Data read by an attempt that later aborts must not drive an external effect.

**Small example:** `T1` and `T2` both read a rule that at least one operator remains active, then each deactivates a different operator. PostgreSQL can reject one commit with SQLSTATE `40001`, leaving a result equivalent to one serial order.

**Trade-off:** It offers the strongest reasoning boundary but adds dependency tracking and retry cost. High-conflict, long transactions can experience retry storms.

**Failure/observability:** Count SQLSTATE `40001`, attempts per successful transaction, conflict hot spots, transaction duration, and end-to-end latency. Also track ordinary lock waits and deadlocks separately; they are different failure paths.

**When not to use it:** Do not enable it without idempotent whole-transaction retries. For one hot counter, an atomic update or deliberately partitioned counter can be more direct.

### Isolation is not locking

**Simple meaning:** Isolation is the promised behavior; locking is one tool an engine may use to deliver behavior.

| Question | Isolation level answers | Locking answers |
|---|---|---|
| What may a transaction observe? | Which versions/outcomes are legal | Whether access to an object must wait now |
| What is the unit? | The transaction and sometimes statement snapshot | A row, index record/gap, page, table, transaction ID, or predicate-tracking object |
| What happens on conflict? | Must preserve the level's contract | Compatible locks proceed; incompatible locks wait, deadlock, time out, or are cancelled |
| Does stronger always mean more blocking? | No | Depends on engine and access pattern |
| Can Read Committed block? | Yes | An update or locking read can wait behind another writer |
| Can Serializable avoid a read wait? | Yes | PostgreSQL may let work proceed and later abort a non-serializable outcome |

**Course correction boundary:** The sentence “every read blocks every other transaction” is too broad outside the exact demo. In MySQL InnoDB, shared row locks are compatible with other shared locks; the demonstrated wait occurs because `T1` holds an exclusive lock and `T2` requests a shared lock on that same row. Unrelated rows and compatible readers can proceed.

**When not to use explicit locks:** Avoid `SELECT ... FOR UPDATE` when a single conditional update already enforces the rule. Locks widen the wait graph and must be acquired in a consistent order to reduce deadlocks.

### Engine and transaction-boundary details

| Detail | MySQL InnoDB course setup | PostgreSQL 18 task setup | Why the difference matters |
|---|---|---|---|
| Default level | Repeatable Read | Read Committed | Never infer the active level from “relational database” |
| Read Uncommitted | Plain reads can be dirty | Treated as Read Committed | The same requested name produces a different trace |
| Read Committed | Fresh snapshot for each consistent read | Fresh snapshot for each statement | Both allow non-repeatable reads in the demonstrated schedule |
| Repeatable Read | First consistent read establishes the read view | First non-control statement establishes the transaction snapshot | Snapshot timing and locking details can affect mixed read/write code |
| Serializable | With autocommit off, plain `SELECT` becomes `FOR SHARE` | Serializable snapshot isolation; dependency tracking may abort | Expect waits in one trace and retries in another |
| Read-read locking | Shared locks are compatible | Plain MVCC reads generally do not conflict | “Serializable means only one transaction runs” is false |

Always verify the database version, storage engine, autocommit state, session/transaction scope, query shape, and whether the read is plain or locking.

## Worked example and calculations

### One-row schedule

Assume `users(id=1, name='A')`. Each row below resets to `A` before the schedule.

| Level and engine | `T1` first action | `T2` action | `T1` next observation | Deciding mechanism |
|---|---|---|---|---|
| MySQL/PostgreSQL Read Committed | Read `A` | Write `B`, commit | Reads `B` | New committed snapshot for the later read/statement |
| MySQL/PostgreSQL Repeatable Read | Read `A` | Write `B`, commit | Reads `A`; a new transaction reads `B` | Stable transaction read view/snapshot |
| MySQL InnoDB Read Uncommitted | Read `A` | Write `B`, do not commit | May read `B`; `T2` can roll back | Dirty version is allowed |
| PostgreSQL Read Uncommitted request | Read `A` | Write `B`, do not commit | Reads `A` | PostgreSQL maps the level to Read Committed behavior |
| Course's MySQL Serializable trace | `T1` writes `B`, remains open | `T2` plain-reads same row | Waits, then reads committed result | Incompatible exclusive/shared locks |
| PostgreSQL Serializable | Read `A`; another transaction commits `B`; try to update | Concurrent commit changes the row | One attempt can fail with `40001`; retry reads the fresh state | Snapshot plus conflict/dependency detection |

### Hot-row capacity estimate

This estimate asks when lock serialization, not total database CPU, becomes the bottleneck.

#### Assumptions

- Every successful transaction updates the same row.
- The incompatible row lock is held for an average of `8 ms = 0.008 s`.
- Arrivals are simplified as independent and service time is stable.
- Ignore disk, network, pool, and retry overhead initially.

#### Steps

1. One serialized row can serve at most approximately:

   ```text
   service rate μ = 1 / 0.008 s = 125 transactions/s
   ```

2. At `80 transactions/s`, utilization is:

   ```text
   ρ = arrival rate / service rate = 80 / 125 = 0.64 = 64%
   ```

3. Under a simplified M/M/1 model, mean time in the lock-serving system is:

   ```text
   W = 1 / (μ - λ) = 1 / (125 - 80) s ≈ 0.0222 s = 22.2 ms
   ```

4. Approximate queue wait is service-inclusive time minus the `8 ms` lock service:

   ```text
   Wq ≈ 22.2 ms - 8 ms = 14.2 ms
   ```

5. At `200 transactions/s`, offered load is:

   ```text
   200 × 0.008 = 1.6 = 160%
   ```

   Demand exceeds the row's idealized `125/s` capacity, so the queue cannot remain stable without backpressure, rejection, batching, sharding, or a shorter critical section.

#### Result and sanity check

The calculation does **not** say PostgreSQL can process only 125 transactions/s. It says one incompatible hot-row lock held for 8 ms creates a local serialized capacity near 125/s. Transactions on independent rows can proceed concurrently. Real arrivals are bursty, so p95/p99 wait can grow earlier than the mean suggests.

### Retry amplification

If the probability that a serializable attempt aborts is `p`, a simplified independent-retry model needs `1 / (1-p)` attempts per success.

| Abort probability | Attempts per success | Extra attempts for 1,000 successful tx/s |
|---:|---:|---:|
| 2% | `1 / 0.98 ≈ 1.020` | about `20/s` |
| 15% | `1 / 0.85 ≈ 1.176` | about `176/s` |

This is a lower-bound-style planning model: retries add load and can raise `p`, so production code needs bounded exponential backoff with jitter, an attempt limit, and an observable failure response.

## Deep mechanism

### Components, ownership, and boundaries

| Component | Owns | Does not prove |
|---|---|---|
| Application transaction wrapper | Begin/commit/rollback and whole-attempt retry | That the chosen SQL protects the business invariant |
| Snapshot/visibility rules | Which committed and own row versions a statement may see | That two writers cannot create a serialization anomaly |
| Row/table locks | Immediate access compatibility and waiting | The entire isolation contract |
| Serializable dependency tracker | Whether the committed history can match a serial order | That an individual attempt will always commit |
| Connection pool | Session reuse and capacity | That session settings were safely reset between borrowers |
| Database metrics/views | Current activity, waits, locks, and errors | Root cause without correlating application attempts |

The application owns retry safety. The database may abort a transaction correctly, but duplicated emails, payments, or queue publications are application failures if they occur outside the retried database boundary.

### Ordering, concurrency, and stale state

#### Question this visual answers

How can two transactions each read a stable snapshot yet produce an invalid combined outcome?

```mermaid
sequenceDiagram
    participant A as T1: deactivate operator A
    participant DB as Snapshot state: A=on, B=on
    participant B as T2: deactivate operator B

    A->>DB: Read B=on
    DB-->>A: on
    B->>DB: Read A=on
    DB-->>B: on
    A->>DB: Write A=off
    B->>DB: Write B=off
    alt Snapshot isolation / Repeatable Read
        DB-->>A: COMMIT accepted
        DB-->>B: COMMIT may be accepted
        Note over DB: A=off, B=off; no serial order explains both decisions
    else Serializable
        DB-->>A: One commit accepted
        DB-->>B: One attempt aborted and retried
    end
```

#### How to read this visual

Each transaction reads the other row and updates a different row, so there is no direct write-write collision. Both local snapshots say the invariant is safe. The branches differ at commit validation.

#### Key insight

Repeatable rows are not the same as a serializable multi-row decision. Correctness depends on the whole dependency graph, not only whether one row changed between two reads.

#### Simplification or limitation

The exact transaction chosen for abort is engine-dependent. PostgreSQL's dangerous-structure detection is more nuanced than this two-edge sketch, and explicit constraints or advisory locks may offer other designs.

### Failure and recovery

| Failure | Observable symptom | Mechanism | Protection/recovery | Remaining risk |
|---|---|---|---|---|
| Non-repeatable decision at Read Committed | Two reads in one transaction disagree; no SQL error | Statement snapshots differ | Use one atomic statement, version predicate, lock, Repeatable Read, or Serializable | Stronger snapshot may still allow serialization anomalies |
| Dirty-read-dependent side effect | External action references a value later rolled back | Uncommitted visibility | Do not use weak visibility for correctness; publish effects after commit | External publish can still have an ambiguous result |
| Row lock contention | Rising `wait_event_type='Lock'`, blocked PIDs, tail latency | Incompatible locks on same object/transaction ID | Shorten transaction, stable lock order, atomic SQL, partition hot key | Skew can move the hot spot |
| Deadlock | SQLSTATE `40P01`; database aborts one participant | Cycle of incompatible waits | Retry whole transaction; acquire locks in consistent order | Retry storms if design remains cyclic |
| Serialization failure | SQLSTATE `40001`; attempt aborts | Non-serializable dependency or concurrent update | Roll back and retry the entire attempt with backoff/jitter | External effects and generated IDs must be retry-safe |
| Long snapshot | Old `xact_start`, vacuum lag, storage growth | Old row versions must remain available | Bound transaction duration; cancel leaked transactions | Large valid reports may still need long snapshots |
| Lost commit response | Client times out without knowing commit outcome | Network fails around commit acknowledgement | Use idempotency/operation key and query outcome | A blind retry may duplicate external effects |
| Pool session leakage | Next request inherits unexpected isolation/read-only state | Session-level setting survives connection reuse | Prefer transaction-scoped settings; reset and test pool state | Driver/pool-specific reset bugs |

### Observability

For PostgreSQL, correlate application attempt IDs with:

- `pg_stat_activity`: `application_name`, `state`, `xact_start`, `query_start`, `wait_event_type`, and `wait_event`;
- `pg_blocking_pids(pid)`: immediate blocker relationships;
- `pg_locks`: granted and waiting locks; `SIReadLock` entries reveal Serializable predicate tracking;
- SQLSTATE `40001`: serialization failure, retried as a whole transaction;
- SQLSTATE `40P01`: deadlock victim, also requiring a whole-transaction retry;
- transaction attempts per successful commit, retry delay, p95/p99 transaction time, and retry exhaustion;
- oldest active snapshot/transaction and table dead-tuple/vacuum signals;
- connection-pool acquisition time, because lock queues can become pool queues.

An alert such as “serialization failures > 1%” needs context. A batch job with safe retries may tolerate it; a latency-critical API whose failure rate jumped from 0.1% to 15% needs conflict-key, transaction-duration, deploy, and traffic-skew investigation.

## Design choices

| Choice | Benefits | Costs/risks | Prefer when | Avoid when |
|---|---|---|---|---|
| Read Committed + atomic conditional SQL | Short, explicit, high concurrency | Only protects the condition encoded in that statement | One row or predicate can express the invariant | Decision spans many reads/writes that cannot be combined |
| Read Committed + `SELECT FOR UPDATE` | Easy pessimistic reasoning for known rows | Blocking, deadlocks, lock-order discipline | Conflicts are common and lock set is small/stable | Range is large, user/network wait occurs inside transaction |
| Repeatable Read | Stable multi-query view | Old snapshots, update conflicts, possible serialization anomalies | Reports/exports and coherent read workflows | Cross-row business invariant must survive concurrent writers |
| Serializable + retry | Strongest committed-outcome reasoning | `40001`, retry amplification, operational complexity | Invariant is important and conflict rate is manageable | External effects cannot be made idempotent or transactions are very long |
| Optimistic version column | No waiting during read; detects stale update | Application retry/merge logic | Conflicts are uncommon and user-visible merge is meaningful | Silent last-writer-wins is unacceptable and retries are expensive |
| Advisory/application lock | Coordinates a logical key not naturally locked | Manual key scheme, lifecycle, and misuse risk | One well-defined logical resource must serialize | Broad ranges or distributed ownership make the lock key incomplete |

Isolation does not replace uniqueness, foreign keys, checks, idempotency keys, or careful statement design. Use the smallest combination that proves the invariant.

## Misconceptions

| Claim/confusion | What is actually true | Evidence or counterexample |
|---|---|---|
| “Serializable runs one transaction at a time.” | It requires serial-equivalent committed outcomes, while engines can execute transactions concurrently. | PostgreSQL allows concurrency and aborts a dangerous history with `40001`. |
| “Repeatable Read means no concurrency bug.” | It prevents non-repeatable reads but may allow a serialization anomaly. | Two transactions can write-skew different rows from stable snapshots. |
| “Read Committed means the whole transaction sees one committed snapshot.” | In PostgreSQL and the course's MySQL example, later statements can see later commits. | `A → T2 commits B → B` inside one transaction. |
| “Read Uncommitted always gives dirty reads.” | The SQL level may permit them; an engine can provide a stronger implementation. | PostgreSQL treats it as Read Committed. |
| “Every Serializable read blocks writers/readers.” | That was an engine/query-specific course trace. | PostgreSQL Serializable plain reads use snapshots; MySQL shared locks are compatible with shared locks. |
| “No lock wait means no isolation work.” | MVCC visibility and Serializable dependency tracking may proceed without a blocking lock. | PostgreSQL exposes nonblocking `SIReadLock` predicate tracking. |
| “A serialization failure means the database is broken.” | It is a correct protective outcome. | The application should retry the entire transaction from a fresh snapshot. |
| “Retry the failed statement.” | Earlier reads belong to the aborted snapshot and may no longer justify the write. | Roll back and rerun the entire transaction function. |
| “A stronger level is automatically faster or slower.” | Performance depends on conflicts, query shape, locks, versions, and retry rate. | A Serializable design can outperform broad explicit locks for some workloads. |
| “Replica consistency is the same as isolation.” | Isolation governs concurrent transactions at the database execution boundary; replica lag is a replication/freshness issue. | A serializable primary transaction does not make an asynchronous replica instantly current. |

## Real backend connection

Consider a FastAPI endpoint that reserves one unit of inventory.

Weak read-then-write shape:

```sql
SELECT available FROM inventory WHERE sku = $1;
-- application checks available > 0
UPDATE inventory SET available = $2 WHERE sku = $1;
```

Two requests can both read `1`. A smaller and often better Read Committed design is one atomic statement:

```sql
UPDATE inventory
SET available = available - 1
WHERE sku = $1 AND available > 0
RETURNING available;
```

The invariant is `available >= 0`, and “one returned row” is the success condition. If the decision spans inventory, credit, and another predicate, use an explicit lock plan or a Serializable transaction.

Natural Python transaction structure:

```python
for attempt in range(max_attempts):
    try:
        async with pool.connection() as conn:
            async with conn.transaction(isolation_level="serializable"):
                result = await apply_database_decision(conn, command)
        return result
    except SerializationFailure:
        if attempt + 1 == max_attempts:
            raise
        await backoff_with_jitter(attempt)
```

Important boundaries:

1. `apply_database_decision` must be safe to execute again.
2. The retry wraps `BEGIN` through `COMMIT`, not only the final statement.
3. Do not send an email, charge a card, or publish a queue message inside the retried function unless an idempotent/outbox design makes replay safe.
4. Record a stable operation ID across attempts and a distinct attempt number for observability.
5. Treat retry exhaustion as an explicit API failure path, not an infinite loop.

This is an example connection to a Python/PostgreSQL backend, not a claim about Rahul's production experience.

## Instructor-assigned tasks

| Task | Faithful purpose | Tools | Reference verified? | Learner status |
|---|---|---|---|---|
| [`SD-BEG-060-T01`](tasks/SD-BEG-060-T01/README.md) | Reproduce isolation behavior with one table, one row, and concurrent sessions; explain the chosen engine's trace | Docker, PostgreSQL 18.6, `psql`, Python standard library | Passed | Not started |

### Codex-added practice

1. **Predict:** At PostgreSQL Read Committed, what do two reads return if another transaction commits `B` between them?
2. **Draw:** Draw the snapshot boundary for the same schedule at Repeatable Read.
3. **Explain:** Why does PostgreSQL not expose the dirty value when `READ UNCOMMITTED` is requested?
4. **Change:** Replace a Serializable plain `SELECT` with `SELECT ... FOR UPDATE`; predict the wait and name the evidence in `pg_stat_activity`.
5. **Defend:** For inventory decrement, compare atomic conditional SQL, pessimistic locking, and Serializable retry.

## Useful English and technical phrases

### Snapshot

- Pronunciation: **SNAP-shot**
- Simple meaning: a rule-defined view of data at a point in database history
- Hindi cue: ek samay ka consistent nazariya
- Why it matters here: statement and transaction snapshots explain which committed row version is visible
- Common misuse: calling it a full physical backup or copy

Examples:

1. Simple: “This snapshot still shows the old value.”
2. Engineering: “Read Committed takes a fresh snapshot for the next statement.”
3. Engineering: “The long transaction keeps an old snapshot alive and delays cleanup.”
4. Interview: “I would first clarify whether the workflow needs a statement snapshot or one stable transaction snapshot.”
5. Professional/design review: “The export is internally consistent because every query uses the same transaction snapshot.”

### Anomaly

- Pronunciation: **uh-NOM-uh-lee**
- Simple meaning: an allowed or observed concurrency result that violates an expected pattern
- Hindi cue: asamanya natija
- Why it matters here: levels are best chosen by the anomaly that must be prevented
- Common misuse: using it for every error, timeout, or stale replica read

Examples:

1. Simple: “Seeing a value that later rolls back is a dirty-read anomaly.”
2. Engineering: “The test creates a controlled non-repeatable-read anomaly.”
3. Engineering: “Stable snapshots still permit this write-skew anomaly.”
4. Interview: “I would name the exact anomaly before choosing Serializable.”
5. Professional/design review: “The incident evidence shows invariant drift, but we have not yet reconstructed the transaction anomaly.”

### Contention

- Pronunciation: **kuhn-TEN-shuhn**
- Simple meaning: multiple operations compete for the same limited resource
- Hindi cue: ek resource ke liye takraav
- Why it matters here: a hot row turns correctness locks into queueing latency
- Common misuse: “There is a contention”; say “transactions contend for the same row lock” or “there is lock contention”

Examples:

1. Simple: “Many buyers contend for the last item.”
2. Engineering: “Transactions contend for the inventory row's exclusive lock.”
3. Engineering: “Partitioning by account reduced contention but did not remove skew.”
4. Interview: “I would inspect blocker PIDs and p99 latency before blaming CPU.”
5. Professional/design review: “The proposed global counter creates a contention point at roughly 125 writes per second under our lock-hold assumption.”

### Serializable

- Pronunciation: **SEER-ee-uh-lie-zuh-buhl**
- Simple meaning: committed concurrent work has an outcome equivalent to some one-by-one order
- Hindi cue: ek valid serial order jaisa natija
- Why it matters here: it is the strongest outcome contract discussed in the lecture
- Common misuse: saying it literally executes every transaction one after another

Examples:

1. Simple: “Both transactions ran together, but their committed result is serializable.”
2. Engineering: “The database aborted one serializable attempt with SQLSTATE 40001.”
3. Engineering: “Our retry wrapper reruns the whole serializable transaction.”
4. Interview: “I would choose Serializable only with an explicit retry and idempotency plan.”
5. Professional/design review: “Serializable protects the cross-row rule, while the outbox keeps external publication outside the retry hazard.”

## Interview practice

### Foundation

**Question:** Explain the four isolation levels with one row and two sessions.

**Strong answer covers:** define concurrent visibility first; show `A → B` schedules; distinguish uncommitted from later committed data; explain stable snapshot versus fresh statement snapshot; define Serializable by serial-equivalent committed outcomes; state that engines can be stronger or use different mechanisms.

**Weak-answer trap:** reciting the four names from weakest to strongest without a schedule, anomaly, or engine boundary.

### SDE-2 working engineer

**Question:** A PostgreSQL Read Committed endpoint reads stock, calls another query, then writes a calculated value. Load tests occasionally oversell. Diagnose and repair it.

**Reasoning checkpoints:**

1. Reconstruct two overlapping transactions and prove the allowed bad outcome.
2. Ask whether one conditional `UPDATE ... WHERE available > 0 RETURNING` protects the invariant.
3. If not, compare `FOR UPDATE`, a version predicate, and Serializable with whole-transaction retry.
4. Add concurrent deterministic tests, SQLSTATE handling, blocker/retry metrics, and an idempotency key.
5. Keep third-party calls outside the transaction.

**Follow-up:** The SKU becomes a flash-sale hot key at 200 requests/s and the row lock is held for 8 ms. Use the capacity estimate to explain the new bottleneck and one mitigation.

### SDE-3 senior design

**Prompt:** Design a reservation workflow that must not oversell, has 5,000 requests/s overall, one SKU can receive 30% of traffic, p99 must stay below 200 ms, and payment is an external system.

**Clarify first:** reservation expiry, inventory ownership, acceptable rejection, payment/idempotency semantics, retry budget, multi-region write ownership, failover RPO/RTO, and whether per-SKU ordering is acceptable.

**Answer outline:**

1. Put the authoritative available/reserved invariant in one owner partition.
2. Prefer an atomic conditional reservation write for the narrow stock rule.
3. Keep payment outside the database transaction; use an idempotent state machine and outbox/event handoff.
4. Partition by SKU, then address the 30% hot key with admission control, batching/token allocation, or a deliberately changed product guarantee.
5. Define timeout and ambiguous-result recovery with a reservation/operation ID.
6. Observe lock wait, rejected conditional updates, reservation age, outbox lag, retries, and p99 by SKU.
7. Explain why globally Serializable transactions across the database and payment provider are neither available nor necessary.

**Requirement change:** Product permits inventory to be oversold by 0.1% during a 60-second campaign and reconciled later. Re-evaluate correctness, customer impact, write path, compensations, and cost instead of merely lowering the SQL isolation level.

### Natural answer outlines

**60 seconds:**

```text
overlapping transactions
→ anomaly to prevent
→ fresh statement snapshot versus stable transaction snapshot
→ Serializable means serial-equivalent commits
→ engine-specific mechanism: MVCC, locks, or abort/retry
→ choose from invariant and measure waits/retries
```

**3–5 minutes:**

```text
define the business invariant
→ draw a two-session schedule
→ name dirty/non-repeatable/phantom/serialization anomaly
→ compare SQL minimum with the actual engine
→ choose atomic SQL, explicit locking, snapshot, or Serializable retry
→ cover deadlocks, 40001 retries, idempotency, and external effects
→ quantify contention and retry amplification
→ close with pg_stat_activity, pg_locks, SQLSTATE, and p99 evidence
```

## Course, verified extensions, and uncertainty

### Course model

- Isolation is the `I` in ACID and controls what overlapping transactions observe about one another.
- The four named levels are Read Uncommitted, Read Committed, Repeatable Read, and Serializable.
- The MySQL examples use two sessions, autocommit disabled, one table, and one row.
- Repeatable Read keeps the consistent read view within the transaction; Read Committed can see a later commit; Read Uncommitted demonstrates a dirty read.
- In the shown MySQL Serializable conflict, a read waits for an updater to commit or roll back.
- The source warns that storage engines differ and assigns the learner to inspect and reproduce behavior on the database they use.

### Verified extensions

- [PostgreSQL 18 transaction-isolation documentation](https://www.postgresql.org/docs/18/transaction-iso.html) defines the four phenomena, documents statement snapshots at Read Committed, transaction snapshots at Repeatable Read, PostgreSQL's stronger phantom protection, and Serializable retry behavior.
- [PostgreSQL 18 `SET TRANSACTION`](https://www.postgresql.org/docs/18/sql-set-transaction.html) confirms that Read Uncommitted is treated as Read Committed and that transaction isolation must be set before the first data statement.
- [PostgreSQL 18 lock monitoring](https://www.postgresql.org/docs/18/monitoring-locks.html) identifies `pg_locks` as the database view for outstanding locks and contention investigation.
- [MySQL 8.4 InnoDB isolation documentation](https://dev.mysql.com/doc/refman/8.4/en/innodb-transaction-isolation-levels.html) confirms its Repeatable Read default, per-read snapshots at Read Committed, dirty reads at Read Uncommitted, and implicit `FOR SHARE` behavior for Serializable plain reads when autocommit is disabled.
- [MySQL 8.4 InnoDB locking documentation](https://dev.mysql.com/doc/refman/8.4/en/innodb-locking.html) shows that shared locks are compatible with shared locks, while an exclusive lock blocks both shared and exclusive requests on the same record.

### Inferences and practical connections

- **Inference:** The course's portable learning method is more valuable than memorizing its exact terminal output: hold schema and schedule constant, switch one isolation property, predict, run, and explain the engine-specific evidence.
- **Inference:** A production isolation decision should begin with an invariant and a failing schedule, then select the smallest mechanism that closes that schedule.
- **Inference:** Retry rate and lock-wait rate are capacity signals as well as correctness signals; both can reveal hot-key skew before average database CPU becomes alarming.

### Unresolved source points

None.

## Final revision card

### Five facts

1. Read Committed can return two committed versions from two statements in one transaction.
2. Repeatable Read gives stable reads but does not universally guarantee serializable outcomes.
3. Dirty means **uncommitted**, not merely old.
4. Serializable defines committed outcomes; it does not require globally one-at-a-time execution.
5. PostgreSQL Read Uncommitted behaves like Read Committed, and PostgreSQL Serializable code must handle SQLSTATE `40001`.

### Three decisions

1. Use one atomic conditional statement when it fully expresses the invariant.
2. Use explicit locking when conflicts are common and the lock set is small, known, and ordered.
3. Use Serializable when a critical multi-row/predicate invariant is otherwise difficult, and only with safe whole-transaction retries.

### One failure

`40001` rises at p99 → concurrent dependencies force serialization aborts → inspect retry rate by operation/key, transaction age, and hot-key skew → shorten or redesign the transaction, add bounded jittered retries, and preserve idempotency.

### Natural 60-second explanation

Start with two overlapping transactions and the anomaly the product cannot accept. Read Uncommitted may expose unfinished data; Read Committed prevents that but can give a later statement a newer committed snapshot; Repeatable Read stabilizes the transaction's view; Serializable allows only commits equivalent to some serial order. Then name the engine: MySQL InnoDB and PostgreSQL differ, especially for Read Uncommitted and Serializable. Finish with the mechanism and operations: MVCC versions, compatible/incompatible locks, possible `40001` retries, and evidence from activity, blockers, locks, and tail latency.

See [review.md](review.md) for closed-book retrieval.
