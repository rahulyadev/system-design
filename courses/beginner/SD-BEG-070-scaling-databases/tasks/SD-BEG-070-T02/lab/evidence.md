# Runtime evidence — SD-BEG-070-T02

## Execution status

- Status: Passed
- Date/time: completed 2026-09-01T16:35:04+05:30
- Environment: Linux 7.0.0-30-generic x86_64; Docker Engine client/server 29.7.2; Docker Compose v5.5.0; MySQL 8.4.11; Node.js v24.19.0; npm 11.17.0; `mysql2` 3.24.2
- Image: `mysql:8.4.11`, observed digest `mysql@sha256:b3b90af2a6552ae30c266fdb7d5dd55f3afb72404bb78d37fe8a23eb857fd3fb`
- Reason if skipped/failed: Not applicable

## Prediction

This is the course/reference prediction, not Rahul’s future learner prediction:

- `apple` and `mango` should exist only on A–M/server `711`.
- `nectar` and `zebra` should exist only on N–Z/server `712`.
- `ZULU` should normalize to `zulu` and use server `712`.
- `9-invalid` should return `422` and create no row.
- Twenty `a-hot-*` keys and two `z-cold-*` keys should produce a 10:1 physical ownership ratio.

## Expected behavior

One centralized normalization/mapping function selects exactly one pool before SQL. POST and GET therefore choose the same owner. Direct queries should show a count of one on the chosen shard and zero on the other. Invalid input has no owner and is rejected before mutation. Fixed alphabetical ranges preserve this correctness invariant but do not guarantee balanced traffic or storage.

## Actual run

From the task directory, the following commands genuinely ran:

```text
python3 lab/preflight.py
npm ci --prefix reference --ignore-scripts --no-audit --no-fund
python3 lab/verify_reference.py
docker version --format 'client={{.Client.Version}} server={{.Server.Version}}'
docker compose version
docker ps -a --filter label=com.rahulyadav.learning-task=SD-BEG-070-T02
docker volume inspect sd-beg-070-t02-am-mysql-8-4 sd-beg-070-t02-nz-mysql-8-4
```

The verifier itself executed the scoped Compose start/stop, schema loads on both shards, reference API requests, and direct correct/wrong-shard assertions.

## Observed evidence

```text
PREFLIGHT status=passed context=default endpoint=unix:///var/run/docker.sock existing_project_containers=0 volumes=absent
HEALTH shard_am=healthy shard_nz=healthy
RUNTIME_IDENTITY shard_am port=127.0.0.1:55711 server_id=711 volume=sd-beg-070-t02-am-mysql-8-4 labels=verified
RUNTIME_IDENTITY shard_nz port=127.0.0.1:55712 server_id=712 volume=sd-beg-070-t02-nz-mysql-8-4 labels=verified
VERSIONS shard_am=8.4.11@711 shard_nz=8.4.11@712 node=v24.19.0 mysql2=3.24.2
SCHEMA_CHECK records_table=present shards=2 independent=true
API_HEALTH shard_am_server_id=711 shard_nz_server_id=712
BOUNDARY key=apple shard=am server=711 owner_count=1 wrong_shard_count=0
BOUNDARY key=mango shard=am server=711 owner_count=1 wrong_shard_count=0
BOUNDARY key=nectar shard=nz server=712 owner_count=1 wrong_shard_count=0
BOUNDARY key=zebra shard=nz server=712 owner_count=1 wrong_shard_count=0
NORMALIZATION input=ZULU stored=zulu shard=nz server=712
INVALID_KEY status=422 rows_unchanged={shard_am:2,shard_nz:3}
SKEW_VARIATION a_hot@711=20 z_cold@712=2 ratio=10:1 wrong_shard_counts=0/0
CLEANUP shard_am=exited shard_nz=exited volumes=retained-and-labeled recoverable=true
SD-BEG-070-T02_REFERENCE_VERIFIED
```

## Explanation

Every API response agreed with `@@server_id` and the physical placement checks. The a/m/n/z cases exercise both inclusive boundaries, proving the one-owner rule for the supplied mapping. Uppercase input followed the documented normalization contract. The invalid request left totals `2/3` unchanged. The variation placed all 20 hot-prefix rows on server `711` and both cold-prefix rows on `712`, with zero wrong-shard rows; identical hardware therefore experienced a controlled 10:1 ownership imbalance.

## Variation

- Changed condition: input distribution changed to 20 `a-hot-*` records and two `z-cold-*` records while mapping and hardware stayed fixed.
- Prediction: A–M owns 20, N–Z owns two, a 10:1 ratio.
- Actual result: `a_hot@711=20`, `z_cold@712=2`, wrong-shard counts `0/0`, ratio `10:1`.
- Explanation: deterministic range ownership preserves correctness but sends every hot-prefix request to one database. Nominal aggregate capacity is not usable evenly when the key distribution is skewed.

## Remaining proof gap

The run proves deterministic placement for two local MySQL 8.4.11 shards, 27 stored rows, and one rejected request. It is not a load benchmark and does not prove failover, replica behavior per shard, concurrent resharding, stale mapping recovery, cross-shard transactions/queries, backup restore, host loss, or production security. Both containers were stopped cleanly; the exact task-labeled volumes were retained and remain recoverable.
