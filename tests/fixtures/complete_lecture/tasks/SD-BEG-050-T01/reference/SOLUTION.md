# Reference solution — SD-BEG-050-T01

> **Spoiler:** Open only after writing a committed attempt. This is a synthetic fixture answer and was not executed.

## Clarifications and assumptions

One output row represents one order. Customer deletion is restricted while orders exist. Emails are display values, not join keys.

## Prediction

The valid join returns three rows ordered by order ID. An insert with a missing customer is rejected by the foreign-key constraint.

## Approach and why it fits

Join `orders.customer_id` to the stable `customers.id`. Select the customer email only after the identity match. Ordering by order ID makes the evidence deterministic.

## Step-by-step solution

```sql
SELECT o.id AS order_id, c.email, o.total
FROM sd_beg_050_t01.orders AS o
JOIN sd_beg_050_t01.customers AS c ON c.id = o.customer_id
ORDER BY o.id;
```

To observe the failure in an expendable transaction, attempt an order whose `customer_id` is absent and roll back after capturing the error. A real task runner should execute this in a way that treats the expected constraint failure as evidence rather than aborting unrelated assertions.

## Correctness invariant

For every non-null `orders.customer_id`, exactly one matching `customers.id` exists. The parent primary key provides uniqueness and the child foreign key provides existence.

## Complexity, capacity, or resource reasoning

For this tiny fixture, performance is irrelevant. At scale, the parent primary key supplies the lookup access path; common customer-to-orders access normally needs an index beginning with `orders.customer_id`.

## Verification status

- Status: skipped
- Evidence: [`../lab/evidence.md`](../lab/evidence.md)
- Limitation: PostgreSQL was not executed by the portable structural fixture.

## Failure modes and recovery

| Failure | Symptom | Response | Remaining risk |
|---|---|---|---|
| Missing parent | Foreign-key violation | Repair workflow/input, not blind retry | Authorization may still be invalid |
| Wrong join key | Missing or multiplied rows | Restate grain and join identities | Dirty business keys can hide the bug |
| Broad reset | Unrelated data loss | Exact schema guard | Human must still verify environment |

## Alternatives

| Alternative | Prefer when | Why not selected here |
|---|---|---|
| Denormalized customer email on order | Immutable historical snapshot is required | It does not replace customer identity or integrity |
| Application-only existence check | Additional friendly validation | It races and other writers can bypass it |

## Interview follow-ups

### SDE-2

Explain the child-side index, constraint error handling, deletion policy, and transaction test.

### SDE-3

Explain what changes when customers and orders have independent service/database ownership, including reconciliation and deletion propagation.

## Compare with Rahul's attempt

Complete this only after Rahul attempts the real task; the fixture intentionally records no comparison.
