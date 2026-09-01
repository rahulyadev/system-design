# Rubric — SD-BEG-060-T01

Score Rahul's evidence independently. Do not award completion for opening or running the reference answer.

| Dimension | Needs work | SDE-2-ready | SDE-3-ready |
|---|---|---|---|
| Requirement understanding | Lists level names only | Reconstructs one-row/two-session schedules with explicit commits | Separates source requirements from PostgreSQL-specific verification and names proof gaps |
| Prediction and invariant | Predicts after seeing output | Predicts every value/wait/error and states the deciding snapshot/commit condition | Writes falsifiable alternatives and connects the schedule to a business invariant |
| Isolation mechanism | Says “stronger is safer” | Explains statement snapshot, transaction snapshot, own writes, and PostgreSQL RU mapping | Distinguishes SQL minimum, engine guarantee, MVCC, explicit locks, and serial outcome |
| Serializable handling | Treats failure as unexpected | Captures `40001` and retries the whole transaction | Designs bounded jittered retry, idempotency, and external-effect boundaries |
| Evidence | Uses timing or expected output as proof | Captures level, values, SQLSTATE, wait event, blocker PID, and final state | Correlates attempt/application identity and distinguishes missing proof from negative evidence |
| Locking variation | Assumes a block | Proves `FOR UPDATE` waits behind the writer and plain read behaves differently | Explains compatibility, deadlock risk, lock ordering, and when atomic SQL is preferable |
| Safety and reset | Uses a broad database/Docker target | Verifies exact root service and resets only `sd_beg_060_t01` | Explains shared-service ownership and prevents cleanup from affecting parallel labs |
| Trade-offs | Ranks levels by speed | Chooses atomic SQL, lock, Repeatable Read, or Serializable from a concrete need | Quantifies hot-key/retry thresholds and defines when to revisit the decision |
| Communication | Memorized definitions | Gives a clear schedule-driven explanation | Leads with clarification, adapts to engine/scale changes, and rejects unjustified complexity |

## Required completion evidence

- [ ] Rahul's own predictions recorded before execution
- [ ] Rahul's own completed session scripts or command trace
- [ ] PostgreSQL identity/version and task-schema evidence
- [ ] Genuine Read Committed, Repeatable Read, and Read Uncommitted-mapping results
- [ ] Genuine Serializable failure/retry result
- [ ] Genuine lock wait and blocker evidence for the variation
- [ ] Mechanism explanation and engine comparison
- [ ] One operational failure/recovery plan
- [ ] One proof gap
- [ ] Closed-book spoken explanation
