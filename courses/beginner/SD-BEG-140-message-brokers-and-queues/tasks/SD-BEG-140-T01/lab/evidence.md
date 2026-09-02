# Runtime evidence - SD-BEG-140-T01

## Execution status

- Status: Passed
- Date/time: completed `2026-09-02T22:42:00+05:30`
- Environment: Linux `7.0.0-30-generic` x86_64; Docker Engine client/server `29.7.2`; Docker Compose `v5.5.0`; local context `default` at `unix:///var/run/docker.sock`; isolated Python `3.14.4`; Pika `1.4.4`; RabbitMQ `4.3.5`
- Image: `rabbitmq:4.3.5-management-alpine`; observed digest `rabbitmq@sha256:5b6a50b2f1dbd987bb1a6a9e20b152910c3dc8ae32e1c9060b543ecd9250f6b9`; observed local image size `88,889,341` bytes
- Runtime scope: project `sd-beg-140-t01-rabbitmq`, service `rabbitmq`, vhost `sd_beg_140`, queue `sd_beg_140_tasks`, loopback ports `5678` and `15678`, no named volume, two deterministic messages
- Reason if skipped/failed: Not applicable to the final run.

## Prediction

This is the course/reference prediction, not Rahul's future learner prediction:

- A confirmed publish should make the deterministic message available in the durable quorum queue; it does not mean consumer work is complete.
- The normal consumer should see `redelivered=false`, validate the message, ack after its synthetic action, and leave the queue empty.
- For the variation, the first delivery should have `redelivered=false`. Closing its connection without ack should cause RabbitMQ to requeue that delivery.
- A new connection should receive the identical body and stable message ID with `redelivered=true`; after its ack, ready and unacknowledged counts should both be zero.
- The observation demonstrates RabbitMQ redelivery, not exactly-once external effects or replicated availability.

## Expected behavior

Publisher confirms and consumer acknowledgements cover opposite hops. The producer's blocking channel should return from `basic_publish` without a nack/unroutable exception only after broker confirmation. The first manual-ack consumer owns a delivery attempt until it acks or its connection/channel closes. Closing that connection should automatically requeue the unacknowledged message. RabbitMQ should preserve its body and message property ID and set the redelivery flag on the later delivery. The final queue must contain no ready or unacknowledged messages.

## Actual run

The following commands genuinely ran from the task directory. Dependency installation targeted only an isolated temporary environment:

```text
python3 lab/preflight.py
uv venv /tmp/sd-beg-140-t01-venv-py314-system --python /usr/bin/python3
uv pip install --python /tmp/sd-beg-140-t01-venv-py314-system/bin/python --requirement requirements.txt
docker compose -f lab/compose.yaml --project-name sd-beg-140-t01-rabbitmq --profile lab up -d
docker compose -f lab/compose.yaml --project-name sd-beg-140-t01-rabbitmq --profile lab ps
python3 lab/preflight.py --expect-running
docker compose -f lab/compose.yaml --project-name sd-beg-140-t01-rabbitmq --profile lab exec -T rabbitmq rabbitmq-diagnostics -q ping
docker compose -f lab/compose.yaml --project-name sd-beg-140-t01-rabbitmq --profile lab exec -T rabbitmq rabbitmqctl version
docker image inspect rabbitmq:4.3.5-management-alpine --format '{{index .RepoDigests 0}} {{.Size}}'
PYTHONDONTWRITEBYTECODE=1 /tmp/sd-beg-140-t01-venv-py314-system/bin/python lab/verify_reference.py
docker compose -f lab/compose.yaml --project-name sd-beg-140-t01-rabbitmq --profile lab exec -T rabbitmq rabbitmqctl list_queues -p sd_beg_140 name type durable messages_ready messages_unacknowledged consumers
docker compose -f lab/compose.yaml --project-name sd-beg-140-t01-rabbitmq --profile lab exec -T rabbitmq rabbitmqctl list_vhosts name
docker compose -f lab/compose.yaml --project-name sd-beg-140-t01-rabbitmq --profile lab down
python3 lab/preflight.py
```

One sandboxed verifier attempt stopped before connecting because the execution sandbox denied socket creation; it produced no broker evidence. The approved loopback-only rerun reached the broker.

The first broker-connected development run exposed an incorrect reference assumption: Pika 1.4.4's blocking `basic_publish` returns `None` after a successful publisher confirm and raises on nack/unroutable failure; it does not return `True`. That run stopped after the first confirmed publish, and the next verifier run purged the exact queue before testing. The code was corrected to use the documented exception boundary.

A later development run passed publish, normal ack, and redelivery assertions but sampled a transient consumer count before cancellation was fully visible. The final verifier checks that count from a fresh connection with a bounded wait. No failed-development output is presented as final passed evidence.

## Observed evidence

```text
PREFLIGHT status=passed context=default endpoint=unix:///var/run/docker.sock project=sd-beg-140-t01-rabbitmq service=rabbitmq image=rabbitmq:4.3.5-management-alpine ports=127.0.0.1:5678,127.0.0.1:15678 container=absent volume=none credentials=synthetic

NAME                                 IMAGE                              STATUS                    PORTS
sd-beg-140-t01-rabbitmq-rabbitmq-1   rabbitmq:4.3.5-management-alpine   Up 12 seconds (healthy)   ... 127.0.0.1:5678->5672/tcp, 127.0.0.1:15678->15672/tcp
PREFLIGHT status=passed ... container=healthy volume=none credentials=synthetic
Ping succeeded
4.3.5
rabbitmq@sha256:5b6a50b2f1dbd987bb1a6a9e20b152910c3dc8ae32e1c9060b543ecd9250f6b9 88889341

PUBLISHED id=baseline-caption-001 queue=sd_beg_140_tasks confirm=true delivery_mode=persistent
CONSUMED id=baseline-caption-001 redelivered=false ack=true
BASELINE same_message=true redelivered=false ack=true
PUBLISHED id=redelivery-caption-001 queue=sd_beg_140_tasks confirm=true delivery_mode=persistent
VARIATION_FIRST id=redelivery-caption-001 redelivered=false ack=withheld action=close-connection
VARIATION_REDELIVERY id=redelivery-caption-001 same_message=true redelivered=true ack=true
FINAL_QUEUE ready=0 consumers=0
SD-BEG-140-T01_REFERENCE_VERIFIED

name                 type    durable  messages_ready  messages_unacknowledged  consumers
sd_beg_140_tasks     quorum  true     0               0                        0
vhost=sd_beg_140

PREFLIGHT status=passed ... container=absent volume=none credentials=synthetic
python=3.14.4 pika=1.4.4
```

Ellipses above shorten repeated, already-recorded identity fields and Docker's unrelated unexposed internal ports; they are not invented values. The decisive queue row and verifier lines are reproduced exactly apart from column spacing.

## Explanation

The normal path proves that the reference producer reached the exact queue under publisher-confirm mode and that the reference consumer performed its validation before manually acknowledging. `redelivered=false` identifies the first delivery attempt; the final zero state shows no retained work after ack.

In the variation, the first connection received but did not acknowledge `redelivery-caption-001`. Closing that connection ended its ownership of the delivery. RabbitMQ then delivered the same body and AMQP message ID to a fresh connection with `redelivered=true`. The final ack allowed the broker to remove the delivery, which agrees with the zero ready/unacknowledged row.

This is at-least-once delivery evidence. If the first consumer had sent an email or committed another external side effect immediately before its connection died, the second attempt could repeat that effect. The broker flag cannot make the domain action idempotent; a stable business key and durable transaction/provider idempotency boundary must do that.

## Variation

- Changed condition: close the connection holding `redelivery-caption-001` after delivery but before acknowledgement.
- Prediction: the message will become eligible again and a fresh connection will receive the identical ID/body with RabbitMQ's redelivery flag set.
- Actual result: first delivery reported `redelivered=false` and `ack=withheld`; the later delivery reported `same_message=true`, `redelivered=true`, and then `ack=true`; final broker counters were zero.
- Explanation: with manual acknowledgements, RabbitMQ automatically requeues deliveries left unacknowledged when their channel or connection closes. The later ack transfers final responsibility to the consumer only after the synthetic action.

## Remaining proof gap

The run proves one local RabbitMQ 4.3.5 node, one Pika 1.4.4 blocking client, the exact queue/message contract, two tiny sequential messages, manual ack, publisher confirm, and connection-close redelivery. It does not prove broker restart persistence, multi-node quorum behavior, leader failover, network partition handling, confirm-loss retry, global or per-key ordering under concurrency, a real database/outbox/idempotency record, third-party side-effect safety, retry backoff, delivery limits, dead-letter routing, TTL, load capacity, tail latency, TLS, secret management, authorization hardening, multi-region behavior, cost, or SQS semantics.

The exact task container and Compose network were removed after evidence capture. No task volume existed, so its synthetic queue state is not recoverable; both loopback ports are free. The pulled image remains in Docker's shared cache and was intentionally not deleted.
