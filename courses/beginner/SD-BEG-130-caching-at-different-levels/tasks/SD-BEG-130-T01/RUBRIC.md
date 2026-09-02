# Rubric - SD-BEG-130-T01

Score Rahul's evidence independently. Do not award completion for reading the reference, running the local companion, or showing an account screenshot without a working image path and mechanism evidence.

| Dimension | Needs work | SDE-2-ready | SDE-3-ready |
|---|---|---|---|
| Source fidelity | Omits account/provider, simple CDN, image URL, or exploration requirement | Completes every source requirement and separates added controls | Identifies source ambiguity without silently rewriting the assignment |
| Scope and safety | Uses a shared/production zone or records secrets/IDs | Uses an authorized disposable target, synthetic image, narrow request budget, and exact cleanup | Anticipates DNS/certificate/cost/blast-radius risk and defines abort/recovery ownership |
| Cacheability and key | Assumes proxied means cached | States method/status/headers/rules and effective safe key | Handles user/tenant/query/encoding/cookie variants and poisoning/isolation tests |
| Mechanism | Says “CDN is fast” | Traces routing, edge lookup, origin miss/fill, hit, freshness, and purge in order | Separates edge tiers, request collapsing, validation, eviction, browser cache, and provider-specific uncertainty |
| Evidence | Uses latency or dashboard alone | Correlates response status/cache status/age/body identity with origin evidence | Distinguishes what one edge/client run proves from global behavior and designs stronger measurement |
| Staleness/invalidation | Treats origin write or purge as universal refresh | Predicts same-URL staleness, exact-URL purge, and browser boundary | Quantifies propagation/freshness SLO and prevents purge-driven origin overload |
| Implementation research | Lists links without learning | Maps one real requirement to mechanism, benefit, trade-off, failure, and signal | Challenges assumptions and transfers the design to a changed scale/consistency/cost requirement |
| Failure/recovery | Covers only happy-path hit | Diagnoses bypass, repeated miss, origin/certificate error, and performs narrow cleanup | Designs origin protection, rollback/versioning, incident evidence, and operational ownership |
| Communication | Names products and screenshots | Gives a clear prediction → evidence → mechanism → trade-off explanation | Leads clarification, quantifies thresholds, and states proof limits naturally |

## Required completion evidence

- [ ] Rahul's own prediction before provider configuration/requests
- [ ] Authorized non-production account/domain/origin boundary with no secrets committed
- [ ] Cloudflare or Akamai documentation and console exploration
- [ ] One configured CDN path and one synthetic image reachable through the CDN URL
- [ ] Exact image identity/version and cache policy
- [ ] First/repeated response headers plus narrow origin evidence
- [ ] Same-URL update and exact-URL purge prediction/result, or a precise blocker
- [ ] Safe cache-key and public/private reasoning
- [ ] One provider/practitioner use case translated into mechanism and trade-off
- [ ] Explicit separation of local-model evidence from real-provider evidence
- [ ] Exact identity-checked cleanup or documented retention/cost
- [ ] Rahul's natural two-minute explanation and one changed requirement
