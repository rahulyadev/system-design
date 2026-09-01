# Reference solution — SD-BEG-070-T02

> **Spoiler:** Open only after writing a committed attempt. This reference is one defensible solution, not proof that every alternative is wrong.

## Clarifications and assumptions

- The source’s “two DB” instruction is implemented as two independent MySQL 8.4.11 servers. They do not replicate each other.
- Keys are normalized to lowercase and must match `^[a-z][a-z0-9_-]{0,63}$`. The source does not specify this grammar; it is a deterministic safety contract.
- First letters `a`–`m` map to shard `am`/server `711`; `n`–`z` map to shard `nz`/server `712`.
- The normalized key is stored. Therefore POSTing `Zebra` stores and later reads `zebra` rather than preserving display case.
- Both POST and GET call the same owner function. Invalid keys are rejected before either database executes SQL.
- This fixed in-code mapping is a learning model, not a production resharding control plane.

## Prediction

`apple` and `mango` should exist only on server `711`; `nectar` and `zebra` should exist only on server `712`. API GET should return the same owner/server identity as POST. `ZULU` should normalize to `zulu` and use server `712`. `9-invalid` should return `422` and leave both shards unchanged. Twenty `a-hot-*` rows and two `z-cold-*` rows should produce direct counts `20/2`, a 10:1 distribution despite identical shard hardware.

## Approach and why it fits

The [reference API](server.mjs) owns two real `mysql2` pools. `normalizeKey` validates once, and `ownerForKey` returns the normalized key, shard name, and pool. Every read and write uses this same function. That makes the ownership decision small enough to test at the a/m/n/z boundaries and prevents POST/GET drift.

The verifier treats physical state as authoritative evidence:

- server `711` must contain every a–m row and zero matching n–z rows;
- server `712` must contain every n–z row and zero matching a–m rows;
- API metadata must agree with direct `@@server_id` and row counts;
- invalid input must not change either table.

## Step-by-step solution

1. Run the read-only preflight and reject unexpected context, project, image, labels, ports, or volumes.
2. Start `shard_am` and `shard_nz`; wait for health and inspect exact container/volume identity.
3. Require MySQL version 8.4.11 and server IDs `711/712`.
4. Load [schema.sql](schema.sql) independently on both shards. This intentionally does not copy data between them.
5. Start [server.mjs](server.mjs) on loopback and require health to query both server IDs.
6. POST `apple`, `mango`, `nectar`, and `zebra`; require expected shard and server identity.
7. GET every key through the API and then query both physical tables. Require correct-owner count `1` and wrong-owner count `0` for each key.
8. POST `ZULU`; require normalized key `zulu` on server `712` only.
9. POST `9-invalid`; require HTTP `422` and unchanged total row counts.
10. POST 20 `a-hot-00`…`a-hot-19` and two `z-cold-00`…`z-cold-01`; query prefix counts directly and require `20/2`.
11. Stop the API and only the two task services; verify exact labeled volumes remain.

Executable assertions live in [`lab/verify_reference.py`](../lab/verify_reference.py), and genuine observed output lives in [`lab/evidence.md`](../lab/evidence.md).

## Correctness invariant

For mapping version 1 and every valid normalized key `k`:

```text
owners(k) = {shard_am} when 'a' <= k[0] <= 'm'
owners(k) = {shard_nz} when 'n' <= k[0] <= 'z'
|owners(k)| = 1
```

POST and GET must evaluate the same function. A rejected key has zero owners and must cause zero database mutations. Direct evidence must show the record on its one owner and absent from the other shard.

During a future reshard, “mapping version 1” becomes essential: old and new processes cannot silently choose different owners. A production migration needs versioning, fencing/forwarding, backfill, verification, and a cutover/rollback plan.

## Complexity, capacity, or resource reasoning

- Validation and two-way range routing are `O(1)` per request.
- Point reads/writes are expected `O(log n)` through each shard’s primary-key index.
- One API process can open up to four connections per shard, or eight total; multiply by every process when budgeting database connections.
- Nominal storage/write capacity is roughly the sum only when data and costly operations are balanced and local.
- In the variation, `20 ÷ 2 = 10`, so the hotter shard receives ten times the controlled records. If both shards cap at the same rate, the hotter owner reaches saturation first while the other retains headroom.
- Range scans confined to one owner are simple; a scan across a–z fans out to both shards and needs merge/error/timeout semantics.

## Verification status

- Status: passed
- Evidence: [`lab/evidence.md`](../lab/evidence.md)
- Limitation: the run proves deterministic placement for two local MySQL servers and 27 stored rows plus one rejected input. It is not a throughput benchmark and does not test replication, failover, concurrent resharding, cross-shard transactions, backups, or remote deployment.

## Failure modes and recovery

| Failure | Symptom | Response | Remaining risk |
|---|---|---|---|
| POST/GET mapping drift | write succeeds but routed GET returns `404` | stop affected traffic, compare mapping code/version and direct rows, repair one central function | earlier wrong-owner rows need reconciliation |
| Stale process after boundary change | same key appears missing or duplicated across versions | fence old writers, use versioned map/forwarding, audit ownership before cutover | cached clients may outlive rollout |
| Hot a–m range | server 711 latency/CPU/queue rises while 712 is idle | split/move hot subrange or isolate hot tenant with a planned migration | migration adds dual-state and load risk |
| One shard unavailable | only its key range errors | fail/degrade that range explicitly; use per-shard replicas/failover if required | cross-shard operations may partially succeed |
| Invalid key silently defaults | unowned data lands on arbitrary shard | reject before SQL and monitor validation failures | changing grammar later needs data migration |
| Cross-shard request times out | partial results or inconsistent retry | define per-shard deadline, idempotency, merge and partial-failure contract | distributed transaction/aggregation cost remains |

## Alternatives

| Alternative | Prefer when | Why not selected here |
|---|---|---|
| Hash/modulo sharding | point access and distribution dominate | hides the source’s explicit a–m/n–z range exercise and complicates range locality |
| Consistent hashing | nodes change often and key movement must be bounded | adds ring/virtual-node concepts not required to complete this exercise |
| Directory-based placement | large tenants need deliberate moves/isolation | introduces a metadata dependency; fixed ranges make the learning invariant visible |
| One larger database | it meets storage/write/latency targets with headroom | the exercise explicitly asks Rahul to implement two shards |
| Database-native distributed SQL | automatic placement/transactions justify product complexity | hides application routing and adds a materially different operational model |

## Interview follow-ups

### SDE-2

- Why must GET and POST share one owner function? Prevent missing reads and duplicate ownership.
- How do you test the m/n boundary? Table-driven a/m/n/z cases plus correct/wrong physical queries.
- What metrics show skew? Per-shard rows/bytes/read/write rate/latency plus hot key or tenant traces.
- What happens to an a–z list query? Fan out, bound deadlines, merge ordering, and define partial failure.

### SDE-3

- Requirement change: one `a` tenant becomes 45% of writes. Design sub-sharding or dedicated placement and a safe migration.
- Scale change: add a third shard without moving all data. Compare range split, directory, and consistent hashing; state mapping-version mechanics.
- Failure change: one shard is down during a cross-shard write. Define transaction boundary, idempotency, compensation, and user-visible state.
- Consistency change: globally unique usernames across shards. Add a dedicated uniqueness owner/reservation workflow or change the key/ownership model.

## Compare with Rahul's attempt

Complete only after Rahul attempts:

- Correct decisions:
- Missing reasoning:
- Different but valid choices:
- One thing to retry closed-book:
