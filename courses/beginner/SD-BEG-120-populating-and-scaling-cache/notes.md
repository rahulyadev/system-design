# SD-BEG-120 - Populating and Scaling a Cache

> **Track:** Beginner<br>
> **Artifact state:** Ready<br>
> **Learning state:** Not started<br>
> **Last updated:** 2026-09-02

## Source and coverage check

- Inspected: the complete transcript, all three slide pages, a full-duration video frame survey, and five-second visual checks across the ending.
- Coverage: complete from 00:00:01.040 through 00:10:34.709; no supplied source gap.
- Visual fidelity: the public diagrams below reconstruct the source ideas in new wording. No slide or video image is copied.
- Unclear source points: the course leaves dual-write atomicity, replica lag, failover, rebalancing, hot-key handling, and exact eviction behavior unspecified. Those boundaries are made explicit below.
- Instructor-task scan: complete; zero tasks. The complete source and ending were checked.

## What I should be able to do

- Trace a lazy cache hit and miss in order and name which store is authoritative.
- Choose lazy fill, eager update, or proactive warming from freshness, reuse, and failure requirements.
- Explain why a TTL bounds residence but does not by itself solve invalidation, eviction, or a cache stampede.
- Quantify hit-path latency, database load, memory, replication cost, and cold-cache amplification.
- Separate vertical scaling, read replicas, and sharding by the bottleneck each one addresses.
- Diagnose stale values, partial dual writes, replica lag, hot keys, shard imbalance, and origin overload from evidence.
- Adapt a cache design when an interviewer changes consistency, latency, availability, scale, or cost.

## Small bridge from earlier ideas

A **cache key** names a reusable result. A lookup is a **hit** only when the entry is present and acceptable for this request; otherwise it is a **miss**. The durable database is normally the **source of truth**, while the cache holds derived copies that may expire or be evicted.

Three database-scaling words reappear here:

- **Vertical scaling:** give one node more CPU, memory, or network capacity.
- **Replication:** copy the same keys to additional nodes, usually for availability and/or read capacity.
- **Sharding:** partition different keys across nodes for aggregate capacity and throughput.

These are bridges, not prerequisites. The cache-specific questions are whether stale data is acceptable, whether a miss path is safe under load, and whether losing a cached copy preserves correctness.

## The 60-second story

The course presents two ways to put data in a cache. With **lazy population**, the API first looks in the cache. A hit returns immediately; a miss reads or computes from the database, stores the result with an expiry, and returns it. This naturally caches only requested data. A joined blog response is the course example.

With **eager population**, the system puts data in the cache before a read miss demands it. The request handling a live score can update the database and cache, or a background decision can warm content expected to become popular, such as recommended video metadata.

When one cache node is no longer enough, first identify the bottleneck. A larger node raises one node's ceiling. Replicas duplicate data and can spread acceptable reads. Shards divide keys and memory across primaries; each shard can also have replicas. None of these choices automatically solves stale values, partial writes, hot keys, cache outages, or origin overload.

## Why the terms matter

| Term | Simple meaning | Why it matters here | Common confusion |
|---|---|---|---|
| Lazy population | Fill only after a request misses | Avoids storing cold data and is the course's default path | Often called cache-aside; it is not the same as a cache product doing read-through automatically |
| Eager population | Put or refresh data before a miss requires it | Reduces first-read latency and can improve freshness | It is an umbrella idea, not one atomic consistency protocol |
| Prewarming | Load predicted hot keys in advance | Helps launches, recommendations, and recovery | Warming everything can overload the source and evict useful keys |
| TTL | A configured time-to-live | Bounds how long an entry may remain usable | TTL expiry is not capacity eviction or source-change invalidation |
| Expiration | A key becomes invalid because its time ended | Controls age and eventual removal | Physical memory reclamation can be implementation-specific |
| Invalidation | Delete or supersede a copy because truth changed | Protects semantic freshness | An invalidation can race with an older in-flight fill |
| Eviction | Remove an entry to reclaim capacity | Keeps bounded memory usable | A valid, popular key can still be evicted under the chosen policy |
| Replica | Another node with a copy of the same key space | Adds failure coverage and sometimes read capacity | A replica may lag; it is not a shard |
| Shard | One owner for a subset of keys | Adds aggregate memory and throughput | One hot key still has one primary owner |
| Hot key | One key receives disproportionate traffic | Can saturate one node despite an even key count | More shards do not split one ordinary key automatically |

## Big picture

**Visual 1 - lazy population**

### Question this visual answers

What exactly happens on a cache-aside hit and miss?

~~~mermaid
sequenceDiagram
    participant U as Client
    participant A as API
    participant C as Cache
    participant D as Authoritative DB

    U->>A: GET blog 42
    A->>C: GET blog:v3:42
    alt usable hit
        C-->>A: cached JSON
        A-->>U: response
    else miss, timeout, or rejected stale value
        A->>D: query blog, author, and tags
        D-->>A: authoritative rows
        A->>C: SET serialized result with policy
        A-->>U: response
    end
~~~

### How to read this visual

Follow the arrows from the client. Every request checks the cache. Only the miss branch performs the expensive database work and attempts a fill. The client can still receive the database result if the optional fill fails.

### Key insight

The correctness path is the authoritative read; the fill is a performance side effect. A cache failure should not silently change the returned data.

### Simplification or limitation

The drawing omits concurrent misses, negative caching, deadlines, authorization in keys, invalidation, transactions, retries, and overload controls. Production code needs explicit policy for each.

**Visual 2 - sharding and replication**

### Question this visual answers

How do key partitioning and replicas combine without confusing their jobs?

~~~mermaid
flowchart LR
    A["API with cluster-aware routing"] -->|"keys in slots owned by S0"| P0["Shard 0 primary"]
    A -->|"keys in slots owned by S1"| P1["Shard 1 primary"]
    A -->|"keys in slots owned by S2"| P2["Shard 2 primary"]
    P0 -. "same keys, asynchronous copy" .-> R0["Shard 0 replica"]
    P1 -. "same keys, asynchronous copy" .-> R1["Shard 1 replica"]
    P2 -. "same keys, asynchronous copy" .-> R2["Shard 2 replica"]
~~~

### How to read this visual

Solid arrows choose one primary owner for a key. Dotted arrows duplicate each shard's keys to its own replica. Moving from one to three primaries partitions capacity; adding replicas duplicates capacity for recovery or selected reads.

### Key insight

Sharding answers “which node owns this key?” Replication answers “which other node has a copy of this owner's keys?” They solve different bottlenecks and can be combined.

### Simplification or limitation

The course is technology-neutral. Real clients must discover ownership changes, handle redirections/retries, tolerate resharding, decide whether replica reads may be stale, and protect multi-key operations. Redis Cluster specifically maps keys through 16,384 hash slots rather than the generic three ranges shown here.

## Core concepts

### 1. Logical cache placement defines the access path

**Simple meaning:** The course draws the cache between the API and database because the API checks the cache before doing expensive database work.

**Formal meaning:** “Between” is a logical dependency order, not necessarily a separate physical network hop. The application, a library, a proxy, or another tier may own the lookup.

**Why it exists:** Without an explicit owner, timeout, fallback, key construction, and observability responsibilities become ambiguous.

**How it works:**

1. The client calls the API.
2. The API derives a safe key from all response-changing inputs.
3. It applies a bounded cache lookup deadline.
4. It either returns a usable hit or follows the authoritative miss path.
5. It records the outcome separately from the final HTTP result.

**Invariant or deciding condition:** Equal cache keys must mean safely interchangeable responses, and cache unavailability must follow a declared fallback or degradation policy.

**Small example:** A FastAPI handler maps tenant 7, blog 42, locale English, and schema version 3 to the key <code>blog:v3:t7:42:en</code>.

**Trade-off:** Application ownership is flexible, but every caller can implement keys, errors, and invalidation differently.

**Failure/observability:** An unbounded cache timeout makes the “fast path” slower than the database. Measure cache attempt latency and outcome, not only endpoint latency.

**When not to use it:** Do not add a remote cache hop when the database query is already cheap, reuse is low, or correctness boundaries are unclear.

**Interview change:** If the cache moves cross-region, network latency and partition probability may erase the intended advantage; prefer a region-local tier or bypass it.

### 2. Lazy population admits data on observed demand

**Simple meaning:** Ask the cache first and fill only after a miss.

**Formal meaning:** Cache-aside is an application-managed lookup/fill pattern. It is “lazy” because demand, not a prior write or forecast, triggers admission.

**Why it exists:** The cache does not need to hold the full database. It spends memory on keys that requests actually use.

**How it works:**

1. Look up the key.
2. On a usable hit, return the cached representation.
3. On a miss, read or compute from the source of truth.
4. Return not-found or the authoritative value as appropriate.
5. Optionally store the result with a freshness and capacity policy.
6. Return the same result even if the fill fails.

**Invariant or deciding condition:** A miss path must be correct without the cache, and a fill must represent the exact version/key contract used by later readers.

**Small example:** The first request for blog 42 joins blogs, authors, and tags and stores the assembled JSON. Later reads reuse that representation.

**Trade-off:** Lazy fill avoids cold keys, but the first read pays the full miss penalty and bursts of simultaneous misses can duplicate work.

**Failure/observability:** Watch miss rate, concurrent fills per key, source QPS, fill errors, cache timeouts, and the latency difference between hit and miss outcomes.

**When not to use it:** It is a weak fit when the first read has a strict latency SLO, the miss computation is unsafe under bursts, or every value must be warm before serving traffic.

**Interview change:** At 100 times more traffic, add request coalescing/single-flight, TTL jitter, admission limits, bounded fallback, and staged warmup.

### 3. TTL bounds age, while invalidation and eviction answer different questions

**Simple meaning:** A TTL says when a key is too old to keep using. Invalidation reacts to a data change. Eviction frees memory.

**Formal meaning:** Expiry is time-based logical invalidity; invalidation is semantic removal or version change; eviction is capacity-driven removal. A product may reclaim physically expired memory lazily or in background work.

**Why it exists:** The course recommends expiry so forgotten entries do not remain indefinitely. Production correctness also needs a maximum acceptable age and a source-change strategy.

**How it works:**

1. Classify the data's allowed staleness.
2. Attach a TTL or an explicit non-TTL lifecycle.
3. On authoritative writes, delete, replace, or version affected keys.
4. Configure a bounded memory limit and eviction policy.
5. Treat any absent/expired/evicted key as a miss.

**Invariant or deciding condition:** No served entry may exceed the application's allowed freshness boundary, regardless of whether it still occupies memory.

**Small example:** Public blog metadata may tolerate 300 seconds; a live score may tolerate only 2 seconds; a permission revocation may require immediate invalidation and must not rely on a long TTL.

**Trade-off:** Short TTLs improve freshness but raise miss traffic. Long TTLs improve hits but enlarge stale windows. Eviction protects capacity but can remove still-useful keys.

**Failure/observability:** Synchronized TTLs cause expiry waves; incorrect invalidation returns stale data; no memory limit may exhaust RAM; a no-eviction policy may reject fills. Track expirations, evictions, rejected writes, memory, key age, and sampled version mismatches.

**When not to use it:** Do not treat TTL as the only revocation mechanism for security-sensitive or strongly consistent data.

**Interview change:** If stale data is forbidden, use commit-aware invalidation/version checks or bypass cache for that read; TTL becomes only a cleanup backstop.

### 4. Eager request-path updates trade miss avoidance for a partial-write problem

**Simple meaning:** When a live score changes, the request updates the durable database and the cached copy so the next reader sees the new score.

**Formal meaning:** The course describes an application-managed dual write within one request. Some systems use “write-through” for a cache layer that coordinates the authoritative write; two independent client calls are not automatically atomic write-through.

**Why it exists:** Waiting for an old score's TTL can produce avoidable stale reads and a miss after expiry.

**How it works:**

1. Validate and authorize the score update.
2. Commit the source-of-truth write.
3. Update or invalidate the matching cache key.
4. Define what to do if step 3 fails.
5. Record a version so readers and repair jobs can detect divergence.

**Invariant or deciding condition:** The cache must never make an uncommitted value look authoritative. The database commit defines truth.

**Small example:** Score version 81 commits in MySQL. The service then writes cache value version 81 or deletes version 80 so the next read refills.

**Trade-off:** Readers get fresher data and fewer misses, but write latency and failure states increase.

**Failure/observability:** Database success plus cache failure leaves an old or absent copy. Cache success plus database failure can expose a value that never committed. Emit operation IDs, database version, cache version, step result, and repair age.

**When not to use it:** Avoid naive dual writes when exposing an uncommitted value is unacceptable or the system cannot reconcile partial success.

**Interview change:** If strong read-after-write is required, route the writer's next read to the database/version-gated path or coordinate the write; do not promise atomicity from two ordinary network calls.

### 5. Proactive warming admits data on predicted demand

**Simple meaning:** Load a key because the system expects many near-future reads.

**Formal meaning:** Prewarming or refresh-ahead is demand prediction plus controlled cache admission before the normal miss path requires the entry.

**Why it exists:** A recommended old video or a popular author's new post can suddenly become hot even though it is not in today's cache.

**How it works:**

1. A trusted signal identifies candidate hot content.
2. A worker fetches the authoritative version.
3. It checks budget, version, and usefulness.
4. It stores the value with TTL and metadata.
5. Reads either hit it or fall back normally.
6. Feedback compares predicted demand with actual hits.

**Invariant or deciding condition:** Expected reuse before expiry or eviction must repay source fetch, cache memory, and displacement cost.

**Small example:** A recommendation batch plans to show video 900 to 500,000 users, so workers warm its metadata in each serving region before the batch activates.

**Trade-off:** It reduces cold latency but can waste bandwidth/memory, evict genuinely hot keys, and amplify source load.

**Failure/observability:** Bad forecasts create warmed-but-never-hit keys. Track warm attempts, warm success, time-to-first-hit, hits per warmed key, bytes admitted, evictions caused, source QPS, and queue lag.

**When not to use it:** Skip warming for uniform one-time scans, low-confidence forecasts, cheap misses, or a source without warmup headroom.

**Interview change:** During disaster recovery, warm the smallest critical working set in controlled waves; never replay the entire key space at once.

### 6. Vertical scaling raises one node's ceiling

**Simple meaning:** Give the cache node more RAM, CPU, or network capacity.

**Formal meaning:** Scale-up increases resources within the same primary failure and ownership boundary.

**Why it exists:** It is operationally simple and often postpones the complexity of a distributed cache.

**How it works:**

1. Identify whether memory, CPU, network, connections, or latency is limiting.
2. Choose a larger instance with explicit headroom.
3. Plan restart/failover and data warmup behavior.
4. Load test the new ceiling and failure path.

**Invariant or deciding condition:** The larger node must address the measured bottleneck and still meet failure-recovery requirements.

**Small example:** A node using 27 GiB of a safe 28 GiB cache budget moves to a class with a 56 GiB safe budget, after accounting for replication and persistence buffers.

**Trade-off:** Simple routing and multi-key behavior remain, but cost can rise nonlinearly and the failure blast radius grows.

**Failure/observability:** A larger node can still saturate network or a single-threaded execution path. Track CPU, memory, allocator fragmentation, bandwidth, connections, command latency, and restart/warm time.

**When not to use it:** Do not scale memory to fix a hot key, bad query, unbounded key cardinality, or miss storm.

**Interview change:** If one-node capacity has a hard ceiling or recovery exceeds the RTO, partition earlier rather than buying only a larger node.

### 7. Replication duplicates data for availability and selected reads

**Simple meaning:** A replica holds copies of the primary's keys and may serve reads if the freshness policy allows.

**Formal meaning:** Replication maintains redundant state across nodes; Redis replication is asynchronous by default, so a replica can lag and an acknowledged write can be absent during a failure window.

**Why it exists:** It provides a promotion candidate after primary failure and may spread read traffic.

**How it works:**

1. Writes go to the primary.
2. The primary sends a replication stream to replicas.
3. Replicas apply updates after some delay.
4. A client or proxy chooses whether reads may use replicas.
5. Failure detection and promotion restore a writable owner.

**Invariant or deciding condition:** A replica read is allowed only when its possible staleness fits the request; failover behavior must fit the loss and availability budget.

**Small example:** A public leaderboard can tolerate a two-second lag and use replicas. A user's immediate score correction reads the primary or uses a version fence.

**Trade-off:** More read/failure capacity costs duplicate memory and operational complexity, and lag weakens read-after-write behavior.

**Failure/observability:** Monitor replication offset/lag, link state, full resynchronizations, promotion time, lost-write window, replica-read latency, and stale-version reports.

**When not to use it:** Do not send strict latest-value reads to an asynchronous replica merely to reduce primary load.

**Interview change:** If the primary fails during a live event, specify whether availability or zero lost cache updates wins; remember the durable database can repair a derived cache.

### 8. Sharding partitions keys for aggregate capacity and throughput

**Simple meaning:** Different cache nodes own different subsets of keys.

**Formal meaning:** A deterministic routing layer maps every key to one primary shard at a time; replicas may duplicate each shard separately.

**Why it exists:** The working set or aggregate operation rate can exceed one node's memory, network, or compute capacity.

**How it works:**

1. Normalize the complete cache key.
2. Hash or range-route it to an ownership unit.
3. Send reads and writes to the current owner.
4. Handle ownership changes and retries safely.
5. Rebalance keys when adding/removing capacity.
6. Add per-shard replicas where availability requires them.

**Invariant or deciding condition:** At a stable point, every key has one unambiguous primary owner; routing changes must not make two divergent copies both look current.

**Small example:** Three primaries own disjoint key groups. In Redis Cluster, keys map to 16,384 hash slots, and each primary owns a subset of slots.

**Trade-off:** Aggregate memory and throughput grow, but multi-key operations, discovery, rebalancing, skew, and failure handling become harder.

**Failure/observability:** Track per-shard QPS, memory, hit/miss rate, latency, errors, slot/key distribution, redirections, reshard progress, and largest/hottest keys.

**When not to use it:** Avoid sharding while one node has safe headroom and distribution complexity would exceed the benefit.

**Interview change:** If one key owns 40% of traffic, adding ordinary shards will not split it. Use request coalescing, read replicas, local copies, key decomposition when semantically safe, or upstream rate shaping.

## Worked example and calculations

### Assumptions

- Read traffic: 10,000 requests/s.
- Usable cache-hit ratio: 95%.
- Hit latency: 1.5 ms end to end.
- Full miss latency: 48 ms, including cache lookup, database work, serialization, and attempted fill.
- Hot set: 20,000 entries.
- Serialized value size: 8 KiB per entry.
- Planning overhead factor: 1.4 for keys, metadata, allocator overhead, and fragmentation. This is an assumption to measure in the real workload.
- Replication factor: 2 total copies, meaning one primary copy and one replica copy.
- Four primary shards with ideal even distribution.

### Steps

1. **Steady database read rate**

   <code>origin QPS = 10,000 x (1 - 0.95) = 500 requests/s</code>

2. **Simplified average latency**

   <code>E[T] = 0.95 x 1.5 ms + 0.05 x 48 ms</code>
   <code>= 1.425 ms + 2.4 ms = 3.825 ms</code>

   This average does not predict p95/p99 during bursts; misses remain about 48 ms.

3. **Cold-cache amplification**

   At 0% hits, the database sees about 10,000 requests/s rather than 500.

   <code>amplification = 10,000 / 500 = 20x</code>

   A “disposable” cache is not operationally disposable if the database cannot absorb that 20x fallback.

4. **Primary working-set memory**

   <code>20,000 x 8 KiB = 160,000 KiB = 156.25 MiB</code>

   Apply the assumed 1.4 overhead factor:

   <code>156.25 MiB x 1.4 = 218.75 MiB</code>

5. **Replication and shard allocation**

   Two total copies require approximately:

   <code>218.75 MiB x 2 = 437.5 MiB fleet-wide</code>

   With four evenly loaded primaries:

   <code>218.75 MiB / 4 = 54.6875 MiB per primary</code>

   Each replica needs roughly the same dataset memory as its primary, plus buffers and process headroom.

6. **Hot-key sanity check**

   If one score key receives 8,000 of the 10,000 requests/s, hashing still maps all ordinary requests for that key to one primary. Four shards do not produce 2,000 requests/s per node for that key.

### Result and sanity check

The cache reduces modeled steady database reads from 10,000 to 500 requests/s and modeled mean latency to 3.825 ms. The 218.75 MiB hot-set estimate is plausible only if the 8 KiB value and 1.4 overhead assumptions are measured. Replication doubles dataset memory, while sharding redistributes primary memory rather than making copies free.

The most important capacity number is the 20x cold-cache amplification. Before launch, compare 10,000 fallback requests/s with measured database headroom and define load shedding or degraded responses.

## Deep mechanism

### Components, ownership, and boundaries

| Component | Owns | Must not silently own |
|---|---|---|
| API | key construction, deadlines, hit/miss decision, fallback, response semantics | durability it cannot provide |
| Database | authoritative committed record | serving full cache-outage traffic unless capacity proves it |
| Cache primary | current derived value for owned keys | truth after a partial dual write |
| Cache replica | asynchronously copied shard state and possible promotion/read role | guaranteed latest reads without a freshness mechanism |
| Warming worker | bounded candidate admission and versioned fill | an unlimited scan of the source |
| Router/client | shard discovery, ownership mapping, redirection/retry behavior | business-level conflict resolution |

### Ordering, concurrency, and stale state

#### Partial dual-write outcomes

| Database result | Cache result | Visible risk | Safe response |
|---|---|---|---|
| Commit succeeds | Update succeeds | Normal bounded staleness elsewhere may remain | Return success; record versions |
| Commit succeeds | Update fails | Old hit or extra miss | Prefer delete/invalidate retry, repair event, or version check |
| Commit fails | Update succeeds | Uncommitted cache value may be served | Never publish cache first without compensation/coordination |
| Commit fails | Update fails | No state change | Return failure with an idempotent retry policy |

#### Stale refill race

1. Reader A misses and reads database version 80.
2. Writer B commits version 81 and deletes the cache key.
3. Reader A resumes and fills version 80 after the deletion.
4. Later readers see stale version 80 until another correction.

The deciding mechanism is ordering, not the mere existence of invalidation. Versioned values, compare-before-set, generation keys, or a coordinated fill policy can prevent an older result from replacing a newer one.

#### Stampede after synchronized expiry

1. A popular key expires.
2. Ten thousand requests observe the same miss.
3. All run the same expensive database computation.
4. The cache recovers, but the database may already be saturated.

Use per-key request coalescing, TTL jitter, stale-while-revalidate where correctness allows, backpressure, and source-capacity limits. A lock needs a bounded lease and failure plan; “add a lock” is not a complete answer.

### Failure and recovery

| Failure | Observable symptom | Mechanism | Protection/recovery | Remaining risk |
|---|---|---|---|---|
| Cache timeout/down | Cache-error rate rises; origin QPS and latency jump | Every attempted hit becomes fallback | Short deadline, circuit breaker, admission/load shedding, degraded response | Correct data may remain unavailable at full traffic |
| Expiry wave | Miss burst at a regular boundary | Many popular keys share one TTL | Jitter, refresh-ahead, coalescing | Traffic can still align around events |
| Partial dual write | Database and cache versions differ | One of two independent writes succeeds | Commit first, invalidate/update, durable repair signal, version audit | Repair lag leaves a stale window |
| Delayed old fill | Stale value appears after a successful invalidation | In-flight reader writes an older version later | Generation/version check, compare-and-set, short TTL | Added metadata and coordination |
| Replica lag | Read-after-write returns an older version | Asynchronous replication has not caught up | Primary read, session stickiness, version fence, bounded-lag policy | Primary load or reduced availability |
| Primary failure | Error spike followed by promotion/reconnect | Detection and failover change ownership | Per-shard replicas, tested client retry budget, rebuild from truth | Acknowledged cache writes may be absent |
| Hot key | One shard saturates while fleet averages look healthy | One key maps to one owner | Coalescing, replicas, local near-cache, safe key split | Staleness/invalidation complexity |
| Shard imbalance | Uneven memory/QPS and eviction rates | Skewed key size or traffic distribution | Measure weighted load, rebalance slots/keys | Moving hot data consumes bandwidth |
| Resharding | Redirections/retries and tail latency rise | Ownership moves while clients have old maps | Cluster-aware client, bounded retries, staged moves | Multi-key work may be restricted |
| Bad warming forecast | Source spike; warmed keys never hit; useful keys evicted | Admission is based on incorrect demand prediction | Budgets, feedback, rate limits, abort switch | Sudden trends remain hard to predict |

### Observability

Measure the request path and the fleet together:

- **Application outcomes:** <code>hit</code>, <code>miss</code>, <code>cache_error</code>, <code>decode_error</code>, <code>stale_rejected</code>, and <code>fill_error</code>, by bounded route/key class and region.
- **Latency:** endpoint and cache lookup/fill/source p50, p95, and p99; never infer tail behavior from one mean.
- **Origin protection:** database QPS, CPU, I/O, pool usage, lock time, query latency, timeouts, and rejected/degraded requests.
- **Memory lifecycle:** used memory, safe maximum, fragmentation, key count, bytes by class, expirations, evictions, rejected writes, and churn.
- **Replication:** link state, offset/lag, resynchronizations, promotion duration, and replica-read stale-version samples.
- **Sharding:** per-shard QPS, bytes, latency, errors, ownership/slot distribution, redirections, retry count, largest keys, and hot-key estimates.
- **Eager paths:** database/cache version mismatch, invalidation lag, repair backlog/age, warming queue lag, warmed-key first-hit time, and hits per warmed byte.

A useful alert ties cause to impact: “cache errors above 5% and database pool above 80% for five minutes” is more actionable than “hit ratio fell.”

## Design choices

| Choice | Benefits | Costs/risks | Prefer when | Avoid when |
|---|---|---|---|---|
| Lazy cache-aside | Admits requested keys; simple durable authority | Cold miss, stampede, application logic | Reuse is skewed and first miss is affordable | Miss bursts can break the source |
| Commit then invalidate | Avoids publishing uncommitted cache data | Next read misses; invalidation can fail/race | Correctness matters more than one extra miss | Miss cost is impossible to absorb without protection |
| Commit then update cache | Fresher next read | Partial write and ordering risks | Versioned repair is available and read freshness matters | Independent writes are being described as atomic |
| Proactive warming | Avoids predictable cold misses | Forecast waste and origin load | Demand is known before reads | Forecast confidence or warm budget is low |
| Longer TTL | Higher hit rate, fewer source reads | Wider stale window | Data changes slowly and staleness is acceptable | Revocation/latest-value requirements |
| Larger node | Lowest distribution complexity | Ceiling, blast radius, nonlinear cost | One node still has an economical safe size | Hot key or unbounded cardinality is the real problem |
| Read replicas | Failure copy and possible read scale | Duplicate memory, lag, failover complexity | Replica staleness is acceptable or reads can be fenced | Every read requires latest committed value |
| Sharding | Aggregate memory and throughput | Routing, resharding, multi-key, skew | Working set/throughput exceeds one node | A single node has ample measured headroom |

## Misconceptions

| Claim/confusion | What is actually true | Evidence or counterexample |
|---|---|---|
| “Every cache entry must always have a TTL.” | A TTL is a strong default for derived entries, but explicit invalidation plus a bounded eviction policy can be valid. The lifecycle must be deliberate. | Redis can enforce <code>maxmemory</code> eviction policies; keys without TTL are not automatically a language-level memory leak. |
| “After five minutes the bytes are deleted at that exact instant.” | The key is logically expired; physical deletion details depend on the cache. | Redis uses passive and active expiry mechanisms, so reclamation is not one global timer callback. |
| “Two writes in one HTTP request are atomic.” | Network proximity does not create one transaction across independent systems. | Database commit can succeed while cache update fails, or vice versa. |
| “Eager population means only dual writes.” | It also includes prewarming or refresh-ahead based on expected demand. | The course's recommendation and popular-author examples fill before a miss without the original write doing both operations. |
| “Replicas always return the latest value.” | Asynchronous replicas can lag. | A primary may acknowledge before a replica applies the update. |
| “Three shards split every key's load three ways.” | Ordinary key routing selects one primary owner. | An 8,000 RPS score key remains hot on its owner. |
| “Sharding scales only writes.” | It also partitions memory and can increase aggregate read throughput across many keys. | Each primary owns a different key subset. |
| “A cache is just a faster database.” | This is a useful source analogy about scaling tools, not a complete role or guarantee. | Durability, authority, consistency, eviction, latency, and failure semantics differ by design. |
| “Cache loss is harmless because data is in the database.” | Durability may be safe while availability fails. | The worked example sends 20 times more reads to the database during a cold-cache event. |

## Real backend connection

Consider a Python/FastAPI blog-detail endpoint backed by PostgreSQL and Redis. This is a Codex-added practical connection, not a claim about Rahul's experience.

~~~text
GET /blogs/42
  derive blog:v3:tenant-7:42:en
  attempt Redis GET with a short deadline
  if value is present, decodes, and satisfies version/freshness:
      return it and record hit
  otherwise:
      query PostgreSQL and assemble blog + author + tags
      try Redis SET with TTL and jitter
      return the PostgreSQL-derived value even if SET fails
~~~

For <code>PATCH /blogs/42</code>, commit PostgreSQL first. Then invalidate or version-update the cache. A durable outbox/CDC repair path becomes justified only when a missed invalidation has enough business impact to repay its complexity. During deployment, version the key when the serialized representation changes.

Test at least these cases: hit, ordinary miss, not-found policy, cache timeout, malformed value, fill failure, concurrent miss, update/miss race, full cache outage, replica lag, hot key, and cold restart. Use synthetic data and an isolated cache, never an existing shared service.

## Instructor-assigned tasks

> No instructor-assigned task found in the supplied source. The complete source and ending were scanned; see [source_manifest.json](source_manifest.json).

### Codex-added practice

1. **Predict:** At 20,000 requests/s and 98% hits, calculate steady database QPS and full-cache-loss amplification.
2. **Draw:** Recreate the cache-aside hit/miss sequence and mark the authoritative boundary.
3. **Explain:** Say why a database success plus cache failure is different from a cache success plus database failure.
4. **Change:** Assume replica reads may be five seconds stale. Name which endpoints can use them and which need primary/version-fenced reads.
5. **Diagnose:** Fleet hit ratio is 96%, but one shard is at 100% CPU. List the per-key and per-shard evidence needed before scaling.

Do these on paper or in <code>ATTEMPT.md</code> only if Rahul creates one later. They are not course homework and no reference solution is included.

## Useful English and technical phrases

### Proactively

- Pronunciation: pro-AK-tiv-lee
- Simple meaning: acting before the expected need or problem arrives.
- Hindi cue: pehle se taiyaari karna
- Why it matters here: prewarming fills likely hot content before its first miss.
- Common misuse: it does not mean “do everything early”; the action still needs a signal and budget.

Examples:

1. Simple: “We proactively carried water because the day would be hot.”
2. Engineering: “The worker proactively warms metadata for scheduled recommendations.”
3. Engineering: “We do not proactively cache every search result because most are never reused.”
4. Interview: “I would proactively warm only the critical working set and rate-limit origin reads.”
5. Professional/design review: “The proposal needs a measurable trigger before we proactively admit these keys.”

### Stale

- Pronunciation: stayl
- Simple meaning: no longer current enough for the need.
- Hindi cue: purana ya outdated
- Why it matters here: a present cache entry can be unusable because the database has a newer value.
- Common misuse: stale is requirement-dependent; an older value is not automatically unacceptable.

Examples:

1. Simple: “The timetable on the wall is stale.”
2. Engineering: “A two-second-old score is stale for this live endpoint.”
3. Engineering: “The replica returned a stale version during replication lag.”
4. Interview: “I will first clarify the maximum acceptable stale window.”
5. Professional/design review: “We need a sampled version audit to detect stale cache responses.”

### Mutually exclusive

- Pronunciation: MYOO-choo-uh-lee ik-SKLOO-siv
- Simple meaning: two categories do not overlap.
- Hindi cue: ek saath dono mein nahin
- Why it matters here: primary shards should own disjoint key subsets at a stable point.
- Common misuse: replicas are not mutually exclusive with their primary because they intentionally duplicate its keys.

Examples:

1. Simple: “For this ticket, the adult and child categories are mutually exclusive.”
2. Engineering: “The three primary shards own mutually exclusive key subsets.”
3. Engineering: “Primary and replica data are not mutually exclusive; they overlap by design.”
4. Interview: “I would verify that stable primary ownership is mutually exclusive before routing traffic.”
5. Professional/design review: “The diagram should separate mutually exclusive shard ownership from replicated copies.”

## Interview practice

### Foundation

**Question:** Compare lazy and eager cache population using one read and one write example.

**Strong answer covers:** Lazy population checks the cache and fills after a miss; eager population updates or warms before a miss. It names the database as source of truth, gives blog and live-score examples, distinguishes TTL from invalidation, and mentions partial-write risk.

**Weak-answer trap:** “Lazy is slow, eager is fast.” Speed depends on hit ratio, miss cost, write frequency, freshness, prediction accuracy, and failures.

### SDE-2 working engineer

**Question:** A FastAPI blog endpoint uses PostgreSQL and Redis. After an edit, some users see the old post for five minutes. Diagnose and repair it.

**Reasoning checkpoints:** Confirm the freshness requirement; inspect response/cache/database versions; separate replica lag from missed invalidation and stale refill; trace write ordering; verify TTL and key version; choose commit-then-invalidate/update; add race protection, bounded fallback, and metrics; test concurrent edit/read ordering.

**Follow-up:** The cache now fails and PostgreSQL connections saturate. Use a short cache deadline, circuit breaker, coalescing, load shedding/degraded fields, and staged warmup based on measured origin headroom.

### SDE-3 senior design

**Prompt:** Design cached live-score reads for 100,000 requests/s across three regions, with an update every few seconds.

**Clarify first:** Required stale window; regional read/write split; payload and hot-key distribution; p95/p99 target; authoritative store; update ordering; database capacity; cache RTO/RPO; failover; cost; whether viewers can see slightly old data.

**Estimation:** At 99.5% hits, steady origin reads are <code>100,000 x 0.005 = 500 requests/s</code>. Total cache loss produces up to 100,000 requests/s, a 200x amplification. One globally hot score key can dominate a shard.

**API/data model:** Version each match state; include match ID and representation version in the key; define update ID/idempotency; carry source version and generated timestamp in the value.

**High-level design:** Commit authoritative state, publish a durable change signal if justified, update/invalidate regional caches, coalesce per-key misses, use short bounded deadlines, and decide whether replicas/local near-caches may serve within the stale budget.

**Bottlenecks:** Hot-key CPU/network, fan-out of updates, cache connection limits, origin read amplification, regional lag, serialization, and resharding.

**Reliability:** Degrade to less detail or a slightly older explicitly timestamped score; cap origin concurrency; test primary loss, regional cache loss, delayed events, and cold recovery.

**Observability:** Per-version age, cache outcomes, per-key/shard load, propagation lag, partial-write/repair age, database headroom, degraded responses, and user-visible stale incidents.

**Trade-off:** Direct eager updates give low latency but couple the write path to caches. Event-driven repair reduces request coupling but adds queue lag and duplicate/out-of-order handling.

**Requirement change:** If every read must reflect the latest committed update, replica/near-cache reads without version fencing are invalid; stronger coordination or an authoritative read path may cost latency and availability.

## Course, verified extensions, and uncertainty

### Course model

- 00:00:01-00:00:46: the cache sits logically between API and database.
- 00:00:45-00:03:43: lazy population checks cache, fetches/constructs on miss, stores with expiry, and reuses a precomputed blog response.
- 00:03:42-00:05:51: eager request-path writes update database and cache for live scores.
- 00:05:49-00:08:31: proactive warming uses expected popularity, including popular-author and recommended-video examples.
- 00:08:33-00:10:27: caches scale vertically, through replicas, and through sharding; each shard may have replicas.
- 00:10:24-00:10:34: closing remarks; no assignment or homework.

### Verified extensions

- Redis sets key expiration with <code>EXPIRE</code> and uses passive plus active mechanisms to remove expired keys. This refines the course's “automatically deleted at five minutes” mental model: [Redis EXPIRE documentation](https://redis.io/docs/latest/commands/expire/).
- Redis can enforce a <code>maxmemory</code> limit with configurable eviction policies, so expiry and capacity eviction are separate controls: [Redis key eviction documentation](https://redis.io/docs/latest/develop/reference/eviction/).
- Redis replication is asynchronous by default; replicas can lag, and there is a failure window in which an acknowledged write is not on the promoted replica: [Redis replication documentation](https://redis.io/docs/latest/operate/oss_and_stack/management/replication/).
- Redis Cluster maps keys to 16,384 hash slots, assigns slot subsets to primaries, and can attach replicas per shard. It does not promise strong consistency: [Redis Cluster scaling guide](https://redis.io/docs/latest/operate/oss_and_stack/management/scaling/) and [Redis Cluster specification](https://redis.io/docs/latest/operate/oss_and_stack/reference/cluster-spec/).

### Inferences and practical connections

- The course's direct eager update is best treated as a partial-write workflow unless a specific coordination mechanism proves stronger guarantees.
- The recommendation example naturally extends to a budgeted regional prewarming worker with feedback on prediction usefulness.
- The scaling examples imply a bottleneck-first sequence: measure, scale up while safe, add replicas for allowed reads/failure coverage, and shard when aggregate capacity requires it. This is guidance, not a universal mandatory order.

### Unresolved source points

- None that block learning. Product-specific write coordination, read consistency, failover, and sharding semantics must be selected from actual requirements rather than inferred from the generic course diagram.

## Final revision card

### Five facts

1. Lazy population admits an entry only after observed demand misses.
2. Eager population includes both request-path update and proactive warming.
3. TTL, invalidation, and eviction remove or reject entries for different reasons.
4. Replication duplicates a shard; sharding partitions different keys across primaries.
5. Cache loss can preserve durable data while causing a large availability/capacity incident.

### Three decisions

1. Choose lazy fill when misses are affordable and demand should select the hot set; add stampede protection at scale.
2. Choose eager update/warming when freshness or predictable first-read latency repays partial-write and admission complexity.
3. Choose scale-up, replicas, or shards only after identifying memory, read, write, hot-key, network, or recovery pressure.

### One failure

Cache key expires → thousands of requests miss together → duplicate database work saturates the pool → cache fills arrive too late → observe miss concurrency and origin saturation → coalesce per key, jitter TTLs, bound fallback, and degrade when the source budget is exhausted.

### Natural 60-second explanation

Use this speaking outline:

1. Cache population decides when a derived copy enters the fast path.
2. Lazy cache-aside fills only on a miss; a blog join is a good example.
3. Eager paths update during a write or prewarm predicted hot content.
4. The database normally remains authoritative, so two independent writes need partial-failure handling.
5. TTL limits age, eviction protects memory, and invalidation reacts to changes.
6. A bigger node, replicas, and shards solve different bottlenecks.
7. Mention one failure—stampede, stale dual write, replica lag, or hot key—and the evidence/protection.

### Natural 3-5 minute explanation

Expand the same flow:

1. Clarify reuse, freshness, first-read latency, database headroom, and authority.
2. Draw the lazy hit/miss path and state the hit/key invariant.
3. Compare live-score eager update with recommendation-driven prewarming.
4. Walk through both partial dual-write failures and the stale-refill race.
5. Calculate steady origin QPS, cold-cache amplification, and memory including replication.
6. Separate vertical scaling, replicas, and shards; then test a single hot key against the design.
7. Cover timeout, expiry wave, replica lag, primary failure, resharding, and staged recovery.
8. Finish with application outcomes, per-shard metrics, origin headroom, version lag, and the alternative of not caching.

See [review.md](review.md) for closed-book retrieval.
