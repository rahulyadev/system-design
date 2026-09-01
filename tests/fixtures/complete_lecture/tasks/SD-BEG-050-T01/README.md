# SD-BEG-050-T01 — Relate orders to customers and prove the invariant

> Synthetic instructor-task fixture. Attempt before opening `reference/SOLUTION.md`.

## Source and fidelity

- Source timestamp/slide: `fixture:00:10-00:12`
- Faithful paraphrase: define customers and orders, connect each order to an existing customer, list each order with the customer's email, and explain what prevents an orphan order.
- Short exact excerpt: Not needed.
- Source ambiguity: deletion behavior was not specified; default to rejecting deletion while orders exist.

## Exact requirement checklist

- [ ] Create the two relations with stable primary keys.
- [ ] Enforce that every order references an existing customer.
- [ ] Seed two customers and three orders deterministically.
- [ ] Return one row per order with the customer email.
- [ ] Demonstrate what happens for a missing customer.
- [ ] Explain the invariant in plain English.

## Codex-added safety or verification

- Use only schema `sd_beg_050_t01` in the disposable learning database.
- Assert the exact result and capture the foreign-key failure separately.
- Do not reset any other schema or database.

## Inputs, constraints, and expected artifact

| Item | Contract |
|---|---|
| Input | Synthetic customers and orders from `lab/01_seed.sql` |
| Constraints | PostgreSQL; one order-grain result row; deterministic ordering |
| Output | Learner query, observed result, failed orphan insert, explanation |
| Completion evidence | Three ordered rows, foreign-key error, and Rahul's own reasoning |

## Before you start: predict

Record the expected three rows, invariant, likely error, and confirming evidence in `ATTEMPT.md` before running anything.

## Setup

Use the root loopback PostgreSQL profile. Follow `lab/README.md`, verify the exact database and schema, then load only the task-owned schema and seed.

## Learner steps

1. Inspect the schema and seed without opening the reference query.
2. Write a deterministic query returning order ID, customer email, and total.
3. Attempt an order whose customer is missing and capture the database response.
4. Explain the result grain and invariant.
5. Predict what changes if customer deletion cascades.

## Progressive hints

<details><summary>Hint 1 — requirement</summary><p>State what one output row represents before choosing the query.</p></details>

<details><summary>Hint 2 — invariant</summary><p>The child row contains the parent's stable identity.</p></details>

<details><summary>Hint 3 — mechanism</summary><p>Match the child reference to the parent key and order by the child identity.</p></details>

## Acceptance criteria

- [ ] Exactly one correctly ordered row per order.
- [ ] An orphan insert is rejected by PostgreSQL, not merely by application prose.
- [ ] Evidence distinguishes expected from observed behavior.
- [ ] Rahul can explain why the invariant ends at the database ownership boundary.

## Cleanup/reset

Run only `lab/05_reset.sql` after confirming the database and exact schema printed by the preflight. The schema contents are disposable; other schemas are untouched.

## Reference answer boundary

After committing to your attempt, open [`reference/SOLUTION.md`](reference/SOLUTION.md). Its execution status is skipped in this fixture; that does not imply learner completion.
