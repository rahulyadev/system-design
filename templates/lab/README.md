# Runtime lab — <TASK-ID>

## Question this lab answers

<One observable mechanism, not “run the technology.”>

## Tool-selection justification

- Selected profile: `<profile from data/tool_profiles.json>`
- Why a real runtime is needed: <reason>
- Why a smaller simulation is insufficient: <reason>
- Version and primary source checked on: <exact version, URL, date>

## Resource budget

| Resource | Estimate |
|---|---|
| CPU | <estimate> |
| Memory | <estimate> |
| Disk/images | <estimate> |
| Startup | <estimate> |
| Data generation | <estimate> |

## Safety preflight

Print and verify the exact local context, project/service, loopback ports, task-owned state, labels, and reset target. Stop on any mismatch.

## Start and health check

```bash
# Exact commands. Use a unique task-local Compose project when compose.yaml exists.
```

## Deterministic setup

```bash
# Exact schema/topology/fixture commands.
```

## Predict before running

Record the expected state transition and evidence in `../ATTEMPT.md`.

## Run

```bash
# Exact learner command(s).
```

## Inspect what happened

```bash
# Exact state/metric/query/log command(s); keep output narrow.
```

## Vary one condition

<One useful controlled change and a fresh prediction.>

## Reset and cleanup

Show and verify the exact target before changing it. Remove only task-owned state. State whether the action is recoverable.

## Troubleshooting

| Symptom | Check | Likely cause | Safe repair |
|---|---|---|---|
| <symptom> | <command/evidence> | <cause> | <repair> |

Record genuine results in [`evidence.md`](evidence.md).
