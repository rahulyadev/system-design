# System Design Learning Lab

This repository is Rahul Yadav's long-term system-design learning system. It turns each lecture into four kinds of understanding:

1. **Explain it** — detailed notes in simple language.
2. **See it** — diagrams, timelines, tables, and small visualizers.
3. **Break it** — safe experiments that expose failure modes.
4. **Defend it** — interview questions, trade-offs, and concise explanations.

The goal is not to collect summaries. The goal is to be able to draw the system, predict its behavior, run it, explain why it behaved that way, and discuss alternatives in an interview.

## Recommended Codex setup

- Open this repository as one Codex project.
- Use **GPT-5.6 Sol** and select **Max** in the model picker for lecture synthesis, difficult lab design, and final quality review.
- Use one new chat per lecture. Keep corrections and note refinement in that lecture's chat.
- Start a separate chat for a lab only when the lab becomes a substantial project.

## Quick start for one lecture

1. Choose the next lecture from [`courses/beginner/README.md`](courses/beginner/README.md).
2. Watch it once and capture your questions, the assigned homework, and only the screenshots that explain a diagram or state change.
3. Put private inputs under `inputs/private/<track>/<lecture-slug>/`. This directory is ignored by Git.
4. Start a new Codex chat in this repository and paste [`docs/prompts/START_LECTURE.md`](docs/prompts/START_LECTURE.md), filling in the placeholders.
5. Review Codex's draft against the lecture. Correct misunderstandings before treating the notes as final.
6. Write the ideas in your physical notebook from memory, then check what you missed.
7. Complete the prediction-observation-explanation homework or lab.
8. Use the interview questions and do a two-minute teach-back without reading.
9. Upload the clean review material to NotebookLM and schedule spaced reviews.

Read [`docs/LEARNING_WORKFLOW.md`](docs/LEARNING_WORKFLOW.md) for the complete cycle.

## Repository map

```text
.
├── AGENTS.md                         # permanent project instructions for Codex
├── courses/
│   ├── AGENTS.md                     # lecture-specific Codex rules
│   ├── beginner/                     # 36-lecture beginner track
│   └── advanced/                     # 16-lecture masterclass track
├── docs/
│   ├── LEARNING_WORKFLOW.md           # Rahul's learning loop
│   ├── LECTURE_PLAYBOOK.md            # exact Codex processing procedure
│   ├── LAB_AND_VISUALIZATION_STANDARD.md
│   ├── NOTEBOOKLM_HANDOFF.md
│   └── prompts/                       # copy-paste prompts
├── templates/lecture/                # required output templates
├── inputs/private/                   # local source material; never committed
├── labs/                             # focused experiments shared by topics
└── projects/                         # larger capstones combining topics
```

Lecture folders are created only when a lecture is processed. This avoids 52 empty directories and lets the structure evolve from real use.

## Output for each completed lecture

```text
courses/<track>/<nn-topic>/
├── notes.md
├── visuals.md
├── english-meaning.md
├── homework.md
├── interview-questions.md
├── review-pack.md
└── source-log.md
```

Code should live in `labs/` or `projects/` and be linked from the relevant lecture instead of being duplicated.

## Tracks

- **Beginner first:** concepts, common building blocks, and standard design questions.
- **Masterclass second:** foundations at greater depth, databases, distributed systems, storage engines, throughput, retrieval, and algorithmic design.

Do not rush into the masterclass merely because the beginner notes exist. Move forward when you can explain the concept without notes, draw the main flow, discuss at least two trade-offs, and complete its important experiment.

## Public-repository boundary

This repository is public. Do not commit course videos, course PDFs, full transcripts, raw screenshots, private Drive URLs or IDs, credentials, or copied course notes. Keep source material under the ignored `inputs/private/` directory. Commit only original explanations, limited attributed excerpts when necessary, independently created diagrams, code, and experiment results.
