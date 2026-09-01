# My attempt — SD-BEG-070-T01

This file belongs to Rahul. Initialization and repair must never overwrite it. Complete it before opening the reference solution.

## Clarifications and assumptions

- Which requests may tolerate stale data?
- What does a successful write prove in the selected replication mode?
- What exact server identities and ports am I expecting?

## Prediction before running or designing

- POST target and expected server ID:
- Eventual GET target and expected server ID:
- Strong GET target and expected server ID:
- Expected result while the replica applier is paused:
- Why:
- Write-routing invariant:
- Evidence I expect from the API:
- Evidence I expect from direct database inspection:

## My approach

Describe the two pools, the routing boundary, request validation, table, replica configuration, and how errors preserve the invariant. Do not paste the reference implementation.

## Actual evidence I observed

Record only commands and output you actually produced. Include service/server identity, replica receiver/applier state, source position, database rows, HTTP status, and which target answered. Do not paste expected output as observed evidence.

## Explanation in my own words

Explain local commit, binary-log position, receive/relay state, apply/query-visible state, and why one read can be stale after a successful write.

## Variation prediction and result

- Changed condition: pause only the replica SQL/applier thread.
- Prediction:
- Primary/strong-read result:
- Replica/eventual-read result before catch-up:
- Replica result after resume and catch-up:
- Why:

## Failure and recovery notes

- Symptom I would alert on:
- Evidence that distinguishes receiver failure from applier failure:
- Safe recovery and abort condition:
- Remaining risk after recovery:

## What I would say in an interview

Use this order: requirement and freshness → two pools → authoritative write invariant → replication mechanism → lag evidence → trade-off → failure/recovery → changed consistency requirement.

## Questions after attempting

- Add questions here after the attempt.
