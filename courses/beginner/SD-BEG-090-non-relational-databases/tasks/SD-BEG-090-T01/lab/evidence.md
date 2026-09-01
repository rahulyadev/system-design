# Runtime evidence - SD-BEG-090-T01

## Execution status

- Status: Skipped for the required MongoDB component; applicable Redis and Neo4j checks passed
- Date/time: `2026-09-01T20:37:09+05:30`
- Environment: Linux `7.0.0-30-generic` x86_64; Docker client/server `29.7.2`; Docker Compose `v5.5.0`; local context `default` at `unix:///var/run/docker.sock`
- Reason if skipped/failed: MongoDB `8.0.29` refused to start because this host kernel is inside MongoDB’s documented incompatible range `6.19` through `7.0.13`. The safety check was not bypassed. Redis `8.10.1` and Neo4j `2026.07.1` ran successfully.

## Prediction

- MongoDB: two task documents; only one has `size=M`; atomic stock update changes `2` to `3` with one matched and modified document.
- Redis: exact profile value is returned; `INCR` changes `270` to `271`; one deleted key has existence `0`.
- Neo4j: three nodes and two relationships produce a two-hop path from Asha to Chen.
- Variation: adding the direct Asha-to-Chen relationship changes the shortest path to one hop.

These are reference-path predictions, not Rahul’s learner prediction.

## Expected behavior

Each runnable exact container should become healthy and carry the task project/service/learning labels, loopback ports, and labeled volume. MongoDB should either run on a compatible kernel or stop with a documented compatibility diagnosis; the verifier must not bypass it. Redis and Neo4j assertions should pass in sequence. Every task service should finish stopped while its exact labeled volume remains recoverable.

## Actual run

```text
python3 lab/preflight.py
python3 lab/verify_reference.py

# After the first run exposed MongoDB's kernel refusal:
docker compose -f lab/compose.yaml --project-name sd-beg-090-t01 --profile lab ps -a
docker compose -f lab/compose.yaml --project-name sd-beg-090-t01 --profile lab logs --no-color --tail 200 mongo

# After adding explicit safe skip handling and a 60-second Neo4j stop grace:
python3 lab/preflight.py
python3 lab/verify_reference.py
```

The first verifier run ended honestly with `mongo did not become healthy: starting`; the task log then showed the exact kernel incompatibility. The final verifier run exited `0` because every **applicable** assertion and cleanup check passed, not because MongoDB was relabeled as passed.

## Observed evidence

```text
PREFLIGHT status=passed context=default endpoint=unix:///var/run/docker.sock
PROJECT sd-beg-090-t01 labels=verified ports=loopback-only volumes=task-labeled

MongoDB: None — execution skipped
MONGODB_EXECUTION_SKIPPED reason="host kernel 7.0.0-30-generic is in MongoDB's documented incompatible range 6.19 through 7.0.13" image=mongo:8.0.29-noble
MONGO_CONTAINER final_state=exited exit_code=1 volume=sd-beg-090-t01-mongo-8-0-data retained_and_labeled=true

RUNTIME_IDENTITY service=redis image=redis:8.10.1-alpine3.23 port=127.0.0.1:55902 volume=sd-beg-090-t01-redis-8-10-data labels=verified
REDIS_OBSERVED {"counter_after_incr":271,"deleted_count":1,"exists_after_delete":0,"profile":"{\"user_id\":42,\"plan\":\"pro\"}","server_version":"8.10.1"}
REDIS_REFERENCE_CHECK status=passed
REDIS_CONTAINER final_state=exited exit_code=0 volume_retained=true

RUNTIME_IDENTITY service=neo4j image=neo4j:2026.07.1 ports=127.0.0.1:55903,127.0.0.1:55904 volume=sd-beg-090-t01-neo4j-2026-07-data labels=verified
NEO4J_BASELINE nodes=3 relationships=2 shortest_hops=2
VARIATION_PREDICTION add_direct_edge=shortest_hops:1
NEO4J_VARIATION_OBSERVED relationships=3 shortest_hops=1
NEO4J_REFERENCE_CHECK status=passed
NEO4J_CONTAINER final_state=exited exit_code=0 volume_retained=true

CLEANUP_SUMMARY services=stopped volumes=retained recoverable=true
SD-BEG-090-T01_APPLICABLE_CHECKS_PASSED mongodb=skipped redis=passed neo4j=passed
```

The final volume inspection returned the exact task ID and disposable label for all three volumes:

```text
sd-beg-090-t01-mongo-8-0-data SD-BEG-090-T01 true
sd-beg-090-t01-redis-8-10-data SD-BEG-090-T01 true
sd-beg-090-t01-neo4j-2026-07-data SD-BEG-090-T01 true
```

## Explanation

The MongoDB absence is evidence of an explicit platform boundary, not a database result. Because the process exited before health, no document was inserted or updated and no MongoDB reference claim is marked passed.

Redis proved the exact-key command path and one-command counter transition: the stored JSON string round-tripped unchanged, `INCR` returned `271`, DELETE removed one key, and EXISTS returned `0`. Neo4j proved the bounded directed path behavior: the baseline two-edge graph required two hops; one direct edge changed the shortest path to one. Both containers matched the exact runtime identity and exited cleanly after a 60-second shutdown grace.

## Variation

- Changed condition: add one direct `FOLLOWS` relationship from Asha to Chen.
- Prediction: shortest path changes from two hops to one.
- Actual result: relationship count changed `2 -> 3`; shortest path changed `2 -> 1`.
- Explanation: the direct edge is a valid directed path with fewer relationships than `Asha -> Ben -> Chen`, so the hop-count selector returns it.

## Remaining proof gap

- MongoDB document/flexible-field/atomic-increment behavior remains unexecuted on this host. Re-run on a compatible kernel and require the full `SD-BEG-090-T01_REFERENCE_VERIFIED` marker.
- Single-node checks do not prove sharding, replication, failover, durability under crash, backup/restore, security hardening, or production performance.
- The reference checks do not prove Rahul made a prediction, completed his own exploration, or can explain the trade-offs.
