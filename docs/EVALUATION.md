# Evaluation Without Overengineering

The framework includes evaluation examples because a Skill description that looks good is not proof that routing and handoffs work. The goal is a small regression set, not a research benchmark.

## Minimum Useful Set

For each important Skill or squad, keep:

- two or three requests that should select it;
- two or three near misses that should route elsewhere;
- one case that checks the handoff artifact;
- one permission-boundary case when external or destructive effects exist.

The files under `evals/` demonstrate the shape. Copy and rewrite them using language your real users employ.

## What To Check

Check observable behavior rather than whether the response sounds polished:

- Was the smallest sufficient squad selected?
- Was a real product ambiguity surfaced?
- Did each member consume the previous handoff instead of restarting?
- Did the proof member map evidence to the claimed result?
- Did the workflow stop at an external-action permission gate?
- Did a near miss avoid an oversized or irrelevant squad?

## Practical Review

You do not need an automated agent benchmark to begin. Run the cases manually with your coding agent and record:

```markdown
| Case | Expected route | Actual route | Handoff usable? | Safety correct? | Notes |
|---|---|---|---|---|---|
```

Automate only when the same cases are run often enough to justify it. Do not report quantitative improvement without actual repeated runs.
