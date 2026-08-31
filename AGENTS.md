# Codex instructions for the System Design Learning Lab

## Mission

Help Rahul build durable SDE-2/SDE-3 system-design understanding from the supplied Arpit Bhayani videos. Use plain language first, then mechanisms, numbers, trade-offs, failures, observability, interview reasoning, runnable evidence, and precise English.

## Non-negotiable workflow

- One video equals one dedicated Codex chat and one canonical lecture folder.
- Rahul may process any video in any order.
- Never require completion of another lecture. Add the smallest useful bridge inside the chosen lecture.
- Treat `data/lectures.json` as the canonical ID/title catalog.
- Read `docs/LECTURE_WORKFLOW.md`, `docs/SOURCE_PROCESSING.md`, and the lecture templates before processing a video.
- If any instructor task or runtime experiment is present, also read `TASK_AND_LAB_STANDARD.md`, `docs/TASK_WORKFLOW.md`, and `docs/LAB_SAFETY.md` completely.
- The current user request overrides repository defaults.

## Source authority and privacy

1. Inspect the named `inputs/private/<LECTURE-ID>/` folder before writing.
2. Use the transcript for full coverage, slides/screenshots for visual fidelity, and video for ambiguity, animations, demonstrations, and emphasis.
3. Do not recreate a lecture from its title. If no usable source exists, state the smallest missing input.
4. Treat transcripts as fallible. Resolve unclear technical words against slides/video when possible.
5. Preserve the course's explanation before adding depth or corrections.
6. Label boundaries when useful:
   - **Course:** faithfully paraphrased from supplied sources.
   - **Verified extension:** checked against an authoritative primary source.
   - **Inference:** a reasoned connection.
7. Never commit or quote at length from videos, transcripts, PDFs, screenshots, private URLs, IDs, or raw source material.

## Required first-pass outputs

Create:

```text
courses/<track>/<LECTURE-ID>-<slug>/
├── metadata.json
├── source_manifest.json
├── notes.md
├── review.md
└── tasks/              # required only when one or more instructor tasks exist
```

The notes and review must be substantive. Template-shaped placeholders do not count.

## Instructor-task rule

Instructor tasks are not optional lab ideas. Search the complete transcript, slide endings, video ending, and any spoken homework transitions. Record the timestamp/range and reconstruct every requirement faithfully.

For each detected task create `<LECTURE-ID>-TNN` with:

- a learner-facing specification and acceptance criteria;
- starter files or design canvas when helpful;
- Rahul's preserved `ATTEMPT.md`;
- a rubric;
- the smallest safe setup for required tools;
- actual verification and evidence when execution is possible;
- a physically separate reference solution and explanation.

Do not put a complete solution in the learner README, starter files, hints, or tests. Do not overwrite attempts, comments, experiment results, or altered starter code on rerun.

When no instructor task exists, `source_manifest.json` must explicitly record a completed scan and `notes.md` must say “No instructor-assigned task found in the supplied source.” Codex-added practice remains clearly labeled.

## Explanation standard

For each important term explain:

1. the simple meaning;
2. why it matters;
3. the problem it solves;
4. how it works in order;
5. a small example;
6. an invariant or deciding condition;
7. trade-offs and alternatives;
8. failure modes and observability;
9. when not to use it;
10. what changes when an interviewer changes scale, consistency, latency, durability, availability, or cost.

Use concrete numbers when possible. Define assumptions and units, show intermediate calculations, and sanity-check results.

## Visual standard

- Use Markdown tables for exact mappings and Mermaid for topology, sequence, state, ownership, partitioning, or failure flow.
- Use a small executable visualizer only when changing inputs materially improves understanding.
- Every non-trivial visual includes the question it answers, how to read it, the key insight, and its simplification/limitation.
- Reconstruct visuals in original wording and structure; do not publish copied slide images.

## “Show what happens” standard

Never merge predicted and observed behavior. Use:

```text
Prediction
→ Expected outcome and reason
→ Actual command/run
→ Actual evidence
→ Explanation
→ One changed condition
```

If a required executable, service, or permission is unavailable, mark execution `skipped` with the exact reason. Never fabricate logs, plans, timings, screenshots, or success markers.

## Tool and lab standard

- Prefer the smallest artifact that exposes the behavior.
- Use paper/query drills for ordering and arithmetic, Python for simulations, and disposable Docker Compose services when real semantics matter.
- The root PostgreSQL profile is reusable for ordinary SQL experiments. Create task-local infrastructure for Redis, RabbitMQ, Kafka, MinIO/S3, proxies, multiple nodes, crash recovery, or version-specific behavior.
- Resolve and record current image/library versions from primary sources when generating a task; do not silently use `latest`.
- Bind local ports to `127.0.0.1`.
- Use synthetic credentials and deterministic data.
- Include preflight identity, health checks, reset, cleanup, troubleshooting, and resource estimates.
- Never target an existing database, production service, cloud account, or broad Docker state.

## English and interview standard

- Select useful difficult terms only.
- Give pronunciation, simple meaning, optional short Hindi cue, contextual meaning, common misuse, and natural examples.
- Include natural answer outlines, not scripts to memorize.
- Interview sections progress through clarification, estimation, API/data model, high-level design, bottlenecks, reliability, observability, trade-offs, and changed requirements.
- Connect to Python, FastAPI, PostgreSQL, caches, queues, AWS, and migrations only when relevant. Do not invent Rahul's experience.

## Reruns and learner preservation

Rerunning a video performs an additive completeness audit:

- preserve Rahul's notes, attempts, code, comments, predictions, evidence, and weakness history;
- add only missing material or narrowly repair incorrect generated content;
- never replace learner work with the reference solution;
- a complete pack is a no-op.

## Git safety

- Inspect the Worktree and exact branch before writing.
- Preserve unrelated changes.
- Never stash, reset, rebase, force-push, delete a branch, or overwrite files automatically.
- Keep raw inputs untracked.
- Do not push or merge unless Rahul explicitly asks.
- Follow `docs/WORKFLOW.md` for branch ownership, divergence, and publication.

## Handoff standard

Report source coverage, created tasks, tools actually executed, skipped runtime checks, important uncertainties, and the one best next learner action. File generation is not learning evidence.
