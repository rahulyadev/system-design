# Quick review - SD-BEG-130 Caching at Different Levels

> Answer before opening [notes.md](notes.md). Keep this review usable in 10-20 minutes. The artifact is ready; Rahul's learning state remains **Not started** until he studies and demonstrates recall.

## Closed-book recall

1. What expensive work does a browser hit, CDN hit, remote-cache hit, and stored database counter each avoid?
2. Why is “bytes exist under a key” insufficient to call a lookup a usable hit?
3. Distinguish a private HTTP cache from a shared HTTP cache. What security question changes?
4. Trace a CDN miss and the following hit in exact order. Which component is the origin?
5. Why is the selected CDN edge not guaranteed to be the geographically closest building?
6. What can `Age` and a provider cache-status header prove, and what can neither prove alone?
7. Distinguish freshness, validation, expiry, invalidation, exact-URL purge, and capacity eviction.
8. Why can users still see an old image after the CDN reports a successful purge?
9. State the `total_posts` invariant. Which publish, retry, delete, and repair operations preserve it?
10. Why is `total_posts = total_posts + 1` safer than application read-modify-write under concurrency?
11. Why does “remote cache” not imply one physical Redis server?
12. Give three reasons an image may repeatedly miss a CDN even when the URL looks unchanged.
13. At `10,000 requests/s`, with `60%` browser hits and `95%` CDN hits among arrivals, calculate browser hits, CDN arrivals, CDN hits, and origin requests.
14. With the same hit ratios, what is the full cold-cache amplification over steady origin QPS?
15. Why must request hit ratio and byte hit ratio be measured separately?
16. Name two workloads where adding another cache level is the wrong choice.
17. Which evidence distinguishes browser staleness, CDN staleness, remote-cache staleness, and database-counter drift?

## Draw from memory

### Placement map

- Components/states: user, browser private cache, CDN shared edge, API, remote cache, database-derived counter, base rows.
- Arrows/order: earlier usable hit returns; each miss moves toward more authoritative or more expensive work.
- Failure boundary: changes move outward through different mechanisms; a server-side purge cannot force a disconnected browser to contact the network.
- Key invariant: every hit is interchangeable for this request under user/tenant/variant/version/freshness policy.

### CDN sequence

- First request: edge key lookup → miss → origin fetch → eligibility decision/store → response.
- Second request: same effective key → fresh hit → provider status and age evidence.
- Source change: origin version changes while an admitted copy can remain fresh.
- Repair: expiry/revalidation, exact-URL purge, or a new content-versioned URL.

### Counter transaction

- Base state: a precisely defined set of published post rows.
- Derived state: `users.total_posts`.
- Publish order: begin transaction → insert/publish once → atomic increment once → commit.
- Other paths: unpublish/delete decrement, idempotent retry, reconciliation and repair.

Then compare with [Big picture](notes.md#big-picture) and [Ordering, concurrency, and stale state](notes.md#ordering-concurrency-and-stale-state).

## Instructor-task recall

Without opening the task pack, restate [`SD-BEG-130-T01`](tasks/SD-BEG-130-T01/README.md):

1. Which two provider choices did the course name?
2. What account/configuration activity was assigned?
3. What exact object must be cached and through which URL must it be retrieved?
4. Which documentation, console, and implementation-example exploration belongs to the exercise?
5. What headers, origin evidence, and privacy controls would make your completion reviewable without exposing credentials?
6. Why does the passed local companion model not complete the real provider exercise?
7. Predict first miss, later hit, same-URL origin change, exact-URL purge, and one changed condition.

Do not open `reference/SOLUTION.md` until your prediction and provider attempt are recorded in `ATTEMPT.md`.

## Answer cues

- One-minute mental model: [The 60-second story](notes.md#the-60-second-story)
- Cache-level map: [Big picture](notes.md#big-picture)
- Placement decision: [Core concept 1](notes.md#1-choose-placement-from-the-guarantee-not-from-the-availability-of-memory)
- Browser/private cache: [Core concept 2](notes.md#2-client-side-caching-can-remove-the-entire-backend-request)
- CDN miss/hit/origin: [Core concept 3](notes.md#3-a-cdn-is-a-shared-cache-and-routing-system-in-front-of-an-origin)
- Remote cache: [Core concept 4](notes.md#4-a-remote-cache-shares-application-results-across-server-instances)
- Database counter: [Core concept 5](notes.md#5-a-database-can-store-a-maintained-derived-value)
- Invalidation boundaries: [Core concept 6](notes.md#6-multi-level-invalidation-is-a-distributed-coordination-problem)
- Overcaching: [Core concept 7](notes.md#7-cache-everywhere-is-an-anti-pattern)
- Arithmetic: [Worked example](notes.md#worked-example-and-calculations)
- Evidence and incidents: [Deep mechanism](notes.md#deep-mechanism)
- Choice matrix: [Design choices](notes.md#design-choices)
- Interview ladder: [Interview practice](notes.md#interview-practice)

## Two-minute teach-back

1. **Problem:** repeated network, query, computation, and byte-delivery work raises latency, load, and cost.
2. **Authority:** base data owns truth; each cache/derived value has a declared reuse contract.
3. **Levels:** browser avoids the network, CDN avoids the origin, remote cache avoids application/database work, and a stored counter avoids an aggregate.
4. **CDN mechanism:** route to edge, compute key, hit or origin miss/fill, then freshness/revalidation/eviction/purge.
5. **Correctness:** key scope plus freshness/version decides reuse; private and shared caches have different leak risks.
6. **Invalidation:** each layer has separate reach and ordering; CDN purge does not erase browser copies.
7. **Counter:** base mutation and increment belong in one transaction, with idempotency and reconciliation.
8. **Numbers:** multiply earlier miss probabilities to get origin rate; test full cold-cache amplification.
9. **Failure:** diagnose with browser, CDN, cache, origin, and database evidence rather than guessing.
10. **Decision:** keep only levels whose measured benefit repays stale-state and operational complexity.

## Interview follow-ups

### Foundation

1. Is every client-held value an HTTP browser cache entry? Why does the distinction matter?
2. Can an expired response remain stored? Can a fresh response be evicted?
3. Why can a CDN hit be old relative to the origin without violating its freshness policy?
4. What makes a response unsafe for a shared cache?
5. Is a database-derived counter a disposable cache or a maintained read model?

### SDE-2

6. The first CDN request is `MISS`; the next is also `MISS`. Give a check order using method, status, headers, cookies, rules, key, edge, capacity, and origin logs.
7. A user edits an avatar but only their current browser stays old. Which level do you inspect first and what evidence settles it?
8. How do content-hashed URLs change invalidation and deployment compatibility?
9. Redis is down and PostgreSQL QPS rises fifty times. Which controls keep a correct fallback from becoming an outage?
10. Two concurrent post publishes leave `total_posts` one too small. Reconstruct the unsafe application read-modify-write.
11. A counter occasionally doubles after timeouts. Where do you add idempotency and what evidence proves one logical mutation applied once?
12. How would you test an exact-URL purge without touching a production hostname or clearing the entire CDN?

### SDE-3

13. At `100,000 requests/s`, browser hits `50%` and CDN hits `99%` of arrivals. Calculate origin QPS and cold amplification.
14. Define a five-second avatar freshness SLO across browser, CDN, metadata API, and origin. Which level is hardest to control?
15. Design cache keys for public profile variants by tenant, locale, encoding, authorization, and schema version. Which dimensions can safely collapse?
16. One celebrity profile produces 30 percent of reads and writes. Analyze edge hot objects, Redis hot keys, and PostgreSQL counter-row contention separately.
17. When is serving stale public media during origin failure correct? State maximum age, user signal, recovery, and audit evidence.
18. A legal deletion must revoke access in five seconds. Why is a long-lived public browser cache incompatible, and what architecture changes?
19. Decide whether another load-balancer cache adds unique value when browser and CDN caches already serve immutable assets.
20. Define operational ownership for version rollout, purge failure, cache poisoning, origin overload, and counter reconciliation.

## Flashcards

| Front | Back | Type |
|---|---|---|
| Earliest cache level? | The earliest boundary whose reuse scope, privacy, and freshness contract make the answer safe—not simply the first component with memory. | decision |
| Browser hit saves what? | The network request and every backend/CDN/origin operation for that resource. | mechanism |
| Shared-cache danger? | One unsafe key or cacheability rule can reuse one user's representation for another. | security |
| CDN origin? | The configured upstream the edge contacts on a miss or revalidation; it may be a service/object store, not necessarily a database. | definition |
| Basic CDN population? | Request reaches edge → key lookup → miss → origin fetch → eligible store → response; later equivalent request may hit. | mechanism |
| “Nearest” edge caveat? | Routing/performance/reliability choice, not guaranteed minimum geographic distance. | boundary |
| Fresh response? | Its current age is within its freshness lifetime, so reuse need not first validate. | mechanism |
| Validation? | Conditional origin check, commonly with an entity tag or modification time, before reusing a stale stored response. | mechanism |
| `no-cache` versus `no-store`? | `no-cache` requires validation before reuse; `no-store` prohibits storage by compliant caches. | misconception |
| Expiry versus eviction? | Expiry changes freshness by time; eviction removes for capacity even if fresh. | comparison |
| CDN purge boundary? | It invalidates selected provider copies; it does not necessarily erase browser/service-worker copies. | failure |
| Remote cache? | A logically shared application cache reached over a network; internal topology may still be sharded/replicated. | definition |
| Counter invariant? | `total_posts` equals base posts satisfying the declared published predicate at the promised consistency point. | invariant |
| Counter transaction? | Apply the base post transition and matching atomic counter change in one transaction. | correctness |
| Counter retry risk? | A repeated logical publish can increment twice without idempotency. | failure |
| Layered origin probability? | Multiply the miss probabilities of every earlier level in the simplified model. | estimate |
| Request versus byte hit ratio? | Requests measure object reuse count; bytes measure origin/delivery volume saved, and large objects can dominate. | observability |
| Cold amplification? | Full logical request rate divided by steady origin-miss rate. | failure |
| Overcaching signal? | A level lacks unique latency/load/egress benefit or lacks safe key, lifecycle, failure, and ownership evidence. | decision |
| Strong cache alert? | Cache failure or stale versions combined with user/origin impact, not hit ratio alone. | observability |

## English speaking check

- Use “stale” in a sentence with a numerical age budget rather than calling every older value wrong.
- Explain “invalidation” without confusing it with capacity eviction.
- Use “origin server” while making clear it is a role, not necessarily one machine.
- Correct this weak phrase: “The CDN always sends users to the geographically closest server.”
- Correct this weak phrase: “We purged Cloudflare, so every browser now has the new image.”
- Improve this design-review sentence: “Redis is remote and centralized, so it cannot be sharded.”

Suggested natural corrections:

- “The CDN routes the request to a suitable edge using its network policy; that edge is often nearby but not guaranteed to be geographically closest.”
- “The URL purge invalidated provider copies, but an existing browser can still reuse a fresh local response.”
- “Remote describes the application's network boundary; the logical cache service may be implemented with shards and replicas.”

## Weakness log

No learner gap has been demonstrated yet. Add a row only after Rahul predicts, calculates, draws, configures, or explains and a specific gap is observed.

| Date | Exact gap | Type | Repair | Retest |
|---|---|---|---|---|

## Next review

- Suggested first closed-book review: 2026-09-03, after studying the notes once.
- Highest-value thing to retest: distinguish the four cache levels by avoided work and invalidation reach, then calculate layered origin QPS without notes.
- Best next action: before opening the reference, write the `SD-BEG-130-T01` miss/hit/stale/purge prediction in `ATTEMPT.md` and identify a disposable provider account/domain path that cannot affect production.
