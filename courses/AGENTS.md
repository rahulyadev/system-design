# Lecture-processing instructions

These rules apply to work under `courses/`. Read the root `AGENTS.md` first.

## Supported modes

Every request must operate in one explicit mode. If the prompt does not name a mode, use `notes`.

| Mode | Purpose | Expected writes |
|---|---|---|
| `ingest` | Inspect and validate private source inputs | source inventory only; no public transcript copy |
| `notes` | Create or improve the seven lecture artifacts | lecture Markdown files |
| `lab-plan` | Design an experiment without implementing it | `homework.md` plus a proposed lab link |
| `lab-build` | Implement and verify an approved lab | `labs/<slug>/` or `projects/<slug>/` plus links |
| `review` | Test mastery and repair weak notes | review dates, corrections, and concise review material |

Do not silently turn `notes` mode into a large code project. Recommend the smallest useful lab and wait for a lab request unless the user explicitly requested implementation.

## Source gate

Before writing lecture-faithful notes:

1. Identify the track, number, canonical title, and output slug.
2. Inventory transcript, video/audio, screenshots, Rahul's rough notes, questions, and assigned homework.
3. Confirm whether the transcript has timestamps and mark any unreadable or ambiguous sections.
4. If no content source is available, stop after creating a source-preparation plan. A lecture title is not enough.
5. Treat transcript text as potentially inaccurate. Cross-check unclear technical terms with timestamps, screenshots, or the local video.

Private inputs may be read but must not be copied into tracked files.

## Per-lecture path

Use lowercase kebab-case and a two-digit prefix:

```text
courses/<beginner|advanced>/<nn-topic-slug>/
```

Create these files from `templates/lecture/`:

```text
notes.md
visuals.md
english-meaning.md
homework.md
interview-questions.md
review-pack.md
source-log.md
```

Links to shared labs belong in `notes.md` and `homework.md`. Do not copy the same lab into multiple lecture folders.

## Processing sequence

### 1. Build a coverage map

Map timestamp ranges to concepts, examples, diagrams, homework, and open questions. Use this map internally to detect omissions. Put only the compact source record in `source-log.md`.

### 2. Extract the instructor's model

First capture what the lecture teaches, including its terminology, assumptions, examples, and homework. Do not yet embellish it with generic system-design knowledge.

### 3. Verify and deepen

Check important factual or implementation-sensitive claims against primary sources. Add details that explain mechanisms, edge cases, or modern production practice. Label these as verified extensions and cite them near the claim.

### 4. Explain from multiple angles

For every central idea, include:

- a one-sentence intuition;
- a concrete step-by-step example;
- the formal mechanism;
- a visual or exact comparison when useful;
- at least two trade-offs;
- at least one failure mode;
- one “when this is the wrong choice” case;
- a connection to a realistic backend system.

### 5. Generate active work

Separate instructor-assigned homework from Codex-added reinforcement. Every experiment must ask Rahul to predict the result before running it and explain any mismatch afterward.

### 6. Prepare interview retrieval

Create questions at foundation, working-engineer, and senior-design levels. Answers should be outlines containing decision points, not memorized paragraphs.

### 7. Run a quality pass

Check fidelity, correctness, clarity, visuals, application, interview value, privacy, links, and any executable commands. Leave visible TODOs for unresolved uncertainty.

## Artifact-specific requirements

### `notes.md`

- Use progressive depth: quick intuition, core model, deep dive, production behavior, trade-offs, failure modes, and revision summary.
- Include prerequisites and links to related lectures.
- Add numerical examples where capacity, probability, latency, throughput, storage, or availability is involved.
- Include “confused with” comparisons and common misconceptions.

### `visuals.md`

- Start each visual with the question it answers.
- Prefer Mermaid for flow, state, sequence, topology, and lifecycle.
- Provide a plain-language reading guide and the key insight after each visual.
- If the behavior depends on time or user input, specify a visualizer rather than faking it in a static diagram.

### `english-meaning.md`

- Select roughly 8–15 high-value terms; use fewer if the lecture is short.
- Include pronunciation, simple English meaning, optional Hindi cue, contextual meaning, and five accurate examples per term.
- Include at least two engineering/interview examples per term.

### `homework.md`

- Preserve instructor-assigned tasks separately and faithfully in short paraphrased form.
- For each task specify objective, prediction, setup, steps, observations to record, explanation prompts, variations, cleanup, and evidence of completion.
- Mark safety requirements before any crash, load, network, or data-loss experiment.

### `interview-questions.md`

- Cover definitions, internal mechanism, trade-offs, failure handling, estimates, and design evolution.
- Include follow-up questions and what a strong answer must mention.
- Include weak-answer traps without manufacturing a single “perfect script.”

### `review-pack.md`

- Make it compact enough for a 10–15 minute revision.
- Include retrieval questions before answers, a draw-from-memory task, a two-minute teach-back outline, and five high-value flashcard seeds.
- Never introduce information that is absent from or inconsistent with the full notes.

### `source-log.md`

- Record source type, local private path, lecture timestamp coverage, external sources actually read, unresolved transcript words, and inference labels.
- Never record private Drive URLs or file IDs.

## Status updates

Update the track table conservatively:

- `⬜ Not started`
- `🟨 Source ready`
- `🟦 Notes reviewed`
- `🟪 Lab completed`
- `✅ Mastered`

“Mastered” requires Rahul to explain the topic without notes, draw the main model, answer the senior trade-off questions, and complete any essential experiment. File generation alone is not mastery.

