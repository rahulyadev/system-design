# Private files for each video

Everything under `inputs/private/` stays local and is ignored by Git.

Create one folder per video. The folder name only needs to be clear to you:

```text
inputs/private/relational-databases/
├── video.mp4
├── transcript.srt          # .md, .txt, and .vtt are also fine
├── slides.pdf              # preferred when the lecture has slides
├── screenshots/            # use when no PDF exists or a video-only visual matters
│   └── transaction-timeline.png
└── my-questions.md         # optional
```

## What to provide

- **Transcript:** the most important input because Codex can search the whole lecture. Timestamps are helpful but not mandatory.
- **Slides PDF:** best for diagrams, tables, equations, and exact terminology.
- **Screenshots:** add only if there is no PDF or something important appears only in the video.
- **Video:** useful for checking unclear transcript passages, animations, and demonstrations.
- **Your questions:** optional; write anything that confused or surprised you.

The transcript does not need perfect grammar. Keep uncertain words as `[unclear]` instead of guessing.

Do not place these raw files anywhere outside `inputs/private/`, and do not copy Drive URLs or file IDs into public notes.
