# SD-BEG-140-T01 - Publish, consume, and recover a RabbitMQ message

> Instructor-assigned task from `SD-BEG-140`. Write your prediction in `ATTEMPT.md`, build your own path, and only then open `reference/SOLUTION.md`.

## Source and fidelity

- Source timestamp/slide: `00:14:37-00:15:20`; the final exercise slide states the same three core actions.
- Faithful paraphrase: install or run RabbitMQ locally, write code that puts data into it and reads data out, then inspect RabbitMQ's documentation and experiment with its features and guarantees until you can explain what the broker does. The instructor conditionally allows SQS instead when the learner already has authorized AWS access.
- Short exact excerpt: Not needed; the spoken and visual requirements agree.
- Source ambiguity: no language, client library, message schema, exchange/queue topology, acknowledgement mode, feature subset, evidence standard, version, resource budget, failure case, retry limit, or cleanup procedure is specified. “Explore the guarantees” is intentionally broad. The optional SQS route does not specify account authority, cost, region, or cleanup.

This pack chooses the source's local RabbitMQ route. It does not create an AWS account or queue. If Rahul later deliberately chooses the conditional SQS alternative, he must use only an authorized non-production account and separately demonstrate SQS semantics; the RabbitMQ reference evidence does not transfer automatically.

## Exact requirement checklist

- [ ] Set up RabbitMQ locally.
- [ ] Write code that pushes/publishes data into RabbitMQ.
- [ ] Write code that pulls/receives data from RabbitMQ.
- [ ] Read current RabbitMQ documentation to identify its features and guarantees.
- [ ] Experiment with the broker rather than stopping at a copied hello-world result.
- [ ] Explain how those behaviors affect a product design.

Conditional source alternative, not an extra requirement:

- [ ] If deliberately using already-authorized AWS access instead, replace RabbitMQ with SQS and investigate SQS's own guarantees without assuming both products behave identically.

## Codex-added safety or verification

These controls make the broad exercise safe and reviewable; they are additions, not instructor wording:

- Use only the task-local Compose project `sd-beg-140-t01-rabbitmq`, service `rabbitmq`, vhost `sd_beg_140`, and queue `sd_beg_140_tasks`.
- Bind AMQP and the management UI only to `127.0.0.1` on ports `5678` and `15678`.
- Use the synthetic credentials in `lab/compose.yaml`; do not reuse personal, employer, cloud, or production credentials.
- Pin `rabbitmq:4.3.5-management-alpine` and `pika==1.4.4`; do not silently substitute `latest`.
- Use a durable quorum queue, persistent messages, `mandatory` routing, and publisher confirms for the reference path. Treat each as a different boundary, not a single “durable” switch.
- Use manual consumer acknowledgement after the synthetic business action.
- Preserve a stable message ID and observe one controlled failure: close the delivery connection before acknowledgement, then verify the identical delivery returns with RabbitMQ's redelivery flag.
- Never create a real email, payment, upload, or cloud side effect. Payloads are deterministic JSON only.
- Inspect queue type, durability, ready count, unacknowledged count, and consumer count rather than trusting prints alone.
- Stop and remove only this exact project after identity checks. No broad Docker cleanup is authorized.
- Reference verification proves only the separate reference path; it does not mark Rahul's learner code or explanation complete.

## Inputs, constraints, and expected artifact

| Item | Contract |
|---|---|
| Runtime | Local Docker Engine and Compose; local Unix/named-pipe endpoint only |
| Broker | RabbitMQ `4.3.5`, exact management-alpine image, one task-local node |
| Client | Python `3.7+` with Pika `1.4.4` in an isolated environment |
| Topology | Default exchange -> routing key `sd_beg_140_tasks` -> durable quorum queue of that name in vhost `sd_beg_140` |
| Message | Deterministic JSON with stable `message_id`, `kind`, and synthetic `video_id`; persistent delivery mode |
| Normal path | Broker confirms publish; one manual-ack consumer validates the body, performs a synthetic action, then acks |
| Failure path | Receive without ack, close only that connection, receive the same ID again, inspect `redelivered=true`, then ack |
| Documentation | Dated official links plus a table covering queue/routing, ack, confirm, durability, prefetch, TTL/dead lettering, and monitoring |
| Output | Rahul-owned code and completed `ATTEMPT.md`, including prediction, genuine output, mechanism, trade-offs, variation, and cleanup |
| Completion evidence | Source checklist, exact runtime identity, publish/consume proof, state counters, redelivery proof, final zero state, documentation synthesis, and spoken explanation |

## Before you start: predict

Write in `ATTEMPT.md` before starting your consumer:

1. what a publisher confirm proves and does not prove;
2. which queue counters should change after publish, delivery-before-ack, and ack;
3. whether the first delivery's `redelivered` flag should be set;
4. what closes when you terminate a consumer and what RabbitMQ should do with its unacknowledged delivery;
5. whether the second delivery can safely repeat the business action;
6. which stable identifier lets your handler recognize the same logical operation;
7. what evidence would falsify your explanation.

Do not read `lab/evidence.md` before committing this prediction in your own words.

## Setup

The exact local runtime and commands are in [`lab/README.md`](lab/README.md). The environment contains one broker container, one vhost, one queue, two tiny synthetic messages, and no named volume. Estimated peak use is below one CPU core for this exercise, roughly `250-500 MiB` memory, about `90 MiB` for the pulled image plus small container metadata, and under one minute of startup on a warm network.

Use an isolated environment; do not install Pika globally:

```bash
python3 -m venv .venv
.venv/bin/python -m pip install --requirement requirements.txt
```

If the host Python lacks `venv`/`pip`, use another isolated supported Python runtime. Do not add packages to the system interpreter merely to finish the task.

## Learner steps

1. Read `lab/README.md`, run the before-start preflight, and verify the exact context, project, service, image, ports, credentials, and absence of task volumes.
2. Start only the task-local broker and require its health check to pass.
3. Inspect `starter/producer.py` and `starter/consumer.py`; fill the TODOs or create equivalent learner-owned files without opening `reference/`.
4. Declare the same named durable queue from both programs so startup order is safe. Choose and explain the queue type.
5. Enable publisher confirms, publish one persistent JSON message through a routable destination, and record the stable ID.
6. Run a consumer with automatic acknowledgement disabled and prefetch bounded. Validate the message, perform only a synthetic action, then acknowledge on the same channel.
7. Inspect queue state after publish, during an unacknowledged delivery, and after acknowledgement. Explain `ready` versus `unacknowledged`.
8. Publish a second stable ID. Receive it without ack, close that consumer connection, then consume again. Prove identity and inspect the redelivery flag before acknowledging.
9. Explain why the observation supports at-least-once delivery but does not prove exactly-once business effects.
10. Read the current official docs linked from the lab and fill the feature map in `ATTEMPT.md`. For each feature, state the boundary and failure it does not solve.
11. Propose an idempotent handler and a bounded policy for poison messages; do not create an infinite requeue loop.
12. Verify the exact target, reset only the named queue if needed, then remove only the task project and record the final absence.
13. Give a two-minute explanation without notes. Only then compare with the reference.

## Progressive hints

<details><summary>Hint 1 - requirement</summary><p>The finish line is not “RabbitMQ is running.” You need your own publish path, consume path, observed feature/guarantee boundaries, and a causal explanation.</p></details>

<details><summary>Hint 2 - invariant</summary><p>A message may leave the queue permanently only after the application has made its intended result safe, or the system has deliberately classified it for another terminal path.</p></details>

<details><summary>Hint 3 - ownership</summary><p>Ask which hop each signal covers: application-to-broker and broker-to-consumer are separate conversations.</p></details>

<details><summary>Hint 4 - state</summary><p>A delivered message awaiting a manual acknowledgement is not “ready,” but it is not yet safely finished either. Inspect both counters.</p></details>

<details><summary>Hint 5 - failure</summary><p>To test recovery without killing Docker, close only the connection that owns an unacknowledged delivery and keep the message ID stable.</p></details>

## Acceptance criteria

- [ ] Every source requirement is represented, including the documentation/guarantee exploration and product-design explanation.
- [ ] Preflight proves a local Docker endpoint, exact task identity, loopback-only ports, synthetic credentials, and no unrelated state.
- [ ] RabbitMQ and Pika versions are exact and recorded; no floating image or package version is used.
- [ ] Rahul's producer and consumer are his own learner-side work and do not import the reference path.
- [ ] Producer evidence distinguishes routing from publisher confirmation.
- [ ] Consumer uses manual acknowledgement after its synthetic action and bounded prefetch.
- [ ] Queue type, durability, ready messages, unacknowledged messages, and consumers are inspected.
- [ ] The failure variation closes the correct connection before ack and observes the identical stable ID with `redelivered=true`.
- [ ] Rahul explains why duplicate delivery and duplicate external effect are related but not identical.
- [ ] An idempotency key/store or equivalent invariant prevents repeated business effects.
- [ ] Retryable and terminal errors have a bounded retry/dead-letter decision; no hot requeue loop is proposed.
- [ ] Durability claims separate durable topology, persistent payload, publisher confirm, and single-node failure limits.
- [ ] The dated documentation map covers the required feature set using official RabbitMQ sources.
- [ ] Final queue state and exact project cleanup are captured; no unrelated container, network, volume, or image is removed.
- [ ] Rahul can explain the lifecycle and one changed requirement naturally at SDE-2 depth.

## Cleanup/reset

Before reset, rerun `python3 lab/preflight.py --expect-running`, then show the exact queue:

```bash
docker compose -f lab/compose.yaml --project-name sd-beg-140-t01-rabbitmq --profile lab exec -T rabbitmq rabbitmqctl list_queues -p sd_beg_140 name type durable messages_ready messages_unacknowledged consumers
```

Reset only after confirming the single target is `sd_beg_140_tasks`:

```bash
docker compose -f lab/compose.yaml --project-name sd-beg-140-t01-rabbitmq --profile lab exec -T rabbitmq rabbitmqctl delete_queue -p sd_beg_140 sd_beg_140_tasks
```

The learner producer/consumer may recreate it because queue declaration is idempotent when properties match. For final cleanup, verify labels with preflight and remove only this project:

```bash
docker compose -f lab/compose.yaml --project-name sd-beg-140-t01-rabbitmq --profile lab down
python3 lab/preflight.py
```

There is no named volume. Final cleanup permanently removes only synthetic broker state in this task container; the repository files remain and can recreate it.

## Reference answer boundary

After writing your prediction, implementing both programs, and completing the failure variation, compare with [`reference/SOLUTION.md`](reference/SOLUTION.md). Its verified status covers only the separate reference files and exact local run recorded in `lab/evidence.md`; `learner_status` remains `not_started` until Rahul supplies his own attempt and explanation.
