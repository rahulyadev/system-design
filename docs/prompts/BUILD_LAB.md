# Prompt for a lab or visualizer

```text
Build the approved practical artifact for this concept.

Related lecture(s): <PATHS>
Artifact type: <micro-lab|visualizer|integration-lab|capstone increment>
Learning question: <ONE PRECISE QUESTION>
My current prediction: <WHAT I EXPECT AND WHY>
Requested scope: <SCOPE>

Read AGENTS.md and docs/LAB_AND_VISUALIZATION_STANDARD.md completely. Read the
related lecture notes and homework before proposing code.

First inspect the repository and produce a concise implementation plan that states:
- controlled and changed variables;
- observable evidence;
- technology choices and why each is necessary;
- safe failure-injection and cleanup boundaries;
- tests and manual experiments;
- explicit non-goals.

Then implement the smallest artifact that answers the learning question. Prefer
Python and disposable Docker Compose infrastructure. Add a README with predict →
run → observe → explain → vary steps, exact setup/health/cleanup commands,
expected evidence, troubleshooting, and links back to the lectures.

Run automated checks and the principal experiment. Compare observed behavior with
the documented expectation. Never target host or existing services for crash,
load, or data-loss testing. Do not push or merge unless I explicitly request it.
```

## PostgreSQL crash/isolation example values

```text
Related lecture(s): courses/beginner/05-relational-databases and
courses/beginner/06-database-isolation-levels
Artifact type: micro-lab
Learning question: What can concurrent PostgreSQL transactions observe at each
isolation level, and what survives client or server failure?
My current prediction: <WRITE THIS BEFORE RUNNING>
Requested scope: disposable PostgreSQL, two-session schedules, lock inspection,
client termination, abrupt container termination, recovery evidence, and retries.
```

