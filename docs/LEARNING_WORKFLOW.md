# Simple learning workflow

You do not need to manage phases or Codex modes. Use one chat for one video and speak normally.

## 1. Choose any video

Beginner videos are a good starting point, but the repository does not force an order. Pick the video you want to study today.

Create one folder under `inputs/private/` and add the video, transcript, slides PDF, and any useful screenshots. See [`inputs/README.md`](../inputs/README.md).

## 2. Start one Codex chat

Use this short prompt:

```text
This chat is for "<video title>". Its files are in `inputs/private/<folder>`.
Please read them and create my notes. Explain in simple words first and then
in depth. Follow the repository instructions and keep the source files private.
```

Codex will identify the course entry, inspect the files, and create `notes.md` plus `review.md`. You do not need to request every section separately.

## 3. Continue asking questions in the same chat

Examples:

```text
I still do not understand repeatable read. Explain it with two users.

Show the same idea as a timeline.

Why does this fail in production?

Add the clearer explanation to my notes.

Ask me interview questions from this video, one at a time.

Create a small PostgreSQL lab so I can observe this behavior.
```

Codex infers the action. There are no mode names to remember.

## 4. Use your physical notebook for recall

Do not copy the entire Markdown file sentence by sentence.

1. Read one major section of `notes.md`.
2. Close the screen.
3. On paper, draw the main flow and explain it in your own words.
4. Reopen the notes and use another pen color for what you missed.
5. Write one compressed revision page: one diagram, key mechanism, trade-offs, failure, and interview answer outline.

The missing or incorrect parts are what you need to review; copying polished text can hide them.

## 5. Choose the next activity naturally

- If the mechanism is unclear, keep asking questions.
- If state changes over time, ask for a diagram or visualizer.
- If the real behavior matters, ask for a small lab.
- If you think you understand it, ask Codex to quiz or review you.
- If your answer exposes a gap, ask Codex to improve the notes.

Labs use the loop **predict → run → observe → explain → vary**. Always write your prediction before running an experiment.

## 6. Revisit briefly

Use `review.md` without opening the full notes first. A simple starting schedule is:

| Review | Suggested time | What to do |
|---|---|---|
| First | Same day | Redraw and explain the mechanism |
| Second | Next day | Answer the recall questions |
| Third | After 7 days | Do interview questions and one failure scenario |
| Later | After 21–45 days | Mix it with related topics or vary the lab |

Adjust the schedule based on recall. You do not need to update dates perfectly for the workflow to be useful.

## When a video is understood well

You should be able to:

- explain the problem in simple words;
- draw the important components or states;
- explain the mechanism in order;
- discuss at least two trade-offs and one failure;
- predict what changes under concurrency, scale, or failure;
- adapt the design when an interviewer changes a requirement.

Markdown is preparation. Your explanations, predictions, and experiments are the real learning evidence.
