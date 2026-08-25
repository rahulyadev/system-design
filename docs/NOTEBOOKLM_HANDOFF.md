# NotebookLM handoff and revision

NotebookLM is the practice layer, not the source-of-truth layer. Correct and approve the repository notes first.

## What to upload

For each completed lecture, prefer:

1. `review-pack.md`
2. `notes.md`
3. `visuals.md`
4. `interview-questions.md`
5. `homework.md` after observations are recorded

Do not upload raw course videos, full transcripts, private screenshots, or copied course PDFs merely to recreate the public notes workflow. Keep those as private reference material according to your access rights.

## Notebook organization

Use one NotebookLM notebook per related module instead of one notebook per video:

- Beginner foundations and evaluation
- Relational and non-relational data systems
- Caching, queues, streams, and pub/sub
- Reliability, balancing, protocols, and storage
- Bloom filters, consistent hashing, and big-data foundations
- Beginner design case studies
- Advanced foundations and distributed systems
- Advanced storage and throughput
- Advanced retrieval and algorithmic design

This lets quizzes compare neighboring ideas, which is more valuable than recalling an isolated definition.

## Quiz prompt

```text
Create a 20-question closed-book quiz from these sources.

- 5 mechanism questions
- 5 compare/contrast questions
- 4 failure-mode or debugging scenarios
- 3 small estimation or ordering questions
- 3 senior interview follow-ups that change a requirement

Ask one question at a time. Do not reveal the answer until I commit to one.
After each answer, identify the exact missing reasoning step and cite the source section.
At the end, group my weaknesses by concept rather than by question number.
```

## Flashcard prompt

```text
Create high-signal flashcards only. Each card should test one decision, mechanism,
trade-off, invariant, or failure mode. Avoid cards that merely ask for an acronym.
Include a short answer, a why, and one common confusion. Tag each card as
foundation, mechanism, trade-off, failure, or estimation.
```

## Mock interview prompt

```text
Act as a senior backend system-design interviewer. Start with one requirement and
let me drive the design. Change one constraint at a time based only on these
sources. Challenge vague statements, ask for estimates, and make me explain
failure recovery. Do not give the architecture unless I am blocked. At the end,
score requirement discovery, assumptions, data model, API, scaling, reliability,
trade-offs, and communication.
```

## Review feedback loop

After a quiz or mock interview:

1. Record only genuine gaps in the lecture's `review-pack.md`.
2. Correct the full notes if the source model itself was unclear or wrong.
3. Add a lab variation when the weakness is predictive rather than verbal.
4. Update the next-review date in the track table.
5. Retest the weak concept in a mixed module quiz, not only the original wording.

Do not expand notes to include every quiz question. Good notes model the subject; quizzes sample that model.
