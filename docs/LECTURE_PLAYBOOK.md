# Codex lecture playbook

This is the operational procedure Codex follows when processing one lecture. Root and `courses/AGENTS.md` rules remain authoritative.

## 1. Parse the request

Extract:

- track: `beginner` or `advanced`;
- lecture number and exact source title;
- mode: `ingest`, `notes`, `lab-plan`, `lab-build`, or `review`;
- private source paths supplied by the user;
- specific confusions or desired depth;
- whether external verification and citations are requested;
- whether code implementation is authorized.

If the title is ambiguous, preserve the source title and flag the ambiguity. Do not normalize it by guessing.

## 2. Inspect before writing

Read the applicable instructions and templates. Then inventory files and check:

- transcript coverage and timestamps;
- screenshot names and whether they can be read;
- Rahul's questions and rough notes;
- assigned homework;
- existing lecture artifacts or user edits;
- related labs or projects that should be linked rather than duplicated.

Preserve existing user-written content. Improve around it or propose a clearly visible rewrite; do not erase personal observations.

## 3. Create a source coverage map

Build an internal table:

| Time range | Concept | Example or visual | Homework | Confidence | Output section |
|---|---|---|---|---|---|

Use it to find missing parts. Do not publish a transcript-by-transcript retelling. The final notes should be organized by the concept's logic.

For a long lecture, process bounded chunks and maintain one cumulative map. Do not finalize until all chunks are accounted for.

## 4. Separate three knowledge layers

Use these labels where the distinction matters:

- **Course model:** faithful paraphrase of the supplied lecture.
- **Verified extension:** added detail supported by a primary source.
- **Inference:** a connection or recommendation reasoned from the evidence.

Example:

> **Course model:** The lecture uses two concurrent sessions to show a non-repeatable read.  
> **Verified extension:** PostgreSQL's implementation and default isolation behavior are checked against the current PostgreSQL manual.  
> **Inference:** This can explain why an application-level “read, validate, update” flow still races without a lock or stronger transaction pattern.

Do not repeat labels on every sentence. Use them when source boundaries or certainty could be misunderstood.

## 5. Verify selectively but seriously

Research claims that are:

- implementation- or version-dependent;
- counterintuitive;
- related to failure or durability;
- quantitative;
- likely to be challenged in an interview;
- unclear because of transcript errors.

Prefer, in order:

1. official product documentation;
2. standards or protocol specifications;
3. original research papers;
4. official engineering documentation from the system's maintainers.

Use a small number of strong sources, usually two to five per lecture, instead of citation dumping. Cite close to the supported claim and record the source in `source-log.md`.

## 6. Draft the artifacts in dependency order

Use this order so later files derive from the full model:

1. `source-log.md`
2. `notes.md`
3. `visuals.md`
4. `homework.md`
5. `interview-questions.md`
6. `english-meaning.md`
7. `review-pack.md`

Do not create a review pack first and expand it into padded notes.

## 7. Deep-explanation checklist

For each central concept, answer:

1. What problem exists without it?
2. What is the simplest mental model?
3. What components or states exist?
4. What happens step by step?
5. What invariants should remain true?
6. What changes under concurrency or partial failure?
7. What is gained and what is paid?
8. When is another approach better?
9. How would we observe it in logs, metrics, queries, or traces?
10. How would an interviewer change the requirement?

If the lecture contains a formula, also explain the units, assumptions, boundary behavior, and a worked example.

## 8. Visual selection

Choose the smallest exact representation:

| Question | Preferred representation |
|---|---|
| What talks to what? | Component or deployment diagram |
| In what order? | Sequence diagram |
| How does state change? | State diagram or timeline |
| What differs exactly? | Table |
| How does load distribute? | Data-flow diagram plus small numeric example |
| How does a parameter change behavior? | Executable visualizer or chart |

Every visual needs a title phrased as a question, a reading guide, and one key takeaway.

## 9. Design homework around evidence

For instructor-assigned work, preserve the intent and label it. For extra practice, add only tasks that expose a misconception or important mechanism.

Each experiment specifies:

- the question;
- the initial prediction;
- controlled variables;
- exact observable evidence;
- expected result with the reason hidden below the prediction prompt when practical;
- one-variable variations;
- safe cleanup.

## 10. Build interview material from decisions

Organize questions into:

- **Foundation:** definition and purpose.
- **Working engineer:** mechanism, implementation, and debugging.
- **Senior design:** requirements, trade-offs, failure, sizing, and evolution.

A strong-answer outline should name assumptions, make a decision, explain the mechanism, state trade-offs, and define how success or failure is observed.

## 11. Audit the result

Score the lecture before handoff:

| Dimension | Points | Evidence |
|---|---:|---|
| Lecture fidelity | 20 | Coverage map, timestamps, homework separation |
| Technical correctness | 20 | Primary-source checks, visible uncertainties |
| Explanation depth | 20 | Mechanism, examples, failure, alternatives |
| Visual clarity | 10 | Exact, readable, explained visuals |
| Practical learning | 10 | Predict-observe-explain tasks |
| Interview usefulness | 10 | Decision-based questions and follow-ups |
| Retrieval quality | 5 | Compact review pack consistent with notes |
| Privacy and reproducibility | 5 | No raw material; commands and cleanup verified |

Target at least 85/100. Never inflate the score to avoid fixing a real gap.

## 12. Handoff format

Conclude with:

- files created or changed;
- source gaps or uncertain interpretations;
- external claims verified;
- the single most valuable lab and why;
- what Rahul should do on paper next;
- the next scheduled review action.

Do not say a lecture is mastered. Only Rahul's retrieval and practical evidence can establish mastery.

