# Rubric — SD-BEG-050-T01

| Dimension | Needs work | SDE-2-ready | SDE-3-ready |
|---|---|---|---|
| Requirement | Missing output grain | Returns exact deterministic rows | Exposes ambiguity and ownership boundary |
| Correctness | Relies on prose | Database constraint preserves local invariant | Explains concurrent writers and migration behavior |
| Evidence | Assumes outcome | Captures query result and constraint failure | States remaining proof gap |
| Communication | Names a join only | Traces keys and rows clearly | Adapts when ownership crosses services |

## Required completion evidence

- [ ] Rahul's prediction and own query
- [ ] deterministic result
- [ ] orphan failure
- [ ] mechanism explanation
- [ ] changed-condition reasoning
