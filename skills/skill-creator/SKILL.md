---
name: skill-creator
description: Creates, improves, and evaluates an individual Skill after its role and squad boundary are understood. Use when drafting a new SKILL.md, refining triggers, adding resources, testing should-trigger and near-miss prompts, evaluating handoff quality, or iterating a Skill based on evidence rather than intuition.
allowed-tools: [Read, Grep, Glob, Write, Edit, Bash]
---

# Skill Creator

Turn a validated role design into a lean Skill and improve it through realistic evaluations. If the role, overlap, or squad composition is still unclear, hand back to `meta-skill-designer` first.

## Readiness Gate

Do not draft until the design package identifies:

- evidenced need and capability tier;
- one owned professional judgment;
- ordinary-language positive triggers;
- exclusions, near misses, and competing Skills;
- required input and concrete output artifact;
- upstream and downstream handoff contracts;
- exit condition and permission boundary;
- the consequence of removing the Skill.

Mark the contract `ready` only when these are specific enough to evaluate. Missing current repository facts may be investigated; missing product meaning or role boundaries block drafting.

## Refuse To Draft

Return to `meta-skill-designer` instead of producing a speculative Skill when:

- the request is only a topic or human job title;
- two candidates own the same judgment;
- deterministic enforcement would be more reliable;
- no realistic near miss can be named;
- the output is advice with no downstream use;
- the Skill exists only because a project archetype mentioned it.

## Capture The Contract

Confirm from existing evidence:

- capability and professional judgment owned;
- ordinary-language trigger contexts;
- expected output artifact;
- explicit exclusions and competing Skills;
- upstream input and downstream handoff;
- safety and permission boundaries;
- objective and qualitative success criteria.

Do not ask the user to repeat information already present in the conversation or design package.

## Draft The Skill

Use a portable structure:

```text
skill-name/
|-- SKILL.md
|-- references/   optional, loaded only when needed
|-- scripts/      optional, deterministic and reviewable
`-- assets/       optional output resources
```

The frontmatter description is the primary trigger surface. It should state what the Skill does and when users naturally need it, including phrases that do not name the Skill.

Keep the body focused on stable method, constraints, handoffs, exit conditions, and output format. Move large variants into references and repeated deterministic work into reviewed scripts.

## Evaluation Set

Create realistic cases before calling the Skill complete:

1. Three or more should-trigger requests with varied phrasing.
2. Three or more near misses that share vocabulary but need another Skill or direct action.
3. One ambiguous case requiring repository context.
4. One squad handoff case that tests whether the output is usable downstream.
5. One permission/safety case when applicable.
6. One competing-Skill conflict case when trigger vocabulary overlaps.
7. One over-routing case proving the Skill stays inactive for low-risk direct work.

For each case record:

```json
{
  "id": "descriptive-id",
  "prompt": "realistic user request",
  "should_trigger": true,
  "expected_behavior": ["observable behavior"],
  "forbidden_behavior": ["regression or overreach"]
}
```

## Iterate

1. Preserve the previous version as a baseline when improving an existing Skill.
2. Run the same cases with the candidate and baseline when the environment supports isolated runs.
3. Grade objective assertions programmatically where possible.
4. Review qualitative output and handoff usability.
5. Compare correctness, trigger precision, token/time cost when available, and safety behavior.
6. Generalize from failures; do not overfit wording to one prompt.
7. Remove instructions that create repeated unproductive work.
8. Repeat until feedback is satisfactory or changes stop producing meaningful gains.

If isolated agent runs are unavailable, perform a documented manual review and state that limitation rather than inventing benchmark results.

## Quality Layers

Evaluate each layer independently. A polished response cannot compensate for a routing or safety failure.

### Structural Quality

- Frontmatter is valid, portable, and names what the Skill does and when it triggers.
- Allowed tools are the minimum required.
- Stable method stays in `SKILL.md`; large references and deterministic scripts are separated.
- Volatile repository facts are queried rather than copied.

### Routing Quality

- Varied positive prompts select the Skill.
- Vocabulary-sharing near misses route elsewhere.
- Competing Skills have explicit precedence or repository-context rules.
- Low-risk direct work does not trigger ceremonial specialization.

### Handoff Quality

- The output matches a named schema or checklist.
- Evidence and inference are distinguishable.
- The downstream actor can continue without repeating the investigation.
- Exit conditions reveal incomplete or blocked work.

### Safety Quality

- Read-only and write-capable behavior match allowed tools.
- External, destructive, paid, production, commit, push, and publication effects remain gated.
- Generated scripts are reviewable and use dry-run behavior for writes when practical.
- Unsupported completion or benchmark claims are forbidden.

Use blocking severity: any routing false positive with material cost, unusable handoff, permission bypass, fabricated evidence, or tool overreach blocks acceptance. Minor wording or formatting issues do not.

## Output

```markdown
## Skill Package
- Path/name:
- Role and squad:
- Trigger description:
- Resources:

## Evaluation
| Layer | Case | Expected | Result | Evidence | Severity |
|---|---|---|---|---|---|

## Changes From Baseline
- Improvements:
- Tradeoffs:
- Remaining risks:

## Handoff
- Upstream artifact consumed:
- Downstream artifact produced:
```

## Execution Checklist

You **MUST** complete these in order:

- [ ] 1. Verify the Readiness Gate: all 8 contract items are present and specific.
- [ ] 2. Refuse to draft if any of the 6 refusal conditions apply; return to `meta-skill-designer`.
- [ ] 3. Draft the SKILL.md following the portable structure (frontmatter, method, constraints, output format).
- [ ] 4. Create a complete evaluation set (7 required case types).
- [ ] 5. Evaluate across all 4 Quality Layers independently (structural, routing, handoff, safety).
- [ ] 6. Iterate until all blocking failures are resolved. Preserve the baseline version for comparison.

<HARD-GATE>
Do NOT accept a Skill while any blocking quality-layer failure remains. Do NOT report quantitative improvement without actual runs. Do NOT broaden allowed tools beyond the Skill's real method. Do NOT weaken exclusions merely to increase trigger frequency.
</HARD-GATE>

## Constraints

- Do not install globally or publish without explicit authorization.
- Generated scripts require review and should default to dry-run when they write.
- Do not report quantitative improvements without actual runs.
- Do not broaden allowed tools beyond the Skill's real method.
- Do not weaken exclusions merely to increase trigger frequency.
- Do not accept the Skill while any blocking quality-layer failure remains.
- Preserve the original name when revising an established Skill unless renaming is an explicit migration.

## Example Triggers

1. "Create the debug Skill from this role design and test its triggers."
2. "This Skill rarely activates; improve its description with near-miss cases."
3. "Evaluate whether the architecture Skill hands enough evidence to code review."

## Safety Statement

This Skill may draft files and run local evaluations when the host agent permits it. Installation, publication, external writes, and execution of unreviewed generated scripts remain explicitly authorized actions.
