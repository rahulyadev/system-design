# Quick review — SD-BEG-100 Picking the Right Database

> Answer before opening `notes.md`. Keep this review usable in 10–20 minutes. Pack generation is not evidence that you know the material.

## Closed-book recall

1. Why is “PostgreSQL or MongoDB?” usually the wrong first question?
2. State the database-selection sequence from business action to validated choice.
3. What is an invariant? Give one order or payment example and say where it is enforced.
4. Turn “get customer orders” into a complete access pattern.
5. Which separate questions are hidden inside “we need consistency”?
6. Why does JSON input not imply a document database?
7. When is a relational database the first strong candidate?
8. Correct “relational databases cannot scale” in two precise sentences.
9. What guarantee changes when a relational design removes cross-shard foreign keys or transactions?
10. When is Redis a strong candidate, and which durability question must still be answered?
11. Why can one hot partition defeat large aggregate cluster capacity?
12. What makes a DynamoDB-style key model efficient, and what new query makes it awkward?
13. What makes a document a good aggregate boundary? Name one unbounded-embedding failure.
14. What query shape earns a graph database instead of an indexed relational edge table?
15. Why is “future-proof document database” an incomplete claim?
16. State the source-of-truth invariant for a polyglot system.
17. Explain the timeout-after-commit retry and its protection.
18. Name six kinds of evidence required before declaring a database choice right.
19. Restate the instructor’s ending exercise without opening the task pack. Which parts were left deliberately unspecified?

## Draw from memory

On paper, reconstruct this decision path without product names first:

- Inputs: business actions, invariants, transaction boundaries, consistency/durability targets.
- Workload: record shape, bytes/growth, retention/TTL, access patterns, peak rate, skew.
- Candidate branches: shared relational correctness; known-key distribution; hot TTL/data structures; bounded document aggregate; relationship traversal.
- Rejoin: representative model and queries.
- Proof loop: concurrency → load → hot key/skew → failover → restore → cost.
- Exit: one authoritative owner, derived projections, metrics, and revisit threshold.

Mark three boundaries:

1. the atomic write owner;
2. the partition/shard routing key;
3. the source-to-projection consistency window.

Then compare with [Big picture](notes.md#big-picture) and [Deep mechanism](notes.md#deep-mechanism).

## Instructor-task recall

For [`SD-BEG-100-T01`](tasks/SD-BEG-100-T01/README.md), answer before opening the task or reference:

1. What exploration did the instructor recommend at `00:11:56–00:12:11`?
2. Why is testing whether one database type can serve another type’s workload more useful than defending a favorite product?
3. Which database count, workload, runtime, output, and success criteria did the source *not* specify?
4. Predict one case where a database can technically fit but loses a useful guarantee or creates extra operations.
5. Name the invariant, access pattern, evidence, and changed condition you would put in the decision canvas.

Do not open `reference/SOLUTION.md` until Rahul has committed to his own comparison. The food-delivery canvas in the notes is separate Codex-added practice, not a second instructor task.

## Answer cues

Use these only after committing to an answer:

| Recall area | Cue | Notes link |
|---|---|---|
| First principle | requirements → guarantees; reject slogans | [60-second story](notes.md#the-60-second-story) |
| Invariant | rule remains true under race/failure | [Core concept 1](notes.md#1-select-guarantees-for-operations-not-a-tribe) |
| Capacity | shape ≠ volume ≠ lifecycle | [Core concept 2](notes.md#2-data-shape-volume-and-lifecycle-are-three-different-questions) |
| Access pattern | predicate + order + bound + rate + freshness | [Core concept 3](notes.md#3-access-patterns-determine-keys-indexes-and-locality) |
| Relational | constraints/transactions/joins; boundary may distribute | [Core concept 4](notes.md#4-relational-databases-make-shared-correctness-and-flexible-queries-explicit) |
| Redis | data structure + TTL + explicit persistence/loss policy | [Core concept 5](notes.md#5-redis-is-valuable-because-of-operations-and-latency-not-merely-key-value-syntax) |
| Distributed KV | known key, bounded query, hot-key envelope | [Core concept 6](notes.md#6-distributed-key-value-design-trades-query-freedom-for-predictable-routing) |
| Document | bounded aggregate, validation, versioned evolution | [Core concept 7](notes.md#7-a-document-database-optimizes-aggregate-shaped-work-not-schema-avoidance) |
| Graph | traversal/path is central; bound depth/degree | [Core concept 8](notes.md#8-a-graph-database-is-selected-by-traversal-questions) |
| Scale | model, consistency, partitioning, replication are separate axes | [Core concept 9](notes.md#9-scale-consistency-and-sqlnosql-are-independent-axes) |
| Multiple stores | one authority; idempotent replayable projections | [Core concept 10](notes.md#10-polyglot-persistence-needs-one-owner-and-recoverable-projections) |
| Instructor exercise | explore database overlap; preserve unspecified constraints | [Task T01](tasks/SD-BEG-100-T01/README.md) |
| Numbers | orders and sessions are different time/authority boundaries | [Worked example](notes.md#worked-example-and-calculations) |
| Failure | symptom → boundary/mechanism → evidence → recovery | [Failure and recovery](notes.md#failure-and-recovery) |

## Two-minute teach-back

Speak naturally; do not memorize a script.

1. **Problem:** Product labels hide the real correctness, query, and operational constraints.
2. **Inputs:** Invariants, transaction boundaries, read observations, durability, data lifecycle, access patterns, rate, skew, and headroom.
3. **Candidates:** Explain one useful condition for relational, Redis, distributed key-value, document, and graph storage.
4. **Boundary:** State that SQL/NoSQL does not determine scale or consistency; exact operations/topology do.
5. **Proof:** Mention a concurrency race, representative query, hot key, failover, restore, and cost.
6. **Ownership:** Name one source of truth and replayable projections.
7. **Change:** Explain what you revisit when consistency, scale, latency, durability, availability, or cost changes.

Self-check: you should use at least one invariant, one access pattern, one calculation with units, one failure symptom, and one rejected alternative.

## Interview follow-ups

1. A team says, “We need MongoDB because product attributes change.” What five questions come before agreement?
2. Orders are 2.628 TB after three years but peak at only 278 writes/s. Which scale dimension is likely to bind first, and what evidence decides?
3. Five million sessions refresh every minute. Recompute the write rate and explain why average payload size is not enough for Redis capacity.
4. A Redis failover loses an acknowledged idempotency key. Which assumption was wrong, and where should the rule live?
5. A DynamoDB partition key is `merchant_id`; one merchant produces 40% of writes. Diagnose and give three redesign options.
6. A product document embeds every review. What symptom appears as reviews grow, and how would you remodel it?
7. A two-hop graph query is fast on average but times out for celebrities. Which distribution did the average hide?
8. A relational system shards by tenant. Product adds global username uniqueness. What coordination or scope choices exist?
9. PostgreSQL commits an order, but the cache and graph projection are stale. Which read behaviors can be correct?
10. Two databases are synchronously dual-written from application code. Trace a timeout and partial-success failure.
11. An interviewer demands always-available global writes plus immediate globally consistent reads during a network partition. Which promise must be clarified or relaxed?
12. Cost must drop 40%. Which evidence tells you whether to consolidate products, reduce copies, archive data, or accept higher latency?

## Flashcards

| Front | Back | Type |
|---|---|---|
| Right first question? | Which invariants, operations, guarantees, scale, and ownership cost must the store satisfy? | decision |
| Invariant? | A rule that must remain true at a defined concurrency/failure boundary. | correctness |
| Complete access pattern? | Operation, predicates/key, order/range, result bound, rate, freshness, and concurrency. | mechanism |
| Data-shape decision alone? | Insufficient; add operations, guarantees, volume, lifecycle, and ownership. | misconception |
| Relational candidate trigger? | Shared constraints/transactions, joins/aggregations, or evolving query flexibility. | decision |
| Relational scaling truth? | It can scale up/out; distributed ownership makes cross-boundary coordination explicit and costly. | misconception |
| Redis candidate trigger? | Hot key/data-structure operations, TTL, counters, sets, rankings, or derived cache state. | decision |
| Redis durability question? | What acknowledged loss is allowed, under which failure, and how is state rebuilt? | durability |
| Distributed key-value invariant? | Critical online operations have a known/bounded key path and each hot key fits capacity. | mechanism |
| DynamoDB new-query cost? | New index/duplicate item/uniqueness protocol/backfill/capacity—not merely another WHERE clause. | trade-off |
| Good document boundary? | Bounded data read/written together with a shared lifecycle and consistency boundary. | modeling |
| Flexible schema truth? | It still needs expected shapes, validation, compatibility, indexing, and migrations. | misconception |
| Graph candidate trigger? | Valuable variable relationship/path traversals dominate. | decision |
| Graph failure to test? | Supernode or unbounded path expansion. | failure |
| Partition-key risk? | Skew/hot key can overload one owner while aggregate capacity is idle. | failure |
| SQL/NoSQL tells consistency? | No; product, operation, configuration, replica, and topology do. | misconception |
| SQL/NoSQL tells scale? | No; placement, partitioning, replication, engine, and workload do. | misconception |
| Timeout after commit? | Retry may duplicate; durable idempotency returns the original result. | concurrency |
| Source-of-truth invariant? | Each fact has one conflict-resolution authority. | correctness |
| Projection contract? | Idempotent delivery, measurable lag, replay/rebuild, and stale/unavailable behavior. | reliability |
| Replica versus backup? | Replica serves current copies/failover; backup enables historical recovery. | distinction |
| Order average rate? | `1,200,000 ÷ 86,400 ≈ 13.89 writes/s`. | estimate |
| Order peak rate at 20×? | About `277.8 writes/s`. | estimate |
| Session refresh rate? | `5,000,000 ÷ 60 ≈ 83,333 writes/s`. | estimate |
| Three-year logical orders? | `1.314B × 2 KB = 2.628 TB` before copies/backups/overhead. | estimate |
| Polyglot decision threshold? | Specialist benefit must exceed synchronization, recovery, cost, and on-call burden. | trade-off |
| Benchmark proves? | Only the modeled operations/data/configuration/failures, not universal suitability. | evidence |
| Best revisit trigger? | A named target, invariant, query, scale, failure, or cost crosses its recorded threshold. | operations |

## English speaking check

- Use `peculiar property` without making it sound merely strange; name the exact property.
- Explain `access pattern` with a key, predicate, order, bound, rate, and freshness.
- State one `invariant` and distinguish it from a latency objective.
- Say naturally: “This candidate list is useful but not exhaustive.”
- Replace “MongoDB is future-proof” with a named expected change and migration claim.
- Correct these weak phrases aloud:
  - “NoSQL scales better.”
  - “Redis is fastest.”
  - “We need graph because users have relationships.”
  - “We will drop constraints to improve scalability.”
  - “Both databases are the source of truth.”

## Weakness log

Record only gaps Rahul demonstrates. Do not infer understanding from generated files.

| Date | Exact gap | Type | Repair | Retest |
|---|---|---|---|---|
| — | No demonstrated gap yet | — | Complete the optional decision canvas without naming a product early | After the first attempt |

## Next review

- Suggested date: 2026-09-03
- Highest-value thing to retest: start from one order invariant and one precise access pattern, then reject at least three database families with boundary- and evidence-based reasons before selecting a candidate.
