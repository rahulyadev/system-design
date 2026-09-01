# Quick review - SD-BEG-090 Non-Relational Databases

> Answer before opening `notes.md`. Keep this review usable in 10-20 minutes.

## Closed-book recall

1. Why is “NoSQL” an umbrella label rather than a guarantee?
2. State one access pattern that favors each of document, key-value, and graph models.
3. Trace a document `$inc` update in order. What is atomic, and what is not proved?
4. Trace an exact-key request from key to shard owner. Where can a hot key defeat aggregate scale?
5. Why is “anything can be modeled as a graph” insufficient justification for a graph database?
6. Give two counterexamples to “non-relational databases have no transactions or partial updates.”
7. Explain the difference between flexible schema and absent schema.
8. Why can a partial update reduce network I/O while still causing internal document reindexing or rewriting?
9. Which metrics distinguish a bad partition key from a generally overloaded cluster?
10. What new correctness problem appears when one service writes a source database and a search/graph projection?

## Draw from memory

- Components/states: access pattern -> model candidate -> product/topology verification.
- Document path: predicate -> owner/document -> update operator -> acknowledgment -> verification read.
- Key path: key -> partition/hash slot -> topology map -> owner -> value.
- Graph path: selective start node -> typed/directed expansion -> path selector -> result.
- Failure boundary: one hot key, one oversized document, or one unbounded traversal.
- Key invariant: every business fact has one authoritative write owner; every critical lookup has a bounded owned path.

Then compare with [Big picture](notes.md#big-picture) and [Deep mechanism](notes.md#deep-mechanism).

## Instructor-task recall

- Restate the one exercise without opening its README: which three local databases must be explored?
- For MongoDB, predict the result of an atomic `stock` increment and name the flexible-field evidence.
- For Redis, name the conceptual course operations and their Redis command equivalents.
- For Neo4j, predict shortest-path length before and after adding a direct relationship.
- Explain what evidence proves capability rather than container startup.
- State the exact safety boundary before any scoped reset.

Task: [`SD-BEG-090-T01`](tasks/SD-BEG-090-T01/README.md).

## Answer cues

- Umbrella/category boundary: [Core concept 1](notes.md#1-nosql-is-a-negative-label-not-a-shared-contract)
- Access-pattern method: [Core concept 2](notes.md#2-choose-by-access-pattern-and-correctness-boundary)
- Documents and partial updates: [Core concept 3](notes.md#3-document-databases-store-aggregates-not-schema-free-blobs)
- Keys, routing, and hot keys: [Core concept 4](notes.md#4-key-value-stores-trade-query-freedom-for-a-narrow-fast-path)
- Traversal deciding condition: [Core concept 5](notes.md#5-graph-databases-optimize-relationship-traversal)
- Numbers: [Worked example](notes.md#worked-example-and-calculations)
- Product-specific corrections: [Verified extensions](notes.md#verified-extensions)

Do not use these cues as a script. Close the notes and reconstruct cause -> state change -> evidence.

## Two-minute teach-back

1. Problem: “NoSQL” hides several unrelated models and guarantees.
2. Simple intuition: documents keep aggregates together; key-value routes by an exact key; graphs follow relationships.
3. Mechanism/invariant: state the owner and atomicity boundary for each.
4. Example: catalog document, session token, and follow path.
5. Trade-off: specialization speeds one path but narrows others and adds operations.
6. Failure/recovery: hot key, lost update, unbounded traversal, or projection drift.
7. Evidence: p99 by access pattern, owner/key skew, conflicts, scan/expansion ratio, lag, and reconciliation.

## Interview follow-ups

1. A product catalog needs exact lookup, optional fields, faceted text search, and an atomic payment/inventory update. Where does each responsibility belong?
2. One key owns 20% of traffic. Why does adding shards not solve it, and how would you split it safely?
3. A shortest-path query times out only for broad user segments. Which start-cardinality, depth, plan, and expansion evidence do you inspect?
4. Search results may lag the catalog by five seconds, but inventory must be current. How does the API combine or separate those guarantees?
5. The team can operate only PostgreSQL today. Which requirements justify adding MongoDB, Redis, or Neo4j rather than using JSONB, indexes, and recursive queries first?

## Flashcards

| Front | Back | Type |
|---|---|---|
| What does “NoSQL” guarantee? | Nothing product-specific by itself; name model, product, topology, operation, and configured guarantee. | boundary |
| Flexible schema vs no schema? | Records may vary, but application contracts, validation, indexes, and migrations still define structure. | misconception |
| Document atomicity deciding condition? | Put fields that must change atomically together inside one document, within size/contention limits. | invariant |
| Why use an atomic increment? | It avoids client read-modify-write payload and lost updates at the supported atomic scope. | mechanism |
| Exact-key ownership path? | key -> partition/slot -> topology map -> owner -> command/value. | mechanism |
| What is a hot key? | One key has disproportionate traffic and saturates its owner despite healthy cluster averages. | failure |
| Why can multi-key work be hard? | Keys may live on different owners; atomicity/routing rules become product- and placement-specific. | trade-off |
| Graph database deciding condition? | Repeated bounded relationship traversal/graph algorithms are central and awkward in a simpler store. | decision |
| First defense against traversal explosion? | Bind a selective start set and bound relationship type, direction, predicates, and depth. | failure |
| Polyglot persistence invariant? | One authoritative writer per fact; derived stores are versioned, replayable, observable, and reconcilable. | reliability |
| Does partial update mean in-place bytes? | No; it is a logical/client API property. Internal storage may rewrite or reindex. | misconception |
| Do relational databases scale horizontally? | Yes; topology may be manual or product-specific, but SQL vs NoSQL is not the scale boundary. | misconception |

## English speaking check

- Use `heterogeneous` naturally in one design sentence.
- Explain `aggregation` without using the word itself.
- Explain `traversal` with a two-hop example.
- Correct this weak phrase: “NoSQL is better because it is schema-less and scalable.”
- Replace “We can put it in graph” with a deciding condition involving repeated path queries.

## Weakness log

Record only gaps Rahul demonstrates. Do not pre-fill predicted weaknesses.

| Date | Exact gap | Type | Repair | Retest |
|---|---|---|---|---|
| - | - | - | - | - |

## Next review

- Suggested date: after completing `SD-BEG-090-T01`, then 2-3 days later.
- Highest-value thing to retest: choose a model from changed access patterns and state the product-specific invariant without relying on category slogans.
