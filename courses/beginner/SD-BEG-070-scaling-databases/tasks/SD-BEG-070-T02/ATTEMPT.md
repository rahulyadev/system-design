# My attempt — SD-BEG-070-T02

This file belongs to Rahul. Initialization and repair must never overwrite it. Complete it before opening the reference solution.

## Clarifications and assumptions

- Exact valid key grammar:
- Case-normalization rule:
- Meaning of “owner” and behavior for a key with no owner:
- Whether range scans or cross-shard operations are in scope:

## Prediction before running or designing

| Key | Normalized key | Predicted shard | Predicted server ID | Why |
|---|---|---|---:|---|
| `apple` | | | | |
| `mango` | | | | |
| `nectar` | | | | |
| `zebra` | | | | |

- One-owner invariant:
- Invalid-key prediction:
- Evidence I expect on the correct shard:
- Evidence I expect on the wrong shard:
- 20 `a-hot-*` versus two `z-cold-*` prediction:

## My approach

Describe the validation/normalization boundary, two pools, routing function, schema, API paths, and error behavior. Do not paste the reference implementation.

## Actual evidence I observed

Record only commands and output you actually produced. Include project/service identity, server IDs, API status and owner, exact physical rows on both shards, invalid-key state, and per-range counts.

## Explanation in my own words

Explain why the subsets are mutually exclusive, why reads and writes must share the mapping, and why nominal aggregate capacity can be misleading under skew.

## Variation prediction and result

- Changed condition: 20 `a-hot-*` keys and two `z-cold-*` keys.
- Prediction:
- Shard A–M count:
- Shard N–Z count:
- Actual ratio:
- Why:
- One mitigation and its migration risk:

## Failure and recovery notes

- Symptom of a wrong mapping:
- Trace/metric that identifies the selected mapping version:
- Safe behavior when one shard is unavailable:
- Remaining cross-shard risk:

## What I would say in an interview

Use this order: requirements → key/access pattern → one-owner invariant → routing → estimates/skew → failure/recovery → observability → resharding → alternative.

## Questions after attempting

- Add questions here after the attempt.
