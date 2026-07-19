---
name: skill-creator
description: Creates, improves, and evaluates an individual Skill after its role and squad boundary are understood. Use when drafting a new SKILL.md, refining triggers, adding resources, testing should-trigger and near-miss prompts, evaluating handoff quality, or iterating a Skill based on evidence rather than intuition.
allowed-tools: [Read, Grep, Glob, Write, Edit, Bash]
---

# Skill Creator

Turn a validated role design into a lean Skill and improve it through realistic evaluations. If the role, overlap, or squad composition is still unclear, hand back to `meta-skill-designer` first.

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

## Output

```markdown
## Skill Package
- Path/name:
- Role and squad:
- Trigger description:
- Resources:

## Evaluation
| Case | Expected | Result | Evidence |
|---|---|---|---|

## Changes From Baseline
- Improvements:
- Tradeoffs:
- Remaining risks:

## Handoff
- Upstream artifact consumed:
- Downstream artifact produced:
```

## Constraints

- Do not install globally or publish without explicit authorization.
- Generated scripts require review and should default to dry-run when they write.
- Do not report quantitative improvements without actual runs.
- Do not broaden allowed tools beyond the Skill's real method.
- Preserve the original name when revising an established Skill unless renaming is an explicit migration.

## Example Triggers

1. "Create the debug Skill from this role design and test its triggers."
2. "This Skill rarely activates; improve its description with near-miss cases."
3. "Evaluate whether the architecture Skill hands enough evidence to code review."

## Safety Statement

This Skill may draft files and run local evaluations when the host agent permits it. Installation, publication, external writes, and execution of unreviewed generated scripts remain explicitly authorized actions.
