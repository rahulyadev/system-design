# Decision canvas — SD-BEG-100-T01

Do not put product names in section 1. This canvas contains no completed answer.

## 1. Workloads before products

| Field | Workload A | Workload B |
|---|---|---|
| Business command/read |  |  |
| Correctness invariant |  |  |
| Complete access pattern |  |  |
| Data size and growth |  |  |
| Average/peak operations per second |  |  |
| Skew/hot-key assumption |  |  |
| Consistency and durability target |  |  |
| Failure/degraded behavior |  |  |

## 2. Candidate properties

| Candidate | Exact useful operation/guarantee | Evidence | Configuration/boundary | What remains unproved |
|---|---|---|---|---|
| A |  |  |  |  |
| B |  |  |  |  |

## 3. Natural and crossed fit

| Mapping | What becomes easy/local/bounded | What becomes hard or unsafe | Extra application/operations work | Decision and condition |
|---|---|---|---|---|
| Candidate A → Workload A |  |  |  |  |
| Candidate B → Workload B |  |  |  |  |
| Candidate A → Workload B |  |  |  |  |
| Candidate B → Workload A |  |  |  |  |

## 4. Failure trace

```text
Initial state:
Action or concurrent events:
Observed/expected state transition:
Invariant at risk:
Evidence to inspect:
Recovery:
Remaining risk:
```

## 5. Changed condition

- One changed scale/consistency/latency/durability/availability/query/cost condition:
- Prediction before revisiting:
- Which earlier assumption or evidence is invalid now:
- Revised decision:

## 6. Two-minute explanation outline

1. Requirements
2. Candidate mechanisms
3. Natural versus forced fit
4. Evidence and missing proof
5. Decision and rejected alternative
6. Failure/recovery
7. Changed requirement
