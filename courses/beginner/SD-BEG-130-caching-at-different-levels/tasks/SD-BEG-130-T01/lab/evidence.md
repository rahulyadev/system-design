# Runtime evidence - SD-BEG-130-T01 local companion

## Execution status

- Status: Passed
- Scope: Codex-added deterministic local companion only; not the assigned provider exercise
- Date/time: 2026-09-02T20:35:07+05:30
- Environment: Python 3.14.4, standard library only, no network/cloud/DNS/service/persistent state
- Assigned provider status: Rahul-owned and not started; this file must not be used as provider completion evidence

## Prediction

Reference prediction before execution: request 1 will miss and read origin once; request 2 after 10 fake seconds will hit `v1` without another origin read; replacing origin bytes at the same URL will not alter the still-fresh edge entry, so it will serve `v1` while origin owns `v2`; exact-key purge will force a miss and fill `v2`; a request exactly at the 300-second freshness boundary will be expired and contact origin again.

This is the reference author's prediction. Rahul must record his own prediction in `../ATTEMPT.md` before reading this evidence.

## Expected behavior

The edge can reuse an entry only while `current_time - stored_time < ttl`. Updating the origin changes no cache state. Purge removes only the exact modeled key. A miss or expired entry increments origin reads, stores the current authoritative bytes/version, and returns age zero.

## Actual run

~~~text
python3 lab/verify.py
~~~

The first implementation check exited `1` before any success marker because the dynamic import helper had not inserted the loaded module into `sys.modules` before Python 3.14's `dataclass` processing. The verifier was narrowly repaired to register that module, then the exact command was rerun. The final run exited `0`.

## Observed evidence

~~~text
preflight mode=deterministic-simulation network=none persistent_state=none
request=1 status=MISS served=v1 age=0 origin_reads=1 sha256=de60f726af94
request=2 status=HIT served=v1 age=10 origin_reads=1 sha256=de60f726af94
origin_changed_same_url status=HIT served=v1 authoritative=v2 age=20 origin_reads=1 sha256=de60f726af94
after_exact_url_purge status=MISS served=v2 age=0 origin_reads=2 sha256=057b24f36411
at_ttl_boundary status=EXPIRED served=v2 age=0 origin_reads=3 sha256=057b24f36411
SD-BEG-130-T01_LOCAL_MODEL_OK
~~~

## Explanation

The first request populated the empty edge from origin. Ten fake seconds later, the same key reused the stored body and did not increase origin reads. Changing only origin bytes left the fresh edge entry untouched: it served `v1` while the authority held `v2`. Exact-key purge removed that entry, so the next request fetched `v2` and produced a different digest. At age exactly equal to the `300`-second TTL, the strict freshness condition `age < ttl` was false, so the model reported `EXPIRED` and fetched origin once more.

The observed states match the reference prediction. The initial loader failure was implementation evidence, not cache-behavior evidence; no success marker was emitted until every cache assertion passed.

## Variation

- Changed condition: origin moves from `v1` to `v2` at the same URL while the edge's `v1` remains fresh, followed by exact-key purge.
- Prediction: the pre-purge request returns a `HIT` for `v1` with unchanged origin reads; the post-purge request returns a `MISS` for `v2` and adds one origin read.
- Actual result: before purge the model returned `HIT served=v1 authoritative=v2 age=20 origin_reads=1`; after purge it returned `MISS served=v2 age=0 origin_reads=2` with a new digest.
- Explanation: changing the authoritative object does not mutate an admitted cache entry. Removing the exact key forces the next request down the origin path and admits the new representation.

## Remaining proof gap

Even a passing local model would prove only its deterministic state transitions. It cannot establish a provider account, DNS/proxy path, real origin, cache eligibility, response headers, edge selection, latency, eviction, propagation, request collapsing, global invalidation, browser behavior, or Rahul's task completion.
