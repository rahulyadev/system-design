# My attempt — SD-BEG-060-T01

This file belongs to Rahul. Initialization and repair must never overwrite it.

## Clarifications and assumptions

- Database/version:
- Default isolation:
- Exact schema:
- Plain or locking read in each schedule:

## Prediction before running or designing

| Schedule | First read | Writer outcome | Predicted second read/wait/error | Why | Evidence that would disprove me |
|---|---|---|---|---|---|
| Read Committed |  |  |  |  |  |
| Repeatable Read |  |  |  |  |  |
| Read Uncommitted request |  |  |  |  |  |
| Serializable conflict |  |  |  |  |  |
| Plain vs `FOR UPDATE` variation |  |  |  |  |  |

## My approach

### Session A commands and order


### Session B commands and order


### Inspection command


## Actual evidence I observed

Do not paste expected or reference output here as observed evidence.

### Runtime identity and server version


### Read Committed


### Repeatable Read


### Read Uncommitted request


### Serializable conflict and retry


## Explanation in my own words

- Isolation contract:
- Snapshot/visibility mechanism:
- Lock mechanism:
- Why PostgreSQL differs from the course's MySQL trace:
- Why the retry must include the entire transaction:

## Variation prediction and result

- Changed condition: plain Serializable `SELECT` → `SELECT ... FOR UPDATE` behind the same uncommitted writer
- Prediction:
- Observed wait/blocker evidence:
- Result after the writer ends:
- Why:

## Failure, observability, and proof gap

- Likely production failure:
- Metric/view/SQLSTATE:
- Safe recovery:
- What this one-row experiment does not prove:

## What I would say in an interview


## Questions after attempting
