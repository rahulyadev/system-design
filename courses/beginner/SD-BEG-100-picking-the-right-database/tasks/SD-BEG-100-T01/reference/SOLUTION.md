# Reference solution — SD-BEG-100-T01

> **Spoiler:** Open only after writing a committed attempt. This is one defensible exploration of the instructor’s open-ended exercise, not a mandated product pair and not proof that every alternative is wrong.

## Clarifications and assumptions

The source leaves the databases, workload, scale, runtime, and deliverable open. This reference chooses two familiar but different candidates:

- **PostgreSQL:** a relational database with constraints, transactions, indexes, SQL, and JSON support.
- **Redis:** an in-memory data-structure server with key-oriented operations, expiration, conditional set options, transactions/scripts, and configurable persistence.

It compares two workload shapes:

1. **Order authority:** create an order and reserve inventory once for one idempotency key. The order is durable, queryable for audit/reporting, and must not oversell stock.
2. **Expiring sessions:** look up a session by token, refresh it once per minute, and reject it after a 30-minute deadline. Session loss is assumed recoverable by reauthentication.

Teaching-scale assumptions come from the lecture notes’ worked example:

- orders peak at about 278 writes/s;
- five million active sessions average 1.5 KB and produce about 83,333 refresh writes/s;
- no real production benchmark or failover test was run.

## Prediction

Both databases can represent both workloads at a basic level. PostgreSQL will be the more natural authority for the multi-row order invariant and reporting. Redis will be the more natural session store because direct key lookup and expiration are central.

The crossed mappings will be technically possible under conditions:

- PostgreSQL can store and validate expiring sessions, but high-rate refreshes and cleanup create write, index, vacuum, partition, and capacity work that Redis makes more direct.
- Redis can store orders and provide conditional/atomic operations, but making it the sole financial authority requires deliberate persistence, replication, backup/restore, multi-key placement, reporting, and recovery design. That burden is not justified by “it is fast.”

Evidence that would change this prediction includes a proved PostgreSQL session design meeting 83k refreshes/s cheaply with failure headroom, or a Redis order design proving every invariant, durability target, restore objective, reporting path, and memory/cost limit more simply.

## Approach and why it fits

The comparison uses the same sequence for each mapping:

1. write the invariant and access pattern;
2. name the exact database mechanism;
3. identify the natural locality/atomicity;
4. identify the lost guarantee or extra work;
5. distinguish official capability from workload proof;
6. choose only after a failure trace and capacity estimate.

This directly serves the instructor’s aim: database categories overlap, so explore the overlap without pretending that the broad storage shape proves suitability.

### Question this visual answers

Where does each natural or crossed mapping gain simplicity, and where does it move complexity?

| Mapping | Useful mechanism | Natural gain | Lost guarantee / added work | Decision |
|---|---|---|---|---|
| PostgreSQL → orders | unique/check/FK constraints, transaction, conditional update, SQL indexes/joins | Shared invariant and reporting stay in one authoritative boundary | Must tune transactions/indexes and plan storage/partition/recovery | Prefer for stated assumptions |
| Redis → sessions | token key, expiration, conditional update, in-memory working set | Lookup, refresh, and TTL are direct operations | Must define eviction, failover, persistence, memory, and reauthentication | Prefer when loss is recoverable |
| PostgreSQL → sessions | primary-key token, `expires_at`, indexed/partitioned cleanup, transaction | Durable, queryable sessions in existing stack | 83k refresh writes/s and expiry cleanup may cause heavy write/index/vacuum work | Accept only if measured and operationally simpler |
| Redis → orders | hashes/strings, `SET ... NX`, `WATCH`/transactions or scripts, persistence options | Low-latency keyed commands and conditional claims | Financial durability, multi-key invariants, reporting, restore, memory, and cluster boundaries need more design | Reject as sole authority here; derived view may fit |

### How to read this visual

Compare rows in pairs. The first two show natural fits; the last two cross the categories. “Useful mechanism” proves possibility. “Lost guarantee / added work” explains why possibility is not yet a good choice.

### Key insight

Moving a workload to another database rarely deletes complexity. It moves the complexity across the database/application/operations boundary. The right decision places the hardest must-have behavior where it is easiest to enforce and recover.

### Simplification or limitation

The table is a design review, not a latency, throughput, or failover benchmark. Exact results depend on versions, topology, schema/key design, persistence, data distribution, hardware/service tier, and client behavior.

## Step-by-step solution

### 1. Define workload A: authoritative order creation

**Command:** Create order `O91`, reserve two units of SKU `S7`, and associate merchant idempotency key `K5`.

**Invariants:**

- `(merchant_id, idempotency_key)` identifies at most one logical order.
- available inventory never becomes negative.
- a successful response refers to a durably committed authoritative state.

**Access patterns:**

- point-read order by `order_id`;
- return the newest 20 orders for one customer;
- audit orders/payments by time and merchant;
- retry creation with the same idempotency key and return the original result.

### 2. Natural mapping: PostgreSQL for orders

A defensible model uses a unique constraint for the idempotency key and one transaction for the conditional inventory decrement, order insert, and outbox intent. The affected-row count proves whether inventory was sufficient. SQL indexes serve order and customer/time reads; joins and aggregates serve operational reports.

[PostgreSQL’s constraint documentation](https://www.postgresql.org/docs/current/ddl-constraints.html) verifies primary, unique, check, and foreign-key mechanisms. It does not prove the schema’s peak latency or failover behavior; those require a representative run.

**Failure trace:** the database commits but the HTTP response is lost. A retry with `K5` conflicts with or finds the existing unique key and returns order `O91` instead of creating `O92`.

### 3. Crossed mapping: Redis for orders

Redis can represent an order as a hash or serialized value. `SET key value NX` can claim an idempotency key only if it is absent. `WATCH` with `MULTI/EXEC`, or a suitable server-side script/function, can make a conditional sequence atomic within supported key/topology boundaries. Official Redis docs verify [conditional `SET`](https://redis.io/docs/latest/commands/set/) and [transactions/optimistic locking](https://redis.io/docs/latest/develop/using-commands/transactions/).

That capability does not settle the design:

1. Order, inventory, and idempotency keys must share an atomic placement/protocol.
2. Redis transactions do not provide relational constraint declarations or rollback semantics identical to PostgreSQL.
3. The required acknowledged-write durability must be mapped to [Redis persistence options](https://redis.io/docs/latest/operate/oss_and_stack/management/persistence/), replication/failover, and tested restore.
4. Long-retained orders, indexes, audit queries, and aggregations need additional structures or a projection.
5. Memory and copy/backup cost must be calculated for years of authoritative orders.

Therefore Redis can fit the key/conditional-operation shape, but it is rejected as the sole order authority under these assumptions. Redis could still hold a rebuildable order-summary cache or a bounded idempotency acceleration layer while PostgreSQL enforces the durable business rule.

### 4. Define workload B: expiring sessions

**Command:** Store or refresh token `T8` for user `U4` with an absolute 30-minute authorization deadline.

**Invariant:** a session must not authorize a request after its recorded deadline.

**Access pattern:** point-read by unpredictable token on every authenticated request; refresh active sessions once per minute; explicit revoke by token; no ad hoc join is required on the hot path.

**Capacity:**

```text
raw working set  = 5,000,000 × 1.5 KB = 7.5 GB
refresh writes/s = 5,000,000 ÷ 60     ≈ 83,333 writes/s
```

This is a hot TTL working set, not a three-year financial ledger.

### 5. Natural mapping: Redis for sessions

A token key can store the payload with an expiration. Redis documents [key expiration and TTL](https://redis.io/docs/latest/develop/using-commands/keyspace/). The application should also keep the absolute expiry inside or alongside the value so authorization does not depend on cleanup timing alone.

The design must still decide:

- whether session loss causes safe reauthentication or an unacceptable outage;
- eviction policy and reserved memory;
- primary/replica/cluster distribution and hot-key risk;
- persistence and failover behavior;
- what happens when Redis is unavailable.

Under the assumption that sessions are recoverable, forced reauthentication is an acceptable degradation. Redis is preferred because the important key and expiration operations are direct.

### 6. Crossed mapping: PostgreSQL for sessions

PostgreSQL can model:

```text
sessions(token PRIMARY KEY, user_id, payload, expires_at, updated_at)
```

Authorization performs a primary-key lookup and requires `expires_at > current_time`. A scheduled delete, batched cleanup, or time partition retirement removes expired rows later. Delayed physical deletion does not violate the authorization invariant if every read checks the deadline.

This can be the right smaller-stack choice at modest rates. At the assumed 83,333 refresh writes/s, however, it needs evidence for connection/transaction overhead, WAL, indexes, dead tuples/vacuum, cleanup/partitioning, replicas, failover, and cost. PostgreSQL remains technically capable in a designed distributed deployment; “one table exists” is not proof that this particular envelope is economical.

### 7. Vary one requirement

Change: session state now contains a security grant that must survive any acknowledged write and must be immediately revocable across regions.

Fresh prediction: the earlier “loss causes reauthentication” assumption is invalid. Revisit the authoritative grant model, regional coordination, acknowledgment, read path, and revocation semantics. Redis might remain a fast projection, but a durable authority or a much stronger Redis durability/topology design is required. The product decision changes because the invariant changed, not because the payload stopped being key-value shaped.

## Correctness invariant

The comparison itself is correct only if each candidate is evaluated against the **same workload contract**. A crossed mapping cannot quietly weaken “durably acknowledged” to “usually present,” remove the order idempotency rule, or change an 83k-writes/s session workload into a tiny demo.

For the selected design:

- PostgreSQL is the conflict-resolution authority for orders.
- Redis session authorization is valid only before the stored deadline.
- Any Redis order view is derived and rebuildable from PostgreSQL.
- A retry with the same order idempotency key returns one logical result.

## Complexity, capacity, or resource reasoning

- Order peak: about 278 writes/s under the stated 20× factor. This is not by itself evidence that a distributed key-value store is needed.
- Session refresh: about 83,333 writes/s, roughly 300× the order peak. Distribution and hot-key testing matter even though each operation is simple.
- Session raw working set: 7.5 GB before allocator/object overhead, replicas, headroom, persistence, and backup.
- PostgreSQL session cleanup cost grows with refresh churn and expiration volume, not only live rows.
- Redis order cost grows with years of retained authoritative state and every index/reporting structure, not only the current hot set.

The reference does not invent benchmark numbers. It identifies the measurements that would decide the crossed fits.

## Verification status

- Status: `not_required`
- Evidence: reviewable design trace plus official PostgreSQL and Redis capability documentation linked above.
- Checks actually run: repository live validation verifies task/source parity, learner/reference separation, required headings, links, and status consistency.
- Limitation: no database runtime, concurrency test, throughput benchmark, failover, persistence-loss, or restore experiment was required by the source or executed for this design-only baseline.

`reference_status: ready` means the example is available for comparison. It does not mean Rahul attempted the task or that either product passed the hypothetical workload.

## Failure modes and recovery

| Failure | Symptom | Response | Remaining risk |
|---|---|---|---|
| Order HTTP timeout after commit | Client retries and might duplicate | Durable unique idempotency claim returns original order | External payment provider still needs its own idempotency/reconciliation |
| Concurrent inventory reservations | Two orders consume one unit | Atomic conditional decrement inside authoritative transaction | Cross-shard inventory needs a different ownership/protocol |
| Redis session eviction | Valid user is logged out | Reauthenticate safely; alert on evictions and fix capacity/policy | Mass logout can still harm availability |
| Redis order persistence/failover gap | Acknowledged order key is missing | Do not use as authority without proved acknowledgment/recovery; reconcile from authority | A sole-Redis design needs a stricter test and runbook |
| PostgreSQL session cleanup falls behind | Table/index bloat and rising write latency | Keep expiry check correct; batch/partition cleanup; tune and measure | 83k refresh writes/s may still make design uneconomic |
| Hot token/tenant | One partition/connection path dominates | Measure top keys/tenants; split or isolate where possible | One indivisible hot entity can remain a limit |
| Unsafe dual write | PostgreSQL order commits but Redis write fails | Transactional outbox/CDC and idempotent replay | Derived read remains stale until recovery |
| Requirement drift | Session becomes non-recoverable but design still assumes loss | Re-run the decision canvas and durability/failure tests | Undocumented changes can invalidate earlier evidence silently |

## Alternatives

| Alternative | Prefer when | Why not selected here |
|---|---|---|
| MongoDB for orders or sessions | Bounded documents are the natural aggregate and its transaction/index/sharding envelope is proved | The two-candidate exercise already demonstrates overlap; adding a product would widen scope |
| DynamoDB for keyed orders/sessions | Access patterns are stable, managed distribution is valuable, and conditional/transaction boundaries fit | It would require a separate key/capacity/cost model not specified by the source |
| PostgreSQL for both | One stack meets the 83k session refresh/expiry envelope with headroom and lower total operating cost | This is plausible but must be measured; the reference predicts heavy churn work |
| Redis for both | Persistence, cluster placement, invariant, reporting, restore, and memory economics all pass | Those are the hardest unproved conditions for authoritative orders |
| Local in-process session cache | One process or sticky session scope is acceptable and loss is harmless | Five million shared active sessions and revocation need a shared ownership design |

## Interview follow-ups

### SDE-2

- How would you prove that an idempotency key prevents the timeout-after-commit duplicate rather than only hiding it?
- Which PostgreSQL metrics would reveal that session refresh churn, not live-row count, is the bottleneck?
- Which Redis evidence distinguishes expiration, eviction, restart loss, and replica/failover loss?
- What changes when the order and inventory keys do not share one Redis cluster slot or transactional boundary?

### SDE-3

- At what measured threshold does one PostgreSQL authority become less operable than split order/session stores?
- How do regional residency and network partitions change the order authority and session-revocation design?
- If Redis becomes an order read model, how are outbox lag, replay, privacy deletion, and source/projection parity owned?
- How would you compare managed PostgreSQL, Redis, DynamoDB, and MongoDB by total cost per business operation rather than node price?

## Compare with Rahul's attempt

Complete only after Rahul attempts:

- Correct decisions:
- Missing reasoning:
- Different but valid choices:
- Evidence stronger than the reference:
- One thing to retry closed-book:
