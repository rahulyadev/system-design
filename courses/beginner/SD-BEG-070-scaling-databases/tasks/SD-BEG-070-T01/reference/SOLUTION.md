# Reference solution — SD-BEG-070-T01

> **Spoiler:** Open only after writing a committed attempt. This reference is one defensible solution, not proof that every alternative is wrong.

## Clarifications and assumptions

- “Primary” is the source’s write-handling database role; the historical source term “master” means the same role here.
- MySQL ordinary asynchronous, file/position replication is sufficient to expose receive/apply lag. The task does not claim synchronous visibility or automatic failover.
- POST and strong GET require primary state. Eventual GET explicitly accepts replica freshness.
- The API runs on loopback and uses two real `mysql2` pools pointing to different published MySQL ports.
- Server IDs `701` and `702`, direct table queries, and replication positions are the evidence authority. A response’s `served_by` label is only supporting evidence.
- The synthetic application user has access only to the task database. The verifier enables `read_only` and `super_read_only` on the replica before API traffic.

## Prediction

With both replica threads running, a primary write should become visible on server `702` after its applied position reaches the captured source position. If only the replica SQL/applier thread is paused, the same write should commit and appear through a strong primary GET on server `701`, while an eventual replica GET temporarily returns `404`. After the applier resumes and `SOURCE_POS_WAIT` succeeds, the eventual GET should return the row. An application-user write directly to the replica should fail because the replica is read-only.

## Approach and why it fits

The task uses two MySQL 8.4.11 containers because the assignment specifically asks for MySQL replication. The source enables a binary log and has a unique server ID. After both independent container initializations finish, the verifier captures the source’s current log file/position and configures the replica from that point. Loading the table only after the channel is running avoids confusing independently initialized state with replicated state.

The [reference server](server.mjs) exposes a deliberately small contract:

- `POST /items` executes through `primaryPool`;
- `GET /items/:id?consistency=eventual` executes through `replicaPool`;
- `GET /items/:id?consistency=strong` executes through `primaryPool`;
- `/health` queries both `@@server_id` values.

This keeps the routing decision visible without introducing a framework, service discovery, proxy, or cloud control plane.

## Step-by-step solution

1. Run the read-only preflight. Reject non-Unix Docker endpoints, unexpected ports/images/labels, and unrelated state.
2. Start `source` and `replica`; wait for both task health checks.
3. Inspect each container’s project, service, task label, loopback binding, and exact volume mount.
4. If the replica channel is new, capture `SHOW BINARY LOG STATUS` on the source, execute `CHANGE REPLICATION SOURCE TO` on the replica, and start replication. If it already exists, verify the exact source host and resume it rather than silently replacing learner state.
5. Require receiver and applier states `Yes`; set `read_only=ON` and `super_read_only=ON` on the replica.
6. Load [schema.sql](schema.sql) on the source and wait until the replica reaches the resulting source position.
7. Start [server.mjs](server.mjs), verify health reports IDs `701/702`, POST baseline item `101`, wait for catch-up, and GET it through the replica.
8. Attempt an app-user insert directly on the replica and require a read-only failure.
9. Pause only `REPLICA SQL_THREAD`. POST item `202`, require strong GET `200` from server `701`, eventual GET `404` from server `702`, and direct counts `1/0` for that ID.
10. Resume the applier, wait for the saved source file/position, require eventual GET `200` from server `702`, and direct counts `1/1`.
11. Stop the API and only the two task services. Verify both exact labeled volumes remain recoverable.

The executable assertions live in [`lab/verify_reference.py`](../lab/verify_reference.py), while observed output is kept in [`lab/evidence.md`](../lab/evidence.md).

## Correctness invariant

For this topology:

1. every mutation executes only against server ID `701` through the primary pool;
2. server ID `702` remains protected by read-only controls for the application user;
3. an eventual read may return a row only when the replica has applied the corresponding source position;
4. a strong read uses the authoritative primary and never changes database within the request;
5. runtime evidence is accepted only after project/service/port/volume/task identity matches exactly.

These invariants prove the routing and visibility boundary. They do not prove automatic failover, zero data loss under source failure, or global strong consistency.

## Complexity, capacity, or resource reasoning

- Route selection is `O(1)` per request.
- Point insert/read is expected `O(log n)` through the InnoDB primary-key index.
- The reference uses at most four connections per pool, so one API process can open up to eight database connections. Production capacity must multiply that by every API process and leave administrative/failover headroom.
- One asynchronous replica adds roughly one full data copy and replication/network/apply work. It adds eligible read capacity but not independent authoritative write capacity.
- The paused-applier variation uses fewer than ten rows, so observed delay comes from the controlled pause rather than dataset size.

## Verification status

- Status: passed
- Evidence: [`lab/evidence.md`](../lab/evidence.md)
- Limitation: the run proves a two-node local MySQL 8.4.11 reference path and controlled apply lag. It does not test source crash/promotion, network partitions, TLS, backup restore, multiple replicas, remote durability, or production load.

## Failure modes and recovery

| Failure | Symptom | Response | Remaining risk |
|---|---|---|---|
| Receiver cannot reach source | `Replica_IO_Running=No`, `Last_IO_Error` | verify exact host/auth/network and retained source log before resuming/rebuilding | source may purge required history |
| Applier stops | receiver may stay `Yes`, SQL state `No`, applied position frozen | inspect `Last_SQL_Error`; resume only after exact cause is resolved | reads remain stale; relay log grows |
| API route regression | server ID disagrees with endpoint policy | fail the request/test and repair the central routing boundary | a privileged wrong-target write could diverge state |
| Replica promoted while behind | accepted primary rows absent after failover | compare positions, fence old primary, choose the safest candidate, reconcile | asynchronous acknowledgment can permit an RPO gap |
| Too many API processes/pools | connection wait/timeouts despite low query CPU | budget total pools, add backpressure/proxy, reduce idle connections | retries may amplify connection pressure |
| Source log removed too early | replica cannot continue from its file/position | rebuild only the replica from a safe snapshot and new coordinates | longer recovery and unavailable replica reads |

## Alternatives

| Alternative | Prefer when | Why not selected here |
|---|---|---|
| In-memory replication simulation | teaching only the state sequence | cannot prove MySQL thread, log-position, or read-only behavior |
| PostgreSQL streaming replication | the product/task explicitly targets PostgreSQL | instructor explicitly names MySQL in the exercise |
| Managed MySQL read replica | production operations and cloud authority are in scope | requires external account/cost and hides the setup this exercise asks Rahul to perform |
| Proxy-owned read/write split | many services need consistent generic policy | business-level read-after-write requirements still need explicit signals; adds another component |
| Semisynchronous MySQL | accepted writes must reach another node before return | this task focuses on observable ordinary asynchronous lag; semisync still does not imply replica apply |

## Interview follow-ups

### SDE-2

- Why can `Replica_IO_Running=Yes` coexist with stale reads? Separate receiver and applier progress.
- How would you test read-after-write without `sleep(1)`? Capture a source position and wait or route to primary.
- What metrics distinguish bad routing from replica lag? Route/server ID, source/received/applied positions, direct row state, and thread errors.
- How do you deploy the second pool safely? Bound connections, add health/fallback policy, trace role, canary endpoints, and test transaction stickiness.

### SDE-3

- Requirement change: RPO zero for accepted payments. Define a stronger remote acknowledgment/fencing design and its partition availability/latency cost.
- Scale change: five replicas across regions. Define freshness classes, load balancing without time-travel reads, and failover candidate selection.
- Failure change: the old primary returns after promotion. Explain fencing, topology metadata, write rejection, and reconciliation.
- Cost change: the larger primary tier costs less than the replica fleet plus on-call burden. State the threshold for removing or postponing replicas.

## Compare with Rahul's attempt

Complete only after Rahul attempts:

- Correct decisions:
- Missing reasoning:
- Different but valid choices:
- One thing to retry closed-book:
