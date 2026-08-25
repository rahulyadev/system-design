# Prompt for reviewing a completed lecture

```text
Review my mastery of one completed system-design lecture.

Lecture path: <courses/...>
Review stage: <same-day|1-day|7-day|21-day|45-day>
My closed-book explanation or answers:
<PASTE MY ANSWER, OR SAY "quiz me interactively">

Read AGENTS.md, courses/AGENTS.md, the full lecture artifacts, and any linked lab
results. Work in review mode.

Do not begin by summarizing the notes. Test retrieval first. Ask or evaluate:
1. the problem and one-sentence intuition;
2. a draw-from-memory component/state/data-flow model;
3. the mechanism in order;
4. two trade-offs and one wrong-use case;
5. one concurrency or failure prediction;
6. one senior follow-up that changes a requirement;
7. one connection to a real backend system.

Identify the exact missing reasoning step rather than saying my answer is vague.
Separate terminology gaps from mechanism gaps and decision gaps. Modify notes only
when the source model is genuinely unclear or incorrect; otherwise update the
review pack with a compact retrieval cue. Recommend a lab variation for predictive
gaps. Update the track status/review date only when evidence supports it.

Finish with a short scorecard and the next review interval.
```

