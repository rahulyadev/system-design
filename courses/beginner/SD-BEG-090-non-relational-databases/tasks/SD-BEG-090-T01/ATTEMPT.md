# My attempt - SD-BEG-090-T01

This file belongs to Rahul. Initialization and repair must never overwrite it. Complete it before opening the reference solution.

## Clarifications and assumptions

- Expected Docker context and endpoint:
- Exact Compose project:
- Why I am running services sequentially or together:
- What “play around” must prove beyond health:
- What this single-node lab cannot prove:

## Prediction before running or designing

### MongoDB

- Optional field that differs between documents:
- Stock before and after the atomic increment:
- Match/modify evidence I expect:
- Atomicity boundary:

### Redis

- Value after SET/GET:
- Counter before and after INCR:
- Existence after DELETE:
- Atomicity boundary:

### Neo4j

- Baseline Asha-to-Chen shortest path and hop count:
- Changed condition:
- Predicted new path and hop count:
- Traversal boundary:

## My approach

Describe the exact service order, task namespaces, commands/queries, and why each observation demonstrates a model capability. Do not paste the reference implementation.

## Actual evidence I observed

Record only commands and output you actually produced. Include:

- preflight identity and versions;
- MongoDB inserted/filtered/aggregated/updated state;
- Redis GET/INCR/DELETE state;
- Neo4j node/relationship counts and both path results;
- final stopped-service state.

Do not paste expected output here as observed evidence.

## Explanation in my own words

### Document model

Explain aggregate shape, flexible fields, partial update, and why a one-document observation says nothing about multi-document or sharded guarantees.

### Key-value model

Explain exact-key routing, `SET` versus conceptual PUT, single-command atomicity, and the secondary-query limitation.

### Graph model

Explain nodes, directed relationships, bounded traversal, and why one extra edge changes the shortest path.

## Variation prediction and result

- Changed condition: add the direct `Asha -> Chen` `FOLLOWS` relationship.
- Prediction made before the change:
- Baseline result:
- Actual changed result:
- Why:
- What this variation still does not prove:

## Failure and recovery notes

| Model | Likely failure | Evidence/metric | Safe response |
|---|---|---|---|
| Document |  |  |  |
| Key-value |  |  |  |
| Graph |  |  |  |

## Model comparison

| Model | Easy access pattern | Awkward access pattern | Observed atomic/transaction scope | When I would not choose it |
|---|---|---|---|---|
| Document |  |  |  |  |
| Key-value |  |  |  |  |
| Graph |  |  |  |  |

## What I would say in an interview

Use this order: access patterns -> correctness/scale assumptions -> chosen model and product topology -> ownership/atomicity mechanism -> evidence -> failure/recovery -> observability -> alternative -> changed requirement.

## Questions after attempting

- Add questions here after the attempt.
