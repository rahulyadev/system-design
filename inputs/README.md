# Private lecture inputs

Store local source material under `inputs/private/`. Everything below that directory is ignored by Git and must remain private.

Recommended layout for one lecture:

```text
inputs/private/beginner/05-relational-databases/
├── transcript.md
├── my-questions.md
├── assigned-homework.md
├── video.mp4                 # optional; local only
└── screenshots/
    ├── 00-12-40-btree-shape.png
    └── 00-31-05-transaction-flow.png
```

## Best input package

Provide Codex with:

1. A timestamped transcript in Markdown, plain text, SRT, or VTT format.
2. Your own questions and points that did not make sense.
3. The instructor's homework copied in your own short wording, with timestamps when possible.
4. Screenshots only for diagrams, equations, tables, or states that the transcript cannot express.
5. The lecture title, track, and number.

The transcript does not need perfect grammar. Preserve timestamps, mark uncertain words as `[unclear]`, and avoid silently guessing technical names.

## Transcript versus full video

A transcript plus selected screenshots is normally better than asking Codex to inspect a large video directly: it is faster to search, easier to cite by timestamp, and easier for you to correct. Keep the local video available for checking ambiguous passages. If no transcript exists, ask Codex to design a local ingestion step that extracts audio, creates a timestamped transcript, and samples keyframes into this private directory. Review that transcript before note generation.

Do not put the shared Drive folder URL, file IDs, copied course PDF, or raw lecture material into public Markdown files.
