# Interview questions — <Lecture title>

Answer aloud before opening the answer outline. Draw when the question involves components, order, or state.

## Foundation

### Q1. <Definition or purpose question>

**Strong answer must mention:**

- <problem>
- <core mechanism>
- <important boundary>

**Answer outline:**

1. <assumption or definition>
2. <mechanism>
3. <short example>

**Weak-answer trap:** <plausible but incomplete answer and why it is weak>

**Follow-up:** <question that tests understanding rather than memory>

## Working engineer

### Q2. <Implementation, debugging, or concurrency question>

**Clarify first:**

- <environment/version/workload question>

**Reasoning path:**

1. <observable symptom>
2. <candidate mechanism>
3. <evidence to collect>
4. <decision and trade-off>

**Likely follow-ups:**

- <follow-up>

## Senior design

### Q3. <Requirement and trade-off question>

**Requirements to clarify:**

- <scale, consistency, latency, durability, cost, availability, or compliance>

**Back-of-the-envelope estimate:**

- Assumptions: <values and units>
- Calculation: <equation>
- Sanity check: <why the result is plausible>

**Decision outline:**

1. <initial choice>
2. <why it fits>
3. <rejected alternative and when it would win>
4. <failure and recovery>
5. <observability>

**Requirement change:** <interviewer changes one constraint>

**How the design should evolve:** <decision, not a memorized full architecture>

## Failure and debugging round

### Scenario

<Concrete symptom with enough evidence to reason, but no answer embedded.>

Questions:

1. What are the top hypotheses?
2. What evidence distinguishes them?
3. What is the safest immediate mitigation?
4. What durable design change prevents recurrence?

## Rapid compare/contrast

| Prompt | Deciding dimension | Short answer cue |
|---|---|---|
| <A vs B> | <dimension> | <cue, not full answer> |

## Experience connection

<A truthful, non-confidential way to connect the concept to Python/FastAPI, database, caching, queue, AWS, or migration work. Do not invent a project claim.>

## Self-score

| Dimension | 0 | 1 | 2 |
|---|---|---|---|
| Mechanism | Missing | Partly correct | Correct and causal |
| Trade-offs | None | Generic | Requirement-specific |
| Failure handling | Ignored | Names a failure | Detects, mitigates, and recovers |
| Evidence | Guessing | One signal | Distinguishes hypotheses |
| Communication | Memorized | Understandable | Structured and adaptable |

