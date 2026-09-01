# Visual standard

Visuals exist to answer a question that prose or a short list cannot answer as clearly.

## Choose the representation

| Question | Representation |
|---|---|
| Which component owns what? | Component/ownership diagram |
| What happens in what order? | Sequence diagram or timeline |
| How does state change? | State diagram |
| Where does data move or duplicate? | Data-flow diagram |
| How do shards/tokens/partitions map? | Ownership map or compact table |
| What differs exactly? | Markdown comparison table |
| How does input change output? | Small chart or interactive visualizer |
| What blocks or races? | Session/lock timeline |
| How does failure propagate/recover? | Failure and recovery sequence |

Avoid a diagram for a single arrow or a simple fact. Split overloaded drawings.

## Required explanation

Every non-trivial visual contains:

```md
### Question this visual answers
### How to read this visual
### Key insight
### Simplification or limitation
```

## Source reconstruction

Use the slide/video to understand the instructor's visual, then recreate the idea with original labels and layout. Do not publish raw slide screenshots. Preserve a timestamp reference and state when the public diagram simplifies an animation.

## Dynamic visualizers

Create a visualizer only when varying inputs changes the learner's mental model—for example a consistent-hash ring, Bloom-filter false positives, token-bucket refill, queue backlog, or replication lag. Keep it local, small, dependency-light, and linked from the lecture/task.

The visualizer must include:

- a clear learning question;
- deterministic default inputs;
- visible state transitions;
- reset;
- at least one failure/edge case;
- explanation of what is simplified compared with production.

## Evidence visuals

Measured charts, screenshots, and execution plans must be generated from an actual run. Label environment, command, profile, and timestamp. Never fabricate a realistic-looking graph merely to fill the template.
