# Rubric — SD-BEG-070-T01

Score evidence independently. Do not award completion for opening the reference answer or running only the reference verifier.

| Dimension | Needs work | SDE-2-ready | SDE-3-ready |
|---|---|---|---|
| Requirement understanding | Omits replication observation or one connection | Reconstructs two targets and request classification | Identifies unspecified freshness, ack point, failover, and security boundaries |
| Correctness/invariant | May send mutations to either node | One authoritative write path; replica is read-only | Proves route identity and handles transaction/read-after-write boundaries |
| Mechanism | Says “data syncs” | Traces binary log, receiver, relay/apply, visibility | Distinguishes received, durable, applied, and promoted states |
| Evidence | Trusts response labels | Captures server IDs, positions, rows, API statuses | Correlates API route, database state, and replica thread progress |
| Trade-offs | Says replicas make the DB faster | Compares read capacity with lag/cost | Quantifies freshness, headroom, failure, and connection budgets |
| Failure/recovery | Tests happy path only | Pauses/resumes the scoped applier and verifies catch-up | Defines fencing/failover limits, abort conditions, and remaining data risk |
| Communication | Lists commands | Explains cause and effect in order | Adapts the design when consistency, latency, or RPO changes |

## Required completion evidence

- [ ] Rahul’s own prediction before execution
- [ ] Rahul’s own two-pool API implementation
- [ ] exact task-local identity and health evidence
- [ ] baseline primary-to-replica row and position evidence
- [ ] paused-applier stale-read evidence
- [ ] resumed/caught-up replica evidence
- [ ] read-only replica write rejection
- [ ] mechanism and invariant explanation
- [ ] one changed requirement discussed
- [ ] comparison with the reference only after the attempt
