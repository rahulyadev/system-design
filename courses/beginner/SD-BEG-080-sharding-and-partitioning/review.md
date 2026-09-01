# Quick review — SD-BEG-080 Sharding and Partitioning

> Answer before opening `notes.md`. Keep this review usable in 10–20 minutes.

## Closed-book recall

1. Define partition, shard, shard key, router, and replica in one sentence each.
2. Why is “partitioning stays on one machine; sharding uses many machines” useful but incomplete?
3. Trace a keyed write from the API through a logical partition to its authoritative shard.
4. State the collective-completeness, mutual-exclusion, and one-current-write-owner invariants.
5. Reproduce the course's arithmetic for 1,500 writes/s on two 1,000-writes/s shards.
6. Why do two shards violate a 70% utilization target in that example, and how many are needed?
7. Predict the two shard loads for a 70/30 distribution. Why does nominal aggregate capacity mislead?
8. Distinguish horizontal partitioning from vertical partitioning and vertical scaling.
9. Compare range, hash, tenant/directory, and local time partitioning against one dominant query each.
10. What makes a query targeted? What makes it scatter-gather?
11. Why can equal bytes across shards still produce severe latency skew?
12. Why does sharding alone not prove higher availability?
13. Name the ordered phases of a safe online ownership migration.
14. What goes wrong when a router uses an old mapping epoch after write cutover?
15. Give three conditions under which one node or local partitioning remains the better design.

## Draw from memory

- Components: client, API/router, versioned shard map, logical partitions, two shard primaries, local partitions, one replica per shard.
- Arrows: shard key → logical partition → physical shard; shard primary → same-shard replica.
- Ownership boundary: circle the one current authoritative write owner.
- Migration states: plan → snapshot/backfill → catch up → verify → cut over → drain → retire.
- Failure boundary: show one unavailable shard and a fan-out query waiting on it.
- Key numbers: 1,500 ÷ 2 = 750; 70/30 = 1,050/450; `ceil(1,500 ÷ 700) = 3` with 30% headroom.

Then compare with [Big picture](notes.md#big-picture), [Worked example](notes.md#worked-example-and-calculations), and [Deep mechanism](notes.md#deep-mechanism).

## Instructor-task recall

No instructor task. The complete supplied source and its ending were scanned, and `source_manifest.json` records zero tasks.

Use these optional source-faithful checks instead:

- Reconstruct the five 100 GB partitions and their 60/40 placement across two shards.
- Explain why the same-data read-replica drawing represents replication rather than a second ownership shard.
- State one advantage and two operational costs of sharding without opening the notes.

## Answer cues

- Vocabulary: [Why the terms matter](notes.md#why-the-terms-matter) → piece, independent owner, copy, route.
- Ownership: [Partitioning versus sharding](notes.md#2-partitioning-describes-division-sharding-describes-distributed-ownership) → complete domain, no overlap, one write owner.
- Keys: [Shard key](notes.md#5-the-shard-key-is-a-workload-decision) → query presence, frequency, monotonicity, stability, locality.
- Numbers: [Worked example](notes.md#worked-example-and-calculations) → ideal split, headroom, 70/30 skew, 60/40 storage.
- Queries: [Routing](notes.md#7-routing-determines-whether-sharding-saves-work) → target set, scatter-gather, slowest shard, merge.
- Availability: [Replication and sharding](notes.md#8-replication-and-sharding-are-independent-axes) → ownership subset versus redundant members.
- Migration: [Rebalancing](notes.md#9-rebalancing-is-an-online-ownership-migration) → copy, stream, verify, fence, drain.
- Operations: [Failure and recovery](notes.md#failure-and-recovery) and [Observability](notes.md#observability).
- Corrections: [Misconceptions](notes.md#misconceptions) → replicas, local partitions, aggregate capacity, availability.

## Two-minute teach-back

1. State the one-node capacity problem and why vertical scaling comes first.
2. Define partition, shard, and replica with one concrete topology.
3. Trace key → logical partition → shard and state the one-owner invariant.
4. Calculate the 750/750 ideal and the 1,050/450 skewed case.
5. Contrast horizontal and vertical partitioning.
6. Explain targeted versus scatter-gather queries.
7. Explain why each shard may need replicas and backups.
8. Name the safe resharding phases and the stale-router failure.
9. Close with when one node or local partitioning is still better.

## Interview follow-ups

1. Your shard storage is 50/50, but p99 is 20 ms on shard A and 400 ms on shard B. Which distributions and waits do you inspect next?
2. A monotonically increasing order ID is range-sharded. Why might all new writes hit one shard, and what alternatives preserve the needed queries?
3. A tenant-based key supports every write, but a new global activity feed lacks `tenant_id`. Would you fan out, change the key, or build a projection?
4. One tenant grows to 45% of writes. Why does moving it to an empty shard only postpone the problem?
5. The router cache is at epoch 41 while the shard rejects writes below epoch 42. What is safe to retry, and what prevents duplicate effects?
6. How do global uniqueness and foreign keys change when related rows can land on different shards?
7. What availability can you honestly promise when each shard has one node? What changes with three replicas per shard?
8. How do you prove a rebalance is safe before, during, and after cutover?
9. When would PostgreSQL local time partitioning solve the actual problem without sharding?
10. A business asks for 99.99% availability and strict cross-region synchronous writes. Which latency and partition-tolerance trade-offs must be made explicit?

## Flashcards

| Front | Back | Type |
|---|---|---|
| Partition versus shard? | A partition is a subset; a shard is an independently routed owner of one or more subsets. | distinction |
| Shard versus replica? | Shards own different subsets; replicas copy the same subset. | distinction |
| Horizontal versus vertical partitioning? | Horizontal splits rows; vertical splits columns or functional groups. | distinction |
| Vertical partitioning versus vertical scaling? | One changes data layout; the other gives one node more resources. | misconception |
| Core routing invariant? | Every valid key maps to one logical partition and one current authoritative write owner for the mapping epoch. | correctness |
| Why use logical partitions? | They let selected small ownership units move between physical shards. | mechanism |
| Course ideal load per shard? | `1,500 ÷ 2 = 750 writes/s`, assuming a perfect 50/50 split and no overhead. | estimate |
| Hot-shard counterexample? | A 70/30 split sends 1,050 writes/s to a 1,000-writes/s shard despite 2,000 aggregate capacity. | estimate |
| Shards needed with 30% headroom? | `ceil(1,500 ÷ (1,000 × 0.70)) = 3`. | estimate |
| Targeted query? | The router can identify one shard or a small subset from the shard-key predicate. | mechanism |
| Scatter-gather query? | The router broadcasts to multiple shards and merges responses. | mechanism |
| Why does shard-key cardinality not guarantee balance? | A few values can still dominate frequency, bytes, or expensive work. | trade-off |
| Range-sharding strength? | Locality and efficient range scans. | decision |
| Range-sharding risk? | A monotonic edge or heavy range can become hot. | failure |
| Hash-sharding strength? | Usually smoother point-operation distribution. | decision |
| Hash-sharding cost? | Poor natural range locality and unsafe naive modulo resizing. | trade-off |
| Does local table partitioning scale across machines? | Not automatically; it may prune and simplify maintenance inside one database boundary. | misconception |
| Does sharding guarantee availability? | No; each shard and routing/metadata path needs redundancy and a degradation policy. | failure |
| Resharding phases? | Plan, backfill, catch up, verify, fenced cutover, drain, retire. | mechanism |
| Most important skew metric? | No single metric: compare max-to-mean traffic, bytes, CPU time, latency, and growth by shard/key. | observability |
| First response to “we need sharding”? | State the violated target, prove the bottleneck, and test simpler sufficient options. | decision |

## English speaking check

- Use `mutually exclusive` to state the ownership invariant naturally.
- Explain `skew` without using the words “uneven” or “imbalance.”
- Use `scatter-gather` in one SDE-2 diagnosis and one design-review recommendation.
- Correct this weak phrase: “We can rebalance by copying the table to the new server.”
- Replace “sharding gives high availability” with a precise conditional statement.
- Say this calculation naturally: “At a seventy-thirty split, the hot shard receives one thousand fifty writes per second.”

## Weakness log

Record only gaps Rahul demonstrates. Pack generation is not evidence of understanding.

| Date | Exact gap | Type | Repair | Retest |
|---|---|---|---|---|
| — | No demonstrated gap yet | — | Do the hot-shard calculation and draw the ownership map closed-book | After the first attempt |

## Next review

- Suggested date: 2026-09-03
- Highest-value thing to retest: distinguish partition, shard, and replica, then use the one-owner invariant to diagnose a stale-router write during resharding.
