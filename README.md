# System Design Learning Lab

This repository helps Rahul study Arpit Bhayani's system-design course deeply, in simple language, with diagrams, interview practice, and working experiments.

## The whole workflow

Use one video per Codex chat. Videos can be studied in any order.

1. Create a private folder for the video, for example:

   ```text
   inputs/private/relational-databases/
   ```

2. Put these files in it:

   ```text
   video.mp4
   transcript.srt          # .md, .txt, and .vtt also work
   slides.pdf              # preferred when available
   screenshots/            # use when there is no PDF or a video-only visual matters
   my-questions.md         # optional
   ```

3. Open a new Codex chat at the repository root and send:

   ```text
   This chat is for "<video title>". Its files are in `inputs/private/<folder>`.
   Please read them and create my notes. Explain in simple words first and then
   in depth. Follow the repository instructions and keep the source files private.
   ```

4. Continue naturally in the same chat. You do not need to name a mode or know a special command.

   ```text
   Explain MVCC again with a small timeline.

   Add this explanation to my notes.

   Quiz me from this video, one question at a time.

   Review my understanding and tell me what I am missing.

   Create a small working lab that makes this concept visible.
   ```

That is all you need to manage. Codex reads the detailed rules and templates automatically.

## What Codex creates

Each processed video gets one folder:

```text
courses/<beginner|advanced>/<nn-topic>/
├── notes.md              # complete explanation, visuals, words, practice, interview questions
└── review.md             # short revision, recall questions, flashcards, weakness log
```

When you explicitly ask for a practical experiment, Codex creates the smallest useful lab under `labs/` or a larger capstone under `projects/`, then links it from the notes.

## How to use the files

- Read `notes.md`, close the screen, and reconstruct the main idea in your physical notebook.
- Use `review.md` for quick recall and NotebookLM/quiz practice.
- Ask every follow-up question in the same video chat. Codex can improve the notes as your understanding grows.
- Start a fresh chat only for another video or a large standalone project.

## Course indexes

- [`courses/beginner/README.md`](courses/beginner/README.md)
- [`courses/advanced/README.md`](courses/advanced/README.md)

The indexes help Codex choose the correct output folder. They do not force a study order.

## Codex setup

Open this repository as one Codex project. The project config selects GPT-5.6 Sol. Select Max for lecture synthesis, difficult questions, and labs when available.

## Public-repository boundary

This repository is public. Everything under `inputs/private/` is ignored by Git. Never commit course videos, transcripts, PDFs, screenshots, Drive links or IDs, credentials, or other raw course material. Commit only original notes, diagrams, code, and your own experiment results.

More detail is available in [`docs/LEARNING_WORKFLOW.md`](docs/LEARNING_WORKFLOW.md), but reading it is optional.
