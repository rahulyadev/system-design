# Workflow for an instructor-assigned task

## 1. Extract the assignment faithfully

Record the timestamp/range, faithful paraphrase, every stated requirement, inputs, constraints, requested output, and unclear points. Separate source requirements from Codex-added safety or verification.

Assign IDs in source order:

```text
<LECTURE-ID>-T01
<LECTURE-ID>-T02
```

## 2. Classify the evidence

Choose one primary type:

- reasoning;
- calculation;
- query;
- coding;
- experiment;
- design;
- incident.

Then decide what would genuinely prove completion. A design answer needs a decision trail and defended trade-offs; a runtime claim needs execution evidence.

## 3. Create the learner side first

Write the task README, attempt canvas, rubric, starter files, deterministic fixtures, and learner-facing verification. Do not include a complete answer.

Hints use boundaries:

1. clarify the requirement;
2. identify the invariant;
3. identify relevant mechanism;
4. suggest one observation;
5. stop before implementation/answer.

## 4. Build the smallest runtime

When tools are required:

1. identify whether the root PostgreSQL profile suffices;
2. otherwise create a task-local Compose file with exact image tags;
3. bind ports to loopback;
4. use deterministic synthetic data;
5. verify Docker context, Compose project, service, database/schema, and volume before destructive actions;
6. add health and readiness checks;
7. add an exact reset and scoped cleanup;
8. document CPU, memory, disk, and expected run time.

Do not require cloud credentials for a mandatory task when a local equivalent can demonstrate the mechanism.

## 5. Create and verify the reference path

Build the answer under `reference/`. Run reference checks when possible. Capture only relevant evidence and label the exact environment. If execution cannot run, set `execution_status` to `skipped`; do not claim verification.

## 6. Show behavior visibly

Use at least one precise trace:

- before/after table;
- session timeline;
- message lifecycle;
- partition or ownership map;
- request flow;
- failure/recovery sequence;
- capacity calculation;
- measured plan/metric.

Explain why the state changed.

## 7. Preserve Rahul's attempt

When Rahul starts, update only learner-owned status/evidence. Do not regenerate or normalize his answer. Compare it with the rubric and reference only after he commits to an approach.

## 8. Vary one condition

After the baseline, change one meaningful property: concurrency, skew, consistency, latency, failure, ordering, durability, capacity, or cost. Require a fresh prediction before running or answering.
