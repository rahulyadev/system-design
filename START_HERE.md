# Start here

## 1. Replace the old bootstrap safely

Use the ZIP only from a clean local Worktree. Inspect existing files before replacing anything. Do not delete or overwrite unrelated work, raw course inputs, or completed lecture folders. The publication workflow in [`docs/WORKFLOW.md`](docs/WORKFLOW.md) deliberately separates local setup from GitHub publication.

## 2. Keep course sources private

For the video you want to study, create:

```text
inputs/private/<LECTURE-ID>/
```

Add the transcript, slides PDF, video, optional screenshots, and optional questions. The transcript is the coverage source; slides preserve diagrams and exact terminology; the video resolves animation, emphasis, and unclear transcript passages.

## 3. Start anywhere

Find the ID in [`COURSE_INDEX.md`](COURSE_INDEX.md). You do not need to complete an earlier video first. Open a new Codex chat and say:

```text
Process SD-BEG-050.
```

or:

```text
Process SD-ADV-110.
```

Codex must inspect the supplied sources before teaching. It may add a short prerequisite bridge, but it must not redirect you to another lecture merely because you chose a later topic.

## 4. What Codex does automatically

During the first pass it:

1. inventories transcript, slides, video, screenshots, and your questions;
2. maps the complete video by timestamp without publishing raw transcript text;
3. creates simple and deep notes with visuals and examples;
4. explains why every important term matters;
5. scans the entire source and the ending for instructor tasks;
6. creates each instructor task's exact requirement checklist;
7. provisions the smallest safe local setup when tools are needed;
8. creates learner files, checks, a rubric, and a separate reference solution;
9. runs the reference path when the environment permits and records actual evidence;
10. creates compact recall and interview material.

## 5. Attempt before opening the answer

For an assigned task:

1. read `README.md`;
2. write predictions in `ATTEMPT.md`;
3. run the learner setup and inspect evidence;
4. explain the result in your own words;
5. only then open `reference/SOLUTION.md`;
6. compare decisions, not just final output.

The solution exists from the beginning because you requested complete learning packs, but it remains physically separate from starter and learner files.

## 6. Validate

Bootstrap structure:

```bash
python scripts/validate_repo.py --profile bootstrap
```

After processing videos:

```bash
python scripts/validate_repo.py --profile live
```

Deterministic self-tests:

```bash
python scripts/validate_repo.py --profile bootstrap --self-test
```

Docker and database experiments are checked by the generated task itself. A structural validation pass does not claim that runtime experiments ran.

## Best first prompt

```text
Process <LECTURE-ID>. Read every local source for this video. Create complete notes and review material, detect every instructor-assigned task, build its learner setup and separate reference solution, run and record the reference evidence when safe and available, and keep all raw course files private.
```
