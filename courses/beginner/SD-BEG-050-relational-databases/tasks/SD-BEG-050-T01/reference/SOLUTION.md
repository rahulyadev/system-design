# Reference solution — SD-BEG-050-T01

> **Spoiler:** Open only after writing a committed attempt. This is one defensible PostgreSQL design and verified reference path, not proof that every different table boundary is wrong.

## Clarifications and assumptions

- PostgreSQL is selected from the instructor's permitted PostgreSQL/MySQL choice because the repository provides a pinned PostgreSQL baseline.
- A user row owns authentication identity; a profile row owns public profile fields.
- For the exercise, signup requires both rows to commit together. The schema's foreign key proves that a profile cannot exist without a user, while the transaction protects the reverse signup requirement during creation.
- Posts and profile photos are owned by the user in this learning model, so deleting the user cascades to them. Real retention, moderation, audit, and legal requirements could require soft deletion or archival instead.
- Following is a many-to-many self-relationship represented by a join table. A composite primary key rejects duplicate edges and a check rejects self-follow.
- The task uses synthetic data, one local PostgreSQL process, default `fsync=on`, default `synchronous_commit=on`, and one retained task-labeled volume.
- The experiment deliberately crashes the database only after verifying exact local identities. It does not test physical storage loss.

## Prediction

The open transaction performs only its first insert and never sends commit. After the verified task-local server is killed and restarted, recovery should show:

```text
app_user=0, profile=0
```

The changed condition commits both inserts before applying the same process failure. After restart it should show:

```text
app_user=1, profile=1
```

An outcome of `1/0` would disprove the intended atomic boundary or reveal that the observation targeted a different schema/database.

## Approach and why it fits

The reference uses five tables in [`00_schema.sql`](00_schema.sql):

| Table | Ownership/relationship | Main invariant |
|---|---|---|
| `app_user` | Independent identity | Primary key, canonical unique email |
| `profile` | One-to-one owned child | `user_id` is both primary key and foreign key |
| `post` | Many posts per author | Every author exists; non-empty body |
| `profile_photo` | Many photos, at most one current photo per user | Foreign key plus a partial unique index |
| `follow` | User-to-user many-to-many edge | Unique directed pair; no self-follow |

Declarative constraints handle stable local rules. The user/profile creation uses an explicit transaction because two statements form one business transition. A trigger is not selected: the business flow is clearer in application/transaction logic, and the task specifically asks the learner to observe that boundary.

The runtime is task-local rather than the shared root service because server crash and recovery are the lesson. [`verify_reference.py`](../lab/verify_reference.py) refuses to run without an explicit crash acknowledgement, runs a read-only preflight, verifies live labels/port/mount/database, and stops only the exact task service.

## Step-by-step solution

1. **Define ownership before SQL.** The profile cannot outlive its user in this model; a follow edge connects two existing users; posts/photos belong to an author/owner.
2. **Guard the target.** Both schema and reset SQL refuse a database other than `sd_beg_050_t01`.
3. **Create keys and constraints.** Use primary keys for identity, foreign keys for referential integrity, checks for row predicates, and uniqueness for canonical values/edges.
4. **Index access paths.** Add child-side indexes for author/photo/follow lookups. PostgreSQL does not automatically create every useful referencing-column index.
5. **Start an explicit transaction.** Insert synthetic user `1001`, then deliberately pause before the profile insert and commit.
6. **Prove the failure point.** A second session checks `pg_stat_activity` for the exact application name with an active transaction. If absent, abort failure injection.
7. **Verify infrastructure identity.** Check the local Docker endpoint, project/service labels, loopback port, database, schema, and retained volume.
8. **Apply the scoped crash.** Send `SIGKILL` only to the verified PostgreSQL service. The waiting client loses its session before commit.
9. **Restart and query.** PostgreSQL recovers from the same task volume. Both counts must be zero.
10. **Vary one condition.** Insert user `2002` and its profile in one transaction and wait for successful commit. Apply the same scoped process failure and restart.
11. **Query again.** Both counts must be one. The crash is held constant; commit status is the deciding changed condition.
12. **Check two schema rules.** A missing-parent profile must raise a foreign-key violation, and deleting a temporary owned user must cascade to its profile.
13. **Stop only the task service.** Retain the labeled volume so the final state remains recoverable.

## Correctness invariant

For this signup experiment:

```text
committed_profile(user_id) implies committed_user(user_id)
and a successful signup transition commits both rows
```

The foreign key enforces the first direction for every writer. The explicit transaction enforces the second direction for this two-statement signup. The crash assertions strengthen the evidence:

```text
before commit: (users, profiles) = (0, 0)
after commit:  (users, profiles) = (1, 1)
```

The schema alone does not force every user to have a profile at all times; that reverse mandatory relationship may require a different aggregate/table model, a deferred constraint trigger, or application workflow depending on lifecycle requirements. This reference does not pretend the foreign key proves more than it does.

## Complexity, capacity, or resource reasoning

- Each primary/foreign/unique index lookup is normally logarithmic in index size; actual cost depends on cache and data distribution.
- One signup does two inserts and several index updates within one transaction. At 500 signups/s, that is 500 commits/s and 1,000 base-row inserts/s before index/WAL amplification.
- The five-table fixture contains only a few rows and runs in well under one second after startup. The runtime cost is dominated by pulling/starting PostgreSQL and two crash recoveries, not query volume.
- A synchronous counter on one user row would serialize competing updates on that key. The reference avoids a counter because it is not required to prove the user/profile invariant.
- The task documents approximately 0.5 CPU, 256–512 MB memory, less than 20 MB task data, and 5–30 seconds startup after the image is available.

## Verification status

- Status: passed
- Evidence: [`lab/evidence.md`](../lab/evidence.md)
- Limitation: The verified run covers two PostgreSQL process crashes with one retained local task volume. It does not cover physical disk/host loss, replication, region failure, or Rahul's learner implementation. No learner completion is implied.

## Failure modes and recovery

| Failure | Symptom | Response | Remaining risk |
|---|---|---|---|
| Wrong Docker context | Preflight shows a non-local endpoint | Abort before starting or killing anything | Context metadata itself may be misconfigured |
| Project/name collision | Existing container/volume lacks task label | Abort and preserve it | Human must decide ownership |
| Crash before commit | Client disconnect; recovered counts `0/0` | Expected rollback/recovery; retry safely | External effects before commit would need compensation |
| Crash after commit | Startup recovery; recovered counts `1/1` | Resume only after health/invariant checks | Disk loss is outside this single-volume proof |
| Lost response during commit | Client cannot classify outcome | Query by operation/idempotency key before retry | Bad idempotency design can duplicate work |
| Foreign-key violation | SQLSTATE `23503` / named constraint | Fix write ordering or reject invalid input; rollback | Another code path may keep generating bad requests |
| Unique violation | Duplicate email/follow edge | Treat as idempotent match or conflict based on intent | Email canonicalization may be wrong |
| Long transaction | `pg_stat_activity` age and lock/version pressure | Shorten boundary and remove network waits | Hot keys may still contend |
| WAL/disk pressure | Commit tail latency rises | Measure WAL/disk/checkpoints; add capacity or reduce amplification | Weakening durability changes the contract |

## Alternatives

| Alternative | Prefer when | Why not selected here |
|---|---|---|
| MySQL InnoDB | Team/product standard is MySQL and its semantics are the learning target | PostgreSQL is already pinned and supported by this repository; the course permits either |
| Shared root PostgreSQL | Ordinary SQL/constraint/isolation task without server failure | Killing a shared service violates the crash-isolation rule |
| Client-session termination only | Learning question is automatic rollback on disconnect | The instructor later explicitly describes killing the database and observing recovery |
| One combined user/profile table | Profile cannot have an independent lifecycle and fields always load together | The assignment explicitly asks for users and profile tables/relationships |
| Deferred constraint trigger requiring a profile | The database must prove every committed user has a profile | Adds hidden complexity and is unnecessary for the focused creation transaction |
| Application compensation without a transaction | Systems cannot share a commit boundary | Both rows live in one PostgreSQL database, so local atomic commit is simpler and stronger |
| Asynchronous workflow | Profile may legitimately appear later | The exercise's invariant requires one signup transition to create both together |

## Interview follow-ups

### SDE-2

- Why does a foreign key from profile to user not prove that every user has a profile? Cue: implication direction and lifecycle.
- What happens if the connection drops while commit is in flight? Cue: ambiguous outcome, operation key, query-before-retry.
- Which PostgreSQL views/metrics reveal a long open transaction? Cue: `pg_stat_activity`, waits, transaction age, pool timing.
- How would you migrate a foreign key onto dirty production data? Cue: inventory/repair, staged validation, compatible application rollout.
- Why keep an email call out of this transaction? Cue: no shared commit boundary; outbox.

### SDE-3

- At 20,000 signups/s, what becomes the bottleneck first? Cue: measure WAL/commit, indexes, pool, hot uniqueness keys, storage; do not guess.
- How does the design change for active-active multi-region signup? Cue: ownership, global uniqueness, latency/availability trade-off, conflict policy.
- What durability guarantee is required for a successful response under region loss? Cue: synchronous remote acknowledgement, RPO/RTO, latency and availability cost.
- A celebrity hot key produces counter contention. Cue: derived, striped, or asynchronous counters and changed freshness guarantee.
- Serializable failures spike. Cue: inspect transaction overlap/key distribution, bound retries, reduce transaction scope, or redesign the invariant.

## Compare with Rahul's attempt

Complete only after Rahul attempts:

- Correct decisions:
- Missing reasoning:
- Different but valid choices:
- Evidence quality:
- One thing to retry closed-book:
