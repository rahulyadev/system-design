# Instructor task, lab, and solution standard

## Purpose

The course task is part of the lecture, not an optional extra. A task pack must let Rahul understand the request, predict behavior, attempt it without seeing the answer, run the smallest faithful setup, inspect what actually happens, and compare against a separate reference solution.

## Detect every assigned task

Search:

- the full transcript for homework, assignment, exercise, try, build, implement, design, calculate, simulate, or “before the next video” language;
- the final 20% of transcript/video carefully;
- final slides and slide speaker notes when available;
- demonstrations that end with an explicit learner action;
- `my-questions.md` for tasks Rahul specifically wants reconstructed.

Do not infer a course assignment from the lecture title. If no instructor task exists, record a completed scan with zero tasks.

## Preserve exact requirements without copying the course

`README.md` must contain:

1. a faithful original-language paraphrase;
2. source timestamp or slide reference;
3. a requirement-by-requirement checklist;
4. inputs, constraints, and outputs explicitly stated by the source;
5. ambiguities or missing constraints that the source leaves open;
6. what proves completion;
7. a short exact excerpt only when necessary to disambiguate wording, never a long copied prompt.

Do not silently expand an instructor task. Put Codex-added constraints or extensions under a separate heading.

## Canonical task pack

```text
tasks/<LECTURE-ID>-TNN/
├── task.json
├── README.md
├── ATTEMPT.md
├── RUBRIC.md
├── starter/                    # optional
├── tests/                      # optional
├── lab/                        # required when observation needs a runtime
│   ├── README.md
│   ├── compose.yaml            # optional, task-specific
│   ├── verify.py               # or another exact verification command
│   ├── fixtures/               # deterministic data/config
│   └── evidence.md
└── reference/
    ├── SOLUTION.md
    └── ...                     # reference implementation/config when useful
```

Required `task.json` fields:

```json
{
  "id": "SD-BEG-060-T01",
  "lecture_id": "SD-BEG-060",
  "source_timestamp": "00:42:10-00:44:05",
  "type": "experiment",
  "instructor_assigned": true,
  "runtime_required": true,
  "tools": ["docker", "postgresql"],
  "learner_status": "not_started",
  "reference_status": "verified",
  "execution_status": "passed"
}
```

Allowed task types: `reasoning`, `calculation`, `query`, `coding`, `experiment`, `design`, and `incident`.

Allowed execution states: `not_required`, `passed`, `failed`, and `skipped`. `passed` requires captured evidence from an actual command or reviewable deterministic check.

## Learner/reference separation

- `ATTEMPT.md`, `starter/`, and learner tests contain no completed answer.
- Hints progress from question framing to invariant to mechanism; the last hint still does not paste the solution.
- `reference/SOLUTION.md` begins with a spoiler warning and contains the complete reasoning.
- Reference code is never imported by learner tests.
- A validator may run the reference path, but it must not report the unsolved learner task as passing.
- Reruns never overwrite Rahul's attempt, starter edits, comments, outputs, or evidence.

## Setup-selection rule

Choose the smallest truthful setup:

| Learning question | Preferred setup |
|---|---|
| Ordering, estimates, capacity | Paper/Markdown calculation with assertions |
| Hash ring, Bloom filter, token bucket | Deterministic Python simulation; add a visual client only if inputs need exploration |
| SQL isolation, locks, replication concepts | Disposable PostgreSQL with deterministic schema/data and coordinated sessions |
| Cache behavior | App simulation first; real Redis only when Redis semantics matter |
| Queue delivery, acknowledgements, retries | Task-local RabbitMQ only when broker semantics matter |
| Streams, offsets, partitions, consumer groups | Task-local Kafka-compatible setup only when real log semantics matter |
| Object storage | Local files first; MinIO/S3-compatible service only for API/durability behavior |
| Load balancing/proxy behavior | Two tiny identifiable servers plus a task-local proxy |
| Leader election/failover | Small deterministic simulation unless real process/network failure is the lesson |
| Full system design | Design canvas, estimates, APIs, data model, failure table, and defended alternatives |

Do not add infrastructure merely to make the task look substantial.

## Reusable PostgreSQL

The root Compose file provides a loopback-only PostgreSQL profile for ordinary database exercises:

```bash
cp .env.example .env
docker compose --profile postgres up -d postgres
docker compose ps postgres
docker compose exec -T postgres sh -lc \
  'pg_isready -U "$POSTGRES_USER" -d "$POSTGRES_DB"'
```

Generated PostgreSQL tasks must use either:

- a unique allowlisted schema in this disposable database; or
- their own uniquely named Compose project/volume when crash, recovery, configuration, or destructive behavior requires isolation.

Each task owns `00_schema.sql`, deterministic seed data, assertions, and an exact reset. It must not depend on another task's residual state.

## Evidence contract

`lab/evidence.md` separates:

| Section | Meaning |
|---|---|
| Prediction | Rahul's expectation before execution |
| Expected behavior | Reasoned result derived from the mechanism |
| Actual run | Commands that genuinely ran |
| Observed evidence | Exact relevant output, state, metric, plan, or screenshot generated locally |
| Comparison | Why prediction and observation agree or differ |
| Variation | One changed condition and its new prediction/result |

Never put plausible-looking synthetic logs in “Observed evidence.” Use `Skipped` with an exact reason when execution cannot run.

## Required visual for a task

Every non-trivial task includes at least one of:

- input/intermediate/output table;
- request or event sequence;
- state transition;
- shard/partition ownership map;
- transaction/lock timeline;
- failure/recovery path;
- measured chart or plan tree.

It must explain how to read the visual, the key insight, and the simplification.

## Solution standard

A reference solution explains:

1. clarification and assumptions;
2. prediction;
3. approach and why it fits;
4. step-by-step implementation or design;
5. correctness invariant;
6. complexity/capacity where meaningful;
7. actual verification status and evidence link;
8. failure modes;
9. reasonable alternatives and why they were not selected;
10. SDE-2 and SDE-3 interview follow-ups.

The reference answer may disagree with a course simplification, but the boundary must be labeled respectfully and supported.

## Completion definitions

`reference_status: verified` means the reference implementation/design passed every available deterministic check. It does not mean Rahul attempted the task.

`learner_status: completed` requires Rahul's own attempt plus explanation. Opening the solution is not completion.
