# Source processing and fidelity

## Source roles

| Source | Primary use | Typical weakness |
|---|---|---|
| Transcript | Complete coverage, timestamps, task detection | Misheard terms, missing visuals, poor punctuation |
| Slides PDF | Exact diagrams, labels, formulas, examples | May omit the spoken mechanism |
| Video | Animation, demonstrations, emphasis, ambiguous speech | Expensive to inspect end-to-end without a transcript map |
| Screenshots | Video-only visuals | Can lose surrounding explanation |
| Rahul's questions | Personal confusion and desired depth | Not a substitute for full source coverage |

## First-pass source inventory

Before writing, record privately:

- files present and readable;
- transcript start/end timestamps and obvious gaps;
- slide count and whether slides cover the full video;
- video duration when inspectable;
- unclear terms needing cross-checking;
- possible task/homework timestamps;
- existing generated files and Rahul-owned work.

The public `source_manifest.json` records source types and coverage status, but never local absolute paths, Drive links/IDs, raw transcript chunks, or copied slide images.

## Coverage map

Build a private timestamp map:

```text
time range → concept → example → visual → instructor task → uncertainty
```

For a long video, work in bounded chunks. Synthesize after all chunks are inspected. Public notes are organized by mental model, not transcript order.

## Instructor-task scan

Search the whole source, not only the last sentence. Then inspect the final 20% carefully. Record:

- scan completed;
- ranges checked;
- tasks found;
- task timestamps;
- whether wording or constraints remain unclear.

If the end of the video is absent from the transcript and the video cannot be inspected, task detection is `incomplete`, not zero.

## Technical verification

Use external verification selectively for version-sensitive, counterintuitive, failure-related, or quantitative claims. Prefer official documentation, standards, specifications, and original papers. A web summary is not a primary source.

Keep three boundaries visible when they could be confused:

- course teaching;
- verified extension/correction;
- inference or practical connection.

## Copyright-safe notes

- Explain in original wording.
- Do not publish raw transcript paragraphs or slide screenshots.
- Preserve exact requirements semantically through a structured checklist.
- Use only a short source excerpt when exact wording is necessary to resolve ambiguity.
- Timestamps are allowed and useful.

## When to stop

Stop and request the smallest missing input when:

- the transcript is absent or materially incomplete;
- the video/title match is ambiguous;
- a technical term changes meaning and cannot be resolved from slides/video;
- the task ending is missing;
- executing the requested task would require unsafe or external authority.
