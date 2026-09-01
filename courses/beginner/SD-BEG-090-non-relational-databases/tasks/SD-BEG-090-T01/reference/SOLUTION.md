# Reference solution - SD-BEG-090-T01

> **Spoiler:** Open only after writing a committed attempt. This is one defensible exploration, not proof that every alternative query or graph database is wrong. Passing this reference does not complete Rahul’s learner task.

## Clarifications and assumptions

- The source gives one local exercise with three databases and no required dataset or output. This solution chooses one small capability per model and one controlled graph variation.
- MongoDB is used as the named document database, Redis as the named key-value store, and Neo4j as the named graph database.
- All services are single-node learning instances. No result is presented as evidence of sharding, replication, high availability, recovery, or production performance.
- “Partial update” means a logical server-side field update. It does not claim that only changed bytes are written internally.
- Redis `SET` is the product command corresponding to the course’s conceptual PUT. `INCR` is intentionally included to show that product-specific key commands exceed a three-operation caricature.
- Neo4j shortest path is by hop count over directed `FOLLOWS` relationships in this fixture; it is not a weighted recommendation algorithm.

## Prediction

- MongoDB accepts two documents with a shared core and different optional fields. `$inc` changes book stock `2 -> 3`, matches/modifies exactly one document, and preserves all other fields.
- Redis returns the exact stored profile string, changes counter `270 -> 271` with one `INCR`, deletes one temporary key, and reports the deleted key absent.
- Neo4j stores three nodes and two directed relationships. `Asha -> Ben -> Chen` is the baseline shortest path at two hops.
- After adding `Asha -> Chen`, the shortest path is one hop and the relationship count is three.

## Approach and why it fits

Use Docker Compose profiles to start one exact product at a time. Before mutation, a Python preflight verifies the local Unix-socket context, project, image, ports, labels, volumes, and namespaces. The separate verifier performs product-native commands inside the containers and asserts parsed state rather than trusting a printed success message.

This fits the source because Rahul genuinely runs and interacts with each named product. It also stays small: no client libraries, application server, browser UI, distributed cluster, or cloud account is necessary to expose the assigned capabilities.

## Step-by-step solution

### 1. Preflight and MongoDB document exploration

Run:

```bash
python3 lab/preflight.py
docker compose -f lab/compose.yaml --project-name sd-beg-090-t01 --profile mongo up -d mongo
```

Use authenticated `mongosh` inside the exact service. In database `sd_beg_090_t01`, first delete only documents tagged `lab_id=SD-BEG-090-T01`. Insert:

```javascript
{
  _id: "book-1",
  lab_id: "SD-BEG-090-T01",
  title: "Distributed Systems",
  category: "book",
  stock: 2,
  author: "Example Author"
}
```

and:

```javascript
{
  _id: "shirt-1",
  lab_id: "SD-BEG-090-T01",
  title: "Learning Lab Shirt",
  category: "apparel",
  stock: 5,
  size: "M"
}
```

Observe that exactly one tagged document matches `size: "M"`. Aggregate by category and expect one product in `apparel` and one in `book`. Apply the atomic single-document update:

```javascript
db.products.updateOne(
  {_id: "book-1", lab_id: "SD-BEG-090-T01"},
  {$inc: {stock: 1}}
)
```

The deciding evidence is `stock_before=2`, `stock_after=3`, `matched_count=1`, and `modified_count=1`, while `book-1` still lacks `size`. This demonstrates flexible document shape, filtering/aggregation, and a server-side document update. It does not establish multi-document transaction or sharding behavior.

Stop only `mongo` and retain its exact labeled volume.

### 2. Redis exact-key and atomic-command exploration

Start only `redis`. Authenticate with the synthetic password and reset exactly:

```text
sd:beg:090:t01:profile:42
sd:beg:090:t01:counter
sd:beg:090:t01:temporary
```

Execute this logical sequence with `redis-cli`:

```text
SET sd:beg:090:t01:profile:42 {"user_id":42,"plan":"pro"}
GET sd:beg:090:t01:profile:42
SET sd:beg:090:t01:counter 270
INCR sd:beg:090:t01:counter
GET sd:beg:090:t01:counter
SET sd:beg:090:t01:temporary delete-me
DEL sd:beg:090:t01:temporary
EXISTS sd:beg:090:t01:temporary
```

Expect the exact profile string, `271` from and after `INCR`, delete count `1`, and existence `0`. `INCR` performs the read/number change/write as one server command. A client-side `GET`, local addition, and `SET` would be a different concurrency boundary and could lose an update.

Stop only `redis` and retain its volume.

### 3. Neo4j relationship and path exploration

Start only `neo4j`. Delete only `LabPerson` nodes with the task `lab_id`, then create three nodes and two directed relationships:

```cypher
CREATE (a:LabPerson {lab_id: 'SD-BEG-090-T01', name: 'Asha'}),
       (b:LabPerson {lab_id: 'SD-BEG-090-T01', name: 'Ben'}),
       (c:LabPerson {lab_id: 'SD-BEG-090-T01', name: 'Chen'}),
       (a)-[:FOLLOWS {lab_id: 'SD-BEG-090-T01'}]->(b),
       (b)-[:FOLLOWS {lab_id: 'SD-BEG-090-T01'}]->(c);
```

Bind the two endpoints and bound traversal type, direction, and depth:

```cypher
MATCH (a:LabPerson {lab_id: 'SD-BEG-090-T01', name: 'Asha'}),
      (c:LabPerson {lab_id: 'SD-BEG-090-T01', name: 'Chen'})
MATCH p=shortestPath((a)-[:FOLLOWS*1..4]->(c))
RETURN length(p) AS hops;
```

Baseline: `3` nodes, `2` relationships, `2` hops.

Predict before changing state. Then add only:

```cypher
MATCH (a:LabPerson {lab_id: 'SD-BEG-090-T01', name: 'Asha'}),
      (c:LabPerson {lab_id: 'SD-BEG-090-T01', name: 'Chen'})
MERGE (a)-[:FOLLOWS {lab_id: 'SD-BEG-090-T01'}]->(c);
```

Repeat the bounded shortest-path query. The graph now has `3` relationships and the shortest path is `1` hop. Stop only `neo4j` and retain its volume.

### 4. Run every deterministic assertion

The reference runner executes the same scoped sequence and stops each service before starting the next. It first checks the host kernel; on a documented-incompatible MongoDB kernel it records that component as skipped and continues only the applicable checks:

```bash
python3 lab/verify_reference.py
```

It prints `SD-BEG-090-T01_REFERENCE_VERIFIED` only when all three products pass. On the observed incompatible host it instead printed `SD-BEG-090-T01_APPLICABLE_CHECKS_PASSED mongodb=skipped redis=passed neo4j=passed`; this is intentionally not full verification.

## Correctness invariant

All mutations belong to exactly one allowlisted namespace under the verified project:

- MongoDB documents require `lab_id=SD-BEG-090-T01` in `sd_beg_090_t01.products`;
- Redis touches only three fully enumerated `sd:beg:090:t01:` keys;
- Neo4j touches only `LabPerson` nodes with the task `lab_id` and relationships attached to those nodes.

For the data result, the observed transition must follow the product’s command/query boundary: one MongoDB document update reaches stock `3`; one Redis `INCR` reaches `271`; the shortest directed path changes from two hops to one only after the direct relationship exists.

## Complexity, capacity, or resource reasoning

- MongoDB `_id` lookup is index-addressed; the two-document aggregation is trivial here but can become a scan or distributed aggregation at scale without a fitting index/shard key.
- Redis GET/SET/INCR/DEL on one key are expected O(1) commands, but one hot key still has one ownership/serialization point.
- The tiny Neo4j traversal is bounded to four hops and two named endpoints. General path search cost grows with branching factor and depth; selective anchors and bounds matter more than this example’s runtime.
- Sequential execution reduces peak memory. The runtime cost of three production-grade databases would include upgrades, backups, observability, security, recovery testing, and on-call ownership—not only container memory.

## Verification status

- Status: skipped for the required MongoDB component; Redis and Neo4j applicable checks passed
- Evidence: [`lab/evidence.md`](../lab/evidence.md)
- Limitation: host kernel `7.0.0-30-generic` is inside MongoDB’s documented incompatible range `6.19` through `7.0.13`, so no MongoDB data assertion ran. Redis `8.10.1` and Neo4j `2026.07.1` passed, including clean exit `0`; distributed-system and learner-completion gaps remain.

## Failure modes and recovery

| Failure | Symptom | Response | Remaining risk |
|---|---|---|---|
| Wrong Docker context or reused port | preflight rejects endpoint/owner | stop before mutation; deliberately select the intended local context or resolve the owner with Rahul | environment can change between checks, so verifier rechecks runtime identity |
| Retained volume has unexpected state | authentication or count mismatch | verify exact volume label; delete only the allowlisted task records/keys/nodes | old engine-format data may require deliberate task-volume replacement, which is not automatic |
| Client read-modify-write race | accepted increments exceed final count | use one atomic product command/operator or conditional version | contention and retry latency remain |
| Hot key/document | one owner’s latency/conflicts rise | split/bucket/copy or serialize with a reconciliation invariant | more keys/documents create read and repair work |
| Broad graph expansion | high rows expanded, memory, timeout | selective indexed anchors; bound direction/type/depth; timeout; precompute | legitimate deep analytics may need another execution path |
| Service fails mid-run | missing marker and stopped/failed service state | retain logs/volumes, stop only the task service, rerun preflight, repair exact cause | the three explorations are independent; do not report an unrun product as passed |

## Alternatives

| Alternative | Prefer when | Why not selected here |
|---|---|---|
| Native host installations | Docker is unavailable and Rahul explicitly wants to manage packages/services | harder to isolate identity, ports, data, versions, and cleanup |
| One Python simulation | teaching a logical model without a product assignment | source explicitly requires running the three databases |
| MongoDB Atlas / Redis Cloud / Neo4j Aura | managed-service behavior is the learning target and cloud authority is supplied | unnecessary credentials, cost, network, and external state |
| PostgreSQL JSONB plus recursive CTE | the team wants one operational system and requirements fit | would not satisfy the instructor’s product-exploration exercise |
| Three separate task IDs | the source assigns three independent deliverables | the source and final slide present one exercise with three listed databases |

## Interview follow-ups

### SDE-2

- Which observation proves only single-document atomicity, and what changes for two documents?
- Why is Redis `INCR` safer than GET/compute/SET under concurrency?
- Which predicate/path bound prevents the Neo4j query from expanding the whole graph?
- What metrics reveal a hot key, a bad MongoDB query, and an exploding traversal?

### SDE-3

- If catalog, session, search, and graph projections all derive from one order transaction, define authority, outbox/CDC, idempotency, replay, and reconciliation.
- If p99 must remain below 20 ms during a regional failure, which acknowledgment, replica-read, and degradation contracts change?
- At what measured threshold does adding a specialized database outweigh using PostgreSQL JSONB/indexes/recursive queries and one operational stack?
- How would a 20%-traffic celebrity key or supernode change partitioning, caching, traversal, and abuse-control design?

## Compare with Rahul's attempt

Complete only after Rahul attempts:

- Correct decisions:
- Missing reasoning:
- Different but valid choices:
- One thing to retry closed-book:
