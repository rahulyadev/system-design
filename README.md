# System Design Learning Lab

This repository turns each supplied Arpit Bhayani course video into a complete, source-faithful learning pack: simple notes, deep mechanisms, reconstructable visuals, interview reasoning, useful English, instructor-assigned tasks, runnable local setup, observed evidence, and a separate reference solution.

## The important rule

Study any video at any time. The 36 Beginner and 16 Advanced entries are an identification catalog, not a mandatory sequence. If a selected lecture uses an unfamiliar idea, Codex adds the smallest bridge needed inside that lecture instead of blocking you.

## One video, one chat, one pack

Place local sources under:

```text
inputs/private/<LECTURE-ID>/
├── transcript.srt       # .txt, .md, and .vtt also work
├── slides.pdf
├── video.mp4
├── screenshots/         # optional
└── my-questions.md      # optional
```

Then open a dedicated Codex chat for that video and say:

```text
Process <LECTURE-ID>.
```

Codex infers the track, title, folder, sources, tasks, tools, and output. See [`START_HERE.md`](START_HERE.md).

## What one processed video produces

```text
courses/<track>/<LECTURE-ID>-<slug>/
├── metadata.json
├── source_manifest.json
├── notes.md
├── review.md
├── visuals/                         # only when separate assets help
└── tasks/
    └── <LECTURE-ID>-T01/
        ├── task.json
        ├── README.md                 # exact requirements, setup, acceptance criteria
        ├── ATTEMPT.md                # Rahul's work; never overwritten
        ├── RUBRIC.md
        ├── starter/                  # optional code/config
        ├── tests/                    # optional acceptance checks
        ├── lab/                      # when runtime behavior matters
        │   ├── README.md
        │   ├── compose.yaml          # only the required disposable services
        │   ├── verify.py
        │   └── evidence.md
        └── reference/
            ├── SOLUTION.md
            └── ...                   # reference code/config when needed
```

Instructor tasks and Codex-added practice are never mixed. If the source assigns a task, its learner setup and separate reference answer are required during the first processing pass. If no instructor task exists, the source manifest records how the video was checked and the notes say so explicitly.

## Evidence, not invented output

Every runnable task separates:

```text
prediction → expected outcome → actual observation → explanation → variation
```

When Docker or another required tool is unavailable, execution is marked `skipped`. Expected behavior remains clearly labeled as reasoned, never observed.

## Privacy

Videos, transcripts, slide PDFs, screenshots, raw quotations, Drive identifiers, secrets, and private notes stay under `inputs/private/` and are ignored by Git. Only original explanations, diagrams, exercises, code, and experiment evidence belong in the public repository.

## Catalog and validation

- [`COURSE_INDEX.md`](COURSE_INDEX.md) — all 52 videos and stable IDs
- [`PROGRESS.md`](PROGRESS.md) — artifact and learning state
- [`TASK_AND_LAB_STANDARD.md`](TASK_AND_LAB_STANDARD.md) — task, solution, and evidence contract
- [`docs/PROMPTS.md`](docs/PROMPTS.md) — everyday prompts
- [`scripts/validate_repo.py`](scripts/validate_repo.py) — bootstrap/live/archive validation

No GitHub operation is required to use this ZIP.
