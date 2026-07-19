---
name: meta-skill-designer
description: Designs or evolves a project's professional Skill roster and two- or three-Skill squads from repeated workflows, quality failures, and repository risks. Use when the user wants to create a Skill team, improve agent collaboration, reduce overlapping Skills, fix team routing, capture recurring work, or decide which specialists and handoffs a project needs.
allowed-tools: [Read, Grep, Glob]
---

# Meta Skill Designer

Design the professional system before drafting individual Skills. The goal is not a larger catalog; it is a small set of distinct capabilities and squads that close real project outcomes.

## Inputs

Collect evidence from:

- ordinary requests and corrections from recent work;
- recurring failures, reviews, incidents, and manual checklists;
- repository architecture and risk boundaries;
- existing Skills, descriptions, handoffs, and usage;
- deterministic tasks that should become scripts or tests instead of Skills.

Ask the user only for missing product priorities or examples that cannot be established from the repository and conversation.

## Workflow

1. Extract repeated outcomes and failure patterns before naming roles.
2. Cluster work by distinct professional judgment, not by file type or personality.
3. Draft each candidate Skill's trigger, owned judgment, output, exclusions, handoff, and safety boundary.
4. Remove or merge candidates that duplicate another Skill.
5. Form squads around outcomes, usually with two members and at most three:
   - primary judgment;
   - optional distinct domain/risk guard;
   - independent proof.
6. Define concrete handoff artifacts and exit conditions.
7. Identify positive, near-miss, ambiguous, handoff, and permission evaluation cases.
8. Hand the design package to `skill-creator` for drafting and iterative evaluation.

## Squad Design Rules

- The router/control plane is not a squad member.
- Two Skills are the default closed loop; a third requires a distinct material boundary.
- Every member must be necessary. Name what is lost if it is removed.
- Do not use a Skill for deterministic work better enforced by a script, test, schema, or lint rule.
- Skills store stable methods; routes, versions, service names, limits, and current feature lists stay in repository evidence.
- A handoff is an artifact, not "then call the next Skill."

## Output

```markdown
## Workflow Evidence
- Repeated outcomes:
- Quality failures:
- Repository risks:

## Proposed Roster
| Skill | Trigger | Owned judgment | Output | Exclusions |
|---|---|---|---|---|

## Proposed Squads
| Outcome | Members | Handoffs | Exit condition | Permission gate |
|---|---|---|---|---|

## Consolidation
- Skills to merge/remove:
- Rules to move into tests/scripts/docs:

## Evaluation Plan
- Positive cases:
- Near misses:
- Handoff cases:
- Permission cases:

## Handoff To Skill Creator
- Skills to draft or revise:
- Evidence and expected behavior:
```

## Constraints

- Do not write a Skill merely because a topic exists.
- Do not copy the entire project manual into a Skill.
- Do not design a permanent mega-squad.
- Do not silently choose product semantics while designing triggers.
- This Skill designs the system; `skill-creator` drafts and evaluates individual Skills.

## Example Triggers

1. "Our agent has too many overlapping Skills. Redesign the team."
2. "Turn our repeated release workflow into a professional squad."
3. "What two or three specialists should handle frontend production work?"

## Safety Statement

This Skill is read-only and produces a design package. It does not install Skills, execute generated scripts, or perform external actions.
