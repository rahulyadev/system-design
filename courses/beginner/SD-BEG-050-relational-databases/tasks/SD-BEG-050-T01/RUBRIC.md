# Rubric — SD-BEG-050-T01

Score evidence independently. Do not award completion for opening the reference answer or for the verified reference run.

| Dimension | Needs work | SDE-2-ready | SDE-3-ready |
|---|---|---|---|
| Requirement understanding | Builds unrelated tables or misses the interruption | Reconstructs the social schema and user/profile transaction faithfully | Separates source requirements, open choices, and Codex safety additions |
| Data model | Names tables without ownership or keys | Models identity, one-to-one profile, and chosen relationships with suitable keys | Defends optionality, delete policy, indexing boundaries, and migration pressure |
| Correctness/invariant | Says "ACID handles it" | States that a required pair is `0/0` or `1/1` and places both writes in one transaction | Covers ambiguous commit, retries, external effects, and concurrent counterexamples |
| Mechanism | Reports counts without cause | Explains commit/abort and crash recovery in order | Connects WAL, visibility, configuration, and failure domain without overclaiming |
| Safety | Runs broad Docker/database commands | Verifies local context, exact project/service, loopback port, database/schema, and volume | Adds abort conditions, scoped recovery, and operational ownership |
| Evidence | Copies expected output | Captures genuine preflight, crash, recovery, counts, server version, and cleanup | Distinguishes proof, correlation, missing evidence, and experiment limitation |
| Variation | Repeats the same run | Commits before the same crash and predicts first | Explains which changed condition caused the new outcome and proposes a second useful variation |
| Trade-offs | Declares constraints/transactions universally best | Compares explicit transaction, constraint, cascade, trigger, and derived data where relevant | Quantifies a contention/durability threshold for revisiting the choice |
| Failure/recovery | Covers only happy-path inserts | Diagnoses constraint error, open-transaction crash, and restart | Covers ambiguous result, retry storm, disk loss, backup/restore, and recovery ownership |
| Communication | Uses ACID as a list of labels | Gives a clear problem -> invariant -> mechanism -> evidence explanation | Leads clarification and adapts to changed concurrency, latency, durability, or region requirements |

## Required completion evidence

- [ ] Rahul's own prediction recorded before execution
- [ ] Rahul's own schema and transaction attempt
- [ ] requirement-to-constraint relationship table
- [ ] verified local failure-injection identity and abort condition
- [ ] genuine open-transaction crash/recovery output
- [ ] genuine committed variation output
- [ ] explanation of atomicity versus durability
- [ ] one failure/observability discussion
- [ ] one remaining proof gap
- [ ] comparison with the reference only after the attempt
