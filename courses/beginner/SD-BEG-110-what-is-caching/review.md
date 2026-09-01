# Quick review — SD-BEG-110 What Is Caching?

> Answer before opening `notes.md`. Keep this review usable in 10–20 minutes. The artifact is ready; Rahul's learning state remains **Not started** until he studies and demonstrates recall.

## Closed-book recall

1. Explain the difference between **caching** and a **cache** without naming Redis.
2. Name the three broad costs the course says a cache can avoid.
3. Trace a cache-aside hit and miss in order. Who owns the authoritative result?
4. What condition makes a cached value safe to reuse?
5. Why is “nearer” relative rather than equivalent to “RAM”?
6. Define temporal locality, working set, hit ratio, and miss penalty.
7. Why can a high hit ratio still describe a bad cache?
8. What inputs belong in a safe cache key for personalized multi-tenant data?
9. Distinguish expiry, invalidation, and eviction by cause.
10. Why can cache loss preserve data but still cause an availability incident?
11. Describe one stale-fill concurrency race after a database update.
12. What evidence distinguishes a slow cache from a low hit ratio?
13. When should you improve the database/query or use no cache instead?
14. Why is a local Redis-versus-PostgreSQL latency ordering not a universal product rule?
15. Name one requirement change that would make you bypass or remove the cache.

## Draw from memory

### Cache-aside flow

- Components/states: client, API, cache, source of truth; hit, miss, fill, response.
- Arrows/order: request → lookup → hit response **or** miss → source fetch → optional fill → response.
- Failure boundary: cache timeout/down → bounded fallback or degradation; never unlimited retries.
- Key condition: equal keys must imply safely interchangeable answers.

### Stale-fill race

- Components/states: reader, cache, database, writer; versions 1 and 2.
- Arrows/order: reader miss → reader fetches v1 → writer commits v2 → writer deletes key → reader fills v1.
- Failure boundary: a correct invalidation can occur before a delayed stale fill.
- Key insight: final state depends on ordering/version rules, not the existence of a delete call.

### Calculation skeleton

```text
E[T] = h × T_hit + (1 - h) × T_miss
origin_QPS = request_QPS × (1 - h)
outage_amplification = full_fallback_QPS / steady_origin_QPS
working_set_bytes ≈ distinct_hot_items × bytes_per_item × overhead_factor
```

Then compare with [Big picture](notes.md#big-picture), [Worked example](notes.md#worked-example-and-calculations), and [Ordering, concurrency, and stale state](notes.md#ordering-concurrency-and-stale-state).

## Instructor-task recall

Without opening the task README, restate all four source actions:

1. local Redis setup;
2. basic put/get interaction;
3. timing measurement;
4. equivalent relational storage/retrieval and comparison.

Then answer:

- Which relational product and exact versions does the supplied task choose as Codex-added controls?
- What payload correctness invariant must hold before timing matters?
- Why keep connections persistent and warm both paths?
- Which four baseline operations are measured?
- Which Redis durability setting differs from the PostgreSQL write path?
- What does the 4 ms variation prove—and what does it not prove?
- Which exact state may cleanup reset?

Attempt [`SD-BEG-110-T01`](tasks/SD-BEG-110-T01/README.md) before reading its evidence or solution.

## Answer cues

- Definition and decision condition: [The 60-second story](notes.md#the-60-second-story)
- Core terms: [Why the terms matter](notes.md#why-the-terms-matter)
- Technique versus location: [Core concept 1](notes.md#1-caching-is-the-technique-a-cache-is-the-reusable-location)
- Relative proximity: [Core concept 2](notes.md#2-nearer-means-cheaper-on-the-real-access-path)
- Reuse and sizing: [Core concept 3](notes.md#3-locality-and-the-working-set-decide-what-deserves-space)
- Hit/miss mechanism: [Core concept 4](notes.md#4-cache-aside-the-application-controls-lookup-and-fill)
- Hit-ratio math: [Core concept 5](notes.md#5-hits-misses-hit-ratio-and-miss-penalty)
- Safe keys: [Core concept 6](notes.md#6-keys-define-the-reuse-and-isolation-boundary)
- Failure/recovery boundary: [Core concept 7](notes.md#7-temporary-copy-source-of-truth-and-recovery)
- Freshness/removal: [Core concept 8](notes.md#8-freshness-expiry-invalidation-and-eviction-are-different)
- Product boundary: [Core concept 9](notes.md#9-redis-and-memcached-are-examples-not-the-definition)
- Numbers: [Worked example](notes.md#worked-example-and-calculations)
- Incident evidence: [Failure and recovery](notes.md#failure-and-recovery) and [Observability](notes.md#observability)
- Exact task: [`SD-BEG-110-T01`](tasks/SD-BEG-110-T01/README.md)

## Two-minute teach-back

Speak without reading full sentences:

1. **Problem:** repeated requests pay the same expensive network, disk, query, or computation cost.
2. **Assumptions:** reusable result, correct key, bounded freshness, measured locality, authoritative recovery path.
3. **Simple idea:** keep the hot reusable subset on a cheaper path.
4. **Mechanism:** cache-aside hit returns; miss fetches source, may fill, then returns.
5. **Invariant:** every served hit is safe for the request/key/version/freshness boundary.
6. **Numbers:** expected latency and database QPS depend on hit ratio and miss penalty.
7. **Trade-off:** speed/origin relief versus memory, stale copies, invalidation, eviction, and another dependency.
8. **Failure:** cache loss or synchronized expiry can stampede the source.
9. **Protection:** bounded timeout, coalescing, TTL jitter, admission/degradation, staged warmup.
10. **Evidence:** outcome latency, hits/misses, fill/invalidation, memory/eviction/hot keys, source headroom, stale incidents.

## Interview follow-ups

### Foundation

1. Is an API server's local disk ever a cache? State the relative expensive path.
2. Why is a present cached value not automatically a hit?
3. Give one workload with strong locality and one with poor locality.
4. What does the course's “glorified hash table” analogy clarify and omit?

### SDE-2

5. Hit ratio falls from 90% to 60% while cache latency stays flat. Which origin metrics should move and why?
6. Hit ratio stays 95% while endpoint p95 doubles. Give five hypotheses and the first evidence for each.
7. A user changes their profile but immediately reads the old copy. Give two fixes and their trade-offs.
8. A popular key expires and 5,000 requests run the same query. Diagnose and mitigate.
9. How would you test a cache client timeout/fallback without risking an existing database?

### SDE-3

10. At 50,000 requests/s and 96% hit ratio, calculate database request rate. What is it during total cache loss?
11. Design degradation if the database can safely handle only twice normal miss traffic, not full fallback.
12. Separate caching policies for public news, personalized profiles, and authentication revocation.
13. What changes when the cache is cross-region rather than region-local?
14. When may Redis become authoritative, and which durability/recovery questions replace the disposable-cache assumption?
15. Define a benchmark that could inform capacity planning rather than merely teach local latency.

## Flashcards

| Front | Back | Type |
|---|---|---|
| Caching vs cache? | Technique of reusable cheaper results vs the place/component holding them. | definition |
| What makes a cache “near”? | Lower measured access cost on the request path, not necessarily RAM or physical distance. | mechanism |
| Hit invariant? | Present **and** safe for key, authorization, version, and freshness. | correctness |
| Miss cost? | Cache lookup plus origin fetch/compute plus optional fill and error handling. | mechanism |
| Hit ratio formula? | usable hits ÷ total lookups for the same outcome definition. | estimate |
| Expected latency formula? | `h × T_hit + (1-h) × T_miss` in the simplified model. | estimate |
| Origin QPS at 1,000 RPS and 90% hits? | About 100 QPS, ignoring writes/background work. | estimate |
| Outage amplification in that example? | 1,000/100 = 10× origin traffic. | failure |
| Working set? | Distinct actively reused data in the chosen time window. | capacity |
| Temporal locality? | Recently used data is likely to be used again soon. | mechanism |
| TTL vs invalidation? | TTL is time-based removal; invalidation reacts to semantic/source change. | comparison |
| Eviction vs expiry? | Eviction frees capacity; expiry follows time policy. | comparison |
| Why version a key? | Isolate representation/semantic changes and prevent old serialization reuse. | correctness |
| Stampede? | Many simultaneous misses duplicate expensive work and overload the source. | failure |
| Hot key? | Disproportionate traffic for one key concentrates load despite good global ratios. | failure |
| Safe cache outage response? | Bounded timeout/fallback with source headroom, admission/degradation, and staged warmup. | reliability |
| Why not cache everything? | Fast capacity is finite; cold entries waste cost and evict the reused set. | trade-off |
| Redis persistence options? | RDB, AOF, neither, or both; configuration decides role/durability. | boundary |
| Microbenchmark prerequisite? | Exact correctness plus disclosed operation, clients, warm-up, samples, units, concurrency, and semantics. | evidence |
| When not to cache? | Low reuse, rapid changes, unclear security/freshness, cheap origin, or unjustified complexity. | decision |

## English speaking check

- Use `locality` naturally in a sentence about recent news.
- Explain `stale` without saying “old data” or “cache.”
- Distinguish `eviction`, `expiry`, and `invalidation` aloud.
- Use `degrade gracefully` to describe a cache-outage response with one concrete reduced feature.
- Correct this weak phrase: “Redis is obviously faster because it is O(1).”
- Improve this design-review sentence: “If cache goes down, database will handle it.”

Suggested natural corrections:

- “I expect a lower Redis latency for this path, but I will verify correctness and a distribution; protocol, persistence, client, payload, and host conditions affect the result.”
- “If the cache fails, miss traffic may multiply database load, so fallback is limited by measured source headroom and a defined degradation policy.”

## Weakness log

No learner gap has been demonstrated yet. Add a row only after Rahul answers, predicts, calculates, draws, or explains and a specific gap is observed.

| Date | Exact gap | Type | Repair | Retest |
|---|---|---|---|---|

## Next review

- Suggested first closed-book review: 2026-09-02, after studying the notes and making a learner-owned task prediction.
- Highest-value thing to retest: derive expected latency and full-fallback database load, then explain why preserved data does not guarantee preserved availability.
- Best next action: open [`SD-BEG-110-T01/ATTEMPT.md`](tasks/SD-BEG-110-T01/ATTEMPT.md), write the four-operation prediction and semantic assumptions, then run only the learner-side preflight/setup without opening the reference evidence.
