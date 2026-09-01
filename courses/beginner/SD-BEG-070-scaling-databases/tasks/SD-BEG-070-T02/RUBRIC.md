# Rubric — SD-BEG-070-T02

Score evidence independently. Do not award completion for opening the reference answer or running only the reference verifier.

| Dimension | Needs work | SDE-2-ready | SDE-3-ready |
|---|---|---|---|
| Requirement understanding | Misses a boundary or uses one database | Reconstructs a–m/n–z and API routing | Identifies normalization, invalid keys, mapping version, migration ambiguity |
| Correctness/invariant | Routes by duplicated ad hoc conditions | One central rule gives every valid key exactly one owner | Proves exclusivity and plans fencing/versioning during resharding |
| Mechanism | Says “split the data” | Traces key → normalize → owner → pool → physical row | Connects routing to locality, cross-shard work, and control-plane state |
| Evidence | Trusts API labels | Captures server IDs and correct/wrong-shard rows | Correlates trace route, mapping version, physical state, and failure evidence |
| Trade-offs | Claims two databases double capacity | Discusses skew and cross-shard cost | Quantifies hot-owner thresholds and migration/cost triggers |
| Failure/recovery | Happy path only | Rejects invalid keys and handles one unavailable shard explicitly | Covers stale maps, partial cross-shard failure, fencing, and recovery ownership |
| Communication | Names sharding | Explains decision and invariant clearly | Leads requirement changes and rejects unjustified sharding |

## Required completion evidence

- [ ] Rahul’s own prediction before execution
- [ ] Rahul’s own two-pool API implementation
- [ ] exact task-local identity and health evidence
- [ ] boundary-key routing evidence for a, m, n, and z sides
- [ ] direct correct-shard presence and wrong-shard absence
- [ ] invalid-key rejection with zero writes
- [ ] controlled skew counts and explanation
- [ ] one-owner invariant and failure/recovery reasoning
- [ ] one changed scale or mapping requirement discussed
- [ ] comparison with the reference only after the attempt
