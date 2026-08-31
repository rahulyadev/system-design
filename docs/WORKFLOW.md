# Git, Worktree, and publication workflow

This document specifies future local behavior. This bootstrap-generation operation does not modify GitHub.

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
5. resume the current Worktree's exact lecture branch even if `main` advanced;
6. stop on divergence or unrelated local changes.

Never automatically stash, reset, rebase, force-push, rewrite, delete, or move Rahul's work.

## Starting any lecture

Lectures are independent. A new lecture branch starts from refreshed `origin/main` only when the clean detached/current state is safely ancestral and no exact branch exists. If the exact local or remote branch exists, attach, track, or fast-forward it only after ownership and divergence checks.

Raw files under `inputs/private/` stay untracked and may be shared locally across Worktrees through Rahul's chosen file placement. Never copy them into tracked content.

## Initialization and repair publication boundary

If initialization publication is ever authorized, automatic push may include only commits created by the current initialization/repair operation. Older local-only learner commits require explicit direction.

Rerunning a lecture initialization is additive and idempotent. Preserve notes, attempts, source manifests, code edits, predictions, evidence, and weakness logs.

## Completion choice

When Rahul completes a lecture and omits publication intent, ask only:

```text
Should I keep the latest lecture changes local, or push them and merge the branch into main?
```

## Local bootstrap prompt

```text
Install the System Design Learning bootstrap locally. Read AGENTS.md and START_HERE.md, inspect the actual repository and all Worktrees, and verify that replacing the old bootstrap will not overwrite unrelated or completed work. Create or resume setup/system-design-learning-bootstrap, install only the validated bootstrap files, run bootstrap validation and self-tests, and commit locally. Do not push, merge, process a lecture, or touch private course inputs. Report conflicts instead of resolving them destructively.
```

## Publication prompt

```text
Publish the validated System Design Learning bootstrap. Re-read AGENTS.md and docs/WORKFLOW.md. Confirm the exact setup branch, clean Worktree, validations, and current-operation-only commits. Push the branch, create a pull request into main, and merge only after checks pass. Never force-push, bypass checks, include older local-only commits, or overwrite unrelated work.
```
