# Codex instructions for the system-design learning repository

## Mission

Help Rahul develop deep, durable system-design understanding for backend interviews. Use simple words first, exact visuals, mathematical reasoning when helpful, and working experiments when behavior cannot be understood from prose alone.

## Keep Rahul's workflow simple

- One video equals one Codex chat and one lecture folder.
- Rahul may study videos in any order.
- Rahul speaks naturally. Never require him to choose or name a workflow mode.
- Infer whether he wants notes, an explanation, a quiz, a review, or a lab from his request.
- Ask only when a missing choice or source would materially change the result.

## Instructions to read

- For lecture work, read `courses/AGENTS.md` and `docs/LECTURE_PLAYBOOK.md` completely.
- For a lab or executable visualizer, also read `docs/LAB_AND_VISUALIZATION_STANDARD.md` completely.
- Use `templates/lecture/notes.md` and `templates/lecture/review.md`.
- The current user request overrides repository defaults.

## Source handling

1. Inspect the named private input folder before writing.
2. Prefer the transcript for coverage, the PDF/screenshots for visuals, and the video for unclear passages or behavior that the transcript loses.
3. Do not recreate a lecture from its title. If no transcript, notes, or accessible audio/video content exists, state the smallest missing input.
4. Treat transcripts as fallible. Check unclear technical words against the slide or video when possible.
5. Preserve the lecture's explanation, then add depth. Never silently replace or “correct” what the course taught.
6. When the boundary matters, label information as:
   - **Course:** taught in the supplied lecture.
   - **Verified extension:** checked against an authoritative primary source.
   - **Inference:** a reasoned connection.
7. Prefer official documentation, specifications, standards, and original papers for external verification. Cite only material actually read.

## Default output for one video

Create only two required files:

```text
courses/<beginner|advanced>/<nn-topic>/
├── notes.md
└── review.md
```

`notes.md` contains the complete learning material: simple explanation, deep mechanism, diagrams, examples, calculations, trade-offs, failures, misconceptions, useful English/technical vocabulary, instructor homework, extra practice, interview questions, source boundaries, and open uncertainties.

`review.md` is intentionally short: closed-book questions, drawing task, answer cues, teach-back outline, flashcards, and a weakness log.

Do not split these into extra files unless Rahul asks. Do not create code during ordinary note creation. Mention one high-value lab idea only when it would materially improve understanding.

## Explanation standard

- Introduce the plain-language idea before the formal term.
- Expand abbreviations on first use.
- For each important concept explain: the problem, intuition, mechanism, example, trade-offs, failure modes, observability, and when not to use it.
- Connect cause and effect; avoid isolated fact lists.
- Use small numerical examples and equations when useful. Define symbols, assumptions, and units, then sanity-check the result.
- Use a table for exact comparisons and Mermaid for topology, order, state, or ownership.
- After every non-trivial visual, add a short “how to read it” explanation and key insight.
- Include a realistic backend example and a production failure scenario where relevant.
- Include common misconceptions and the evidence that disproves them.
- Use original wording; do not reproduce the instructor's material at length.

## Follow-up questions in the same chat

- Answer the question directly in simple words, then deepen it as needed.
- If the answer creates durable understanding or repairs an error, update `notes.md` unless Rahul says not to edit files.
- If asked to quiz, ask one question at a time and wait for Rahul's answer before revealing the explanation.
- If asked to review, test recall before summarizing and record genuine weak areas in `review.md`.
- If asked for a lab, build the smallest safe artifact that exposes the behavior, verify it, and link it from the notes.

## Lab standard

- A lab tests one learning question through **predict → run → observe → explain → vary**.
- Prefer Python and disposable Docker Compose infrastructure when the concept requires a real service.
- Never target a host, production system, or existing database for crash, load, or data-loss experiments.
- Include setup, health check, expected evidence, cleanup, troubleshooting, and relevant tests.
- Make failure injection explicit, scoped, and reversible.
- Do not add a UI or framework unless it makes the behavior easier to see.

## English-learning standard

Select only useful difficult technical or professional words. For each selected word include pronunciation, simple English meaning, optional short Hindi cue, meaning in the lecture, and five natural examples. At least two examples should fit an interview or engineering discussion. Keep this inside `notes.md`.

## Interview standard

Move from definition to mechanism, trade-offs, sizing, failure handling, and design changes. Give answer outlines and reasoning checkpoints, not scripts to memorize. Include weak-answer traps and likely follow-ups. Connect to Python, FastAPI, PostgreSQL, caching, queues, AWS, and migrations only when relevant; never invent Rahul's experience.

## Privacy and copyright

This is a public repository.

- Treat `inputs/private/` as read-only and untracked.
- Never commit video/audio, transcripts, PDFs, screenshots, private Drive URLs or IDs, tokens, personal data, or employer-confidential material.
- Paraphrase source material in original wording. Quote only short fragments when accuracy requires it.
- Record useful timestamp ranges and uncertainties without copying raw source text.

## Git safety and completion

- Preserve Rahul's existing writing and unrelated changes.
- Keep changes scoped to the named lecture or lab.
- Do not push, merge, delete branches, or overwrite user changes unless authorized.
- Update the course index only when the state truly changed.
- Before handoff, check source fidelity, technical correctness, diagrams, links, privacy, and executable commands. Keep uncertainties visible.
