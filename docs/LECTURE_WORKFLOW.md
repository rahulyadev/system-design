# Workflow for one video chat

## 1. Resolve the lecture

Accept an ID, exact title, or clear private input folder. Resolve it against `data/lectures.json`. If two entries share a title, use the ID or track. Never infer a source video from a similar public title.

Videos are independent. Recommended background may be mentioned, but it never blocks processing. Add a compact bridge before the dependent explanation.

## 2. Inspect sources and existing work

Read every available source and existing lecture file. Preserve Rahul's writing. Report a compact inventory and gaps before synthesis.

## 3. Build the internal map

Map timestamps to concepts, examples, diagrams, calculations, claims, tasks, and uncertainties. Scan task language across the complete source and final 20%.

## 4. Create the lecture pack

Canonical path:

```text
courses/<track>/<LECTURE-ID>-<slug>/
```

Required files:

- `metadata.json` — identity and states;
- `source_manifest.json` — coverage and task scan without raw private content;
- `notes.md` — complete learning material;
- `review.md` — compact retrieval practice.

Use templates as contracts, not as filler. Remove irrelevant optional sections.

## 5. Build instructor tasks automatically

For every assigned task, follow `docs/TASK_WORKFLOW.md`. This occurs during initial lecture processing; Rahul does not need a second “build the lab” request.

Codex-added practice is allowed but remains separate. A high-value optional lab may be proposed when no instructor task exists, but it is not mislabeled as course homework.

## 6. Verify and update status

Run:

```bash
python scripts/validate_repo.py --profile live
```

Run safe task-specific checks. Update artifact state only from actual files. Do not advance learning state to Comfortable without observed recall and explanation.

## 7. Continue in the same chat

In the lecture chat Rahul can ask naturally:

- “Explain this part simply.”
- “Show one more visual.”
- “Let me attempt task 1.”
- “Run the task and show what changes.”
- “Quiz me one question at a time.”
- “Review my answer like an SDE-3 interviewer.”

Durable clarifications update notes. Demonstrated gaps update the weakness log. Learner work remains preserved.

## Handoff

Report:

- source coverage and uncertainties;
- concepts explained;
- instructor tasks detected and created;
- runtime tools actually used;
- executions passed, failed, or skipped;
- reference solution status;
- the next action Rahul should perform without opening the solution.
