# Runtime lab - SD-BEG-140-T01

## Question this lab answers

After RabbitMQ delivers a message with manual acknowledgement enabled, what observable state transition occurs when the consumer connection closes before the acknowledgement, and what does that prove about redelivery and duplicate-safe handlers?

## Tool-selection justification

- Selected profile: `rabbitmq-task-local`.
- Why a real runtime is needed: the instructor explicitly asks Rahul to run RabbitMQ and write publish/consume code; channel ownership, publisher confirms, manual acknowledgements, connection-close requeueing, and the broker-set redelivery flag are product/protocol behavior.
- Why a smaller simulation is insufficient: a simulation could illustrate a state machine but could not prove what RabbitMQ 4.3.5 actually does with an unacknowledged delivery or how Pika exposes it.
- RabbitMQ version: `4.3.5`, a community-supported 4.3 patch on the check date. Verified on `2026-09-02` using [RabbitMQ release information](https://www.rabbitmq.com/release-information).
- Image: `rabbitmq:4.3.5-management-alpine`. The exact tag and supported architectures were verified on `2026-09-02` in the [Docker Official Images RabbitMQ registry](https://github.com/docker-library/official-images/blob/master/library/rabbitmq).
- Python client: `pika==1.4.4`, verified on `2026-09-02` using the [Pika package record](https://pypi.org/project/pika/).
- Behavioral sources: RabbitMQ's [Python hello-world tutorial](https://www.rabbitmq.com/tutorials/tutorial-one-python), [work-queue tutorial](https://www.rabbitmq.com/tutorials/tutorial-two-python), [acknowledgement and confirms guide](https://www.rabbitmq.com/docs/confirms), and [reliability guide](https://www.rabbitmq.com/docs/reliability).

## Resource budget

| Resource | Estimate or observed boundary |
|---|---|
| CPU | normally below one core for two tiny messages; no load test |
| Memory | approximately `250-500 MiB` including broker VM and management plugin |
| Disk/images | pulled image observed as `88,889,341` bytes; no named volume; queue bodies are below `1 KiB` total |
| Image download | roughly `90 MiB` plus registry/layer overhead when uncached |
| Startup | observed healthy in about 12 seconds; allow up to 60 seconds |
| Data generation | two deterministic JSON messages; effectively immediate |
| Network | loopback AMQP and management HTTP only; image/package downloads occur only during setup |

These are learning-stack estimates and one observed image size, not production sizing claims.

## Safety preflight

From the task directory, run:

```bash
python3 lab/preflight.py
```

It refuses a Docker endpoint other than a local Unix socket or Windows named pipe. It validates the exact project, service, image, labels, `127.0.0.1` port bindings, absence of named volumes, and either free ports or an already-existing correctly labeled task container. Stop on any mismatch.

The permitted identity is:

| Boundary | Exact value |
|---|---|
| Compose project | `sd-beg-140-t01-rabbitmq` |
| Service | `rabbitmq` |
| Learning label | `SD-BEG-140-T01` |
| Disposable label | `true` |
| AMQP | `127.0.0.1:5678` |
| Management UI | `127.0.0.1:15678` |
| Vhost | `sd_beg_140` |
| Queue | `sd_beg_140_tasks` |
| Credentials | synthetic `learner` / `local-only-demo` |
| Volume | none |

## Start and health check

```bash
docker compose -f lab/compose.yaml --project-name sd-beg-140-t01-rabbitmq --profile lab up -d
docker compose -f lab/compose.yaml --project-name sd-beg-140-t01-rabbitmq --profile lab ps
python3 lab/preflight.py --expect-running
docker compose -f lab/compose.yaml --project-name sd-beg-140-t01-rabbitmq --profile lab exec -T rabbitmq rabbitmq-diagnostics -q ping
```

Do not continue until Compose reports the exact container as healthy and diagnostics says `Ping succeeded`.

## Deterministic setup

Create an isolated Python environment and install only the exact client:

```bash
python3 -m venv .venv
.venv/bin/python -m pip install --requirement requirements.txt
.venv/bin/python -c 'import platform,pika; print(platform.python_version(), pika.__version__)'
```

The reference verifier purges only `sd_beg_140_tasks` at its start, then creates:

| Phase | Message ID | Kind | Video ID |
|---|---|---|---|
| Normal | `baseline-caption-001` | `caption-video` | `video-42` |
| Failure variation | `redelivery-caption-001` | `caption-video` | `video-84` |

The queue is durable and uses RabbitMQ's quorum type. The messages use persistent delivery mode. The publisher enables confirms and requires routing; these choices are separate and all remain limited by the single-node lab.

## Predict before running

In `../ATTEMPT.md`, predict the queue's `ready`/`unacknowledged` states and the `redelivered` flag for both deliveries. Also predict which external side effect could duplicate if a worker completed it immediately before losing its acknowledgement.

Do not inspect `evidence.md` or `reference/` until the prediction is committed.

## Run

Learner path, after completing the TODOs:

```bash
.venv/bin/python starter/producer.py
.venv/bin/python starter/consumer.py
```

Use separate terminals when you want to pause the consumer before acknowledgement and inspect state. Do not change `auto_ack` to make the exercise pass.

Reference-only verification, after your own attempt:

```bash
PYTHONDONTWRITEBYTECODE=1 .venv/bin/python lab/verify_reference.py
```

The verifier exits nonzero on a failed assertion and prints `SD-BEG-140-T01_REFERENCE_VERIFIED` only after publish confirm, normal manual ack, connection-close redelivery, stable identity, redelivery flag, and final ready/consumer assertions pass. It does not inspect or award completion to learner files.

## Inspect what happened

```bash
docker compose -f lab/compose.yaml --project-name sd-beg-140-t01-rabbitmq --profile lab exec -T rabbitmq rabbitmqctl list_queues -p sd_beg_140 name type durable messages_ready messages_unacknowledged consumers
```

### Question this state visual answers

Who owns the delivery before acknowledgement, and how do the two queue counters change when that owner disconnects?

### How to read this visual

Read each row in time order. `Ready` is broker-held work eligible for delivery. `Unacknowledged` is work already delivered to a live consumer/channel but not yet settled. The connection-close row transfers the unfinished attempt back toward broker-ready ownership.

| Moment | Ready | Unacknowledged | Meaning |
|---|---:|---:|---|
| After publish, before delivery | `1` | `0` | Queue owns a deliverable message |
| Delivered with manual ack pending | `0` | `1` | Consumer connection currently owns the delivery attempt |
| Connection closes before ack | returns toward `1` | returns toward `0` | RabbitMQ makes that delivery eligible again |
| Redelivered and acked | `0` | `0` | Consumer accepted ownership after its successful action |

### Key insight

Delivery is not deletion in manual-ack mode. Closing the connection before ack restores retry eligibility, which protects unfinished work but creates a duplicate-attempt boundary.

### Simplification or limitation

The table shows one message and one consumer. Counters are snapshots and can change between commands; multiple consumers, prefetch, retries, and broker-node failure can make intermediate values overlap. Correlate them with the stable message ID and broker-set flag rather than inferring a complete history from one sample.

## Vary one condition

Baseline: let the normal consumer process and acknowledge one message.

Variation: publish the second ID, fetch it with manual ack, deliberately close only that AMQP connection without acknowledging, reconnect, and fetch again. Predict first. The expected evidence is the same body and AMQP message ID with first `redelivered=false`, later `redelivered=true`, followed by a final ack and zero queue counts.

This failure is safe: it affects one synthetic delivery in one exact task queue. Abort if preflight identity changes. Recovery is reconnect plus consume/ack or final project recreation.

## Reset and cleanup

Show the exact target before deletion:

```bash
python3 lab/preflight.py --expect-running
docker compose -f lab/compose.yaml --project-name sd-beg-140-t01-rabbitmq --profile lab exec -T rabbitmq rabbitmqctl list_queues -p sd_beg_140 name type durable messages_ready messages_unacknowledged consumers
```

Optional queue-only reset:

```bash
docker compose -f lab/compose.yaml --project-name sd-beg-140-t01-rabbitmq --profile lab exec -T rabbitmq rabbitmqctl delete_queue -p sd_beg_140 sd_beg_140_tasks
```

Final cleanup after label verification:

```bash
docker compose -f lab/compose.yaml --project-name sd-beg-140-t01-rabbitmq --profile lab down
python3 lab/preflight.py
```

The cleanup removes the exact container and its Compose network. With no volume, the synthetic queue state is not recoverable; rerunning setup recreates it. The pulled image remains in the shared Docker image cache and is not deleted by this task.

## Troubleshooting

| Symptom | Check | Likely cause | Safe repair |
|---|---|---|---|
| Preflight refuses endpoint | `docker context show` and context inspect output | Remote/TCP Docker context | Switch deliberately to an authorized local context; do not bypass the check |
| Port unavailable | Preflight and `docker ps` for this exact project | Another local process or old task container | Stop only the identified owner or choose new loopback ports consistently in code and Compose |
| Broker never becomes healthy | `docker compose ... ps` and narrow `logs --tail 100 rabbitmq` | Image/startup/resource issue | Keep scope exact, inspect the first error, then retry; do not prune Docker globally |
| Authentication or vhost error | Compare Compose environment with learner constants | Host port, credentials, or vhost drift | Restore the documented synthetic values |
| Queue declaration closes channel | Compare name, durable flag, and queue type in both programs | Property-equivalence mismatch | Make both declarations identical; do not delete an unrelated queue |
| Published print but no message | Require confirm mode and mandatory routing; inspect queue | Unroutable publish or claim made before broker ack | Fix declaration/routing and handle confirm/return exceptions |
| Message disappears on consumer crash | Inspect `auto_ack` | Automatic acknowledgement enabled | Use manual ack and place it after the successful action |
| Message requeues repeatedly | Inspect error classification and redelivery count | Poison message or unconditional requeue | Stop the consumer; add bounded retries and a reviewed dead-letter path |
| Reference cannot open sockets in a sandbox | Run only with explicit permission for `127.0.0.1` | Execution sandbox blocks socket creation | Grant narrow local-network authority; never widen to an external broker |

Record only genuine results in [`evidence.md`](evidence.md).
