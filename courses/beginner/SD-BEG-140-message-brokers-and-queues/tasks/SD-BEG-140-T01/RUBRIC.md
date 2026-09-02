# Rubric - SD-BEG-140-T01

Score Rahul's evidence independently. Do not award completion for opening or running the reference answer.

| Dimension | Needs work | SDE-2-ready | SDE-3-ready |
|---|---|---|---|
| Source requirements | Runs a broker or copies code without explaining it | Runs local RabbitMQ, publishes, consumes, and maps documented features | Converts broad “features and guarantees” wording into an explicit, evidence-backed boundary |
| Topology and message contract | Uses an unnamed queue/string | Names producer, exchange/route, queue, consumer, schema, and stable ID | Versions the contract and reasons about incompatible producers/consumers |
| Publish safety | Treats a socket write as broker acceptance | Uses a publisher confirm and a routable destination | Explains ambiguous confirm loss, retry, and possible duplicate publish |
| Consume safety | Uses automatic acknowledgement or acks before work | Uses manual acknowledgement after successful work | Places the ack after an idempotent transaction and handles partial failure |
| Failure evidence | Describes a crash without running it | Closes the consumer connection before ack and observes redelivery | Distinguishes redelivery evidence from proof of exactly-once effects |
| Queue state | Relies only on application prints | Inspects ready, unacknowledged, consumer, type, and durable state | Connects backlog age/rates and consumer capacity to scaling decisions |
| Retry policy | Requeues every failure forever | Separates retryable from terminal failure | Bounds retry, backoff, dead-letter handling, replay ownership, and alerts |
| Durability | Says `durable=true` guarantees everything | Separates durable queue, persistent message, confirm, and single-node limits | Chooses replicated queue/storage based on RPO, availability, throughput, and cost |
| Trade-offs | Calls asynchronous universally faster | States latency, complexity, staleness, duplicate, and operational costs | Gives a quantified threshold for changing worker count, queue partitioning, or technology |
| Communication | Lists RabbitMQ terms | Explains the lifecycle in causal order | Leads clarification and adapts when ordering, consistency, latency, or cost changes |

## Required completion evidence

- [ ] Rahul's own prediction before starting the consumer
- [ ] Rahul's own producer and manual-ack consumer code
- [ ] exact local preflight and runtime identity
- [ ] successful publish and normal consume evidence
- [ ] ready and unacknowledged state interpreted correctly
- [ ] controlled connection-close-before-ack failure
- [ ] identical message ID plus `redelivered=true` on the later delivery
- [ ] final acknowledgement and empty-queue evidence
- [ ] dated official-document feature/guarantee map
- [ ] one idempotency design and one bounded poison-message policy
- [ ] exact scoped cleanup evidence
- [ ] Rahul's natural two-minute explanation
