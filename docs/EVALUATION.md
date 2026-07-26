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

## Evidence Provenance

Before adding provenance fields to a contract Schema, classify every important fact in a real-project record using the smallest applicable class:

| Class | Meaning | Does not prove |
|---|---|---|
| `claimed` | An Agent's response or self-report. | That a host event or command result occurred. |
| `host-observed` | A host session export, Task event, permission event, or tool event. | That an Agent's interpretation of the event is correct. |
| `command-evidence` | A reproducible local command, actual exit status, and bounded output. | The Agent route that chose the command. |
| `artifact-evidence` | A persisted handoff, diff, or other bounded file reference. | That a downstream Agent semantically used it. |
| `human-confirmed` | A named human decision, approval, or review conclusion; a personal project may explicitly designate its project owner as the human reviewer. | Any unrecorded execution detail. |

Do not merge these classes into a health score or a single `passed` flag. A Task can complete while its test fails; an Agent can correctly describe a failure while reporting the wrong exit status. The [LAS provenance case](../references/host-acceptance/las-5.2.3-opencode-1.18.5-2026-07-26.md) records both conditions from one real local project. Its designated project owner confirmed the card's reviewability for this personal-project case. The taxonomy is available as documentation and the local [CLI](CLI.md) display classification, but it is not a contract Schema field or independent user research.

### Evidence Card

Start every provenance record with a compact card before the detailed log. A reviewer should not need to reconstruct the experiment from a long session export to identify the current conclusion:

| Field | Required content |
|---|---|
| Question | The narrow behavior or claim under review. |
| Scope | Target revision, permitted effects, and known local changes excluded from the case. |
| Agent claim | The bounded conclusion being tested. |
| Independent result | Command outcome, persisted artifact, or human decision that can support or contradict the claim. |
| Verdict | `supported`, `contradicted`, `partial`, or `unavailable`, with one sentence explaining why. |
| Sources | Links to bounded record sections or a statement that raw host evidence remains local and why. |

Keep the card short. Detailed host events, command output, and artifact contents belong below it. A reviewer who says the card is unclear has supplied feedback about the presentation, not proof that the underlying host or command behavior changed.
Render the card and its verdict in the reviewer or target user's preferred language. Keep evidence-class labels, commands, identifiers, and source paths verbatim when translating their surrounding explanation would reduce traceability.

## Host Acceptance

For host-specific behavior, prepare the bundled fixture with `scripts/prepare_host_acceptance_fixture.py` and follow [Host Acceptance](HOST_ACCEPTANCE.md). Keep the original routing prompts outside the generated target, record host-produced events, and distinguish an evaluator-run check from a command actually executed by the host session.

Do not use a model budget cap, a structural validation pass, or a local edit alone as evidence that a route completed. The current OpenCode and Claude Code pilots are partial observations; their records explain the specific gaps.

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
