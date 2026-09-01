# Rubric — SD-BEG-110-T01

Score Rahul's evidence independently. Do not award completion for running the reference verifier or opening the reference answer.

| Dimension | Needs work | SDE-2-ready | SDE-3-ready |
|---|---|---|---|
| Source requirement | Omits setup, put/get, timing, or database comparison | Completes all four source requirements | Separates source requirements from added benchmark controls |
| Correctness/invariant | Times operations without checking returned data | Proves both systems return the exact payload | Explains key/table ownership, isolation, reset, and stale-state boundaries |
| Measurement method | Uses one sample or includes connection/setup accidentally | Uses warm-up, persistent clients, multiple samples, and units | Explains percentiles, coordinated omission, concurrency, cache state, and workload representativeness |
| Semantic fairness | Calls the operations identical because both store bytes | States the Redis/PostgreSQL durability and query differences | Designs a decision-relevant comparison or rejects a misleading one |
| Evidence | Says Redis is faster without actual output | Captures versions, commands, correctness, and latency summaries | Preserves raw reasoning, explains noise, and states what remains unproved |
| Cache mechanism | Names memory or Redis only | Connects hit path to avoided work and lower database load | Quantifies hit-rate sensitivity, miss penalty, invalidation, and failure behavior |
| Failure/recovery | Covers only the happy path | Handles cache miss/down and exact scoped reset | Covers stampede, hot keys, stale authorization, fallback saturation, and ownership |
| Communication | Lists numbers without a conclusion boundary | Gives a clear mechanism-backed comparison | Adapts the decision when latency, durability, consistency, availability, or cost changes |

## Required completion evidence

- [ ] Rahul's own prediction before execution
- [ ] Redis installed/running locally with exact identity checked
- [ ] Rahul's own Redis put/get interaction
- [ ] Rahul's own relational write/read interaction
- [ ] repeated measurements with units and warm-up stated
- [ ] exact payload correctness for both systems
- [ ] explanation of at least one semantic mismatch
- [ ] one changed-condition prediction and result
- [ ] scoped reset/cleanup evidence
- [ ] a natural two-minute explanation without reading the reference
