# Rubric - SD-BEG-090-T01

Score learner evidence independently. Do not award completion for opening the reference answer or running only the supplied reference verifier.

| Dimension | Needs work | SDE-2-ready | SDE-3-ready |
|---|---|---|---|
| Requirement understanding | Starts containers but omits one database or capability | Completes all three source-required explorations | Separates source wording, added evidence, and product/topology boundaries |
| Correctness/invariant | Uses broad/unscoped data or assumes category guarantees | Keeps exact namespaces and states each observed atomic boundary | Distinguishes logical model, command/transaction scope, replication, partitioning, and authority |
| Mechanism | Lists commands | Traces document update, key command, and path traversal in order | Connects routing/planning/storage behavior to concurrency and failure evidence |
| Evidence | Reports “healthy” | Captures identities, versions, before/after state, path counts, and stop state | Explains what evidence falsifies, what remains unproved, and why causation is justified |
| Trade-offs | Says each product is fast/flexible | Names one fitting and one awkward pattern per model | Quantifies thresholds and defends a simpler relational or derived-projection alternative |
| Failure/recovery | Tests happy path only | Predicts one controlled graph change and uses scoped reset/stop | Covers hot keys, lost updates, traversal explosion, projection drift, abort conditions, and ownership |
| Communication | Uses category slogans | Gives a clear access-pattern-first comparison | Adapts naturally when consistency, latency, durability, availability, scale, or cost changes |

## Required completion evidence

- [ ] Rahul’s own prediction before executing each model
- [ ] preflight proof of exact local identity and safe namespaces
- [ ] MongoDB version, flexible-field evidence, and stock `2 -> 3` atomic update evidence
- [ ] Redis version, SET/GET, counter increment, and deletion/absence evidence
- [ ] Neo4j version, three-node/two-relationship baseline, and two-hop path evidence
- [ ] direct-edge prediction made before the one-hop variation
- [ ] Rahul’s own mechanism and model-comparison explanation
- [ ] one failure and useful metric per model
- [ ] stopped task services with retained recoverable volumes
- [ ] explicit statement of what the single-node experiment does not prove
- [ ] comparison with the reference only after Rahul commits to an attempt
