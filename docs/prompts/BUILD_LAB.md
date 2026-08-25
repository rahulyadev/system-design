# Simple lab prompt

Use this in the same video chat:

```text
Create a small working lab for this video that makes the most important hidden
behavior visible. Read the notes first, use safe disposable resources, implement
the smallest useful experiment, run and verify it, and give me simple predict →
run → observe → explain → vary instructions.
```

If you already know the exact question, add one sentence:

```text
The question I want to test is: <your question>.
```

Example:

```text
Create a small PostgreSQL lab for this video. I want to see what two concurrent
transactions observe at different isolation levels and what survives when the
client or disposable database container is killed.
```

You do not need to choose a lab type, technology, file layout, or workflow mode. Codex will read the repository's safety and verification rules.
