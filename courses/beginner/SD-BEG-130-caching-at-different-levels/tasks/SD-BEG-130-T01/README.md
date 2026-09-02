# SD-BEG-130-T01 - Configure a CDN and serve one image

> Instructor-assigned task from `SD-BEG-130`. Write your prediction in `ATTEMPT.md`, complete your own provider attempt, and only then open `reference/SOLUTION.md`.

## Source and fidelity

- Source timestamp/slide: `00:11:48-00:12:52`; slide 47 supplies the concrete three-step exercise.
- Faithful paraphrase: explore Cloudflare or Akamai documentation and console behavior, create an account with one of them, configure a simple CDN, put one simple image behind that CDN, retrieve it through the CDN URL, and learn from provider or practitioner implementation examples rather than stopping at theory.
- Short exact excerpt: Not needed; the spoken assignment and final exercise slide are semantically consistent.
- Source ambiguity: the instructor does not choose a provider, account/plan, domain, origin, image, cache headers, cache key, TTL, proof headers, number/location of requests, cost limit, cleanup, or privacy treatment. The source also does not say what to do when Rahul does not own a disposable domain/origin.

The spoken “number one” hands-on exploration and “number two” documentation/video use-case exploration are kept in one task because both support the same configured-image outcome. The checklist below preserves both parts.

## Exact requirement checklist

- [ ] Choose either Cloudflare or Akamai.
- [ ] Create an account with the chosen provider.
- [ ] Explore its CDN documentation and console/configuration options.
- [ ] Configure a simple CDN with an origin.
- [ ] Cache one simple image through the CDN.
- [ ] Access that image by its CDN URL.
- [ ] Study provider channels/tutorials or implementation examples showing how CDN configuration supports real use cases.
- [ ] Explain what you learned by doing the configuration.

## Codex-added safety or verification

These controls are additions, not instructor wording:

- Use only an account, origin, object, and domain/subdomain Rahul owns and is authorized to change. Never target an employer, shared, or production zone.
- Prefer a disposable test subdomain and an original synthetic image below `100 KiB`; do not upload private course material, personal data, copyrighted assets, credentials, or secrets.
- Check the provider plan, request, storage, egress, domain, and certificate implications before creating anything. Stop if a paid upgrade or ownership change appears.
- Do not place API tokens, account/zone/property IDs, email addresses, full dashboard screenshots, or unredacted private hostnames in this repository.
- Use a unique versioned image path for a clean observation; make fewer than 20 deliberate requests.
- Capture response status, `Cache-Control`, `Age` when present, provider cache-status evidence when available, selected edge/point-of-presence evidence when available, and narrow origin access evidence. Do not assume the first two requests must be `MISS` then `HIT`.
- Change the origin bytes at the same URL only after predicting the stale result; purge only that exact URL, never the whole cache, and observe the next request.
- Record current provider documentation links and date because console labels and plan behavior change.
- Delete only the exact test object/rule/record after verifying its identity, or state why it is intentionally retained. Never delete an apex/production DNS record as cleanup.
- Run the deterministic local companion only to understand mechanism. Its passed output does not fulfill the real provider account/configuration task.

## Inputs, constraints, and expected artifact

| Item | Contract |
|---|---|
| Provider | Cloudflare or Akamai, as named by the course; record the product/path actually used |
| External identity | Rahul-owned, non-production account and test zone/property; no secrets or private identifiers committed |
| Origin | Rahul-owned disposable HTTP(S) origin that returns one synthetic image and observable request evidence |
| Object | One original/synthetic image below `100 KiB`, at a unique versioned path |
| Cache policy | Explicitly record origin response headers and any provider override; do not rely on an unexplained default |
| Requests | Same CDN URL requested repeatedly from one declared client/location, then one controlled origin change and exact-URL purge |
| Research | At least one current official provider guide and one provider/practitioner implementation example; extract a mechanism and trade-off rather than only listing links |
| Output | Rahul-owned `ATTEMPT.md` entries with redacted configuration outline, predictions, narrow headers/origin evidence, variation, cleanup, and explanation |
| Completion evidence | A reachable CDN URL during the experiment, proof of origin-versus-edge behavior, the image bytes/hash/version, and Rahul's explanation; reference/local output does not count |

If Rahul does not have an authorized disposable domain and origin, the provider portion is **blocked**, not silently replaced. Record that exact prerequisite in `ATTEMPT.md`. The local companion can still teach miss/hit/purge mechanics, but the source requirement remains incomplete.

## Before you start: predict

Write in `ATTEMPT.md` before opening the provider console:

1. what the first request to a unique image URL will do at the edge and origin;
2. what a second equivalent request from the same client/location should do;
3. which exact response/origin evidence would support `MISS`, `HIT`, or bypass;
4. what happens if origin bytes change at the same URL before freshness expires;
5. what an exact-URL purge can invalidate and which browser-held copy it may not reach;
6. the safe cache-key scope and maximum acceptable stale period;
7. one result that would falsify your explanation.

Do not read `lab/evidence.md` or the reference solution until this prediction is committed in your own words.

## Setup

### Assigned provider environment

You need a browser, one authorized Cloudflare or Akamai account, a disposable domain/subdomain and origin, one synthetic image, and an HTTP inspection tool such as browser DevTools or `curl`. Use the provider's current official onboarding and caching documentation rather than following stale dashboard coordinates from this pack.

Expected scope: one account, one test zone/property or subdomain, one origin, one image below `100 KiB`, one narrowly scoped cache rule only if the origin policy is insufficient, fewer than 20 requests, roughly 30-90 minutes, and negligible traffic. Provider/domain charges are not assumed; verify before proceeding and stop at any payment prompt you did not plan for.

Before changing external state, write down the exact test hostname/object/rule and how it can be recovered. Confirm that changing its DNS cannot affect production. Never paste credentials into a shell command that will be recorded.

### Codex-added local companion

[`lab/README.md`](lab/README.md) describes a standard-library Python model of one origin and one edge. It has no network, cloud, DNS, credentials, service, or cleanup state. Run it only after your prediction. It cannot demonstrate routing, provider headers, real latency, eviction, propagation, or task completion.

## Learner steps

1. Record provider choice, authority, test hostname/origin, cost check, image identity, and cleanup target without storing secrets.
2. Read the provider's current official onboarding, cacheability, response-evidence, TTL, and URL-purge documentation. Record the dated links.
3. Before configuration, write the first/second-request and stale/purge predictions in `ATTEMPT.md`.
4. Configure only the disposable test hostname/property so traffic reaches the provider before the declared origin.
5. Make the image explicitly and safely cacheable, or document the exact provider rule and origin headers controlling it.
6. Request the unique CDN image URL. Capture narrow response headers and origin evidence without private identifiers.
7. Request the same effective key again. Determine which layer served it; do not infer a hit from latency alone.
8. Change the origin image at the same URL, predict first, request within the freshness window, and explain the observed version.
9. Purge only that exact URL, request again, and correlate provider evidence with the origin fetch/version.
10. Study one implementation example and map its requirement → cache level/key/freshness/invalidation → benefit → failure risk → evidence.
11. Run the local companion if useful, then explicitly separate its evidence from the provider experiment.
12. Verify the exact external target and perform narrow cleanup or document intentional retention.
13. Explain the mechanism aloud without the reference.

## Progressive hints

<details><summary>Hint 1 - requirement</summary><p>The output is not an account screenshot. It is one image demonstrably delivered through a configured CDN URL, plus an explanation grounded in provider and origin evidence.</p></details>

<details><summary>Hint 2 - invariant</summary><p>A hit is safe only if the same effective cache key selects bytes that satisfy the declared public scope and freshness policy.</p></details>

<details><summary>Hint 3 - mechanism</summary><p>Separate routing through the provider from storage at the edge. A proxied response can still be uncacheable or bypassed.</p></details>

<details><summary>Hint 4 - observation</summary><p>Correlate a provider cache-status/age signal with narrow origin access evidence and an exact image version or digest. Latency by itself is not proof.</p></details>

<details><summary>Hint 5 - changed condition</summary><p>Ask whether changing origin bytes at a stable URL sends any message to an edge or browser that already considers its copy fresh.</p></details>

## Acceptance criteria

- [ ] Every source requirement is represented in Rahul's own attempt, including documentation/example exploration and the image-through-CDN-URL result.
- [ ] Rahul proves authority over a non-production account, origin, and hostname without committing credentials or private identifiers.
- [ ] Provider, dated primary documentation, configuration scope, origin, object path/version, cache policy, and cleanup target are stated.
- [ ] The CDN URL returned the expected synthetic image, with status and body identity/hash captured.
- [ ] First and repeated requests are explained using provider response evidence plus origin evidence, not latency alone.
- [ ] Cache key and public/private scope are safe and explicitly reasoned.
- [ ] TTL/freshness and exact-URL invalidation are distinguished from capacity eviction and browser caching.
- [ ] Same-URL origin change and exact-URL purge were each predicted first, observed, and explained, or a precise provider limitation/blocker is recorded.
- [ ] One implementation example is translated into requirement, mechanism, benefit, trade-off, failure, and observable signal.
- [ ] The local companion, if used, is labeled non-provider evidence and is not claimed as task completion.
- [ ] Cleanup is exact, identity-checked, and non-production; retained resources and possible cost are documented.
- [ ] Rahul can give a natural two-minute explanation without opening the reference.

## Cleanup/reset

Before cleanup, list the exact test hostname, origin object, cache rule/property version, and DNS record. Remove or disable only those learner-created resources using the provider/origin's current supported workflow. Do not clear the entire CDN, delete an account, change an apex nameserver, delete a production/shared origin, or use broad cloud cleanup.

If the test configuration is intentionally retained, verify it serves only synthetic public content, record expected ongoing cost/exposure, and set a review/removal date. The local companion creates no persistent resources and needs no cleanup.

## Reference answer boundary

After writing your prediction and completing a first provider attempt, compare with [`reference/SOLUTION.md`](reference/SOLUTION.md). The supplied reference and passed local model do not create Rahul's account, configure DNS, or prove a live CDN URL, so `learner_status` remains `not_started` until Rahul supplies his own evidence and explanation.
