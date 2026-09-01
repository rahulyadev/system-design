# Everyday prompts

## Process any video

```text
Process <LECTURE-ID>.
```

Expanded form when desired:

```text
Process <LECTURE-ID> in its own isolated Worktree on the exact branch lecture/<LECTURE-ID>. Read every local source for this video. Create complete notes and review material, detect every instructor-assigned task, build its learner setup and separate reference solution, run and record reference evidence when safe and available, and keep all raw course files private. Other lecture Worktrees may process in parallel, but do not publish this lecture concurrently with another.
```

## Find a video

```text
Find the best System Design course video for <topic, interview question, or production problem>. Return its canonical ID, exact source title, track, short reason, related videos, whether its private sources and generated pack exist, and the exact processing prompt. Do not process it yet.
```

## Ask for a simpler explanation

```text
Explain <concept> from this video in very simple words first. Use one small backend example and one visual, then explain the exact mechanism and why the term matters. Update notes.md if this repairs or improves durable understanding.
```

## Attempt an instructor task

```text
Let me attempt <TASK-ID>. Show only the task, acceptance criteria, setup, and progressive hints. Do not reveal or use the reference solution. Ask for my prediction before execution and preserve everything I write.
```

## Run and observe

```text
Run the safe local setup for <TASK-ID>. First ask for my prediction. Then execute the smallest faithful experiment, capture actual evidence, explain why the state changed, vary one condition, and keep expected behavior separate from observed behavior.
```

## Compare with the answer

```text
I have committed to my solution for <TASK-ID>. Review it against the rubric first, then reveal and compare with the reference solution. Explain the exact reasoning gaps, alternatives, and what an SDE-2 versus SDE-3 interviewer would expect.
```

## Quiz/review

```text
Review this video closed-book. Ask one question at a time, wait for my answer, and move from simple explanation to mechanism, trade-offs, estimation, failure, and changed requirements. Update only genuine weak areas in review.md.
```

## Keep work local

```text
I completed <LECTURE-ID>. Validate the pack and my task evidence, preserve all attempts, and keep changes local. Do not push or merge.
```

## Publish later

```text
I completed <LECTURE-ID>. In its isolated Worktree and exact lecture/<LECTURE-ID> branch, validate and commit only this lecture. Serialize publication: fetch origin, normally merge the latest origin/main, stop and report any conflict, revalidate, push, open a pull request, and wait for checks. Immediately before merging, fetch and compare origin/main again; if it moved, repeat the normal merge, validation, push, and checks. Then use a normal merge commit and fast-forward a clean local main. This authorizes push and merge only for this validated lecture branch. Never rebase, force-push, reset, stash, squash-merge, overwrite learner work, include unrelated commits, or publish private inputs.
```
