# SD-BEG-130 - Caching at Different Levels

> **Track:** Beginner<br>
> **Artifact state:** Ready<br>
> **Learning state:** Not started<br>
> **Last updated:** 2026-09-02

## Source and coverage check

- Inspected: the complete transcript, all four slide pages, a full-duration video frame survey, five-second checks across the spoken exercise, and five-second checks across the final 20 percent.
- Coverage: complete from `00:00:01.199` through the `00:19:02.484` video ending; the final caption ends at `00:19:02.520` because of subtitle rounding.
- Visual fidelity: the diagrams below reconstruct the course's client, CDN, remote-cache, database-counter, and multi-layer invalidation ideas in original wording. No source image is copied.
- Transcript corrections: the visual sources resolve ASR errors including Redis, Akamai, staleness, invalidation, precomputed, `total_posts`, origin server, and Content Delivery Network.
- Unclear source points: the course does not define a complete HTTP cache key, provider routing algorithm, exact browser/CDN policy, remote-cache topology, counter-repair process, or safe provider-lab setup. The numerical claim about how commonly CDNs use lazy population is unsupported, so the notes retain it only as a qualitative course model.
- Instructor-task scan: complete; one combined exercise was detected at `00:11:48-00:12:52` and on slide 47. See [`SD-BEG-130-T01`](tasks/SD-BEG-130-T01/README.md).

## What I should be able to do

- Draw where a request may be answered by a browser cache, CDN, remote application cache, or database-held derived value.
- Explain CDN pull-on-miss population in order and identify the origin, cache key, freshness decision, and proof of a hit.
- Choose the shallowest useful cache from reuse, freshness, security, latency, failure, invalidation, and cost requirements.
- Explain why purging a CDN does not necessarily refresh a browser that already holds a fresh copy.
- Maintain a `total_posts` counter with its base write, state its invariant, and identify concurrency, retry, delete, and repair risks.
- Quantify how layered hit ratios change origin requests, origin bandwidth, and mean response latency.
- Diagnose wrong-user content, stale assets, low hit ratio, origin overload, cache stampedes, counter drift, and purge storms from evidence.
- Adapt the design when an interviewer tightens consistency, latency, availability, privacy, durability, or cost.

## Small bridge from earlier ideas

A **source of truth** owns the authoritative state. A **cache** holds a reusable copy or derived result so a later request can skip more expensive work. The copy is useful only while it is safe for the current request.

Four lifecycle terms matter:

- **Freshness** asks whether the stored response is still within the policy that permits reuse.
- **Expiry** makes an entry stale after time passes; physical removal can happen separately.
- **Invalidation** makes an entry unusable because the underlying meaning changed.
- **Eviction** removes an entry to reclaim capacity, even when it is still fresh.

A **cache key** answers “which requests may share this answer?” A hit is not merely “bytes exist.” It is a hit only when the key, authorization scope, representation variant, and freshness/version policy all permit reuse.

These are bridges, not prerequisites. This lecture's new question is placement: which component should own a reusable copy, and what guarantee changes when the copy moves closer to the user?

## The 60-second story

Caching can happen at many points, not only in Redis. A browser can reuse an image or JavaScript bundle without sending any request. A CDN can keep a shared copy near network users and fetch from an origin on a miss. Application servers can share a remote cache over the network. A database row can hold a precomputed value such as `total_posts`, replacing an expensive repeated aggregate with a cheap read.

Moving a copy closer usually removes more network and downstream work, but it also moves control away from the source. A server can delete a Redis key. A CDN offers purge APIs. A browser that already has a fresh response may not contact either one. Each extra level therefore adds a separate cache key, lifetime, capacity policy, failure mode, metric, and invalidation boundary.

The design rule is not “cache everywhere.” Cache at the smallest number of levels that produce a measured benefit while satisfying freshness, privacy, correctness, availability, and cost. If the system cannot say which layer served a response, how old it was, and how it will be repaired, the cache is not yet operationally designed.

## Why the terms matter

| Term | Simple meaning | Why it matters here | Common confusion |
|---|---|---|---|
| Cache level | A component boundary at which a reusable answer is stored | Placement determines avoided work, control, scope, and invalidation reach | A level is not necessarily a separate product |
| Private cache | A cache dedicated to one user, commonly a browser cache | It can avoid the entire backend path but is hardest for the server to purge | `private` controls shared storage; it does not encrypt content |
| Shared cache | A cache whose entries may serve multiple users, such as a CDN | A wrong key or policy can leak one user's response to another | Shared does not mean the source data is public by default |
| Origin server | The configured upstream a CDN contacts when it cannot serve a response | It owns the fill path and must survive misses, expiry waves, and purges | Origin is a role, not necessarily one machine or the database |
| Lazy population | Fetch and store only after a request cannot use an entry | This is the course's basic CDN path and admits data after observed demand | It does not guarantee one global copy or one origin fetch |
| Remote cache | A cache reached across a network by application instances | It offers fleet-wide reuse but adds a network dependency | Remote describes access; it does not require one physical node |
| Derived counter | A stored summary computed from base rows | It makes profile reads cheap at the cost of extra write and repair logic | It is not an independent source of truth unless the data model declares it so |
| Fresh | Reusable without first validating with the origin | Freshness is a policy decision, not the same as “identical to truth now” | A fresh cached response can still be semantically outdated after an unobserved source change |
| Purge | Provider operation that invalidates selected edge copy or copies | It can shorten CDN staleness after a change | Purging the CDN does not erase a fresh browser copy |
| Overcaching | Adding cache levels whose benefit does not repay their consistency and operating cost | It is the lecture's closing warning | More hits do not automatically mean lower end-to-end risk or cost |

## Big picture

### Question this visual answers

At which boundaries can one request avoid downstream work, and where does authoritative data remain?

~~~mermaid
flowchart LR
    U["User"] --> B["Browser private cache"]
    B -->|"network miss"| E["CDN shared edge cache"]
    E -->|"edge miss"| A["API / application"]
    A -->|"application lookup"| R["Remote cache"]
    R -->|"miss or rejected value"| Q["Database read path"]
    A -->|"cache bypass"| Q
    subgraph DB["Database boundary"]
        C["Stored derived counter"]
        P["Base post rows / aggregate"]
    end
    Q -->|"cheap maintained value"| C
    Q -->|"compute from authority"| P
    C -. "must agree under its defined invariant" .-> P
    Q -. "change signal or request-path action" .-> R
    R -. "purge / refresh when selected" .-> E
    E -. "response policy; no universal forced delete" .-> B
~~~

### How to read this visual

Follow solid arrows left to right. The earliest usable answer wins. A browser hit avoids the network. A CDN hit avoids the origin application. A remote-cache hit avoids a database read or computation. The derived counter is an alternative database read model: the API reads one maintained value instead of recounting base posts. Dotted arrows show that changes may need to move outward, but each boundary has a different invalidation mechanism.

### Key insight

The closer cache usually skips more work, but the farther it is from the authority, the less direct control the write path has over every copy. Placement is a guarantee decision before it is a technology decision.

### Simplification or limitation

One real request does not always traverse every box. A static image may use only browser, CDN, and object origin; a private API may use API, remote cache, and database. The drawing omits regional tiers, service-worker caches, process-local caches, replicas, authorization, request collapsing, retries, and multiple representations.

### Question this visual answers

How does a basic CDN fill lazily, and why can an origin update remain invisible until expiry or purge?

~~~mermaid
sequenceDiagram
    participant U as User
    participant E as CDN edge
    participant O as Origin

    U->>E: GET /image-v1.png
    E->>O: Miss: forward equivalent request
    O-->>E: image bytes + cache policy + validator
    E-->>U: Store eligible response; return MISS
    U->>E: Same cache key again
    E-->>U: Reuse fresh copy; return HIT + age
    Note over O: Origin bytes change at the same URL
    U->>E: Same cache key before expiry
    E-->>U: Old but still fresh cached copy
    Note over E: Exact-URL purge or freshness expiry
    U->>E: Same cache key
    E->>O: Fetch or revalidate
    O-->>E: New bytes
    E-->>U: New representation
~~~

### How to read this visual

The first request pays the origin path and may populate one edge cache. The second equivalent request can reuse the stored response. Changing the origin does not send a magical update to every stored copy. Until policy requires revalidation or an invalidation reaches the edge, that edge can keep serving the admitted representation.

### Key insight

“The origin has version 2” and “this edge may still reuse version 1” can both be true. The deciding condition is the cache's reuse policy for that key, not the mere existence of newer origin bytes.

### Simplification or limitation

Real CDNs have many edge locations and sometimes upper cache tiers. Two requests can reach different caches; eviction can cause a fresh object to miss; a provider may collapse concurrent misses; a browser can answer before the CDN; and provider status names vary.

## Core concepts

### 1. Choose placement from the guarantee, not from the availability of memory

**Simple meaning:** A component *can* retain data without that being the right cache boundary.

**Formal meaning:** A cache placement is valid only when the set of requests allowed to reuse one representation, the acceptable age/version, the authority, and the failure behavior are explicit at that boundary.

**Why it exists:** Without a placement decision, teams add independent copies that reduce steady-state latency but cannot be invalidated, secured, capacity-planned, or diagnosed as one system.

**How it works:**

1. Define the expensive work: bytes transferred, query, computation, or remote call.
2. Define which requests may safely share the result: user, tenant, locale, encoding, device, authorization, query, and version.
3. Set the maximum acceptable staleness and decide whether validation is required.
4. Estimate reuse before expiry/eviction and the cost of misses.
5. Choose the shallowest level that removes the expensive work without violating the contract.
6. Define invalidation, outage behavior, capacity bounds, and observable proof before rollout.

**Invariant or deciding condition:** Every cache hit must be interchangeable with the answer allowed for that request under the declared consistency and security policy.

**Small example:** A fingerprinted public logo can live in browser and CDN caches for a long time. A user's exact current balance should use an authoritative or explicitly coordinated path; copying it casually into a shared CDN is invalid.

**Trade-off:** Earlier answers reduce more latency and load, while increasing distribution, invalidation delay, and loss of central control.

**Failure/observability:** Wrong-user responses, unexplained old versions, or a low origin QPS with high complaints signal a policy/key error. Record outcome, key version, value version/age, layer, and fallback reason on traces and metrics.

**When not to use it:** Skip a cache when reuse is low, the source is already cheap, the result is highly personalized or fast-changing, or the team lacks an invalidation and failure budget.

**Interview requirement changes:** Higher scale or tighter latency favors earlier reuse; stronger consistency or privacy pushes reads toward controlled/authoritative boundaries; higher availability may permit explicitly bounded stale responses; lower cost favors caching only where origin work or egress is actually significant.

### 2. Client-side caching can remove the entire backend request

**Simple meaning:** The browser or mobile client reuses something it already holds.

**Formal meaning:** For HTTP, a browser is normally a private cache that decides storage and reuse from request/response semantics, freshness metadata, validators, local policy, and user actions. Applications can also hold non-HTTP local state, but that has a separate synchronization contract.

**Why it exists:** Static images, fonts, JavaScript, CSS, and other reusable representations otherwise pay network latency and bandwidth on every view.

**How it works:**

1. The client requests a resource and receives bytes plus cache policy and possibly `ETag` or `Last-Modified`.
2. It stores an eligible representation under a cache key.
3. A later request either reuses a fresh representation, validates a stale one conditionally, or performs a full fetch.
4. A versioned URL creates a new key, so a deployment can coexist with older cached assets.

**Invariant or deciding condition:** A private cached response is reusable only for the same effective representation and user scope, and only when freshness or successful validation permits it.

**Small example:** `/assets/app.8f31c.js` can be immutable because changed bytes deploy as a different filename. `/api/account/balance` can respond with `Cache-Control: no-store` when local storage is unacceptable.

**Trade-off:** This level provides the largest path reduction but server-side purge generally cannot force every device to discard an already-fresh object.

**Failure/observability:** An old bundle can call a removed API, local watch progress can conflict across devices, or sensitive content can persist. Inspect browser DevTools cache source, resource URL/version, response policy, transfer size, validators, and application sync events.

**When not to use it:** Avoid storing secrets, cross-user responses, one-time tokens, or data whose immediate revocation cannot tolerate a disconnected client. Prefer short freshness plus validation, an authoritative read, or no storage.

**Interview requirement changes:** Offline availability may justify local state and conflict resolution; five-second freshness needs short policy or version checks; zero stale tolerance can remove direct reuse; bandwidth-sensitive mobile clients benefit from validation even when full reuse is disallowed.

### 3. A CDN is a shared cache and routing system in front of an origin

**Simple meaning:** A distributed provider stores reusable responses near network users so most requests do not travel to the application's origin.

**Formal meaning:** A CDN is an HTTP intermediary with many points of presence. Routing brings a request to a suitable edge; cacheability, key selection, freshness, validation, eviction, and provider rules determine whether that edge can answer.

**Why it exists:** Long network paths and repeated delivery of the same bytes add user latency, origin bandwidth, compute load, and exposure to traffic spikes.

**How it works:**

1. DNS/proxy configuration routes an eligible hostname through the CDN.
2. Network routing selects an edge; “near” usually means a routing/performance choice, not guaranteed geographical minimum distance.
3. The edge computes a cache key and checks an eligible stored response.
4. On a usable hit, it returns the copy and typically exposes provider/HTTP age evidence.
5. On a miss, it contacts the configured origin, receives the response, stores it if permitted, and returns it.
6. Later requests reuse the copy until expiry, revalidation, eviction, purge, or a changed key.

**Invariant or deciding condition:** The edge may reuse a response only when the request selects the same representation and shared caching plus freshness/validation rules allow that reuse.

**Small example:** An Indian user's first request for an image may reach an edge that fetches from an Australian origin. Later equivalent requests reaching a cache with that object can avoid the Australia round trip.

**Trade-off:** CDNs cut origin latency, load, and egress, but add provider configuration, distributed cache states, purge delay, cache-key/security risk, and cost.

**Failure/observability:** `MISS` on every request can result from an uncacheable method/status, `private`/`no-store`, cookies, a changing query key, rule mismatch, eviction, or different edge locations. Inspect provider cache status, `Age`, key-relevant inputs, response headers, edge/point-of-presence identity, origin logs, cache-rule matches, and byte hit ratio.

**When not to use it:** Do not share personalized or authorization-sensitive responses without a proven key and cacheability policy. Bypass it when content has negligible reuse, strict immediate consistency, or an origin path already meeting cost/latency goals.

**Interview requirement changes:** Global users and large public objects increase CDN value; strict purge deadlines need versioned URLs or measured invalidation SLOs; regional data residency may restrict cache locations; origin failure may justify `stale-if-error` only if the business accepts its age.

### 4. A remote cache shares application results across server instances

**Simple meaning:** APIs call a cache service over the network instead of each process keeping its own private copy.

**Formal meaning:** A remote cache is a logically shared cache boundary reachable by multiple application instances. Its implementation may be one node, replicated, sharded, managed, or distributed; “remote” describes the call boundary rather than the topology.

**Why it exists:** It prevents every API instance from recomputing the same frequently accessed value and makes a shared invalidation policy possible.

**How it works:**

1. The API constructs a namespaced, versioned key.
2. It performs a bounded lookup over the network.
3. A usable hit returns the derived value.
4. A miss reads/computes from the authority, then attempts a fill with an explicit lifecycle/capacity policy.
5. Writes invalidate, replace, or version affected keys according to ordering and failure rules.

**Invariant or deciding condition:** Cache loss must not lose authoritative data when the service is being used as a disposable cache, and a served value must satisfy the request's user/tenant/version/freshness scope.

**Small example:** All FastAPI instances use `profile:v4:tenant-7:user-42` for the same public profile summary. The database owns the profile; Redis may hold its serialized read model.

**Trade-off:** Fleet-wide reuse and centralized operations cost an extra network hop, serialization, connection capacity, cluster management, and a new shared failure domain.

**Failure/observability:** A cache timeout can fan all traffic to PostgreSQL, one hot key can saturate a shard, and an expiry wave can trigger duplicate fills. Measure hit/miss/rejected-stale/error separately, latency and timeouts, per-key/shard load, connection saturation, memory/eviction, source fallback QPS, and coalesced waiters.

**When not to use it:** A process-local bounded cache may be enough for tiny immutable metadata; no cache may be better for cheap low-reuse reads; an authoritative durable store is required if the value cannot be reconstructed.

**Interview requirement changes:** More instances increase shared reuse; lower latency may favor a small near-cache but creates another invalidation layer; stronger read-after-write needs versions/fencing or authoritative reads; cache outages require bounded fallback, load shedding, or degraded fields.

### 5. A database can store a maintained derived value

**Simple meaning:** Store an answer such as a post count once, then update it when posts change instead of recounting on every profile read.

**Formal meaning:** The course calls this database caching. More precisely, it is denormalized or materialized derived state stored beside or near authoritative rows. Its lifecycle is normally write-maintained or asynchronously refreshed rather than time-expired.

**Why it exists:** Repeated aggregation can consume CPU, I/O, index traversal, locks, and latency even though the result changes far less often than it is read.

**How it works:**

1. Define exactly which rows count, such as published and not deleted posts.
2. Store `users.total_posts` with a starting value.
3. In one database transaction, insert/publish the post and atomically increment the matching user counter.
4. Handle unpublish/delete with the inverse transition.
5. Make retries idempotent so one logical event changes the counter once.
6. Periodically reconcile the stored value against an authoritative aggregate and repair drift.

**Invariant or deciding condition:** For each user, `total_posts` must equal the count of base rows that satisfy the declared “published post” predicate at the consistency point promised by the API.

**Small example:** If user 123 has 77 published posts, one new publish transaction inserts the post and executes `UPDATE users SET total_posts = total_posts + 1 WHERE id = 123`; after commit, both become visible together.

**Trade-off:** Profile reads become constant-size lookups, while every relevant write gains work, row contention, retry semantics, backfill, and repair responsibility.

**Failure/observability:** Separate transactions can commit only one side; non-idempotent retries double-increment; deletes omit decrements; bulk imports bypass logic; one celebrity's user row becomes a write hotspot. Measure reconciliation error, counter update failures/retries, row-lock wait, update rate per user, negative values, and age of last repair.

**When not to use it:** Keep the aggregate on read when reads are rare, the indexed aggregate is cheap enough, write contention dominates, or the exact counting predicate changes often. A materialized view or asynchronously built read model may fit batch freshness.

**Interview requirement changes:** Exact immediate counts favor one transaction or a database constraint/trigger boundary; high write volume may favor event-driven sharded counters with stated lag; audit-critical numbers require reconstructable events and reconciliation; lower cost may accept an approximate count.

### 6. Multi-level invalidation is a distributed coordination problem

**Simple meaning:** Updating the source does not automatically update every copy in every browser, edge, process, cache cluster, and database read model.

**Formal meaning:** Each cache level has independent ownership, keys, freshness clocks, invalidation APIs, reachability, ordering, retries, and failure states. End-to-end freshness is bounded by the least-controlled copy that is still allowed to answer.

**Why it exists:** A write can succeed while one invalidation is delayed, lost, reordered, or impossible to push to a disconnected client.

**How it works:**

1. Commit the authoritative change under the required transaction boundary.
2. Produce an idempotent version/change record when multiple caches need repair.
3. Invalidate or refresh only the levels that hold the affected representation.
4. Reject delayed fills that carry an older version.
5. Let short freshness or versioned URLs bound copies that cannot be directly purged.
6. Observe propagation age and repair failures against a user-visible freshness SLO.

**Invariant or deciding condition:** No cache may serve a version outside the endpoint's accepted age/version window, even when another cache level has already updated.

**Small example:** Purging `/avatar.png` at the CDN makes the next edge request fetch again, but a browser with a still-fresh `/avatar.png` can keep showing old bytes. Deploying `/avatar.<content-hash>.png` changes the key and avoids waiting for that old entry.

**Trade-off:** Event-driven invalidation shortens stale windows but adds delivery, ordering, idempotency, and retry complexity. Short TTLs reduce worst-case age but increase origin load. Versioned keys improve rollout safety but leave old objects until eviction/cleanup.

**Failure/observability:** Missing one variant, tenant, query value, or region causes partial staleness; a purge-everything event can create an origin spike. Track change version/time, per-level purge acknowledgements, version age in responses, origin surge after purge, and user reports by URL/region/device.

**When not to use it:** Do not build cross-layer invalidation for an endpoint that can simply read the authority within its budget. Avoid a browser cache for immediately revocable data that cannot tolerate offline reuse.

**Interview requirement changes:** A five-minute stale budget may need only TTL; five seconds may need active invalidation and version telemetry; read-your-own-write may bypass caches or require session/version fencing; high availability may explicitly allow stale-on-error with an age cap.

### 7. “Cache everywhere” is an anti-pattern

**Simple meaning:** Every extra cache must earn its place.

**Formal meaning:** A cache level has positive value only when avoided downstream cost multiplied by usable reuse exceeds lookup, storage, miss, invalidation, failure, security, and operational cost under both steady state and recovery.

**Why it exists:** Happy-path benchmarks hide cold starts, purge waves, low-reuse keys, duplicated memory, stale data, and incident-debugging time.

**How it works:**

1. Establish a no-cache baseline and an SLO/cost objective.
2. Add one candidate level and measure user latency, origin load, byte savings, and stale/error outcomes.
3. Test cold cache, outage, mass expiry, invalidation, and key-cardinality growth.
4. Keep it only when benefits persist and the failure plan is affordable.
5. Remove redundant levels whose hit contribution or guarantee is unclear.

**Invariant or deciding condition:** Every retained level has a named owner, measurable objective, bounded state, safe key, freshness rule, invalidation/recovery path, and observable outcome.

**Small example:** A browser already caches a versioned public bundle and the CDN has a 99 percent byte hit ratio. Adding a load-balancer cache for the same bundle may save little while creating another purge target.

**Trade-off:** Fewer levels are simpler and fresher; more levels can protect expensive origins and reduce tail latency when each serves a distinct need.

**Failure/observability:** High cache hit ratio can coexist with higher latency if serialization/lookup exceeds the source cost. Compare end-to-end latency and downstream work, not hit ratio alone; track unused warmed bytes and per-level unique contribution.

**When not to use it:** Do not cache low-reuse, cheap, highly volatile, security-sensitive, or already-optimized results merely because a component has RAM or disk.

**Interview requirement changes:** Traffic or distance growth can justify another level; tighter freshness can require removing one; an origin with little headroom may justify request collapsing or stale-on-error; a cost cap may prefer CDN bytes while rejecting an expensive application cache.

## Worked example and calculations

### Assumptions

- Clients request one public `200 KiB` image at `10,000 requests/s`.
- Browser usable hit ratio is `60%` of all logical image requests.
- CDN usable hit ratio is `95%` of requests that reach it.
- Simplified mean latency is `3 ms` for a browser hit, `25 ms` for a CDN hit, and `220 ms` for a path that reaches the origin.
- Each request selects the same safe representation; misses are independent; there is enough cache capacity; and origin responses are cacheable.

### Steps

**1. Requests answered at each level**

Browser hits:

`10,000 x 0.60 = 6,000 requests/s`

Requests reaching the CDN:

`10,000 x (1 - 0.60) = 4,000 requests/s`

CDN hits:

`4,000 x 0.95 = 3,800 requests/s`

Origin requests:

`4,000 x (1 - 0.95) = 200 requests/s`

As fractions of all logical requests, the browser answers `60%`, the CDN answers `38%`, and the origin answers `2%`. The deepest-level probability is the product of earlier miss probabilities: `(1 - 0.60) x (1 - 0.95) = 0.02`.

**2. Origin bandwidth**

Without either cache:

`10,000 requests/s x 200 KiB = 2,000,000 KiB/s`

`2,000,000 / 1,024 / 1,024 = 1.907 GiB/s`

With the assumed browser and CDN hits:

`200 origin requests/s x 200 KiB = 40,000 KiB/s = 39.06 MiB/s`

The simplified origin-request and origin-byte reduction is:

`1 - (200 / 10,000) = 98%`

This does not remove CDN-to-user delivery bytes; it removes the repeated origin path for the modeled traffic.

**3. Mean response latency**

`(0.60 x 3 ms) + (0.38 x 25 ms) + (0.02 x 220 ms)`

`= 1.8 + 9.5 + 4.4 = 15.7 ms`

Without caches, the simplified mean would be `220 ms`. A production design must use measured percentiles and conditional distributions rather than treating this weighted mean as a p95 or p99.

**4. Database-counter read/write shift**

Suppose a public profile is read `5,000 times/s`, while users publish `20 posts/s`. Recounting on every read runs `5,000 aggregates/s`. A maintained counter replaces those aggregates with ordinary row reads and adds about `20 counter updates/s`, plus deletes/unpublishes, retries, and reconciliation. This arithmetic does not prove that the aggregate was slow; an execution plan and database measurements decide whether the write amplification is worthwhile.

### Result and sanity check

The origin sees only `2%` of the logical image request rate because two conditional miss probabilities multiply. The result is plausible only if the hit ratios are measured at the defined denominators. Reporting “CDN hit ratio 95%” without saying that browser hits never reached the CDN would hide the end-to-end `98%` origin reduction.

A full browser-cache flush changes the origin calculation less than a full CDN loss: with browser hits gone but CDN still at `95%`, origin QPS becomes `10,000 x 0.05 = 500`; with both caches ineffective it becomes `10,000`, which is `50x` the steady `200`. Capacity planning must cover or deliberately reject that recovery path.

## Deep mechanism

### Components, ownership, and boundaries

| Level | Typical owner | Reuse scope | Authority | Direct invalidation reach | Main proof |
|---|---|---|---|---|---|
| Browser/mobile | User agent or app | One user/device/profile | Usually no | Weak; policy/versioning is more reliable than push | DevTools/cache source, transfer bytes, validators, URL version |
| CDN edge | CDN/provider configuration | Many users whose requests share a safe key | No; origin is upstream | Provider purge/rule API, often asynchronous/distributed | Cache-status header, `Age`, edge ID, origin logs |
| Remote cache | Application/platform team | Application fleet/tenant/key | Usually no | Application delete/update/version event | Cache outcome/latency, key/value version, source fallback |
| Database derived field | Database/application data model | All reads of that row/read model | Derived; base rows remain reconstructive truth | Same transaction, trigger, job, or event consumer | Reconciliation query, transaction result, lock/retry metrics |
| Base database rows | Data-owning service | Authoritative business state | Yes in this model | Normal write/transaction semantics | Commit/version/audit evidence |

Ownership matters during incidents. “Clear the cache” is incomplete until the responder names the level, exact key/URL/tenant/variant, expected next state, origin budget, and proof that the operation propagated.

### Ordering, concurrency, and stale state

**Stale fill race:** Reader R misses remote cache and reads database version 10. Writer W commits version 11 and invalidates. R then fills version 10 after W's invalidation. A delayed old result has recreated staleness. Generation keys, compare-and-set/version checks, short freshness, or an ordered change stream can close or bound this race.

**CDN/browser split:** A URL purge invalidates provider copies, but a browser holding a fresh response can answer locally and never observe the purge. Versioned asset URLs make the new representation a different key; short browser freshness plus validators is another choice when stable URLs matter.

**Counter concurrency:** `total_posts = total_posts + 1` in the database is an atomic row update, but the whole invariant still depends on grouping the base post change and counter update in one transaction. Application read-modify-write (`read 77`, then both writers write `78`) can lose an increment. Idempotency must also prevent a retried publish from applying twice.

**Expiry wave:** Many objects sharing one expiry time can miss together. Per-key request collapsing, TTL jitter, staged warming, and bounded origin concurrency protect the authority; none changes the semantic freshness decision by itself.

### Failure and recovery

| Failure | Observable symptom | Mechanism | Protection/recovery | Remaining risk |
|---|---|---|---|---|
| Unsafe shared key | One user receives another user's data | Tenant/auth/variant omitted or response incorrectly marked shareable | Bypass shared cache; include safe dimensions; test isolation; purge affected keys | Previously exposed data requires security response, not only a cache fix |
| Old browser asset | Some devices retain old UI after CDN purge | Browser answers a still-fresh stable URL | Content-hashed URLs; compatible deployments; short freshness and validators | Offline or long-lived clients can run old versions |
| Repeated CDN miss | Low hit ratio and high origin egress | Uncacheable response, cookie, rule mismatch, key fragmentation, eviction, or multiple edges | Inspect status/headers/rules/key; use explicit safe policy; size/version assets | Provider policy and topology can still vary by plan/location |
| CDN purge storm | Origin QPS and latency jump immediately | Many edge copies become cold simultaneously | Purge exact URLs; rate/stage changes; request collapse; origin limits | First request per cold cache still reaches upstream |
| Remote-cache outage | Cache errors plus database pool saturation | Optional fast path fails and all traffic falls back | Short cache deadline; circuit breaker; per-key coalescing; load shedding/degraded fields | Correct fallback can still be unavailable if origin capacity is insufficient |
| Stale refill | Old value reappears after invalidation | Delayed miss fill races with newer write | Version/generation check; ordered event; delete-after-commit plus race defense | Cross-region ordering may only bound, not eliminate, lag |
| Counter drift | Stored count differs from aggregate | Partial update, omitted transition, duplicate retry, or manual import | One transaction; idempotency; reconciliation and repair | High-contention rows and changing predicates need redesign |
| Capacity eviction | A fresh hot-path entry unexpectedly misses | Cache reclaims memory independently of TTL | Capacity/headroom alarms; admission/eviction tuning; safe miss path | Workload shifts can change the hot set quickly |

### Observability

Observe the same user outcome from every boundary:

- **Response identity:** representation/build/data version, generated time, accepted stale budget, and whether the response was degraded.
- **Browser:** URL fingerprint, DevTools “memory/disk cache” evidence, `transferSize`, validators, service-worker path, and client sync conflicts.
- **CDN:** provider cache status, `Age`, edge/point-of-presence, requests and bytes by hit/miss/revalidated/stale/bypass, cache-key cardinality, purge propagation, and origin-fetch count.
- **Application/remote cache:** lookup outcome, latency, timeout/error, key namespace/version, value age/version, serialization errors, coalesced waiters, evictions, memory, hot keys, and fallback QPS.
- **Database derived state:** base mutation and counter update in one transaction trace, row-lock wait, retry/idempotency result, reconciliation delta, and last repair age.
- **End to end:** user latency/error/stale-version SLO, origin CPU/connection headroom, egress cost, and complaint correlation by URL, user scope, region, app build, and time.

Alert on impact plus mechanism. A lower hit ratio during a planned deploy may be harmless; cache errors combined with origin saturation and user latency are urgent. An excellent hit ratio is dangerous when it is serving the wrong tenant or an unacceptable version.

## Design choices

| Choice | Benefits | Costs/risks | Prefer when | Avoid when |
|---|---|---|---|---|
| Browser cache with content-hashed URL | Avoids all network work; long safe lifetime | Old clients retain old URLs; asset cleanup/version compatibility | Public immutable assets whose changes create new names | Immediately revocable or user-specific data |
| Browser validation on stable URL | Can keep URL stable and transfer only when changed | Still makes a network request; validators and origin/CDN behavior matter | Content changes and stale display must be bounded | Offline use or zero-network latency is the main goal |
| CDN shared cache | Global latency/origin egress/load reduction | Distributed state, key/policy leaks, purge/cold-start risk | Public reusable objects or safely keyed responses | Personalized, low-reuse, or strict-authority reads |
| Remote application cache | Reuse across API instances; controlled keys/invalidation | Network dependency, stampede, memory and topology operations | Expensive high-reuse application reads with bounded staleness | Cheap queries, low reuse, or non-reconstructable data |
| Database derived counter | Cheap reads; can share one database transaction | Write amplification, drift repair, hot-row contention | Read-heavy aggregate with a stable predicate | Write-heavy hot entity or cheap/rare aggregate |
| Multiple cache levels | Different levels can remove distinct network/compute costs | Multiplying keys, stale states, invalidations, and incident paths | Measurements show a separate benefit and each level has ownership | Added level duplicates another's benefit without a unique SLO |
| No cache | Simplest consistency and operations | Higher repeated latency/load/egress | Source meets SLO/cost and reuse is insufficient | Origin cannot meet measured demand or distance budget |

## Misconceptions

| Claim/confusion | What is actually true | Evidence or counterexample |
|---|---|---|
| “Redis is the cache.” | Redis is one possible remote-cache implementation; browsers, CDNs, processes, proxies, and stored derived data can all avoid repeated work. | A browser hit returns an asset without contacting Redis or any backend. |
| “The nearest CDN is always geographically closest.” | Routing considers network paths, capacity, reliability, and traffic engineering; geographic minimum is not guaranteed. | A nearby city can have a worse BGP path or lack available capacity. |
| “Browsers automatically cache every image.” | Storage and reuse depend on HTTP semantics, response headers/status, validators, browser policy, reload mode, and capacity. | `Cache-Control: no-store` forbids storage by compliant caches. |
| “A fresh response must equal the database now.” | Fresh means the cache may reuse it without validation under its policy; the origin may have changed since admission. | Origin v2 can exist while v1 remains within a 300-second freshness lifetime. |
| “`no-cache` means do not store.” | In HTTP semantics, `no-cache` generally requires validation before reuse; `no-store` is the storage prohibition. | A stored response can validate with `ETag` and receive `304 Not Modified`. |
| “Expiry, purge, invalidation, and eviction are the same.” | Expiry is time/freshness, purge is an explicit provider operation, invalidation is a semantic unusability action, and eviction is capacity-driven removal. | A fresh object can be evicted; an expired object can remain stored but require validation. |
| “Every remote-cache key needs TTL or memory leaks.” | A TTL is an excellent default for derived data, but bounded memory also depends on admission/eviction, and some managed entries intentionally persist. | A cache can evict a fresh key under pressure; a permanent coordination key may need another lifecycle. |
| “Remote cache means one centralized machine.” | It means applications cross a network boundary to a logically shared service; that service can be replicated and sharded. | One key may route to a shard with replicas while clients see one logical cache. |
| “The database counter is automatically correct.” | It is a second representation whose invariant requires transactions, idempotency, all inverse transitions, and reconciliation. | Retrying a publish without an idempotency guard can increment twice. |
| “Purging the CDN refreshes every user.” | A browser or service worker may answer before contacting the CDN. | A fresh stable URL remains usable locally after an edge-only purge. |
| “More cache levels always make the system faster.” | Each lookup has a cost and each miss continues downstream; low-benefit levels can add latency and operations. | A remote lookup slower than an indexed local database read makes hits unhelpful. |
| “Fresh data can never be cached.” | Exact-authority requirements can make caching unattractive, but validation, versions, write-maintained read models, and bounded staleness are design options. | A transactionally maintained counter is cached/derived yet visible atomically with the base write in one database. |

## Real backend connection

Consider a Python/FastAPI service backed by PostgreSQL and a remote cache, with public assets behind a CDN:

| Endpoint/resource | Reasonable starting policy | Why |
|---|---|---|
| `/assets/app.<hash>.js` | Browser + CDN, long freshness, immutable name | Changed bytes get a new key; highest reuse and low privacy risk |
| `/avatars/<content-hash>.jpg` | Browser + CDN; exact-URL purge only for exceptional rollback | Content version is visible in the URL and safe to share when public |
| `/profiles/{id}` public summary | Remote cache; CDN only if explicitly public and safely keyed | Repeated database/join work may be avoided, but visibility and update lag must be defined |
| `/me` | Private/no shared cache; perhaps a short user-scoped client policy | Authorization makes shared reuse dangerous unless proven otherwise |
| `/accounts/{id}/balance` | Authoritative path or rigorously coordinated read model; often `no-store` at HTTP clients | Incorrect recency can create a high-impact user-visible contradiction |
| `users.total_posts` | Maintain with post publish/unpublish in one PostgreSQL transaction | Turns repeated aggregate reads into a cheap column read |

Example transaction shape:

~~~sql
BEGIN;
INSERT INTO posts (id, user_id, status, body)
VALUES (:post_id, :user_id, 'published', :body);

UPDATE users
SET total_posts = total_posts + 1
WHERE id = :user_id;
COMMIT;
~~~

The SQL is only a mechanism sketch. Production code must make `:post_id` idempotent, ensure exactly one user row changed, handle unpublish/delete, decide whether drafts count, retry serialization/deadlock failures safely, and reconcile the counter. PostgreSQL documents that a transaction groups steps into an all-or-nothing operation: [PostgreSQL transaction tutorial](https://www.postgresql.org/docs/18/tutorial-transactions.html).

For the remote-cache path, put tenant/user/representation version in the key, enforce a short cache timeout, and cap database fallback. Returning correct database data when Redis is down is not an availability plan if the fallback traffic exhausts PostgreSQL.

## Instructor-assigned tasks

| Task | Faithful purpose | Tools | Reference verified? | Learner status |
|---|---|---|---|---|
| [`SD-BEG-130-T01`](tasks/SD-BEG-130-T01/README.md) | Explore provider documentation/examples, configure a simple CDN, cache one image, and retrieve it through the CDN URL | Browser, Cloudflare or Akamai account, disposable origin/domain, HTTP inspection; optional local Python companion | Local cache-mechanism model passed; real provider setup remains learner-owned and pending | Not started |

The supplied reference does not create an account, change DNS, expose an origin, or claim that Rahul completed the provider exercise. The task pack separates those external actions from a safe deterministic local model.

### Codex-added practice

These are not course homework:

1. **Predict:** An image has browser `max-age=3600` and CDN `s-maxage=300`. The CDN is purged after an origin update. Which existing clients can still see old bytes, and why?
2. **Draw:** Recreate browser → CDN → origin, then mark the cache key, first miss, second hit, expiry, exact-URL purge, and the boundary a purge cannot cross.
3. **Calculate:** At `20,000 requests/s`, browser hits `50%` and CDN hits `98%` of arrivals. Calculate CDN QPS, origin QPS, and origin amplification if both levels become cold.
4. **Explain:** Defend either a stored `total_posts` counter or an aggregate-on-read design for `4,000 profile reads/s` and `200 post mutations/s`.
5. **Change:** Tighten an avatar freshness SLO from one hour to five seconds. Decide whether to use stable URLs plus revalidation/purge or content-versioned URLs, and state the failure evidence.

## Useful English and technical phrases

### Stale

- Pronunciation: `stayl`
- Simple meaning: old enough that it may no longer satisfy the requirement.
- Hindi cue: `purana ho chuka data`
- Why it matters here: every level may hold a different version, and “old” is acceptable only inside a declared budget.
- Common misuse: do not call every older value stale; a cached value can be older than the source yet still allowed by the product's freshness policy.

Examples:

1. Simple: “This bread has gone stale.”
2. Engineering: “The browser served a stale avatar from a stable URL.”
3. Engineering: “Reject the cache entry when its version is stale relative to the required generation.”
4. Interview: “I would first ask how much stale data the product can tolerate.”
5. Professional/design review: “The proposal needs a measurable stale-response SLO and a repair owner.”

### Invalidation

- Pronunciation: `in-val-ih-DAY-shun`
- Simple meaning: making a previously reusable value no longer valid for use.
- Hindi cue: `purani copy ko invalid karna`
- Why it matters here: source writes must stop affected cache copies from serving outside the freshness contract.
- Common misuse: updating an entry and deleting it can both be reactions to a change, but invalidation specifically describes making the old representation unusable; refresh/replacement is more precise for writing the new one.

Examples:

1. Simple: “The rule change caused invalidation of the old pass.”
2. Engineering: “Commit the profile update before publishing its cache invalidation.”
3. Engineering: “URL versioning avoids depending on browser invalidation for immutable assets.”
4. Interview: “My invalidation plan is idempotent and carries the source version.”
5. Professional/design review: “We need evidence for invalidation propagation across every region, not only a successful API response.”

### Origin server

- Pronunciation: `OR-ih-jin SUR-ver`
- Simple meaning: the upstream system a CDN asks when the edge cannot answer.
- Hindi cue: `asli upstream server`
- Why it matters here: misses, expiry, purges, and edge failures transfer work to this boundary.
- Common misuse: the origin is not automatically a single machine or the database; it can be a load-balanced service or object store.

Examples:

1. Simple: “The parcel returned to its origin.”
2. Engineering: “The first edge miss fetched the image from the origin server.”
3. Engineering: “A full purge increased origin-server requests by forty times.”
4. Interview: “I would capacity-plan the origin server for cold-cache recovery, not only steady misses.”
5. Professional/design review: “Please state the origin ownership, timeout, authentication, and overload behavior.”

## Interview practice

### Foundation

**Question:** Compare client-side caching, a CDN, a remote cache, and a database-held derived counter.

**Strong answer covers:** The work each level skips; private versus shared scope; CDN origin miss/fill; network boundary of a remote cache; the counter invariant; who owns truth; one example each; TTL/invalidation/eviction distinctions; and why more levels increase staleness and operational cost.

**Weak-answer trap:** Listing browser, Cloudflare, Redis, and PostgreSQL without explaining reuse scope, authority, cache key, freshness, miss path, or failure behavior.

### SDE-2 working engineer

**Question:** An avatar was updated successfully. New devices see it, but some existing browsers show the old image for an hour. The CDN dashboard says the URL purge succeeded. Diagnose and fix it.

**Reasoning checkpoints:** Confirm stable versus versioned URL; inspect browser DevTools before assuming CDN; compare response URL, `Cache-Control`, validators, `Age`, provider cache status, edge ID, and origin version; recognize that a browser hit bypasses the CDN; choose content-hashed URLs or a shorter browser freshness/validation policy; keep old API/asset compatibility; test normal reload, hard reload, multiple devices, and post-deploy metrics.

**Follow-up:** The team changes every response to `no-store`, and origin egress triples. Restore caching selectively: immutable versioned public assets first, short validated stable resources second, and keep private/revocable data excluded.

### SDE-3 senior design

**Prompt:** Design caching for a global profile-and-media service serving `100,000 requests/s`, with public images, public counters, private settings, and a five-second avatar update SLO.

**Clarify first:** Public/private field boundaries; request and byte distribution; regional users/origins; p95/p99; maximum stale age per field; read-your-own-write; delete/revocation; authorization; origin capacity; availability during origin failure; data residency; cost; and provider purge SLO.

**Estimation:** Separate logical requests from browser-to-CDN arrivals and CDN-to-origin misses. At `50%` browser hits and `99%` CDN hits of arrivals, origin QPS is `100,000 x 0.50 x 0.01 = 500`. Cold loss of both levels is `200x` that steady origin rate. Estimate bytes independently because image byte-hit ratio matters more than request-hit ratio for egress.

**API and data model:** Use content-versioned image URLs in profile responses; keep private settings on authenticated non-shared endpoints; define `users.total_posts` from an exact published predicate; carry source version/update time; make mutation IDs idempotent.

**High-level design:** Browser and CDN cache versioned public media; a remote cache holds safe public profile read models; PostgreSQL owns users/posts and transactionally maintains the counter when contention permits; updates return the new content URL/version; URL-specific purge handles rollback or stable aliases; bounded fallback and request collapsing protect origins.

**Bottlenecks:** Hot celebrity keys/counter rows, purge fan-out, edge cold starts, origin egress, cache connection limits, serialization, key-cardinality explosion, and regional invalidation lag.

**Reliability and recovery:** Versioned assets make old and new deployments coexist; remote-cache loss degrades optional fields or sheds load before exhausting PostgreSQL; reconciliation repairs counters; origin failure may serve explicitly bounded stale public media but never silently shares private settings.

**Observability:** User-visible representation version/age, browser transfer evidence, CDN outcome/age/edge, purge propagation, origin fetches/bytes/headroom, remote-cache outcomes and hot keys, transaction/counter drift, and freshness-SLO breaches.

**Trade-off:** Stable URLs plus purge offer simple references but depend on distributed invalidation. Content-versioned URLs avoid overwrite races and permit long lifetimes but require metadata updates, compatibility, and old-object cleanup. Strong immediate private-data consistency may deliberately bypass shared caches.

**Requirement change:** If legal deletion must make an image inaccessible worldwide within five seconds, a long-lived public browser copy cannot satisfy the guarantee. Use authenticated short-lived delivery or encryption/key revocation, minimize local freshness, measure revocation propagation, and state that already-downloaded bytes cannot be remotely erased from an uncontrolled device.

## Course, verified extensions, and uncertainty

### Course model

- `00:00:01-00:00:50`: Redis is common but is not the only cache location; every possible level still needs a “should we?” decision.
- `00:00:50-00:03:31`: caching trades freshness for speed; financial-balance recency illustrates a poor casual-cache candidate; expiry and proactive invalidation are introduced.
- `00:03:31-00:05:41`: browsers/mobile clients can reuse images, JavaScript, user information, and local progress, avoiding the backend request at the cost of device staleness.
- `00:05:40-00:11:47`: a CDN is geographically distributed; a user reaches a nearby edge; the edge returns a hit or lazily fetches from its configured origin, stores the response, and applies an expiry.
- `00:09:49-00:11:38`: the India/Mumbai edge and Sydney origin example shows first-request origin travel followed by lower-latency regional reuse.
- `00:11:48-00:12:52`: assigned exercise to explore Cloudflare/Akamai material and console behavior, configure a CDN, and learn from implementation examples; slide 47 makes the image-through-CDN-URL output explicit.
- `00:12:50-00:14:06`: a remote Redis cache is shared over the infrastructure network; capacity is smaller than the database and entries need deliberate lifecycle policy.
- `00:14:04-00:16:39`: database caching is illustrated by storing and transactionally incrementing `users.total_posts` instead of recounting posts on every profile read.
- `00:16:37-00:19:02`: load balancers and other components could cache, but caching at every level multiplies staleness and invalidation work; the course closes with “can” versus “should.”

### Verified extensions

- HTTP distinguishes a private cache dedicated to one user from a shared cache serving multiple users. Reuse depends on storage rules, cache keys including `Vary` dimensions, freshness, and validation; `Age` estimates time since origin generation/validation: [RFC 9111 - HTTP Caching](https://www.rfc-editor.org/rfc/rfc9111.html).
- Cloudflare's documented default behavior treats common static extensions such as images as cache candidates, while request method, status, origin directives, cookies, and rules affect the final decision. Its `CF-Cache-Status` and `Age` headers provide evidence rather than a guarantee that two requests must be miss then hit: [default cache behavior](https://developers.cloudflare.com/cache/concepts/default-cache-behavior/) and [cache responses](https://developers.cloudflare.com/cache/concepts/cache-responses/).
- Cloudflare uses anycast/BGP routing, and its support documentation says the selected data center is not necessarily the geographically closest when reliability and traffic engineering intervene. This refines the course's “nearest server” picture: [TCP and anycast connections](https://developers.cloudflare.com/fundamentals/reference/tcp-connections/) and [geographic routing caveat](https://developers.cloudflare.com/support/troubleshooting/general-troubleshooting/geographic-traffic-routing/).
- Cloudflare recommends purging an exact URL instead of clearing everything because a global cold cache can increase origin traffic: [purge guidance](https://developers.cloudflare.com/cache/how-to/purge-cache/purge-everything/).
- Akamai documents that individual edge servers have separate caches, demand can populate a particular edge, and capacity eviction can remove an object before its TTL ends. This separates lazy population, freshness, and retention: [Akamai caching model](https://techdocs.akamai.com/property-mgr/docs/know-caching).
- PostgreSQL transactions make grouped base-row and counter changes all-or-nothing and hide intermediate states from concurrent transactions. That supports the course's same-transaction counter pattern, while idempotency and reconciliation remain application responsibilities: [PostgreSQL transactions](https://www.postgresql.org/docs/18/tutorial-transactions.html).

### Inferences and practical connections

- The best level is the earliest safe reusable boundary, not necessarily the earliest technically possible one.
- Content-addressed or versioned asset URLs convert an invalidation problem into key selection, which is especially useful for browser caches the server cannot reliably purge.
- A remote cache can be logically centralized for clients while physically sharded/replicated; placement and topology are independent design axes.
- The stored post count is better treated as a maintained read model than as a disposable TTL cache because base writes and repair define its correctness.
- Layered origin load is multiplicative in earlier miss probabilities, while invalidation and failure paths are additive operational responsibilities.

### Unresolved source points

- None block learning. Provider account availability, domain/origin prerequisites, current console labels, plan-specific caching behavior, and real edge routing must be observed in Rahul's own task environment rather than inferred from the generic course model.

## Final revision card

### Five facts

1. A browser hit can avoid the complete backend path; a CDN hit avoids the configured origin path; a remote-cache hit avoids application/database work.
2. A CDN miss commonly pulls from an origin and may populate only the edge or cache tier that handled that request.
3. Freshness, validation, invalidation, purge, and capacity eviction answer different lifecycle questions.
4. A database counter is a derived representation whose invariant needs atomic base writes, idempotency, inverse transitions, and reconciliation.
5. Every extra cache level adds a key, stale state, capacity policy, failure path, metric, and operational owner.

### Three decisions

1. Cache at the earliest level whose reuse scope, privacy, and freshness contract make the answer interchangeable for the request.
2. Prefer versioned URLs for immutable public assets; prefer controlled validation/authoritative reads for stable URLs or tightly fresh/private data.
3. Retain a cache level only when measured latency/load/egress savings repay miss, invalidation, security, recovery, and ownership cost.

### One failure

Avatar bytes change at a stable origin URL → CDN URL is purged → some browsers keep a still-fresh local copy → only existing devices show the old image → browser DevTools reveals a local hit while new devices show version 2 → deploy a content-versioned URL or shorten browser freshness and validate, while preserving compatibility.

### Natural 60-second explanation

Use this speaking outline:

1. Caching is reusable work, not just Redis.
2. Browser, CDN, remote cache, and database-derived data skip different downstream costs.
3. The earlier the hit, the more work disappears and the less direct invalidation control the source has.
4. A CDN routes to an edge, uses a key/freshness policy, and pulls from the origin on a miss.
5. A stored counter trades repeated reads for write-path maintenance.
6. Every level needs a safe key, freshness rule, bounded capacity, failure plan, and evidence.
7. Finish with the lecture's rule: cache where measured benefit justifies staleness and invalidation complexity, not everywhere possible.

### Natural 3-5 minute explanation

1. Start with source of truth, derived copy, cache key, usable hit, freshness, invalidation, and eviction.
2. Walk from browser to CDN to API/remote cache and show exactly which request or computation each hit removes.
3. Trace the first CDN miss, origin fill, second hit, origin update, stale-but-fresh reuse, and exact-URL purge/expiry.
4. Explain private versus shared scope and why authorization, tenant, locale, encoding, and query variants belong in the cache decision.
5. Show `total_posts` as a maintained read model and state the equality invariant, transaction, idempotency, delete, contention, and reconciliation requirements.
6. Calculate layered origin QPS by multiplying earlier miss probabilities; separate request hit ratio from byte hit ratio and cold-cache amplification.
7. Diagnose browser staleness, low CDN hits, cache outage, stale refill, purge storm, and counter drift from layer-specific evidence.
8. Close by adapting placement when consistency, latency, availability, privacy, global scale, or cost changes.

See [review.md](review.md) for closed-book retrieval.
