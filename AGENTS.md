# Codex instructions for the system-design learning repository

## Mission

Help Rahul build deep, durable system-design understanding for senior backend interviews. Optimize for comprehension and retrieval, not document volume. Rahul learns best through simple language, exact visual models, mathematical reasoning when useful, and working experiments.

## Instruction map

- Read this file for every task.
- Before creating or editing lecture artifacts, also read `courses/AGENTS.md` and `docs/LECTURE_PLAYBOOK.md` completely.
- Before creating a lab or visualizer, also read `docs/LAB_AND_VISUALIZATION_STANDARD.md` completely.
- Use the matching file in `templates/lecture/` rather than inventing a new lecture format.
- User instructions for the current task override repository defaults.

## Working principles

1. Work on one named lecture or one named lab at a time unless Rahul explicitly asks for a cross-lecture synthesis.
2. Begin by inventorying the available inputs. State what is present, missing, or unreadable.
3. For lecture-faithful notes, require a transcript, Rahul's notes, or accessible video/audio. Never reconstruct a lecture from its title alone.
4. Distinguish clearly among:
   - **Course:** a claim or model taught in the supplied lecture.
   - **Verified extension:** supporting detail checked against an authoritative primary source.
   - **Inference:** a reasoned connection not explicitly present in either source.
5. Prefer official documentation, specifications, standards, and original papers for verification. Use secondary sources only when a primary source is unavailable or too narrow, and label that choice.
6. Never silently “correct” the course. Preserve what it taught, then add a clearly labeled correction or nuance with evidence.
7. Ask only questions that materially change the output. Otherwise make a visible, reversible assumption and continue.

## Explanation standard

- Use simple words first, then introduce the formal term.
- Expand every abbreviation on first use.
- Explain each major concept through: problem, intuition, mechanism, example, trade-offs, failure modes, and when not to use it.
- Connect cause and effect explicitly. Do not write isolated fact lists.
- Use small numerical examples and equations when they improve understanding; define every symbol and unit.
- State assumptions before calculations and sanity-check the result.
- Contrast easily confused ideas in a table.
- Give at least one concrete backend example and one production failure scenario for important concepts.
- Include common misconceptions and the observable evidence that disproves each one.
- Use original wording. Do not mimic or reproduce the instructor's material at length.

## Visual standard

- Use Mermaid when topology, order, state, or ownership is the point.
- Use a Markdown table for exact comparisons and mappings.
- Add a short “how to read this” explanation after every non-trivial visual.
- Keep diagrams small enough to understand at a glance; split overloaded diagrams.
- Never use decorative diagrams. Every visual must answer a named question.
- If a static diagram cannot expose the behavior, propose a deterministic executable visualizer or lab.

## Lecture deliverables

A completed lecture normally contains:

- `notes.md`
- `visuals.md`
- `english-meaning.md`
- `homework.md`
- `interview-questions.md`
- `review-pack.md`
- `source-log.md`

Do not create all files mechanically when an item has no value. Record an explicit `Not applicable` with a reason instead of filler.

## Lab and code standard

- A lab must test a question, not merely demonstrate happy-path code.
- Use the **predict → run → observe → explain → vary** loop.
- Prefer Python for services and scripts because it matches Rahul's backend experience. Use PostgreSQL, Redis, Kafka-compatible tooling, or other infrastructure only when the concept requires it.
- Use Docker Compose for disposable infrastructure where practical. Never experiment against a host or production database by default.
- Provide setup, verification, expected output, cleanup, and troubleshooting commands.
- Make failure injection explicit, reversible, and confined to disposable resources.
- Add automated tests for deterministic behavior and a repeatable manual experiment for concurrency, timing, or crash behavior.
- Do not add a framework, dependency, dashboard, or UI unless it helps answer the learning question.

## Interview standard

- Progress from definition to mechanism, trade-offs, sizing, failure handling, and follow-up design changes.
- Provide answer outlines and reasoning checkpoints, not scripts to memorize.
- Include traps, weak answers, and likely interviewer follow-ups.
- Where relevant, connect the concept to Rahul's Python/FastAPI, PostgreSQL, caching, queue, AWS, and migration experience without inventing work history or exposing confidential client details.

## English-learning standard

Select only useful hard technical terms or strong professional English words from the lecture. For each term include pronunciation, simple English meaning, optional Hindi meaning when useful, meaning in this lecture, and five natural examples. At least two examples should sound like an interview or engineering discussion. Avoid elementary filler words.

## Source, privacy, and copyright rules

This is a public repository.

- Never commit videos, audio, course PDFs, full transcripts, raw screenshots, private Drive URLs or file IDs, tokens, secrets, personal data, or proprietary employer material.
- Treat `inputs/private/` as read-only source material and keep it untracked.
- Quote only short fragments when necessary for accuracy, attribute them in `source-log.md`, and otherwise paraphrase in original language.
- Do not cite a source that was not actually read.
- Record timestamp ranges for lecture-derived material whenever the input supplies timestamps.

## Git workflow

- Prefer one branch per lecture or substantial lab: `lecture/<track>-<nn>-<slug>` or `lab/<slug>`.
- Keep generated changes scoped to the requested lecture or lab.
- Review the diff and run relevant checks before declaring completion.
- Do not push, merge, delete branches, or overwrite user changes unless the current request authorizes it.
- Update the track progress table only after the corresponding state is genuinely reached.

## Definition of done

Before calling lecture work complete, verify that:

- the notes are faithful to the supplied source and important additions are cited;
- simple explanations and formal terminology agree;
- diagrams render and are explained;
- calculations include assumptions and units;
- homework distinguishes instructor-assigned work from Codex-added practice;
- interview answers include trade-offs and failure modes;
- glossary examples are natural and accurate;
- no private or copyrighted raw material is staged;
- any code runs from the documented clean setup and has a safe cleanup path;
- open uncertainties are visible rather than hidden.

