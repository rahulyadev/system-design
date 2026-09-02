# Reference solution - SD-BEG-130-T01

> **Spoiler:** Open only after writing a committed prediction and completing a first provider attempt. This is one defensible evidence plan, not proof that every provider or valid setup behaves identically.

## Clarifications and assumptions

- The course allows Cloudflare or Akamai. This reference uses Cloudflare terminology for a concrete path, while keeping the proof provider-neutral.
- Rahul owns and is authorized to change a disposable non-production domain/subdomain and origin. If that prerequisite is absent, the provider exercise is blocked rather than replaced by a simulation.
- The origin serves one original synthetic PNG below `100 KiB` at a unique path and can expose narrow access evidence.
- The image is public and identical for all users. No authorization, cookie, personal data, course asset, or secret is involved.
- The origin explicitly sends a public cache policy with an integer freshness lifetime and an image content type. The effective CDN and browser policies are recorded separately.
- The experiment uses fewer than 20 requests from one declared client/location. One run cannot prove global edge behavior.
- Provider console names, plans, and defaults change. Current official documentation outranks this reference's navigation language.
- Exact account, domain, zone/property, and origin identifiers are never committed.

Cloudflare's current official entry points are [account creation](https://developers.cloudflare.com/fundamentals/account/create-account/), [domain onboarding](https://developers.cloudflare.com/fundamentals/manage-domains/add-site/), [cache getting started](https://developers.cloudflare.com/cache/get-started/), [default cache behavior](https://developers.cloudflare.com/cache/concepts/default-cache-behavior/), [cache-response evidence](https://developers.cloudflare.com/cache/concepts/cache-responses/), and [purge guidance](https://developers.cloudflare.com/cache/how-to/purge-cache/purge-everything/). Akamai's corresponding conceptual route is its [caching model](https://techdocs.akamai.com/property-mgr/docs/know-caching) and [Property Manager caching behavior](https://techdocs.akamai.com/property-mgr/docs/caching-2).

## Prediction

For a previously unused, eligible image URL reaching one edge:

1. The first request should be forwarded to the origin and can populate the edge; its provider status commonly reports a miss-like outcome.
2. A second equivalent request reaching a cache that retained the entry before expiry should return the same body from cache, commonly with a hit-like status and an `Age` value.
3. Replacing origin bytes at the same URL sends no automatic change to an edge/browser that still considers its stored copy fresh, so version 1 may remain visible.
4. Purging the exact CDN URL should make the next relevant edge request fetch or validate and expose version 2.
5. A browser can still answer a fresh private copy without contacting the purged CDN.

These are hypotheses, not guaranteed provider outputs. A response can bypass cache; two requests can reach different edge states; eviction can cause another miss; cookies/headers/rules can prevent storage; and a prior request can make the “first” observed request a hit. Provider headers plus origin evidence and body identity decide what happened.

## Approach and why it fits

Use a real provider only for the assignment's account, configuration, URL, and console-learning requirements. Use one tiny public image because it is safe, cheap, highly reusable, and normally easy to make cache-eligible. Use an explicit origin policy and a unique path so the experiment can explain causality rather than reverse-engineering an old cache entry.

Evidence is triangulated:

- **client response:** status, body digest/version, `Cache-Control`, `Age`, and provider cache-status/edge headers;
- **origin:** narrow access evidence for this exact object and time window;
- **provider configuration:** redacted description of proxy, origin, cache rule, TTL, and exact-URL purge acknowledgement.

Latency is supporting information only. A fast origin response can look like a hit, and a distant/busy hit can be slower than a nearby miss.

## Step-by-step solution

### 1. Establish the safety boundary

Choose a disposable test subdomain and a Rahul-owned origin. Record its owner, expected cost, request cap, DNS/certificate impact, exact object path, exact rule/record, rollback, and cleanup. Abort if the workflow asks for an unplanned payment, production nameserver change, broad permissions, or secret publication.

### 2. Create the provider account and onboard only the test scope

Use the provider's current official flow. For Cloudflare full setup, an onboarded domain and a proxied eligible DNS record place the provider between the client and origin. Do not interpret “DNS exists” as “CDN cache is working”; proxy/routing and cache storage are separate facts.

If an existing production apex would need to change, stop and choose another authorized sandbox. Do not follow this reference into a risky migration.

### 3. Publish one safe, identifiable image at the origin

Use a path unique to this exercise, for example a semantic equivalent of `assets/sd-beg-130/image-v1.png`. Record byte length and a SHA-256 digest or visible embedded version. Return the correct image content type and an explicit public freshness policy. Separate browser `max-age` from shared-cache `s-maxage` when the provider supports/honors it and record any rule that overrides origin headers.

The important invariant is: all requests that map to one shared cache key are authorized to receive identical bytes during the accepted freshness interval.

### 4. Verify routing before claiming storage

Request the CDN hostname over HTTPS. Confirm the certificate/hostname, expected body digest, provider routing evidence, and origin response. A successful proxied response proves the request passed through the provider; it does not alone prove an edge hit.

### 5. Observe a controlled miss and later hit

Use a new versioned path or perform an exact-URL purge before the observation. Request the identical URL twice from one declared client/location. Capture only safe headers and the body digest. Match origin logs to the same time/path.

A defensible conclusion looks like this:

| Observation | Supported conclusion | Not yet proved |
|---|---|---|
| Miss-like provider status + one origin access + correct v1 digest | This request reached origin and returned v1; it may have populated the handling cache | Every edge now has the image |
| Hit-like status + age + unchanged origin count + same digest | The later request reused a retained copy for the same effective key | Global hit ratio or latency improvement |
| Bypass/dynamic status + origin access twice | Traffic was proxied but this response was not reused by that cache path | Exact cause until method/status/headers/cookies/rules/key are inspected |

Cloudflare documents `CF-Cache-Status` outcomes and `Age`; Akamai exposes different provider-specific evidence. Use the actual provider's current documentation.

### 6. Expose staleness deliberately and safely

Before changing anything, predict the result. Replace the origin body with version 2 at the same URL without altering the cache key. Request within the declared freshness lifetime. If the edge returns version 1 with hit/age evidence and no origin access, the result demonstrates stale relative to origin but reusable under cache policy.

This controlled test uses a synthetic object only. Never use a sensitive deletion or security update to demonstrate staleness.

### 7. Invalidate exactly one URL and verify recovery

Use the provider's single-URL purge, not a whole-zone purge. Record the exact redacted target and acknowledgement. Request again and correlate the next provider status/body digest with an origin access. Expect a miss/revalidation-like transition to version 2, but report the actual provider result.

Then check browser behavior separately. A normal browser navigation can still use a fresh private copy; DevTools cache evidence, a clean profile, or a new versioned URL distinguishes that from an edge issue.

### 8. Translate one implementation example

Choose one current provider/practitioner example and write:

`requirement → shareable representation/cache key → freshness/invalidation → origin protection → failure → observable signal`

For example, a media-thumbnail case may use content-versioned URLs, long browser/CDN freshness, high byte hit ratio, and safe old/new coexistence. A personalized account page likely bypasses shared caching or uses a rigorously scoped key. The learning is the decision chain, not the brand name.

### 9. Clean up narrowly

List the exact test object, cache rule/property, proxied record, and hostname before changing them. Remove only learner-created non-production resources through current provider/origin controls, or record why a synthetic public setup is retained and its cost/removal date. Do not delete an account, apex record, nameserver, shared origin, or whole CDN cache as routine cleanup.

## Correctness invariant

For every edge/browser reuse, the effective cache key must select a representation that is public to the same audience, body-compatible with the request's variants, and no older than the accepted freshness/version rule. A provider status saying `HIT` proves a cache decision, not that this invariant was designed correctly.

For the experiment, one additional evidence invariant applies: a claim about origin avoidance requires both cache-side evidence and the absence of a matching origin access in the bounded observation window. Latency alone is insufficient.

## Complexity, capacity, or resource reasoning

Let logical image request rate be `R`, browser usable hit ratio be `H_b`, and CDN usable hit ratio among arrivals be `H_c`.

- CDN arrival rate: `R x (1 - H_b)`
- Origin request rate: `R x (1 - H_b) x (1 - H_c)`
- Simplified cold amplification over steady origin rate: `1 / ((1 - H_b) x (1 - H_c))`

At `R = 10,000/s`, `H_b = 60%`, and `H_c = 95%`, the CDN receives `4,000/s`, the origin receives `200/s`, and full loss of both cache levels is `10,000 / 200 = 50x` steady origin load.

One provider experiment with two requests measures none of these fleet ratios. It proves a bounded state transition. Production sizing also needs byte hit ratio, object-size distribution, points of presence, TTL/eviction, request collapse, purge frequency, origin egress, regional traffic, and provider cost.

The learner run should stay below 20 requests and `2 MiB` total image transfer for a `100 KiB` object, excluding provider control-plane overhead. That is a safety cap, not a source requirement.

## Verification status

- Status: partially verified; provider reference remains ready, not live-verified
- Evidence: the deterministic local reference path is recorded in [`../lab/evidence.md`](../lab/evidence.md)
- Limitation: no provider account, domain, DNS, origin, edge, CDN URL, browser, or external cache was created or tested. Only the one-origin/one-edge state model was executed. Rahul must complete and explain the real provider path.

## Failure modes and recovery

| Failure | Symptom | Response | Remaining risk |
|---|---|---|---|
| DNS/proxy not active | Origin works directly but provider evidence is absent | Recheck exact non-production record/status and certificate using official onboarding docs | DNS/certificate propagation is external and variable |
| Response not cacheable | Repeated bypass/dynamic/miss and repeated origin access | Inspect method, status, `Cache-Control`, cookies, rules, and key; change only synthetic test policy | Provider plan/defaults can differ |
| Requests hit different edge states | Miss/hit sequence is inconsistent | Record edge evidence; repeat a small bounded set; avoid global claims | One location never proves global distribution |
| Unsafe cache key | Wrong user/variant could reuse bytes | Use public identical object; include required variants; bypass personalized responses | A previous leak requires incident response and purge |
| Browser masks edge result | Old image persists after edge purge | Inspect private cache; use clean profile/versioned URL; separate browser and CDN TTL | Uncontrolled clients may retain downloaded bytes |
| Whole-cache purge overload | Origin requests/latency spike | Purge exact URL; stage changes; cap origin fallback; use versioned assets | Cold edges still need a safe first fetch |
| Origin changes without invalidation | Hit returns old digest within freshness lifetime | Accept bounded age, purge exact URL, validate, or change content-versioned URL | Purge propagation and browser caches remain separate |
| Origin unavailable | Miss returns error or provider serves permitted stale bytes | Define stale-on-error policy and age cap; restore origin; observe user impact | Availability and freshness trade against each other |
| Unexpected cost/permission | Console asks for upgrade or broad access | Stop; do not accept; choose authorized free/sandbox route or record blocker | Provider offerings can change |

## Alternatives

| Alternative | Prefer when | Why not selected here |
|---|---|---|
| Akamai Property Manager | Rahul has authorized Akamai access and wants its rule/edge model | This reference uses Cloudflare labels for a more concrete path; the course permits either |
| Local reverse proxy | Real HTTP headers/process boundaries matter but no provider account exists | It still cannot satisfy the assigned provider account/console/CDN URL and adds setup |
| Deterministic Python model | Prediction and state transitions need safe repeatable evidence | It cannot prove routing, provider cacheability, real headers, latency, or propagation |
| Browser cache only | One user's repeat-load latency is the only objective | It does not demonstrate a shared geographically distributed CDN |
| Object storage public URL without CDN proxy | Durable object hosting alone is required | It does not prove an edge cache or provider routing path |
| No cache | Content has low reuse or strict immediate revocation | It fails the assigned exercise but can be the correct production design |

## Interview follow-ups

### SDE-2

- **Repeated `MISS`:** In what order would you inspect method, status, `Cache-Control`, cookies, provider-rule match, effective key/query, edge ID, object size, eviction, and origin evidence?
- **Old image after purge:** How do you prove browser versus CDN ownership using URL version, DevTools cache source, provider status/`Age`, and origin digest?
- **Safe deployment:** How do content-hashed asset URLs let old and new application versions coexist without a global purge?
- **Origin protection:** What timeout, request-collapsing, concurrency cap, load shedding, and degraded response keep a cold edge from overwhelming origin?

### SDE-3

- **Global proof:** Design a measurement that separates browser hit ratio, CDN request/byte hit ratios by region, upper-tier hits, origin fetches, and user latency without assuming one client represents the world.
- **Five-second update SLO:** Allocate freshness and invalidation time across metadata, browser, edge, remote cache, and origin; define breach evidence and operational owner.
- **Private variants:** Decide whether authorization/tenant/locale/device/encoding belong in the key or require bypass. Explain poisoning and cross-user isolation tests.
- **Failure change:** If origin is down, when may the edge serve stale media? State maximum age, user-visible marker, recovery, audit, and content categories that must fail closed.
- **Deletion change:** Explain why a public browser-cached object cannot be remotely erased from a device and redesign with short-lived authorization or encryption/key revocation.

## Compare with Rahul's attempt

Complete only after Rahul attempts:

- Correct decisions:
- Missing reasoning:
- Different but valid provider choices:
- Evidence that supports or contradicts the prediction:
- One thing to retry closed-book:
