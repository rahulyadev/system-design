# Bootstrap bundle manifest

## Identity and scope

This is a source-processing bootstrap for the 52-video System Design catalog currently recorded in `data/lectures.json`:

- 36 Beginner lecture identities;
- 16 Advanced lecture identities;
- zero blocking prerequisites;
- two ambiguous supplied titles preserved for source-based correction;
- no processed lecture folders;
- no private transcript, slide, video, screenshot, answer attempt, secret, or runtime volume.

The artifact is intended to replace the prior bootstrap in a clean, inspected Worktree. It does not delete, migrate, or overwrite completed work automatically.

## Canonical sources

| Concern | Source |
|---|---|
| Lecture identity/title/track | `data/lectures.json` |
| Initial progress | `data/progress.json` rendered by `scripts/render_catalog.py` |
| Tool-selection rule | `data/tool_profiles.json` |
| Lecture behavior | `AGENTS.md` and `docs/LECTURE_WORKFLOW.md` |
| Instructor tasks | `TASK_AND_LAB_STANDARD.md` and `docs/TASK_WORKFLOW.md` |
| Git/Worktree safety | `docs/WORKFLOW.md` |
| Validation mutations | `validation/expected_mutations.json` |

## Bootstrap exclusions

Archive validation rejects:

- `.git` and Worktree metadata;
- `inputs/private/` and raw audio/video/transcript/PDF source files;
- real `.env`, credentials, tokens, secrets, and private paths;
- virtual environments, caches, coverage output, logs, database files, WAL, dumps, and backups;
- generated lecture packs and root learner directories;
- symlinks, duplicate ZIP entries, directory-only entries, wrapper directories, and unsafe paths.

The final artifact identity and recalculated counts live in the separate hash-named validation report generated after the immutable ZIP.
