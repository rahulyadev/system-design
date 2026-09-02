# My attempt - SD-BEG-130-T01

This file belongs to Rahul. Initialization and repair must never overwrite it.

Do not open `reference/SOLUTION.md` until you have written the prediction and completed your first provider attempt. Do not record passwords, API tokens, account/zone/property IDs, personal email, private hostnames, or unredacted dashboard screenshots.

## Clarifications and assumptions

- Provider/product selected:
- Why I am authorized to use this non-production account/domain/origin (no identifiers):
- Current official documentation links and checked date:
- Test hostname (redact if private):
- Origin type and region (no credentials):
- Synthetic image path, byte size, and version/hash:
- Origin `Cache-Control`, validator, and content type:
- Provider cache rule/TTL/key behavior in my own words:
- Browser-cache policy:
- Expected monetary cost and request limit:
- Exact cleanup target and recovery plan:
- Source ambiguity I had to resolve:

## Prediction before running or designing

- First unique-URL request edge status and origin effect:
- Second equivalent request edge status and origin effect:
- Evidence I expect for a miss:
- Evidence I expect for a hit:
- Effective cache key and safe reuse scope:
- Maximum accepted stale age:
- Same-URL origin-change prediction before expiry:
- Exact-URL purge prediction:
- What the purge cannot force a browser to do:
- Failure/bypass I expect might occur:
- Evidence that would falsify my explanation:

## My approach

Describe the account/onboarding boundary, disposable origin and DNS path, image policy, requests, narrow purge, implementation example, and cleanup. Explain why no production or shared resource is in scope.

Do not copy a complete provider tutorial. Record the decisions you made and the evidence that settled them.

## Actual evidence I observed

Do not paste expected or reference output here as observed evidence. Redact tokens, IDs, email, cookies, private hosts, account-specific URLs, and full screenshots.

- Provider/date/product:
- Exact request form with safe/redacted hostname:
- First response: status, cache status, `Age`, `Cache-Control`, edge evidence, image version/hash:
- Matching origin evidence for first response:
- Repeated response: status, cache status, `Age`, edge evidence, image version/hash:
- Matching origin evidence for repeated response:
- Same-URL origin change: old/new version, timing, edge/browser evidence:
- Exact-URL purge: target, provider acknowledgement, next response, origin evidence:
- Unexpected redirect, cookie, key, bypass, eviction, routing, or certificate behavior:
- What this evidence proves:
- What this evidence does not prove:

## Explanation in my own words

Use: client → routing → edge key/eligibility → fresh hit or origin miss → store/return → expiry/revalidation/eviction/purge. State separately what the browser may cache and which system owns the authoritative image.

Then map one documentation/video implementation example:

- Requirement:
- Cache level/key/freshness/invalidation:
- Benefit:
- Cost or failure mode:
- Observable evidence:

## Variation prediction and result

- Changed condition:
- Prediction made before change:
- Actual result and narrow evidence:
- Why:
- Which conclusion still holds:

## Cleanup evidence

- Exact resources inspected before cleanup:
- Exact narrow action taken, or why retained:
- Confirmation production/shared resources were untouched:
- Remaining cost/exposure and removal date, if retained:

## Local companion boundary

- Did I run `python3 lab/verify.py` after my prediction?
- Which mechanism did it clarify?
- Why does it not prove provider routing, headers, latency, propagation, or task completion?

## What I would say in an interview

Use: requirement and public/private scope → origin and cache key → first miss/later hit → freshness and invalidation → evidence → failure/recovery → one changed requirement.

## Questions after attempting

-
