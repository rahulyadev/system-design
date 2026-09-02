# Quick review - SD-BEG-120 Populating and Scaling a Cache

> Answer before opening [notes.md](notes.md). Keep this review usable in 10-20 minutes. The artifact is ready; Rahul's learning state remains **Not started** until he studies and demonstrates recall.

## Closed-book recall

1. Trace a lazy cache hit and miss in exact order. Which operation is optional for correctness?
2. Why does lazy population tend to admit only demanded data?
3. Use the blog-detail example to explain precomputation.
4. What three different questions do TTL/expiry, invalidation, and eviction answer?
5. Why is “every entry must have a TTL” useful course advice but not a universal invariant?
6. Name the two eager-population forms taught in the course.
7. Walk through both partial outcomes of an application writing database and cache.
8. Why can commit-then-delete still lose to an older in-flight fill?
9. When does proactive warming repay its cost? What metric exposes bad forecasts?
10. Separate vertical scaling, replication, and sharding by bottleneck.
11. Why can an asynchronous replica return an older value?
12. Why does adding shards not solve one hot score key?
13. At 10,000 requests/s and 95% hits, calculate database QPS and full-outage amplification.
14. Calculate primary and replicated memory for 20,000 entries, 8 KiB each, and a 1.4 overhead factor.
15. Which signals distinguish low hit ratio, cache slowness, shard skew, and origin overload?
16. Give two workloads where adding a cache or eager warming is the wrong choice.

## Draw from memory

### Lazy population

- Components/states: client, API, cache, authoritative database; usable hit, miss/error/stale rejection, fill.
- Arrows/order: request → cache lookup → hit response **or** source read/compute → optional fill → response.
- Failure boundary: the source result remains correct when fill fails; fallback must still respect the source capacity budget.
- Invariant: equal keys imply safely interchangeable answers, and every served hit satisfies freshness/version policy.

### Shards with replicas

- Components/states: cluster-aware router, three primary owners, one replica per owner.
- Arrows/order: one key routes to one primary; the primary's key subset is copied to its own replica.
- Failure boundary: a stale route needs bounded redirection/retry; an asynchronous replica may lag.
- Key fact: shards partition; replicas duplicate.

### Ordering race

- Reader misses and reads version 80.
- Writer commits version 81 and invalidates.
- Reader later fills version 80.
- Mark where a generation/version check must reject the old fill.

Then compare with [Big picture](notes.md#big-picture) and [Ordering, concurrency, and stale state](notes.md#ordering-concurrency-and-stale-state).

## Instructor-task recall

No instructor task. The complete transcript, all slide pages, a full video survey, and the ending were checked; the manifest records zero tasks.

Do not turn the Codex-added drills into course homework. Instead, without notes:

- calculate database QPS at 20,000 requests/s and 98% hits;
- calculate the amplification at zero hits;
- explain which endpoints may use a replica that can be five seconds stale;
- diagnose 96% fleet hit ratio with one shard at 100% CPU.

## Answer cues

- One-minute model: [The 60-second story](notes.md#the-60-second-story)
- Vocabulary boundaries: [Why the terms matter](notes.md#why-the-terms-matter)
- Hit/miss order: [Core concept 2](notes.md#2-lazy-population-admits-data-on-observed-demand)
- TTL versus invalidation/eviction: [Core concept 3](notes.md#3-ttl-bounds-age-while-invalidation-and-eviction-answer-different-questions)
- Dual writes: [Core concept 4](notes.md#4-eager-request-path-updates-trade-miss-avoidance-for-a-partial-write-problem)
- Prewarming: [Core concept 5](notes.md#5-proactive-warming-admits-data-on-predicted-demand)
- Scale-up, replicas, shards: [Core concepts 6-8](notes.md#6-vertical-scaling-raises-one-nodes-ceiling)
- Numbers: [Worked example](notes.md#worked-example-and-calculations)
- Races and incidents: [Deep mechanism](notes.md#deep-mechanism)
- Decision matrix: [Design choices](notes.md#design-choices)
- Interview ladder: [Interview practice](notes.md#interview-practice)

## Two-minute teach-back

1. **Problem:** repeated expensive reads need a reusable, bounded fast path.
2. **Authority:** database owns committed truth; cache owns derived copies.
3. **Lazy:** lookup, hit return, or miss → source → optional fill → return.
4. **Eager:** update after a source write or warm from a forecast before reads.
5. **Lifecycle:** freshness/TTL, invalidation, and capacity eviction are distinct.
6. **Correctness:** keys and versions define safe reuse; dual writes and delayed fills can diverge.
7. **Numbers:** hit ratio reduces origin QPS, but cold-cache amplification sets the failure budget.
8. **Scale:** larger node raises one ceiling; replicas duplicate; shards partition.
9. **Failure:** stampede, stale value, replica lag, hot key, or resharding.
10. **Evidence:** cache outcomes/latency, origin headroom, memory lifecycle, versions, lag, and per-shard/key load.

## Interview follow-ups

### Foundation

1. Is proactive warming always eager population? Is every eager update warming?
2. Why is a cache entry's presence insufficient to call it a usable hit?
3. When would a blog cache intentionally use a long TTL and event invalidation?
4. Explain why a cache can be logically between API and database while physically elsewhere.

### SDE-2

5. Database version is 81 and cache version is 80 after a successful API response. Which logs and metrics reconstruct the write?
6. Cache p99 is unchanged but database QPS triples. Give likely causes and tests.
7. A key expires and 5,000 requests recompute it. Compare coalescing, TTL jitter, and stale-while-revalidate.
8. How would you deploy a serialization version change without serving incompatible cached JSON?
9. A replica read returns an old score. Choose primary reads, version fencing, or accepted staleness from requirements.
10. How do you test cache outage and cold restart without touching a shared Redis/database?

### SDE-3

11. At 100,000 requests/s and 99.5% hits, what database QPS remains? What is the failure amplification?
12. Design origin protection when the database can handle only 2x steady miss traffic.
13. A single match key gets 80% of regional traffic. Which mitigations preserve acceptable freshness?
14. Define a regional warming budget and the feedback that disables a bad forecast.
15. During resharding, which ownership, redirect, retry, and multi-key risks must the client handle?
16. When should the “derived disposable cache” assumption be rejected because Redis now owns non-reconstructable state?
17. What changes if every read must reflect the latest committed write?

## Flashcards

| Front | Back | Type |
|---|---|---|
| Lazy population trigger? | An observed miss triggers the source read and optional fill. | mechanism |
| Eager population forms in the course? | Request-path database/cache update and proactive predicted-demand warming. | comparison |
| Cache-aside correctness boundary? | The source result is authoritative; fill may fail without changing that result. | invariant |
| TTL? | Time-based usable lifetime/residence policy, not source-change invalidation or capacity eviction. | definition |
| Invalidation? | Removal/replacement/versioning because authoritative meaning changed. | correctness |
| Eviction? | Capacity-driven removal according to policy. | capacity |
| Dangerous dual-write order? | Publishing cache before the database commits can expose an uncommitted value. | failure |
| Stale-refill race? | An older in-flight miss fills after a newer write invalidates. | concurrency |
| Good warming condition? | Expected reuse before expiry/eviction repays fetch, memory, and displacement cost. | decision |
| Bad warming metric? | Warmed keys/bytes with no later hits, plus induced source load and eviction. | observability |
| Vertical scaling? | More resources inside one node/failure boundary. | scale |
| Replica? | A copy of one primary/shard's keys; it may lag. | scale |
| Shard? | One primary owner for a subset of keys. | scale |
| Redis Cluster ownership unit? | One of 16,384 hash slots assigned to a primary. | verified extension |
| Hot-key trap? | More ordinary shards do not split one key's requests. | failure |
| Origin QPS formula? | request QPS x (1 - usable hit ratio), in the simplified read model. | estimate |
| Outage amplification? | full fallback QPS divided by steady origin QPS. | failure |
| Replication memory cost? | Approximately one full dataset copy per replica, plus operational headroom. | capacity |
| Useful cache alert? | Cache failure plus user/origin pressure, not hit ratio alone. | observability |
| When not to cache? | Low reuse, cheap source, unclear freshness/security, or unjustified complexity. | decision |

## English speaking check

- Use “proactively” in a sentence that includes a measurable trigger and budget.
- Explain “stale” without claiming every older value is unacceptable.
- Contrast “mutually exclusive” primary shard ownership with overlapping replica data.
- Correct this weak phrase: “We write to Redis and MySQL at the same time, so it is consistent.”
- Improve this design-review sentence: “We will add more cache shards if traffic grows.”

Suggested natural corrections:

- “The request performs two independent writes, so I need an order, idempotency, partial-failure recovery, and version observability.”
- “I will first locate the constraint—memory, aggregate throughput, read load, network, or one hot key—then choose scale-up, replicas, sharding, or a hot-key mitigation.”

## Weakness log

No learner gap has been demonstrated yet. Add a row only after Rahul calculates, predicts, draws, or explains and a specific gap is observed.

| Date | Exact gap | Type | Repair | Retest |
|---|---|---|---|---|

## Next review

- Suggested first closed-book review: 2026-09-03, after studying the notes once.
- Highest-value thing to retest: trace the dual-write and stale-refill failure states, then calculate cold-cache amplification without notes.
- Best next action: draw the lazy hit/miss and shard-plus-replica diagrams from memory, then answer closed-book questions 7, 8, 11, and 13 aloud.
