# Private source placement

Everything under `inputs/private/` stays local and is ignored by Git and archive validation.

Recommended layout:

```text
inputs/private/SD-BEG-060/
├── transcript.srt
├── slides.pdf
├── video.mp4
├── screenshots/
└── my-questions.md
```

The folder may use a clear title instead, but a canonical ID avoids collisions between Beginner and Advanced lectures with the same title.

## Source priority

- Transcript: complete coverage and task discovery.
- Slides PDF: diagrams, formulas, exact labels, final assignments.
- Video: unclear words, animations, demonstrations, emphasis, and task ending.
- Screenshots: only for video-only visuals.
- Questions: what Rahul wants clarified or explored.

Timestamps are helpful. Imperfect transcripts are acceptable; use `[unclear]` rather than silently guessing.

Do not put raw course files, private URLs/IDs, credentials, or personal material outside `inputs/private/`.
