---
name: meta-skill-designer
description: Designs or evolves a project's professional Skill roster and two- or three-Skill squads from repeated workflows, quality failures, and repository risks. Use when the user wants to create a Skill team, improve agent collaboration, reduce overlapping Skills, fix team routing, capture recurring work, or decide which specialists and handoffs a project needs.
allowed-tools: [Read, Grep, Glob]
---

# Meta Skill Designer

Design the professional system before drafting individual Skills. The goal is not a larger catalog or a simulated human company; it is a small set of distinct judgments and squads that close real project outcomes.

## Inputs

Collect evidence from:

- ordinary requests and corrections from recent work;
- recurring failures, reviews, incidents, and manual checklists;
- repository architecture and risk boundaries;
- existing Skills, descriptions, handoffs, and usage;
- deterministic tasks that should become scripts or tests instead of Skills.
- progressive evidence gathered while the agent completes ordinary project work, so system design can grow from use instead of requiring an upfront workshop.
- human experience and judgment about lived pain, failed attempts, acceptable tradeoffs, and which recurring outcomes matter enough to formalize.

Ask the user for missing product priorities and for experiential evidence that repository inspection cannot establish. A repository can show structure and failures; it cannot fully reveal which friction matters most, which compromise is acceptable, or whether a proposed abstraction fits how the user wants to work.

Do not require the human to learn the framework or enumerate future workflows before useful work begins. When evidence is still sparse, preserve observations and defer Skill creation rather than blocking the current task.

## Workflow

1. Build an evidence ledger before naming roles. Separate observed recurring work, repository-proven risks, human experience, user priorities, and unproven hypotheses.
2. Map risk traits and recurring outcomes. Project labels such as "SaaS" or "CLI" are hints, not sufficient evidence.
3. Cluster work by distinct professional judgment, not by file type, technology, personality, or human job title.
4. Classify candidate capabilities using the Capability Tiers below.
5. Apply the Creation Gate with the user. Reject candidates that are deterministic, rare and low-cost, duplicative, unstable, unable to produce a reusable handoff, or inconsistent with the user's experienced pain and preferred working model.
6. Draft each surviving candidate's trigger, owned judgment, output, exclusions, competing Skills, handoff, exit condition, and safety boundary.
7. Remove or merge candidates that duplicate another Skill. Apply the Removal test to every existing capability.
8. Form squads around outcomes, usually with two members and at most three:
   - primary judgment;
   - optional distinct domain/risk guard;
   - independent proof.
9. Define concrete handoff artifacts, routing precedence, exit conditions, and permission gates.
10. Identify positive, near-miss, ambiguous, conflict, handoff, permission, and over-routing evaluation cases.
11. Hand the design package to `skill-creator` for drafting and iterative evaluation.

## Capability Tiers

Tiers guide evaluation; they are not an installation manifest.

### Universal candidates

Evaluate these for almost every maintained software project:

- routing and requirement translation;
- root-cause debugging;
- code review;
- fresh verification;
- architecture impact analysis when cross-boundary change is common.

A universal candidate belongs in the project's capability pool only when it adds value beyond the host agent's reliable built-in behavior. It does not run on every task. For example, a project should usually have code-review capability, but a typo fix should not automatically summon it.

### Conditional specialists

Add only when repository evidence exposes a repeated material boundary, such as authorization, migration safety, billing, UX, accessibility, performance, deployment, backward compatibility, LLM evaluation, or external integration recovery.

### Exceptional specialists

Reserve for domain-specific judgments with high error cost or repeated expert work, such as financial ledger integrity, medical safety, tenant isolation, embedded resource limits, or regulatory traceability.

## Creation Gate

A new Skill must satisfy all of these:

1. A recurring outcome or material failure boundary is evidenced.
2. Existing Skills or deterministic controls do not already cover the judgment.
3. The method is stable enough to outlive current paths, versions, and incidents.
4. Ordinary-language triggers and near misses can be distinguished.
5. The Skill produces a concrete artifact another actor can consume.
6. Failure has enough cost to justify added routing and context complexity.
7. The human has reviewed the evidence, tradeoff, and expected maintenance cost rather than merely approving a generated artifact.

If any condition fails, recommend direct agent behavior, documentation, a script, schema, lint rule, test, or deferred observation instead.

## Removal test

For each proposed and existing Skill ask:

- What necessary judgment is lost if this Skill is removed?
- Can another Skill own that judgment without becoming incoherent?
- Has it been selected by real work or only by hypothetical examples?
- Is its stable method still distinct from repository facts?
- Does its handoff save downstream investigation?

Merge, narrow, archive, or remove capabilities that cannot answer these questions convincingly.

## Squad Design Rules

- The router/control plane is not a squad member.
- Two Skills are the default closed loop; a third requires a distinct material boundary.
- Every member must be necessary. Name what is lost if it is removed.
- Do not use a Skill for deterministic work better enforced by a script, test, schema, or lint rule.
- Skills store stable methods; routes, versions, service names, limits, and current feature lists stay in repository evidence.
- A handoff is an artifact, not "then call the next Skill."
- Possessing a capability does not imply invoking it for every task.
- Project archetypes seed questions; repository risk traits decide the roster.

## Output

```markdown
## Workflow Evidence
- Repeated outcomes:
- Quality failures:
- Repository risks:
- Evidence confidence: observed / repository-proven / user-priority / hypothesis

## Capability Classification
| Capability | Tier | Evidence | Decision | Reason |
|---|---|---|---|---|

## Proposed Roster
| Skill | Trigger | Owned judgment | Output | Exclusions | Competing Skill |
|---|---|---|---|---|---|

## Proposed Squads
| Outcome | Members | Handoffs | Exit condition | Permission gate |
|---|---|---|---|---|

## Consolidation
- Skills to merge/remove:
- Rules to move into tests/scripts/docs:
- Capabilities to observe before creating:

## Evaluation Plan
- Positive cases:
- Near misses:
- Routing conflicts and precedence:
- Over-routing cases:
- Handoff cases:
- Permission cases:

## Handoff To Skill Creator
- Skills to draft or revise:
- Contract readiness for each Skill: ready / blocked
- Evidence, expected behavior, and acceptance rubric:
```

## Execution Checklist

You **MUST** complete these in order:

- [ ] 1. Build evidence ledger from observed work, repository risks, and user priorities.
- [ ] 2. Cluster work by distinct professional judgment (not file type, technology, or job title).
- [ ] 3. Classify each candidate capability via Capability Tiers (universal / conditional / exceptional).
- [ ] 4. Apply the Creation Gate: all 7 conditions must be satisfied.
- [ ] 5. Apply the Removal test to every existing capability.
- [ ] 6. Form squads: 2 members default, max 3; define concrete handoff artifacts.
- [ ] 7. Define evaluation plan: positive, near-miss, conflict, handoff, permission, and over-routing cases.
- [ ] 8. Hand the complete design package to `skill-creator` with contract readiness per Skill.

<HARD-GATE>
Do NOT create a Skill from a job title, topic, technology choice, or project archetype alone. Do NOT draft before role boundaries and handoffs are clear. Do NOT design a permanent mega-squad. Do NOT reduce the human role to goal input and permission approval.
</HARD-GATE>

## Constraints

- Do not write a Skill merely because a topic exists.
- Do not copy the entire project manual into a Skill.
- Do not design a permanent mega-squad.
- Do not copy PM, architect, developer, tester, and operator job titles unless each owns a distinct evidenced judgment.
- Do not turn project archetype recommendations into project facts.
- Do not silently choose product semantics while designing triggers.
- Do not treat model confidence as a substitute for the user's experience or independent judgment.
- Do not reduce the human role to goal input and permission approval; system evolution requires informed review and correction.
- This Skill designs the system; `skill-creator` drafts and evaluates individual Skills.

## Example Triggers

1. "Our agent has too many overlapping Skills. Redesign the team."
2. "Turn our repeated release workflow into a professional squad."
3. "What two or three specialists should handle frontend production work?"

## Safety Statement

This Skill is read-only and produces a design package. It does not install Skills, execute generated scripts, or perform external actions.
