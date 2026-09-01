# My attempt — SD-BEG-050-T01

This file belongs to Rahul. Initialization and repair must never overwrite it.

## Clarifications and assumptions

- Is a profile mandatory at signup, or may it be created later?
- Which social-network entities will I include beyond the required user/profile experiment?
- What should happen to each child when a user is deleted?
- Which database and version am I using?

## Prediction before running or designing

- Expected result/state after interruption before commit:
- Why:
- Invariant:
- Evidence I expect:
- Expected result after successful commit followed by the same interruption:

## My schema and relationship decisions

| Table/relationship | Ownership and cardinality | Constraint | Invalid state prevented |
|---|---|---|---|

## My approach

Record commands and decisions in your own words. Do not paste the reference implementation.

## Actual evidence I observed

Do not paste expected output here as observed evidence. Include the verified context/project/service/database/schema/volume identities, actual commands, narrow relevant output, and cleanup status.

## Explanation in my own words

Explain the open-transaction result first. Then explain the committed variation. Keep atomicity and durability distinct.

## Variation prediction and result

- Changed condition:
- Prediction made before running:
- Actual result:
- Why:

## Failure, observability, and remaining proof gap

- One failure I can now diagnose:
- Evidence/metric/query I would inspect in production:
- What this local experiment does not prove:

## What I would say in an interview

Use a reasoning outline: requirement -> invariant -> schema/transaction boundary -> crash outcomes -> concurrency/durability caveat -> evidence -> trade-off.

## Questions after attempting
