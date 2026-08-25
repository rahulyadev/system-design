# Codex playbook for one video chat

This is an internal checklist. Rahul uses normal language and never needs to choose a workflow mode.

## 1. Understand the request

Infer the current intent:

- initial note creation;
- a follow-up explanation or correction;
- interactive quiz or understanding review;
- a lab or visualizer;
- a direct question that needs no file edit.

Use the video title and private folder to match the beginner or advanced course index. Videos can be processed in any order. Ask one concise question only if the match or required source is genuinely ambiguous.

## 2. Inspect the source and existing work

Before lecture-faithful writing, inspect:

- transcript coverage and timestamps;
- slide PDF and screenshots;
- video/audio availability for ambiguous passages;
- Rahul's questions or rough notes;
- existing `notes.md`, `review.md`, and linked labs;
- user-written content that must be preserved.

Report a compact source inventory. Do not ask Rahul to restate metadata Codex can infer from the folder and course index.

## 3. Cover the full video

Create an internal timestamp-to-concept map so important sections, examples, visuals, and homework are not lost. For long videos, inspect bounded chunks and synthesize only after all chunks are covered.

Organize public notes by the concept's logic, not by transcript paragraphs. Never copy the full transcript or publish raw screenshots.

## 4. Build a trustworthy explanation

First preserve the course's model and terminology. Then selectively verify claims that are version-dependent, counterintuitive, quantitative, related to durability/failure, or likely to be challenged in an interview.

Prefer official documentation, specifications, standards, and original papers. Use a small number of strong sources. Label course teaching, verified additions, and inference where the boundary matters.

For each major concept, cover:

1. problem;
2. simple intuition;
3. components or states;
4. mechanism in order;
5. worked example;
6. concurrency, ordering, or failure behavior;
7. trade-offs and alternatives;
8. observability;
9. wrong-use cases and misconceptions;
10. interview requirement changes.

For calculations, state assumptions and units, show intermediate steps, and sanity-check the result.

## 5. Choose useful visuals

| Learning question | Representation |
|---|---|
| What talks to what? | Component or data-flow diagram |
| In what order? | Sequence diagram or timeline |
| How does state change? | State diagram |
| What differs exactly? | Markdown table |
| How does a parameter affect behavior? | Small numerical example, chart, or executable visualizer |

Each non-trivial visual must state the question it answers, how to read it, and the key insight. Split overloaded diagrams.

## 6. Create only two lecture files

Draft `notes.md` first from `templates/lecture/notes.md`, then derive the compact `review.md` from it. Do not create extra lecture files unless Rahul explicitly asks.

In `notes.md`, keep instructor homework separate from Codex-added practice. Include only valuable vocabulary. Make interview answers reasoning outlines, not scripts.

In `review.md`, put questions before cues. Do not introduce facts that are absent from or inconsistent with the notes.

## 7. Handle follow-ups

- Lead with the answer, not repository mechanics.
- Prefer one clear mental model and a small example before deeper detail.
- Update the notes when the clarification is durable or corrects an error, unless Rahul asks for discussion only.
- During a quiz, ask one question and wait; do not reveal the next answer early.
- During a review, identify the missing reasoning step and distinguish terminology, mechanism, and decision gaps.
- For a lab request, read the lab standard and implement the smallest safe experiment that exposes the hidden behavior.

## 8. Quality check and handoff

Before finishing, check:

- full source coverage and visible uncertainties;
- agreement between simple and formal explanations;
- technical claims and nearby citations;
- rendered Mermaid syntax and working links;
- instructor homework separation;
- interview trade-offs and failure handling;
- no private/raw course material in tracked files;
- lab setup, tests, evidence, and safe cleanup when code exists.

Tell Rahul what changed, important uncertainties, and the one best next action in his notebook or lab. Never claim mastery solely because files were generated.
