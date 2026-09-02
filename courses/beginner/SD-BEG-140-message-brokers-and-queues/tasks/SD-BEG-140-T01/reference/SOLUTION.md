# Reference solution - SD-BEG-140-T01

> **Spoiler:** Open only after writing a committed prediction and completing a first learner-side attempt. This is one defensible RabbitMQ solution, not proof that every other client or topology is wrong.

## Clarifications and assumptions

- “Push” means an AMQP publisher sends a message through RabbitMQ's default exchange to one named queue.
- “Read” means a registered consumer receives a delivery. RabbitMQ normally pushes deliveries to subscribed consumers; polling with `basic.get` is used only inside the bounded failure verifier.
- The synthetic product action is validation of a caption-task record. No email, payment, object-store, database, or cloud effect occurs.
- Broker acceptance and consumer completion are different facts, so the publisher uses confirms and the consumer uses manual acknowledgements.
- The stable `message_id` identifies one logical caption job. Production handlers would enforce that ID in a durable idempotency or domain-result store.
- A durable single-node quorum queue is chosen to expose a modern RabbitMQ queue contract. One member cannot prove replica failover or high availability.
- The exercise's SQS option is not used. SQS receive/visibility/delete semantics are not substituted into RabbitMQ code.

## Prediction

On the normal path, a confirmed persistent publish should create one ready delivery. A subscribed consumer should receive it with `redelivered=false`, perform the synthetic action, acknowledge on the same channel, and leave the queue empty.

On the changed path, the first consumer should receive `redelivery-caption-001` with `redelivered=false`. Closing that connection without `basic_ack` should cause RabbitMQ to requeue the unacknowledged delivery. A later connection should receive the identical body/message ID with `redelivered=true`. Acknowledging it should leave zero ready messages and zero consumers.

The broker may deliver work at least once; it cannot atomically combine an arbitrary external business side effect with the AMQP acknowledgement. Therefore the handler must tolerate a repeated delivery.

## Approach and why it fits

The solution deliberately separates five contracts:

1. [`common.py`](common.py) owns the exact endpoint, credentials, vhost, queue, and durable quorum declaration.
2. [`producer.py`](producer.py) serializes deterministic JSON, marks it persistent, requires routing, enables publisher confirms, and treats Pika confirm exceptions as failure.
3. [`consumer.py`](consumer.py) subscribes with `auto_ack=False`, bounds prefetch at one, validates the body, performs the synthetic action, and acknowledges afterward.
4. [`verify_reference.py`](../lab/verify_reference.py) proves the normal path, then closes the precise connection that owns an unacknowledged delivery and checks identity plus `redelivered=true` on the next attempt.
5. [`preflight.py`](../lab/preflight.py) proves the runtime is the local, labeled, loopback-only task project before mutation or cleanup.

This is the smallest setup that satisfies the instructor's actual RabbitMQ requirement and exposes the lecture's failure case without creating a real side effect.

## Step-by-step solution

### 1. Make topology declarations repeatable

Both producer and consumer declare `sd_beg_140_tasks` with the same properties: `durable=True` and `x-queue-type=quorum`. Queue declaration is idempotent only while the name and properties agree. A mismatch is a protocol error rather than an implicit migration.

### 2. Establish publisher-to-broker responsibility

The publisher uses the default exchange and sets the queue name as the routing key. `mandatory=True` makes an unroutable publish observable. `confirm_delivery()` changes the channel into confirm mode; Pika's blocking publish waits for RabbitMQ's acknowledgement and raises on broker negative acknowledgement or mandatory return. In Pika 1.4.4, successful `basic_publish` returns `None`; success is the absence of those exceptions, not a truthy return value.

Persistent delivery mode plus a durable queue describes recovery intent. The confirm tells the publisher when RabbitMQ has accepted responsibility according to that queue's semantics. None of this says a consumer has run.

### 3. Establish broker-to-consumer responsibility

The consumer registers with `auto_ack=False`. RabbitMQ tracks the delivery as unacknowledged. The callback validates that the JSON `message_id` matches the AMQP property, constructs the synthetic result, and only then calls `basic_ack` using the delivery tag from the same channel.

`prefetch_count=1` caps this consumer's unacknowledged work. That protects a slow worker from receiving a large in-flight batch, at the cost of possible throughput if one round trip cannot keep the worker busy.

### 4. Demonstrate failure and recovery

The verifier publishes a second message, receives it manually without acknowledging, then closes exactly that AMQP connection. RabbitMQ owns the still-unfinished delivery again and makes it eligible. A fresh connection obtains the same body and property ID with its broker-supplied redelivery bit set.

The second consumer acknowledges only after proving stable identity. The final passive queue declaration and broker CLI show no ready or unacknowledged messages.

### 5. Make duplicate effects harmless in a real service

For a PostgreSQL-backed caption job, one robust pattern is:

1. begin a transaction;
2. insert `message_id` into a table with a unique constraint, or lock/read the domain operation keyed by that ID;
3. if already completed, treat the message as a successful duplicate;
4. otherwise write the caption result and mark the operation completed in the same transaction;
5. commit;
6. acknowledge RabbitMQ.

If the process crashes after commit but before ack, redelivery repeats the lookup, observes completion, skips the second domain mutation, and safely acks. The database transaction and unique/domain invariant protect the side effect; the broker's redelivery flag is diagnostic evidence, not the idempotency key.

An irreversible third-party call needs that provider's idempotency key or a reconciled state machine. A local “processed” flag written before an external call can suppress work that never happened; written after the call, it can still leave an ambiguous crash window.

### 6. Convert documentation into design decisions

| RabbitMQ feature | What it covers | What it does not cover |
|---|---|---|
| Exchange, binding, routing key | Selects zero, one, or many destination queues | Consumer completion or business correctness |
| Mandatory publish | Reports that a publish reached no matching queue | Broker persistence by itself |
| Publisher confirm | Broker accepted responsibility for a publish | Consumer processing/acknowledgement |
| Manual consumer acknowledgement | Application declares a delivery successfully handled | Exactly-once external effects |
| Durable queue + persistent message | Restart recovery intent for topology and payload | Confirmation of disk/replica acceptance or single-node availability |
| Quorum queue | Replicated data safety when deployed with multiple members | Availability without a live majority; this lab has only one member |
| Prefetch | Bounds per-consumer in-flight deliveries and affects throughput/fairness | Global overload control |
| TTL and length limits | Bound age or resource accumulation | Successful processing; expired/overflowed data needs an explicit policy |
| Dead-letter exchange | Routes rejected, expired, over-limit, or delivery-limited messages when configured | Automatic diagnosis, safe replay, or guaranteed transfer in every configuration |
| Ready/unacknowledged/rate metrics | Expose backlog and current delivery state | End-to-end business success without application metrics |

## Correctness invariant

For every logical `message_id`, either the intended durable business result is not yet committed and the delivery remains eligible for retry, or the result is committed exactly once and every later delivery becomes a no-op before acknowledgement.

The lab proves the broker half of this invariant - an unacknowledged delivery is eligible again after connection closure. It does not create a durable business-effect store, so the learner must reason about that second half explicitly.

## Complexity, capacity, or resource reasoning

Publishing, routing to one queue, decoding one fixed-size message, and acknowledging it are each `O(message_bytes)` in application work; queue storage also scales with retained bytes plus metadata. That notation hides the operational constraints that matter: disk flush/replication latency, queue hot path, connection/channel count, message size, prefetch, consumer processing time, and retry traffic.

For sizing, define arrival rate `lambda` messages/s and sustainable completion rate `mu`. Backlog changes at approximately `lambda - mu`. If `lambda > mu` for `t` seconds, backlog grows by `(lambda - mu) * t`; if the post-spike rate becomes smaller than `mu`, drain time is `backlog / (mu - lambda_after)`. Scale from observed service time and target headroom rather than queue length alone.

The reference run used two sub-kilobyte messages, one producer at a time, one consumer at a time, prefetch one, and one local broker. It is correctness evidence, not a throughput result.

## Verification status

- Status: passed
- Evidence: [`lab/evidence.md`](../lab/evidence.md)
- Verified scope: exact local RabbitMQ 4.3.5 image, Pika 1.4.4, publisher confirms, required routing, persistent messages, durable quorum queue, normal manual ack, connection-close redelivery, identical ID/body, broker-set redelivery flag, final zero state, and exact cleanup.
- Limitation: no replication/failover, broker restart persistence, database idempotency, poison-message DLQ, TLS/auth hardening, concurrent ordering, load, or SQS path was executed.

## Failure modes and recovery

| Failure | Symptom/evidence | Response | Remaining risk |
|---|---|---|---|
| Publish connection fails before confirm arrives | No confirm; outcome may be ambiguous | Reconnect and republish stable ID | Original may also exist, so consumer must be idempotent |
| Unroutable publish | Mandatory return/exception; queue remains empty | Repair exchange/binding/routing contract | Retrying unchanged route repeats failure |
| Consumer crashes before business commit | Unacknowledged delivery returns | Retry on same or another consumer | Repeated poison input can hot-loop |
| Consumer crashes after commit but before ack | Same ID is redelivered | Detect committed ID/result, no-op, ack | Idempotency store/provider must itself be durable |
| Handler rejects every attempt with requeue | High redelivery rate, no progress, CPU churn | Bound retries/backoff; dead-letter terminal work | DLQ can silently accumulate without owner/alert |
| Ack sent on wrong channel | Channel-level protocol exception | Ack with delivery tag on owning channel | Connection recovery may trigger more redelivery |
| Consumers slower than publishers | Growing ready count and message age | Reduce work, add safe consumers/queues, or shed upstream load | Downstream API/database may become the new bottleneck |
| Single broker stops | Connection failures and no progress | Reconnect after recovery; deploy replicated queues for required availability | Majority loss, disk failure, and client recovery still need design |
| TTL/length limit discards data | Expiry/overflow/dead-letter metrics | Align retention with outage budget; alert and own replay | Storage is finite; an infinite buffer is impossible |

## Alternatives

| Alternative | Prefer when | Why not selected here |
|---|---|---|
| Direct synchronous call | Caller needs the result now and downstream latency/reliability fits request budget | Does not satisfy the assigned RabbitMQ exploration or long-running failure case |
| Standard-library queue simulation | Teaching only generic state transitions without product semantics | Cannot prove RabbitMQ ack/confirm/redelivery behavior |
| RabbitMQ classic queue | Disposable or non-replicated behavior is enough and its feature/performance profile is intentional | Quorum is the modern replicated-safety direction and the current tutorial default for durable work |
| RabbitMQ stream | Replay, offset tracking, and repeated reads are central | This exercise is work completion with acknowledgement, not log replay |
| Amazon SQS | Managed AWS queue, polling/visibility semantics, and cloud operations are acceptable | Conditional source alternative requires authorized account/cost scope and behaves differently |
| Kafka-compatible log | Partitioned ordered replay and consumer offsets are primary | Adds a heavier model and does not match the assigned RabbitMQ queue task |
| Automatic acknowledgement | Loss is acceptable and lowest overhead matters | Defeats the required crash-before-ack recovery behavior |

## Interview follow-ups

### SDE-2

- Where exactly do you place `basic_ack` around a PostgreSQL transaction, and why?
- A queue shows `messages_ready=0` and `messages_unacknowledged=50,000`. What do you inspect next?
- A worker repeatedly sees `redelivered=true`. How do you separate poison input from a crash loop or ack bug?
- What must the producer do if its connection dies before a publisher confirm arrives?
- When would prefetch one reduce throughput, and how would you tune it safely?

### SDE-3

- Design asynchronous video captioning at 5,000 uploads/s with a 10-minute completion SLO. Clarify message size, per-job cost, ordering key, retry budget, idempotency store, and downstream limits before choosing worker/queue topology.
- If the product now requires per-video stage order but maximum cross-video parallelism, partition or route by stable video ID and state the hot-key trade-off.
- If duplicate emails are unacceptable, explain why “exactly-once broker” is insufficient and design the domain/provider idempotency boundary.
- If a region is unavailable for 30 minutes, quantify retention/storage, recovery rate, RPO/RTO, replay ownership, and overload protection.
- If cost must fall by 40%, compare fewer consumers, batching/prefetch, payload pointers instead of large bodies, managed versus operated broker, and the SLO impact.

## Compare with Rahul's attempt

Complete only after Rahul attempts:

- Correct decisions:
- Missing reasoning:
- Different but valid choices:
- Evidence that still does not prove the claim:
- One thing to retry closed-book:
