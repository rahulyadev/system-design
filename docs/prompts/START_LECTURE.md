# First prompt for every video

Open a new Codex chat at the repository root and paste this:

```text
This chat is for "<video title>". Its files are in `inputs/private/<folder>`.
Please read them and create my notes. Explain in simple words first and then
in depth. Follow the repository instructions and keep the source files private.
```

Replace only the video title and folder. You do not need to give a lecture number, track, mode, output list, or implementation plan; Codex will infer those from the repository.

If you already wrote questions in `my-questions.md`, Codex will read them. Otherwise ask questions naturally after the notes are created.

Keep using the same chat for every question about this video. Start another chat for another video.
