# Repository tree and lifecycle

## Clean bootstrap

```text
system-design-learning/
├── AGENTS.md
├── START_HERE.md
├── README.md
├── COURSE_INDEX.md
├── PROGRESS.md
├── TASK_AND_LAB_STANDARD.md
├── NOTEBOOKLM.md
├── BUNDLE_MANIFEST.md
├── compose.yaml
├── data/
├── docs/
├── inputs/
│   └── README.md
├── courses/
│   ├── beginner/README.md
│   └── advanced/README.md
├── templates/
├── tests/fixtures/
├── validation/
└── scripts/
```

`inputs/private/` exists only on Rahul's machine and is ignored. Actual lecture directories are absent until processed.

## After one video is processed

```text
courses/<track>/<LECTURE-ID>-<slug>/
├── metadata.json
├── source_manifest.json
├── notes.md
├── review.md
├── visuals/
└── tasks/
    └── <LECTURE-ID>-T01/
        ├── task.json
        ├── README.md
        ├── ATTEMPT.md
        ├── RUBRIC.md
        ├── starter/
        ├── tests/
        ├── lab/
        └── reference/
```

Optional folders appear only when they improve the actual lecture or instructor task. Empty decorative folders are not required.
