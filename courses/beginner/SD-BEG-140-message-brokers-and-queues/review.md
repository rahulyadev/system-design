# Quick review - SD-BEG-140 Message Brokers and Queues

> Answer before opening `notes.md`. Keep this review usable in 10-20 minutes. Do the task prediction before opening its reference evidence.

## Closed-book recall

1. What user/system problem does an asynchronous operation boundary solve? Name one case that should remain synchronous.
2. Draw client, API, operation database/outbox, exchange, queue, worker, business store, acknowledgement, and status read in causal order.
3. What is the difference between a broker, exchange, queue, producer, and consumer?
4. Name the three distinct facts “API accepted,” “broker accepted,” and “business completed.” What proves each?
5. In RabbitMQ manual-ack mode, what states can a message occupy before and after delivery?
6. Why can a worker crash after a successful side effect and still cause a repeated attempt?
7. State an idempotency invariant using a stable `message_id`.
8. What do a durable queue, persistent message, publisher confirm, and replicated queue each add? What does none of them prove alone?
9. Compare RabbitMQ acknowledgement/redelivery with SQS visibility timeout/delete.
10. If `lambda=500 msg/s` and `mu=400 msg/s` for 10 minutes, how large is the backlog?
11. If arrivals then fall to `200 msg/s` while capacity stays `400 msg/s`, how long does a `60,000`-message backlog take to clear?
12. What is the difference between ready and unacknowledged messages? Give one likely diagnosis for each being high.
13. Why are queue depth, FIFO, and `redelivered=true` each incomplete evidence by themselves?
14. How do TTL, retry, and a dead-letter path answer different questions?
15. When would a direct call or database job table be simpler and safer than RabbitMQ?

## Draw from memory

- Components/states: client, API, `PENDING` operation, outbox/relay, exchange/routing, ready queue, unacknowledged delivery, worker, domain commit, ack, `SUCCEEDED`/`FAILED`.
- Arrows/order: validate -> durable intent -> publish/confirm -> return operation ID -> deliver -> commit -> ack -> report status.
- Failure boundary: domain commit succeeds but ack/connection fails, so the same logical ID becomes eligible again.
- Capacity invariant: stable over the chosen horizon only when average effective arrival rate, including retries, is below sustainable completion rate.
- Business invariant: for one logical ID, the durable externally visible transition happens at most once even if handler attempts repeat.

Then compare with [Big picture](notes.md#big-picture), [Acknowledgement lifecycle](notes.md#question-this-lifecycle-visual-answers), and [Components, ownership, and boundaries](notes.md#components-ownership-and-boundaries).

## Instructor-task recall

Without opening the task README, restate all source requirements:

- What must run locally?
- What two directions must Rahul's code demonstrate?
- What must he learn from documentation and experimentation?
- What conditional cloud alternative did the instructor mention?

Before running [`SD-BEG-140-T01`](tasks/SD-BEG-140-T01/README.md), predict:

1. first publish/consume result;
2. ready and unacknowledged counters at each state;
3. first `redelivered` flag;
4. effect of closing the consumer connection before ack;
5. later message identity and flag;
6. final state after ack;
7. exactly what the evidence still cannot prove.

## Answer cues

1. **Async decision:** caller need-now versus accept-now/finish-later; operation ID and state machine. See [Core concept 1](notes.md#1-choose-the-asynchronous-boundary-deliberately).
2. **Topology:** publish to exchange; route to queue; deliver to consumer. See [Core concept 2](notes.md#2-broker-exchange-queue-producer-and-consumer).
3. **Capacity:** backlog slope `lambda - mu`; finite buffer; age matters. See [Core concept 3](notes.md#3-buffering-and-load-leveling).
4. **Ack:** delivery is unfinished until safe result then same-channel ack; connection close requeues. See [Core concept 4](notes.md#4-acknowledgement-ownership-and-redelivery).
5. **Duplicates:** stable ID plus domain/provider invariant; flag is only evidence. See [Core concept 5](notes.md#5-delivery-semantics-and-idempotency).
6. **Failure policy:** classify, bound, delay, terminal owner, alert/replay. See [Core concept 6](notes.md#6-retention-ttl-retries-and-dead-letters).
7. **Durability:** topology, payload, broker acceptance, replication are separate. See [Core concept 7](notes.md#7-durable-queue-persistent-message-publisher-confirm).
8. **Order:** name the key/scope; protect commit with sequence/version. See [Core concept 8](notes.md#8-ordering-and-concurrency).
9. **Product boundary:** RabbitMQ ack/channel lifecycle is not SQS visibility/delete. See [Verified extensions](notes.md#verified-extensions).
10. **Task:** learner attempt remains unstarted even though separate reference verification passed. See [Instructor-assigned tasks](notes.md#instructor-assigned-tasks).

## Two-minute teach-back

1. Start with one concrete problem: a multi-minute VM/caption job should not hold an HTTP request open.
2. State the asynchronous contract: durable acceptance, operation ID, status/callback, eventual result.
3. Draw publisher -> exchange/routing -> queue -> consumer and identify the owner at each boundary.
4. Separate publisher confirm from consumer acknowledgement.
5. Walk through normal ready -> unacknowledged -> domain commit -> ack -> removed.
6. Change one condition: connection dies after domain commit but before ack.
7. Explain stable ID and idempotent business effect.
8. Quantify `lambda`, `mu`, backlog, bytes, oldest age, and drain time.
9. Bound retention/retries/dead letters and name the owner.
10. Finish with metrics and one alternative you would prefer under different requirements.

## Interview follow-ups

1. Where exactly should a RabbitMQ worker acknowledge relative to a PostgreSQL transaction? What crash windows remain?
2. How does a transactional outbox repair the operation-row/publish dual write, and why can it still duplicate?
3. Your queue has `ready=0`, `unacknowledged=50,000`, and no ack progress. What evidence do you inspect before scaling?
4. Publisher confirm times out. May the producer safely retry? What must the consumer guarantee?
5. How would you route caption stages for per-video order and maximum cross-video parallelism?
6. A bad message is immediately requeued forever. Design bounded retry, delay, terminal state, DLQ ownership, and replay safety.
7. The arrival spike doubles and the completion SLO halves. Recalculate worker capacity, backlog bytes, and drain headroom.
8. When would you choose a database job table, SQS, RabbitMQ, or a Kafka-style log?
9. What changes when the business can tolerate loss but not latency? What changes when it tolerates delay but not loss?
10. How would multi-region active-active processing change message identity, ordering, idempotency, and reconciliation?

## Flashcards

| Front | Back | Type |
|---|---|---|
| What does asynchronous acceptance prove? | Only that recoverable intent was accepted under the API contract; not final completion. | boundary |
| Broker versus queue? | Broker is intermediary/server; queue is one storage/delivery destination it manages. | term |
| Exchange role in RabbitMQ? | Routes publishes to queues using bindings/routing information; it does not store messages. | mechanism |
| Publisher confirm versus consumer ack? | Confirm covers publisher -> broker; ack covers consumer delivery -> broker. They are orthogonal. | boundary |
| Why acknowledge after commit? | A pre-commit crash leaves the message eligible; a post-commit retry can be made a safe no-op. | invariant |
| Why can effects duplicate? | Effect may commit while ack is lost; later delivery repeats the attempt. | failure |
| What makes a handler idempotent? | Stable logical ID plus durable rule ensuring repeated attempts create no extra domain effect. | correctness |
| Is `redelivered=true` the idempotency key? | No. It is a broker hint/evidence; use stable business identity. | misconception |
| Backlog slope? | Approximately `lambda - mu`, including retry/amplification in effective arrivals. | estimate |
| Drain time after arrivals fall? | `backlog / (mu - lambda_after)` when `mu > lambda_after`. | estimate |
| Ready high means? | Work awaits delivery; capacity/routing/consumer availability may be insufficient. | observability |
| Unacknowledged high means? | Work is in flight; handlers may be slow/stuck or prefetch too large. | observability |
| Durable queue alone proves? | Queue definition restart intent, not persistent payload, confirm, replication, or consumer success. | durability |
| What does TTL prove? | Only that data becomes ineligible after age/policy; not successful completion. | retention |
| Why bound retries? | Permanent failures otherwise hot-loop, consume capacity, and block healthy work. | reliability |
| What must a DLQ have? | Alert, owner, reason/context, retention, safe disposition/replay procedure. | operations |
| Does FIFO mean global completion order? | No; scope, multiple producers/consumers, retries, and commit order matter. | ordering |
| RabbitMQ failure-before-ack recovery? | Closing delivery channel/connection automatically requeues unacknowledged work. | product behavior |
| SQS failure-before-delete recovery? | Visibility expires and the stored message becomes visible again; duplicates remain possible. | comparison |
| Why send a video pointer? | Keeps broker payload bounded and avoids repeating large bytes on storage/redelivery. | design |

## English speaking check

- Use `acknowledgement`, `idempotent`, `backlog`, `redelivery`, and `decouple` naturally in one explanation.
- Explain `idempotent` without using the word itself: “Running the same logical request twice creates no second business effect.”
- Correct this weak phrase: “RabbitMQ guarantees exactly once and deletes the message when I read it.”
- Natural repair: “With manual acknowledgements, RabbitMQ retains responsibility for a delivery until the consumer acknowledges it; failure can redeliver, so the business handler must be duplicate-safe.”
- Replace “the queue is slow” with evidence: “Oldest-message age is rising because effective arrivals exceed acknowledgement rate; ready count is growing while consumer capacity is below target.”
- Say the contrast precisely: “The broker decouples timing and pace, but producer and consumer remain coupled through schema, routing, capacity, and business semantics.”

## Weakness log

Record only gaps Rahul demonstrates. Pack generation is not evidence of a weakness or of mastery.

| Date | Exact gap | Type | Repair | Retest |
|---|---|---|---|---|
| - | No demonstrated gap yet; learning state is `Not started`. | - | Attempt `SD-BEG-140-T01` before opening the reference. | After first attempt |

## Next review

- Suggested date: after the first study/attempt session, then one day later; progress remains unset until Rahul actually studies.
- Highest-value thing to retest: explain the crash-after-effect-before-ack window and derive the idempotency invariant without saying only “use exactly once.”
