# My attempt - SD-BEG-140-T01

This file belongs to Rahul. Initialization and repair must never overwrite it.

Do not open `reference/SOLUTION.md` or `lab/evidence.md` until you have written your prediction and completed a first run.

## Clarifications and assumptions

- Message schema and unique ID:
- Queue name and queue type:
- What “published successfully” means:
- What “processed successfully” means:
- Where acknowledgement happens:
- What may safely happen more than once:
- Retry limit or poison-message decision:

## Documentation feature map

Record dated official RabbitMQ links and explain each chosen feature in your own words.

| Feature | Problem it solves | Guarantee boundary | Failure or trade-off | Evidence I will inspect |
|---|---|---|---|---|
| Queue and exchange/routing |  |  |  |  |
| Consumer acknowledgement |  |  |  |  |
| Publisher confirm |  |  |  |  |
| Durable queue and persistent message |  |  |  |  |
| Prefetch |  |  |  |  |
| TTL or dead lettering |  |  |  |  |

## Prediction before running or designing

- Expected result after one publish:
- Expected first-delivery `redelivered` flag:
- Expected state while processing but before acknowledgement:
- Expected state after successful acknowledgement:
- Expected result if the consumer connection closes before acknowledgement:
- Correctness invariant:
- Exact evidence I expect:

## My approach

Implement your own producer and consumer under `starter/` or in new learner-owned files. Preserve a stable message ID. Use manual acknowledgement and acknowledge only after the synthetic business action succeeds.

## Actual evidence I observed

Do not paste predicted or reference output here as observed evidence.

- Exact commands:
- Docker context/project/service/image:
- Broker and client versions:
- Queue type and durability:
- Publish-confirm result:
- First consumer result:
- Ready/unacknowledged counts before acknowledgement:
- Result after acknowledgement:
- Failure-injection result:
- Redelivery flag and stable message ID:
- Final queue state:
- Cleanup state:

## Explanation in my own words

Explain the ownership transfer in order: publisher to broker, broker to consumer, consumer business action, acknowledgement, and broker deletion. State why a publisher confirm and a consumer acknowledgement prove different boundaries.

## Variation prediction and result

- Changed condition: close the consumer connection after receiving but before acknowledging.
- Prediction before running:
- Actual result:
- Why it changed:
- Duplicate side-effect risk:
- How I would make the handler idempotent:

## What I would say in an interview

Use: requirement -> asynchronous boundary -> message contract -> delivery semantics -> idempotency -> retry/dead-letter policy -> capacity -> observability -> failure recovery -> alternative.

## Questions after attempting

-
