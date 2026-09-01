# Quick review — SD-BEG-050 Relational Databases

> Synthetic validation fixture. Answer before opening `notes.md`.

## Closed-book recall

1. What does one row mean in each relation?
2. What invariant does the foreign key enforce?
3. Why is an application check alone race-prone?
4. Draw one customer with two orders and label the keys.
5. When should a relationship not be enforced by a local foreign key?
6. What is the output grain of a customer-to-orders join?
7. What evidence distinguishes a constraint failure from a query bug?

## Draw from memory

Draw parent identity, child reference, cardinality, and the transaction boundary. Then add a separate-service boundary and show why the local constraint stops there.

## Instructor-task recall

Restate `SD-BEG-050-T01`, predict the valid and invalid inserts, explain the invariant, and name one changed condition.

## Answer cues

Use the row-grain, deep-mechanism, and failure sections in [notes.md](notes.md). Do not open the reference solution until after an attempt.

## Two-minute teach-back

Cover problem, row meaning, keys, one concrete join, the race prevented by a constraint, trade-off, and cross-service limit.

## Interview follow-ups

1. How does deletion policy change the model?
2. Why might the child-side access path still need an index?
3. What replaces a foreign key when ownership crosses services?

## Flashcards

| Front | Back | Type |
|---|---|---|
| What does a foreign key prove? | A local referenced value satisfies the declared parent-key rule in the database transaction boundary. | invariant |
| What must be stated before joining? | Input and output grain plus relationship cardinality. | mechanism |
| Why not cross-service foreign keys? | Independent ownership and failure/transaction boundaries. | trade-off |

## English speaking check

Use “referential integrity” naturally, explain it without saying “foreign key,” and replace “database will manage everything” with a bounded claim.

## Weakness log

| Date | Exact gap | Type | Repair | Retest |
|---|---|---|---|---|

## Next review

- Suggested date: after the first attempt
- Highest-value thing to retest: application check versus database invariant
