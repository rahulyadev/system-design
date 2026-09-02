# Runtime lab - SD-BEG-130-T01 local companion

## Question this lab answers

In a deterministic one-origin, one-edge model, what state causes first-request `MISS`, later `HIT`, stale reuse after a same-URL origin change, a new fetch after exact-key purge, and re-fetch at the TTL boundary?

This is a **Codex-added companion**, not the instructor-assigned provider environment. Passing it does not create an account, route DNS, configure a CDN, deliver a real image URL, prove provider headers/latency, or complete Rahul's task.

## Tool-selection justification

- Selected profile: `python-simulation`.
- Why a runtime is useful: assertions make cache state, fake time, served version, body digest, purge, and origin-read count visible instead of leaving the sequence as an untested diagram.
- Why a smaller prose answer is insufficient: prose cannot provide actual evidence that the reference transitions and invariants agree with their implementation.
- Why a real local proxy is unnecessary: the assigned provider run is learner-owned external work, while the companion question needs only deterministic key/freshness/purge state. A proxy would add ports and process cleanup without proving global routing.
- Version: standard-library Python `3.10+`; verified with Python `3.14.4` on 2026-09-02. No service, image, package, network, account, DNS, or credential is used.
- Reference model: [`reference/cdn_cache_model.py`](../reference/cdn_cache_model.py). The verifier is reference-only evidence and does not report the unsolved provider exercise as learner completion.

## Resource budget

| Resource | Estimate |
|---|---|
| CPU | below `0.1` core for well under one second |
| Memory | below `30 MiB` including the interpreter on this tiny run |
| Disk | two source files and no generated/persistent data; below `50 KiB` |
| Startup | normally below one second |
| Data generation | two in-memory synthetic byte strings |
| Network/cloud | none |

## Safety preflight

From the task directory, inspect the exact command and identities:

~~~bash
pwd
python3 --version
python3 -c 'from pathlib import Path; paths=[Path("lab/verify.py"), Path("reference/cdn_cache_model.py")]; print("files_ok=" + str(all(path.is_file() for path in paths))); print("network=none persistent_state=none")'
~~~

Expected scope is exactly `lab/verify.py` loading `reference/cdn_cache_model.py`. The model uses fake seconds and in-memory synthetic bytes. It performs no socket, DNS, subprocess, environment-variable, filesystem-write, deletion, account, or provider operation.

## Start and health check

No service starts and no health check is needed. Python import plus assertions are the complete local runtime boundary.

## Deterministic setup

The verifier creates these in memory on every run:

| Item | Value |
|---|---|
| Cache key | `/assets/sd-beg-130-image.png` |
| Initial origin body/version | synthetic bytes / `v1` |
| Updated origin body/version | different synthetic bytes / `v2` |
| Edge TTL | `300` fake seconds |
| Initial clock | `0` fake seconds |
| Persistent state | none |

## Predict before running

In `../ATTEMPT.md`, predict the five output states first:

1. first request status/version/origin-read count;
2. second request after 10 seconds;
3. request after origin changes at the same URL but before TTL;
4. request immediately after exact-key purge;
5. request exactly 300 seconds after the new fill.

Do not inspect [`evidence.md`](evidence.md) before writing the prediction.

## Run

From the task directory:

~~~bash
python3 lab/verify.py
~~~

The command exits nonzero on any failed assertion. The unique success marker is printed only after every state and origin-read assertion passes.

## Inspect what happened

Read each line as:

`event → cache status → served version → optional authoritative version → age → cumulative origin reads → body digest prefix`

The critical proof is not the word `HIT` alone. Before purge, the model must show `served=v1`, `authoritative=v2`, and an unchanged origin-read count. After purge, it must show `MISS`, `served=v2`, a changed digest, and one more origin read.

## Vary one condition

After predicting, change **one** copied reference input outside Rahul's original attempt—for example TTL from `300` to `15` fake seconds—and explain why the same 20-second request becomes `EXPIRED` rather than `HIT`. Restore the reference files afterward by discarding only your temporary copy; do not edit the canonical reference merely to record a learner variation.

The provider variation remains separate: changing origin bytes and purging an exact real CDN URL requires Rahul's authorized external setup and evidence.

## Reset and cleanup

No reset or cleanup command exists because every object lives only inside one Python process and disappears at exit. Re-running starts at fake time zero. Do not infer any permission to clean cloud, DNS, provider, browser, or origin state from this local property.

For the assigned provider resources, follow the exact identity-checked cleanup boundary in [`../README.md`](../README.md).

## Troubleshooting

| Symptom | Check | Likely cause | Safe repair |
|---|---|---|---|
| Python is older than 3.10 | `python3 --version` | Unsupported interpreter | Use an isolated Python 3.10+ interpreter; install no package |
| Model file cannot load | Run from task directory and list the two exact files | Pack is incomplete or path changed | Restore the canonical task files; do not copy private inputs |
| Assertion fails | Read the first traceback assertion and `git diff --` for the two files | Reference code was altered | Review the intentional change or restore only your disposable copy |
| Provider behavior differs | Compare real headers/rules/edge/origin evidence | This model omits provider semantics | Record the difference in `ATTEMPT.md`; do not alter observed evidence to match the model |

The genuine reference run is recorded in [`evidence.md`](evidence.md).
