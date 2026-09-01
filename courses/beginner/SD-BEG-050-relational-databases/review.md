# Quick review — SD-BEG-050 Relational Databases

> Answer before opening `notes.md`. Keep this review usable in 10–20 minutes.

## Closed-book recall

1. A request inserts a user and required profile. State the invariant and draw the smallest correct transaction boundary.
2. Explain atomicity, consistency, isolation, and durability without reusing one definition for another letter.
3. Predict the state after four interruption points: before `BEGIN`, after the first insert, after both inserts but before commit, and after commit succeeds.
4. Why can a transaction still have a race at Read Committed? Give one conditional-write or locking repair.
5. When is `ON DELETE CASCADE` correct ownership modeling, and when is it dangerous?
6. What does a foreign key prove? What performance property does it not automatically provide on the child side in PostgreSQL?
7. Why is "Serializable means one transaction runs at a time" wrong for PostgreSQL?
8. Contrast ACID consistency, transaction isolation, and replica freshness.
9. What evidence distinguishes a lock-contention problem from slow SQL or connection-pool saturation?
10. Why are a successful commit, a successful backup job, and a successful restore drill three different claims?
11. A connection breaks during commit. What are the two possible database outcomes, and how should a retry be made safe?
12. A synchronous post counter is correct but slow for one celebrity. Which invariant is protected, where is the bottleneck, and what guarantee can be relaxed?

## Draw from memory

- Components/states: request, connection, `BEGIN`, user insert, profile insert, constraints, `COMMIT`/`ROLLBACK`, WAL, recovered state.
- Arrows/order: open transaction -> writes -> validation -> commit record -> durable acknowledgement -> visibility.
- Failure boundary: crash before commit versus crash after successful commit.
- Relationship boundary: one user to one profile; one user to many posts/photos; user-to-user follows through a join table.
- Key number/invariant: the task's pair count is either `0/0` or `1/1`, never `1/0` after recovery.

Then compare with [Big picture](notes.md#big-picture) and [Deep mechanism](notes.md#deep-mechanism).

## Instructor-task recall

Without opening the task README:

1. Restate the instructor's three broad actions and identify which entity pair is the minimum transaction experiment.
2. Predict the post-recovery counts when the server is interrupted after only the first insert.
3. Explain why interrupting a client before commit and interrupting the disposable database server before commit should lead to the same committed row counts, while exercising different failure paths.
4. Name the exact safety evidence required before killing a local database container.
5. Predict the committed variation before running it.

Attempt [`SD-BEG-050-T01`](tasks/SD-BEG-050-T01/README.md) before opening its reference solution.

## Answer cues

- **Transaction and atomicity:** [Transaction boundary](notes.md#transaction-boundary) and [Atomicity](notes.md#atomicity-no-partial-transaction-effect).
- **Valid state:** name the invariant first, then select constraints and transaction logic; see [Consistency](notes.md#consistency-preserve-declared-invariants).
- **Concurrent state:** level names are not proofs; construct two overlapping transactions; see [Isolation](notes.md#isolation-concurrency-with-defined-anomalies).
- **Crash state:** open work has no committed outcome; acknowledged commit relies on WAL/configuration; see [Durability](notes.md#durability-committed-work-outlives-covered-failures).
- **Hot counter:** calculate writes to the same key, not only total writes; see [Worked example](notes.md#worked-example-and-calculations).
- **Ambiguous result:** query by operation/idempotency key rather than assuming rollback.

## Two-minute teach-back

1. State the user/profile invariant and why two independent commits can violate it.
2. Describe the transaction mechanism from `BEGIN` through commit or rollback.
3. Assign one distinct responsibility to each ACID letter.
4. Predict the open-transaction crash and committed-transaction crash.
5. Explain one constraint, one isolation anomaly, and one durability limit.
6. Name the measurements that would prove a lock, WAL, or pool bottleneck.
7. Finish with one alternative: outbox for cross-system work or asynchronous counter for a hot display value.

## Interview follow-ups

1. Two requests spend from the same balance at Read Committed. Give a schedule that breaks a read-then-write implementation, then repair it.
2. An API writes user, profile, and an email call. Where is the true atomic boundary, and what does an outbox change?
3. A foreign-key rollout fails on old rows. Give a compatibility-safe cleanup and deployment sequence.
4. Serializable retries jump from 0.1% to 15%. Which evidence do you inspect before changing isolation?
5. Product now permits a post count to lag by 30 seconds. How does that change the write transaction and failure model?
6. The durability requirement changes from one-node crash to region loss with RPO=0. Which latency and availability costs appear?

## Flashcards

| Front | Back | Type |
|---|---|---|
| What is the atomicity invariant in the task? | User and required profile commit together: after recovery the new pair is `0/0` or `1/1`. | invariant |
| Does atomicity prevent concurrent execution? | No. It governs transaction outcome; isolation governs concurrency. | misconception |
| What does ACID consistency depend on? | The invariants declared in constraints and correctly implemented by transaction/application logic. | mechanism |
| PostgreSQL 18 default isolation? | Read Committed; each statement reads a fresh committed snapshot. | decision |
| MySQL InnoDB default isolation? | Repeatable Read; do not generalize it to every relational engine. | comparison |
| Does PostgreSQL Serializable run only one transaction globally? | No. It permits concurrency and aborts an outcome that cannot match a serial order. | mechanism |
| Safe use of cascade? | Child is owned by the parent and cannot meaningfully survive it. | decision |
| What survives an open-transaction crash? | None of that transaction's changes become committed. | failure |
| What survives a normal successful commit then process crash? | Committed data, under the tested durability configuration and retained storage. | failure |
| Why can a lost commit response be dangerous? | The server may have committed; a blind retry can duplicate the operation. | failure |
| One hot-row symptom? | Lock waits and tail commit latency rise for transactions touching the same key. | observability |
| WAL is not what? | It is not by itself an independent backup or protection from storage destruction. | boundary |

## English speaking check

- Use `invariant` naturally while describing the profile relationship.
- Explain `atomic` without using the words "all" or "nothing."
- Use `durable` while naming the exact failure boundary, not as a synonym for "reliable."
- Correct this weak interview phrase: "The database is ACID, so there cannot be a race condition."
- Replace "There is a contention" with a natural sentence that names the competing transactions and shared row.

## Weakness log

No demonstrated gaps are recorded yet. Add a row only after Rahul attempts recall, explains a mechanism, or runs the task.

| Date | Exact gap | Type | Repair | Retest |
|---|---|---|---|---|

## Next review

- Suggested date: after the first attempt of `SD-BEG-050-T01`, then one day later for closed-book recall.
- Highest-value thing to retest: explain why the two crash outcomes differ without merging atomicity and durability into one definition.
