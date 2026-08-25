# Initial prompt for a new lecture chat

Copy the block below into a new Codex chat opened at the repository root. Replace every `<...>` value. Attach or place the private source files before sending it.

```text
Process one system-design lecture in notes mode.

Track: <beginner|advanced>
Lecture number: <NN>
Exact source title: <TITLE>
Private input directory: <inputs/private/...>
My main confusions/questions:
- <QUESTION 1>
- <QUESTION 2>

Instructor-assigned homework, if I captured it:
- <HOMEWORK OR "see assigned-homework.md">

Depth preference: deep, but explain in simple words first. Use math and small
numerical examples when they improve the model. I learn especially well from
diagrams, state changes, comparisons, and experiments.

Instructions:
1. Read AGENTS.md, courses/AGENTS.md, docs/LECTURE_PLAYBOOK.md, and all lecture
   templates before editing.
2. Inspect the private input directory and existing repository state. Report a
   short source inventory and coverage gaps before drafting.
3. Do not infer the lecture from its title. If the available source is inadequate
   for lecture-faithful notes, stop after giving me the smallest source-preparation
   action needed.
4. Create or update only courses/<track>/<NN-topic>/ and the corresponding track
   status entry. Preserve my existing writing.
5. Produce notes.md, visuals.md, english-meaning.md, homework.md,
   interview-questions.md, review-pack.md, and source-log.md from their templates.
6. Explain each important idea through problem, intuition, mechanism, example,
   trade-offs, failure modes, observability, and when not to use it.
7. Distinguish the course model, verified extensions, and inferences when the
   boundary matters. Verify implementation-sensitive claims using current primary
   sources and cite only sources you actually read.
8. Keep videos, transcripts, screenshots, course PDFs, Drive links/IDs, and other
   private source material untracked. Use original wording in public notes.
9. In homework.md, separate instructor-assigned work from Codex-added practice.
   Recommend the single highest-value lab or visualizer, but do not build a large
   project in notes mode.
10. Run a final fidelity, correctness, privacy, link, and Mermaid review. Leave
    uncertainties visible.

At handoff, tell me:
- what you created;
- which source parts remain uncertain;
- which claims you verified externally;
- what I should reconstruct in my physical notebook before rereading;
- the best next practical exercise.
```

## If you only have the video

Use this prompt first instead of requesting notes:

```text
Work in ingest mode for <TRACK> lecture <NN>, <TITLE>. The local video is at
<PRIVATE PATH>. Read the repository instructions, inspect available local tools,
and propose the smallest reproducible private ingestion pipeline for a timestamped
transcript and selected keyframes. Keep every generated source artifact under
inputs/private/ and out of Git. Do not draft public lecture notes until I review
the transcript's unclear technical terms.
```

## Chat policy

Use this same chat to correct and finalize this lecture. Open a new chat for the next lecture. If the recommended lab grows beyond a small experiment, use `BUILD_LAB.md` in a separate chat so code decisions do not bury lecture-source discussions.

