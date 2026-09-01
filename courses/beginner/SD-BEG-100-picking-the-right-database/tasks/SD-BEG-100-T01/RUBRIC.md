# Rubric — SD-BEG-100-T01

Score Rahul’s own evidence independently. Do not award completion for opening the reference answer.

| Dimension | Needs work | SDE-2-ready | SDE-3-ready |
|---|---|---|---|
| Source fidelity | Treats Codex-added constraints as instructor wording | Preserves the exploratory assignment and its ambiguity | Explains how ambiguity affects evidence and scope without inventing requirements |
| Requirement framing | Starts with favorite products | States invariants, access patterns, scale, and failure promises first | Separates hard constraints, preferences, and revisit thresholds |
| Cross-category mechanism | Says only “both can store JSON/keys” | Names exact constraints, conditions, TTLs, indexes, transactions, documents, or traversals | Connects mechanism to ownership, concurrency, and distribution boundaries |
| Correctness/invariant | Reports a result without a rule | Shows how each candidate preserves or weakens one invariant | Designs reconciliation or coordination and names remaining inconsistency windows |
| Evidence | Repeats marketing/category claims | Uses official capability evidence or genuine observation with limits | Distinguishes capability, configuration, workload proof, and missing evidence |
| Trade-offs | Declares one database best | Shows natural fit, forced fit, and extra application/operational cost | Quantifies the threshold at which the decision changes |
| Failure/recovery | Covers only the happy path | Traces one concurrency, dependency, or recovery failure | Defines degradation, authority, replay/repair, metrics, and operational owner |
| Variation | Changes a requirement but not the decision trail | Re-evaluates after one scale/consistency/latency/durability/availability/cost change | Explains which boundary moved and which earlier evidence became invalid |
| Communication | Uses SQL/NoSQL slogans | Gives a clear requirements → mechanism → evidence → decision explanation | Leads clarification and defends alternatives without product tribalism |

## Required completion evidence

- [ ] Rahul’s own prediction before reading the reference
- [ ] two workload definitions with invariants and access patterns
- [ ] natural and crossed candidate mappings
- [ ] exact capability evidence and proof limitations
- [ ] one failure trace and recovery/remaining risk
- [ ] one changed condition with a fresh prediction
- [ ] Rahul’s own two-minute explanation
- [ ] comparison with the reference only after the attempt
