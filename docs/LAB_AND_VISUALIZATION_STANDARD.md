# Lab and visualization standard

## Purpose

A practical artifact exists to reveal behavior that prose alone hides. It should answer a concrete question and make a wrong mental model easy to detect.

## Choose the smallest useful artifact

| Artifact | Typical time | Use when | Example |
|---|---:|---|---|
| Paper or query drill | 10–20 min | Arithmetic or ordering is the lesson | Capacity estimate, transaction schedule |
| Micro-lab | 30–90 min | One mechanism needs observable evidence | Isolation anomaly in two SQL sessions |
| Visualizer | 1–4 h | State changes with inputs and spatial intuition matters | Consistent-hash ring, token bucket |
| Integration lab | 2–6 h | Two or three components interact | Cache stampede with app, Redis, and database |
| Capstone | Multiple sessions | Many topics must be combined and defended | URL shortener or notification platform |

Do not create a UI for a concept that two terminal sessions explain more precisely.

## Required learning contract

Every lab README begins with:

1. **Question:** what behavior are we testing?
2. **Prior mental model:** what does Rahul currently expect?
3. **Prediction:** exact expected output or state.
4. **Variables:** what changes and what stays fixed?
5. **Evidence:** which query, log, metric, trace, or state proves the result?
6. **Explanation:** what mechanism caused it?
7. **Variation:** what one change should produce a different result?

## Default technical choices

- Python 3 for services, clients, experiment orchestration, and tests.
- FastAPI only when an HTTP boundary is part of the lesson; otherwise use a smaller script.
- Docker Compose for PostgreSQL, Redis, Kafka-compatible services, or other disposable infrastructure.
- `pytest` for deterministic behavior.
- Structured logs with correlation IDs when concurrency or asynchronous flows are involved.
- A simple React/Vite UI only for interactive visualizers where motion, input, or state inspection adds real value.
- Mermaid for static architecture and sequence documentation.

Pin meaningful dependency versions and explain version-sensitive behavior.

## Standard lab layout

```text
labs/<lab-slug>/
├── README.md
├── docker-compose.yml        # when infrastructure is needed
├── Makefile                  # optional short task interface
├── src/
├── tests/
├── scripts/
├── observations/             # small original results, never raw course files
└── .env.example
```

The README includes prerequisites, setup, health check, experiments, expected evidence, troubleshooting, cleanup, and related lecture links.

## Safety rules

- Use disposable containers and named lab-specific volumes for data-loss, crash, network, and concurrency experiments.
- Print the exact target container or resource before destructive failure injection.
- Never use host-wide process killing, broad filesystem deletion, or an existing database.
- Distinguish graceful shutdown from process termination and machine-style crash; they test different guarantees.
- Provide a cleanup command and explain whether it preserves or deletes the disposable volume.
- Redact credentials and use non-secret local defaults in `.env.example`.
- Put load limits in the scripts so a typo cannot generate uncontrolled traffic.

## PostgreSQL transaction and crash lab roadmap

The beginner database module should have one focused lab with disposable PostgreSQL and two or more client sessions.

### Experiments

1. **Atomic commit and rollback:** change multiple rows, force an error, and inspect which changes survive.
2. **Read Committed:** demonstrate statement-level snapshots and a non-repeatable read when supported by the schedule.
3. **Repeatable Read:** repeat the schedule and observe the stable transaction snapshot plus conflict behavior.
4. **Serializable:** create a dangerous concurrent pattern and observe serialization failure; retry safely.
5. **Locks:** hold a row lock, inspect blockers/waiters, then release or terminate the client backend.
6. **Client failure:** kill the client connection during an open transaction and verify rollback.
7. **Database-process crash:** kill only the disposable PostgreSQL container during uncommitted and committed transactions, restart it, and inspect atomicity/durability.
8. **Crash recovery evidence:** inspect PostgreSQL logs and data after restart; explain Write-Ahead Logging (WAL) at the level supported by the lecture and official docs.

Before every experiment Rahul writes a prediction. The lab must clearly distinguish terminating one database session, stopping the server gracefully, and killing the server process abruptly.

## High-value beginner labs and visualizers

| Topic cluster | Artifact | Core question |
|---|---|---|
| Relational DB and isolation | PostgreSQL transaction lab | Which values can concurrent transactions observe, and what survives failure? |
| Scaling and partitioning | Query-routing simulator | How does key choice affect balance and cross-partition work? |
| Cache population | Cache-stampede lab | What happens when many misses arrive together? |
| Queues versus streams | Delivery-semantics lab | What changes with acknowledgement, replay, and consumer position? |
| Load balancing and breakers | Failure-control lab | How do timeout, retry, breaker, and health checks interact? |
| Bloom filters | Probability visualizer | How do bit-array size and hash count change false positives? |
| Consistent hashing | Ring visualizer | How many keys move when a node joins or leaves? |
| Rate limiting | Token/leaky/sliding-window visualizer | Which traffic bursts are allowed or rejected? |

## Visualizer interaction standard

An executable visualizer should expose:

- adjustable inputs with valid ranges and units;
- current internal state, not only final output;
- step, play, pause, and reset where order matters;
- an event log that explains each transition;
- a deterministic seed for repeatable examples;
- at least one preset that demonstrates the key failure or edge case;
- an explanation panel connecting the animation to the formal algorithm;
- tests for the underlying algorithm independent of the UI.

Animation must not hide causality. Users should be able to step one event at a time.

## Capstone evolution

Use a capstone as a design history, not a final architecture dropped all at once.

For each evolution step record:

1. new functional or non-functional requirement;
2. observed limit in the current design;
3. decision and rejected alternatives;
4. data model or API change;
5. failure behavior and recovery;
6. capacity estimate;
7. validation evidence;
8. new complexity introduced.

Keep Architecture Decision Records (ADRs) for major changes. A senior interview is often a discussion of this evolution, not a drawing contest.

## Verification before handoff

- Start from a clean checkout or clean lab state.
- Run setup and health checks.
- Run automated tests.
- Execute at least the principal manual experiment.
- Compare observed and documented output.
- Run cleanup and confirm it affects only the lab resources.
- Review the diff for private inputs, generated bulk data, secrets, or accidental course material.

