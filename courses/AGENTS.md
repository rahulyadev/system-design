# Instructions for processing one course video

Read the root `AGENTS.md` first. Rahul should not need to understand this file.

## One video, one chat

- Rahul can choose any beginner or advanced video in any order.
- Use the title and private input folder to find the matching row in the course indexes.
- Create the output at `courses/<beginner|advanced>/<nn-topic-slug>/`.
- If two index entries could match, ask one short clarifying question. Otherwise infer the track, number, and slug.
- Never ask Rahul to choose a processing mode.

## First request in a video chat

1. Read the named private input directory.
2. Report a short inventory: transcript, video, PDF, screenshots, Rahul's questions, and obvious coverage gaps.
3. Inspect any existing lecture files and preserve Rahul's writing.
4. Use the transcript to cover the complete lecture, slides/screenshots to reconstruct visuals, and the video to resolve ambiguity.
5. Create or improve:

   ```text
   notes.md
   review.md
   ```

6. Update the matching course-index status after the files are genuinely ready.

If no usable content source is available, do not guess from the title. Explain exactly what file is needed next.

## What normal requests mean

| Rahul says something like | Codex action |
|---|---|
| “Create notes for this video” | Inspect all inputs and create/update `notes.md` and `review.md` |
| “Explain this more simply” | Answer directly; update the notes if the clarification is reusable |
| “Add this to my notes” | Edit the best matching notes section |
| “Quiz me” | Ask one question at a time, then explain the gap after each answer |
| “Review my understanding” | Test recall first and update the weakness log in `review.md` |
| “Create a lab/visualizer” | Read the lab standard and build the smallest artifact that answers one question |

Do not make Rahul specify artifact names, workflow phases, or technical implementation choices unless his preference materially affects the result.

## Source coverage

Build a private working map from timestamps to concepts, examples, visuals, and homework. Use it to prevent omissions, but write the final notes by concept rather than as a transcript summary.

For long videos, inspect the source in bounded chunks and combine them into one coherent `notes.md`. Never publish raw transcript chunks.

Keep course claims, verified additions, and inferences distinguishable where readers could confuse them. Record external sources and unresolved transcript words in the source section at the end of `notes.md`.

## Output rules

- Use `templates/lecture/notes.md` and `templates/lecture/review.md` as guides; remove unused optional sections rather than adding filler.
- Keep the full explanation in `notes.md` and the quick retrieval material in `review.md`.
- Instructor-assigned homework and Codex-added practice must be visibly separate.
- Interview answers are outlines with decisions, trade-offs, failures, and follow-ups—not memorized scripts.
- Link shared labs rather than duplicating code inside lecture folders.

## Status table

The status table is navigation for Rahul; Codex maintains it.

- `⬜ Not started`
- `📝 Notes ready`
- `🔁 Reviewing`
- `✅ Comfortable`

File generation alone does not mean `✅ Comfortable`; use it only after Rahul demonstrates recall and can discuss trade-offs.
