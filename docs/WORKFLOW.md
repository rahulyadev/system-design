# Git, Worktree, and publication workflow

This document governs local work and GitHub publication.

## Branch names

```text
bootstrap: setup/system-design-learning-bootstrap
lecture:   lecture/<LECTURE-ID>
project:   project/<PROJECT-ID>
```

Use exact uppercase IDs. Do not create shortened, lowercase, suffixed, `-2`, or `-new` variants.

## Worktree ownership

Before writing:

1. inspect all Worktrees and their owned branches;
2. inspect exact local and remote branch existence;
3. require a clean current Worktree;
4. stop if another Worktree owns the exact branch;
5. give each lecture its own isolated Worktree on the exact branch `lecture/<LECTURE-ID>`;
6. resume that exact lecture Worktree and branch even if `main` advanced;
7. allow lecture processing to run in parallel, but serialize publication;
8. stop on divergence or unrelated local changes.

Never automatically stash, reset, rebase, force-push, rewrite, delete, overwrite, or move Rahul's work.

## Starting any lecture

Lectures are independent. A new isolated lecture Worktree and exact branch start from refreshed `origin/main` only when no exact local or remote branch exists. If the exact branch exists, attach, track, or fast-forward it only after ownership and divergence checks.

Raw files under `inputs/private/` stay untracked and may be shared locally across Worktrees through Rahul's chosen file placement. Never copy them into tracked content.

## Initialization and repair publication boundary

If initialization publication is ever authorized, automatic push may include only commits created by the current initialization/repair operation. Older local-only learner commits require explicit direction.

Rerunning a lecture initialization is additive and idempotent. Preserve notes, attempts, source manifests, code edits, predictions, evidence, and weakness logs.

## Authorized lecture publication

This workflow is explicit authorization to push and merge only the current validated `lecture/<LECTURE-ID>` branch. It does not authorize publishing another branch, changing `main` directly, bypassing checks, or resolving conflicts by guesswork.

Only one completed lecture may be in the publication sequence at a time:

1. confirm the isolated Worktree, exact lecture branch, clean scope, and learner-work preservation;
2. validate and commit only that lecture's completed work;
3. fetch `origin` and normally merge the latest `origin/main` into the lecture branch;
4. stop and report any merge conflict instead of resolving it automatically;
5. revalidate, push the lecture branch, open a pull request into `main`, and wait for all checks to pass;
6. immediately before merging, fetch `origin` and compare the branch with the latest `origin/main`;
7. if `origin/main` moved, normally merge it again, stop on conflict, revalidate, push, and wait for checks again;
8. merge the pull request with a normal merge commit, never a squash or rebase merge;
9. fetch `origin` and fast-forward a clean local `main`.

Never rebase, force-push, reset, stash, squash-merge, overwrite learner work, or publish anything under `inputs/private/`.

## Local bootstrap prompt

```text
Install the System Design Learning bootstrap locally. Read AGENTS.md and START_HERE.md, inspect the actual repository and all Worktrees, and verify that replacing the old bootstrap will not overwrite unrelated or completed work. Create or resume setup/system-design-learning-bootstrap, install only the validated bootstrap files, run bootstrap validation and self-tests, and commit locally. Do not push, merge, process a lecture, or touch private course inputs. Report conflicts instead of resolving them destructively.
```

## Publication prompt

```text
Publish the validated System Design Learning bootstrap. Re-read AGENTS.md and docs/WORKFLOW.md. Confirm the exact setup branch, clean Worktree, validations, and current-operation-only commits. Push the branch, create a pull request into main, and merge only after checks pass. Never force-push, bypass checks, include older local-only commits, or overwrite unrelated work.
```
