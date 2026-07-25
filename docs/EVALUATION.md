# Evaluation Without Overengineering

The framework includes evaluation examples because a Skill description that looks good is not proof that routing and handoffs work. The goal is a small regression set, not a research benchmark.

## Minimum Useful Set

For each important Skill or squad, keep:

- two or three requests that should select it;
- two or three near misses that should route elsewhere;
- one case that checks the handoff artifact;
- one permission-boundary case when external or destructive effects exist.
- one competing-Skill case when trigger language overlaps;
- one over-routing case for low-risk direct work.

The files under `evals/` demonstrate the shape. Copy and rewrite them using language your real users employ.

When a repeated outcome needs machine-checkable routing, handoff, verification, or authorization boundaries, define a JSON contract under `.idc/` and validate it with `scripts/validate_contracts.py`. See [Machine-Readable Contracts](CONTRACTS.md). This remains offline validation; it does not prove an Agent selected the expected route.

For a recorded Agent run, use `scripts/evaluate_contracts.py` to compare its `evaluation-record` with the contract and case. The script evaluates supplied records only; it never invokes a model.

## What To Check

Check observable behavior rather than whether the response sounds polished:

- Was the smallest sufficient squad selected?
- Was a real product ambiguity surfaced?
- Did each member consume the previous handoff instead of restarting?
- Did the proof member map evidence to the claimed result?
- Did the workflow stop at an external-action permission gate?
- Did a near miss avoid an oversized or irrelevant squad?
- Did overlapping Skills resolve by explicit precedence or repository context?
- Did the Skill pass structural, routing, handoff, and safety quality independently?

For the two meta Skills, treat these as blocking failures:

- creating a Skill from a job title, topic, technology, or project archetype without evidence;
- drafting before role boundaries and handoffs are ready;
- accepting a Skill whose downstream consumer must repeat the investigation;
- broadening triggers until low-risk work over-routes;
- bypassing a permission boundary or fabricating evaluation evidence.

## Practical Review

You do not need an automated agent benchmark to begin. Run the cases manually with your coding agent and record:

```markdown
| Case | Expected route | Actual route | Handoff usable? | Safety correct? | Notes |
|---|---|---|---|---|---|
```

Automate only when the same cases are run often enough to justify it. Do not report quantitative improvement without actual repeated runs.
