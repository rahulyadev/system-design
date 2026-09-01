# Quick review — SD-BEG-070 Scaling Databases

> Answer before opening `notes.md`. Keep this review usable in 10–20 minutes.

## Closed-book recall

1. Name six possible database bottlenecks. Which metric would support each diagnosis?
2. When is vertical scaling the best next move, and what two ceilings remain?
3. Trace an asynchronous write from API acknowledgment through replica query visibility.
4. What is the difference between “replica received the change” and “replica can return the change in a query”?
5. Which reads may use a replica? Give three that should usually remain on the primary or wait for a position.
6. State the ownership invariant for a two-shard a–m/n–z design.
7. Why can two 20,000-write/s shards fail at 30,000 writes/s total?
8. How do replication and sharding combine rather than replace one another?
9. Name two failure modes for a replica and two for a shard router.
10. Which observation would make you reject sharding and keep one larger node?

## Draw from memory

- Components/states: client, API/router, primary, source log, replica receiver, relay/apply state, replica; then two shard owners and one replica per owner.
- Arrows/order: write → primary commit/log → receive → apply → replica read; key → normalize → mapping version → exactly one shard.
- Failure boundary: primary acknowledged before replica apply; router using a stale shard map.
- Key numbers/invariants: exactly one owner per valid key and mapping version; `90:10` is an example workload, not a universal constant.

Then compare with [Big picture](notes.md#big-picture) and [Deep mechanism](notes.md#deep-mechanism).

## Instructor-task recall

### SD-BEG-070-T01

- Restate the four source requirements without opening the task README.
- Predict what a replica read returns while its SQL/applier thread is paused after a primary write.
- Name the evidence that proves the API used two database targets rather than returning a hard-coded label.
- Explain the recovery condition before the replica may serve the new row.

### SD-BEG-070-T02

- Restate the two range ownership rules and the API routing requirement.
- Predict the owners of `apple`, `mango`, `nectar`, and `zebra`.
- Explain how direct per-shard queries prove absence from the wrong owner.
- Predict what 20 `a…` keys and two `z…` keys show about useful capacity.

## Answer cues

- Scaling decision: [Core concepts](notes.md#core-concepts) → measured bottleneck, simplest sufficient move, changed requirement.
- Replica mechanism: [Read replicas](notes.md#3-read-replicas-and-explicit-request-routing) → authoritative write path, receive/apply, freshness policy.
- Acknowledgment boundary: [Replication mode](notes.md#4-replication-mode-is-an-acknowledgment-contract) → received versus logged versus applied.
- Sharding: [Sharding divides ownership](notes.md#5-sharding-divides-ownership) → deterministic owner, balance/locality, resharding.
- Numbers: [Worked example](notes.md#worked-example-and-calculations) → show intermediate arithmetic and failure headroom.
- Operations: [Failure and recovery](notes.md#failure-and-recovery) and [Observability](notes.md#observability).

## Two-minute teach-back

1. State a concrete latency/capacity target and why evidence comes first.
2. Explain vertical scaling and its ceiling.
3. Separate read scaling from authoritative write/storage scaling.
4. Trace primary log → replica receive → replica apply → routed read.
5. State the freshness and one-owner invariants.
6. Give the 80/20 hot-shard counterexample.
7. Close with failure recovery, metrics, and when the decision changes.

## Interview follow-ups

1. A replica’s receiver is running but applied position is frozen. What evidence and safe recovery do you use?
2. The product changes from five-second catalog staleness to strict read-after-write. How does routing change?
3. A tenant becomes 45% of writes on one shard. How do you mitigate it without moving every tenant?
4. A managed database offers a larger tier for ₹X/month. What engineering and operational costs must be compared with sharding?
5. During failover, how do you prevent the old primary and a promoted replica from both accepting writes?

## Flashcards

| Front | Back | Type |
|---|---|---|
| What does a read replica scale? | Eligible read execution; it does not remove the primary’s authoritative writes. | mechanism |
| What must “synchronous” specify? | The acknowledgment threshold and whether remote state is received, flushed, or applied. | invariant |
| Why can a replica return stale data? | The primary acknowledged before the replica reached the write’s applied position. | failure |
| Replica versus shard? | Replica copies one owner’s data; shard owns a mutually exclusive subset. | distinction |
| Range-shard invariant? | Every valid key maps to exactly one owner under one mapping version. | correctness |
| What limits useful shard capacity? | The busiest shard plus cross-shard overhead, not nominal aggregate capacity. | estimate |
| First response to “database is slow”? | State the target and identify the saturated/waiting resource with evidence. | decision |
| Why is a replica not a backup? | It can quickly copy deletion/corruption and lacks independent restore history. | misconception |

## English speaking check

- Use `bottleneck` naturally in one simple sentence and one design-review sentence.
- Explain `replication lag` without using either word.
- Use `skew` to describe both uneven storage and uneven traffic.
- Correct this weak interview phrase: “We will shard because horizontal scaling is unlimited.”
- Replace “replica is consistent” with a precise statement naming its applied position or freshness bound.

## Weakness log

Record only gaps Rahul demonstrates. No gap has been observed merely because the pack was generated.

| Date | Exact gap | Type | Repair | Retest |
|---|---|---|---|---|
| — | No demonstrated gap yet | — | Attempt one task before opening its reference | After attempt |

## Next review

- Suggested date: 2026-09-03
- Highest-value thing to retest: explain received-versus-applied replication state, then use it to predict a read-after-write result.
