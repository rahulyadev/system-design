# English, communication, and interview standard

## Useful English

Choose only terms Rahul is likely to need while learning or explaining the lecture. For each:

- term or phrase;
- pronunciation or simple phonetic cue;
- plain English meaning;
- optional short Hindi cue;
- why it matters in this lecture;
- common misuse or nearby confusing word;
- five natural examples: simple, two engineering, interview, and professional/design-review.

Do not turn the section into a dictionary. Prefer important words such as contention, bottleneck, durable, idempotent, eventual, skew, saturation, quorum, invariant, trade-off, degradation, and mitigation only when the video actually uses or needs them.

## Spoken explanation

Create a natural 60-second outline and a deeper 3–5 minute outline. They are reasoning structures, not memorized scripts.

Useful answer flow:

```text
problem and requirement
→ important assumptions
→ simple design/mental model
→ mechanism and invariant
→ scale/failure behavior
→ trade-off and alternative
→ evidence/observability
```

## Interview ladder

Every lecture includes questions at three levels.

### Foundation

- Define the idea plainly.
- Explain the mechanism in order.
- Give a small example and one misconception.

### Working engineer / SDE-2

- Choose it under concrete requirements.
- Explain implementation boundaries.
- Diagnose a failure from evidence.
- Discuss testing, deployment, observability, and cost.

### Senior / SDE-3

- Clarify requirements and quantify scale.
- Defend data ownership and consistency.
- Identify bottlenecks and failure domains.
- Explain degradation, recovery, and operational ownership.
- Reject unjustified complexity.
- Adapt when one requirement changes.

## Design-case rubric

Score independently:

1. requirement clarification;
2. estimates and assumptions;
3. API and data model;
4. high-level architecture;
5. correctness and consistency;
6. scaling and bottlenecks;
7. reliability and recovery;
8. observability and operations;
9. security and abuse boundaries;
10. trade-offs and communication.

Do not reward technology-name listing without cause-and-effect reasoning.
