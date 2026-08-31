# NotebookLM handoff

Correct the repository notes first. NotebookLM is the retrieval-practice layer, not the source of truth.

For a studied video upload:

1. `review.md`;
2. `notes.md`;
3. a task's `README.md` and `lab/evidence.md` only after Rahul attempted it;
4. never raw transcripts, videos, screenshots, or course PDFs.

Group related videos—databases, caching/messaging, reliability, protocols/storage, data structures, design cases, or advanced internals—instead of one notebook per video.

Recommended quiz prompt:

```text
Ask one closed-book question at a time. Mix mechanisms, comparisons, failures, estimates, and changed requirements. Do not reveal the answer before I commit. After each answer, identify the exact missing reasoning step and cite the notes section. End with a weakness map.
```

Bring the weakness map back to the same Codex lecture chat so `notes.md` or `review.md` can be repaired without copying every quiz question.
