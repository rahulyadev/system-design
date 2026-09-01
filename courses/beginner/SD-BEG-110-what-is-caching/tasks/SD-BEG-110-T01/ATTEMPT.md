# My attempt — SD-BEG-110-T01

This file belongs to Rahul. Initialization and repair must never overwrite it.

Do not open `reference/SOLUTION.md` until you have written a prediction and completed a first measurement.

## Clarifications and assumptions

- Redis operation and payload:
- PostgreSQL operation and payload:
- Iteration count and warm-up count:
- Persistent connection or connection per operation:
- Sequential or concurrent clients:
- Durability settings being compared:
- What the timing includes and excludes:

## Prediction before running or designing

- Expected Redis `SET` result and latency shape:
- Expected Redis `GET` result and latency shape:
- Expected PostgreSQL write result and latency shape:
- Expected PostgreSQL primary-key read result and latency shape:
- Why I expect any difference:
- Correctness invariant:
- Evidence I expect:

## My approach

Use `starter/benchmark.py`, write an equivalent script, or document another repeatable method. Keep one logical key and one payload constant. Warm both systems before recording samples. Do not silently change durability, batching, payload size, client lifetime, or concurrency between systems.

## Actual evidence I observed

Do not paste predicted or reference output here as observed evidence.

- Exact command:
- Environment and versions:
- Redis correctness result:
- PostgreSQL correctness result:
- Redis write latency summary:
- Redis read latency summary:
- PostgreSQL write latency summary:
- PostgreSQL read latency summary:
- Unexpected noise/outliers:

## Explanation in my own words

Explain which mechanism produced the difference. Separate network round trips, parsing, query execution, transaction commit/durability, client overhead, and the operation's actual semantics. State why one local microbenchmark does not prove production capacity.

## Variation prediction and result

- Changed condition:
- Prediction before running:
- Actual result:
- Why it changed:
- Which conclusion remains valid:

## What I would say in an interview

Use: requirement → comparable operations → measurement boundary → observed evidence → semantic difference → trade-off → production follow-up.

## Questions after attempting

-
