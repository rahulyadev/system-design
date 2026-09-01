# SD-BEG-100-T01 — Explore overlap between database types

> Instructor-assigned exercise from `SD-BEG-100`. Attempt before opening `reference/SOLUTION.md`.

## Source and fidelity

- Source timestamp: `00:11:56–00:12:11`.
- Faithful paraphrase: choose databases you find useful or familiar, explore their distinctive properties, and investigate how one type of database can serve a workload normally associated with another type. Approach the comparison creatively and curiously instead of defending a fixed database category.
- Short exact excerpt: Not needed; the requirements can be preserved without quoting the source.
- Source ambiguity: the instructor does not specify how many databases to choose, which workload to use, whether “play around” requires a live runtime, what implementation language to use, what artifact to submit, or what result counts as success.

The source’s learning intent is **category overlap**: discover what a database can actually do, then identify the guarantees or operational cost hidden by a broad label.

## Exact requirement checklist

- [ ] Choose one or more databases to explore.
- [ ] Investigate the distinctive properties those databases provide.
- [ ] Try or reason through how a database from one broad type could serve a workload commonly associated with another type.
- [ ] Compare based on actual behavior or properties rather than loyalty to a favorite category.
- [ ] Explore with curiosity and record what becomes easier, harder, or unsafe.

The source does **not** require a cloud service, production data, a specific product pair, or a runnable implementation.

## Codex-added safety or verification

The items below make the open-ended exercise reviewable. They are additions, not instructor wording:

- Compare at least two database families and two workload shapes.
- State one invariant and one complete access pattern for each workload.
- Separate “technically possible” from “natural, safe, and operable.”
- Support product-capability claims with official documentation or genuine local evidence.
- Change one requirement and revisit the answer.
- Do not connect to a production, employer, shared, or personal database. A runtime is optional; if used, keep it disposable, synthetic, local, and separately documented before running it.

## Inputs, constraints, and expected artifact

| Item | Contract |
|---|---|
| Input | Database candidates Rahul chooses, plus two small workload shapes |
| Source constraints | Explore distinctive properties and cross-category fit; no fixed products, scale, runtime, or output were specified |
| Codex-added assumptions | At least two families, two workloads, one invariant/access pattern per workload, and one changed requirement |
| Output | Completed [`starter/DECISION_CANVAS.md`](starter/DECISION_CANVAS.md) or an equivalent decision note |
| Completion evidence | Rahul’s prediction, capability evidence, fit/loss analysis, defended choice, failure behavior, and variation |

### Question this visual answers

What reasoning must connect a workload to a defensible database comparison?

| Stage | What to record | Why it matters |
|---|---|---|
| Input | Invariant, access pattern, scale, failure promise | Prevents product-first reasoning |
| Candidate mechanism | Exact operation/guarantee each database provides | Replaces category slogans with testable facts |
| Fit | What becomes local, bounded, or atomic | Shows why the candidate helps |
| Loss/cost | What needs a scan, protocol, duplicate copy, coordination, or extra operator | Shows the price of forcing the fit |
| Evidence | Official capability or genuine observation | Separates belief from proof |
| Decision | Prefer, reject, or accept conditionally | Produces a reviewable conclusion |

### How to read this visual

Read one workload from top to bottom. Do not jump from input directly to a product. A candidate earns a decision only after both its useful mechanism and lost guarantee/extra cost are visible.

### Key insight

Many databases can technically imitate another category’s basic storage shape. The important difference is which invariants and access patterns remain natural at the required scale and failure boundary.

### Simplification or limitation

The table does not benchmark a real deployment and cannot prove product-specific latency, durability, or failure behavior. Runtime claims still require an actual controlled experiment.

## Before you start: predict

Write in `ATTEMPT.md` before opening the reference:

1. which database pair you will explore;
2. which workload each is usually associated with;
3. where you expect the cross-category fit to work;
4. which invariant, query, or operational property you expect to become harder;
5. what evidence could disprove your prediction.

## Setup

No runtime is required because the source specifies no product or executable outcome. Use the design canvas and official product documentation.

If Rahul voluntarily adds a runtime later, define its exact database/version, synthetic fixtures, loopback-only network, resource budget, preflight identity, reset, cleanup, prediction, and observed evidence before execution. That optional runtime must not overwrite this attempt or turn expected output into claimed observation.

## Learner steps

1. Choose two database families and name exact candidate products only after writing the workload needs.
2. Define workload A and B with one invariant, one access pattern, scale, consistency/durability target, and failure promise each.
3. Write why candidate A naturally fits workload A and candidate B naturally fits workload B.
4. Cross the mapping: assess candidate A for workload B and candidate B for workload A.
5. Identify the mechanism that makes each crossed fit possible.
6. Identify the lost guarantee, extra application protocol, query amplification, capacity risk, or operational burden.
7. Record evidence and decide: prefer, reject, or accept under named conditions.
8. Change one condition—scale, consistency, latency, durability, availability, query flexibility, or cost—and decide again.
9. Explain the result aloud without saying only “SQL” or “NoSQL.”

## Progressive hints

<details><summary>Hint 1 — requirement</summary><p>Start with a business command and read query, not with JSON versus tables.</p></details>

<details><summary>Hint 2 — invariant</summary><p>Choose one rule that must survive concurrency, such as unique idempotency or non-negative inventory.</p></details>

<details><summary>Hint 3 — mechanism</summary><p>Look for the exact conditional write, unique constraint, transaction, TTL, index, document boundary, or traversal that serves the rule or query.</p></details>

<details><summary>Hint 4 — observation</summary><p>Ask what work crosses a document, partition, shard, or database and what metric or failure trace would reveal it.</p></details>

## Acceptance criteria

- [ ] Every faithful source requirement is addressed.
- [ ] The source’s unspecified runtime/output constraints remain labeled as unspecified.
- [ ] At least two families and two workloads are compared without product-first framing.
- [ ] Each workload has an invariant and complete access pattern.
- [ ] Each crossed fit names both a useful mechanism and a lost guarantee/extra cost.
- [ ] Capability claims have official or genuine observed evidence; predicted and observed behavior are not merged.
- [ ] One failure mode and one changed requirement alter or test the decision.
- [ ] Rahul can explain why “possible” and “right” are different in two minutes.

## Cleanup/reset

Reasoning-only baseline: no resources are created, so no cleanup is required.

For any learner-added runtime, stop only task-owned services and reset only verified synthetic task-owned data. Record the exact commands and recoverability before running them. Never use broad Docker cleanup, real credentials, or an existing database.

## Reference answer boundary

After committing to your own comparison, open [`reference/SOLUTION.md`](reference/SOLUTION.md). Its design is one example, not the instructor’s mandated product choice and not evidence that Rahul completed the exercise.
