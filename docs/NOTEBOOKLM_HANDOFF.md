# NotebookLM handoff and revision

NotebookLM is the quiz and flashcard layer. Correct the repository notes first.

## What to upload

For each studied video, upload:

1. `review.md`
2. `notes.md`
3. a linked lab's `README.md` only when you completed the experiment

Do not upload raw course videos, full transcripts, private screenshots, or copied course PDFs merely to recreate the notes workflow.

## Notebook organization

Use one NotebookLM notebook for a related group of videos rather than one notebook for every video. This lets quizzes compare similar ideas such as isolation levels, cache strategies, or queues versus streams.

Possible groups:

- Beginner foundations
- Databases
- Caching and messaging
- Reliability, protocols, and storage
- Data structures for scale
- Design case studies
- Advanced distributed systems
- Advanced storage, throughput, and retrieval

## Quiz prompt

```text
Create a 20-question closed-book quiz from these sources.

- 5 mechanism questions
- 5 compare/contrast questions
- 4 failure or debugging scenarios
- 3 small estimation or ordering questions
- 3 senior interview follow-ups that change a requirement

Ask one question at a time. Do not reveal the answer until I commit to one.
After each answer, identify the exact missing reasoning step and cite the source
section. At the end, group my weaknesses by concept.
```

## Flashcard prompt

```text
Create high-signal flashcards. Each card should test one decision, mechanism,
trade-off, invariant, or failure mode. Avoid acronym-only cards. Include a short
answer, why it is true, and one common confusion.
```

## Mock interview prompt

```text
Act as a senior backend system-design interviewer. Start with one requirement and
let me drive the design. Change one constraint at a time based on these sources.
Challenge vague statements, ask for estimates, and make me explain failure
recovery. Do not give the architecture unless I am blocked. At the end, score my
requirements, assumptions, data model, API, scaling, reliability, trade-offs, and
communication.
```

## Bring weaknesses back to the video chat

Return to the same Codex chat and say:

```text
NotebookLM exposed these weak areas:
- <gap>
- <gap>

Test whether I understand them and update notes.md or review.md where useful.
```

Do not add every quiz question to the notes. Repair the underlying concept instead.
