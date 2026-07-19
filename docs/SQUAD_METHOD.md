# Professional Squad Method

## Skill, Squad, And Router

These are different abstractions:

| Layer | Purpose | Example |
|---|---|---|
| Skill | One stable professional capability and output contract | Root-cause diagnosis |
| Squad | Two or three complementary Skills assembled around one outcome | Diagnose -> implement -> verify |
| Router | Control plane that translates intent, selects a squad, tracks state, and enforces permission gates | `team` |

The router is not counted as a squad member. The main coding agent may perform implementation between specialist handoffs, but implementation must still consume the squad's evidence and satisfy its exit conditions.

## Why Two Or Three Skills

One Skill often produces a recommendation without closing the loop. Too many Skills increase context, duplicate judgment, and blur responsibility.

A useful default is:

```text
Two-Skill Squad = primary judgment + independent proof
Three-Skill Squad = primary judgment + domain/risk guard + independent proof
```

Examples:

```text
Bug squad: debug -> verify
Feature squad: architecture -> verify
Risky feature squad: architecture -> code-review -> verify
Skill design squad: meta-skill-designer -> skill-creator
Release squad: code-review -> verify -> project-specific deploy
```

Order may change when evidence must precede review. Define the actual handoff rather than relying on the names alone.

## Member Roles

### Primary Specialist

Owns the task-specific judgment that the main agent should not improvise. It produces the model of the problem, design, diagnosis, or plan.

### Guard Specialist

Owns a distinct failure boundary such as security, UX, data consistency, prompt contracts, deployment, or production operations. Add it only when that boundary is materially present.

### Proof Specialist

Independently checks whether the claimed result is supported. Verification is the common proof role; a review Skill may be the proof role when the requested outcome is findings rather than implementation.

## Squad Contract

Every reusable squad should define:

| Field | Question |
|---|---|
| Outcome | What observable result does the squad close? |
| Trigger | What ordinary user language or repository context selects it? |
| Exclusions | What similar work belongs elsewhere? |
| Members | Which two or three Skills are required? |
| Unique contribution | Why can no member be removed without losing a necessary judgment? |
| Order | Which work is sequential and which may run independently? |
| Handoff artifact | What evidence or contract passes between members? |
| Exit condition | What must be true before the squad returns control? |
| Permission gate | What side effect still requires the human? |
| Evaluation cases | Which positive, near-miss, handoff, and safety examples test the squad? |

If two members produce the same judgment, merge or narrow them. If the handoff artifact cannot be named, the composition is probably ceremonial rather than functional.

## Standard Formations

### Two-Skill Closed Loop

Use when one specialist can make the primary judgment and another can prove the result.

```text
[Primary specialist]
  -> handoff: diagnosis/design/contract
[Main agent implementation, when needed]
  -> handoff: changed behavior and acceptance claims
[Proof specialist]
```

Examples: `debug -> verify`, `architecture -> verify`.

### Three-Skill Risk Loop

Use when a separate domain guard is required.

```text
[Primary specialist]
  -> [Main agent implementation]
  -> [Guard specialist]
  -> [Proof specialist]
```

Examples: `architecture -> code-review -> verify`, or a project-specific `ux -> frontend-design -> verify`.

The guard does not repeat the primary specialist. It inspects a different failure boundary.

### Meta-Design Loop

Use to create or evolve the professional system itself.

```text
[meta-skill-designer]
  -> artifact: role map, squad contract, boundaries, trigger hypotheses
[skill-creator]
  -> artifact: Skill drafts, positive/negative evals, iteration evidence
```

Add `verify` when packaging or publishing the resulting files. Do not add it merely to make the meta squad look larger.

## Composition Test

Before registering a squad, answer:

1. Can one member safely close the outcome alone? If yes, a squad may be unnecessary.
2. Do the members own distinct judgments? If no, remove overlap.
3. Is there a concrete artifact at every handoff? If no, define one.
4. Does the final member prove the squad's outcome? If no, add or change the proof role.
5. Is a high-risk effect hidden inside ordinary execution? If yes, add an explicit permission gate.
6. Can a near-miss request avoid this squad? If no, narrow the trigger.

## Anti-Patterns

- **Skill pile**: listing many available Skills without an outcome-specific formation.
- **Ceremonial review**: adding review when it checks no distinct risk.
- **Router as expert**: placing architecture, debugging, or security conclusions in the control plane.
- **No handoff**: each Skill starts from scratch and ignores previous evidence.
- **Permanent mega-squad**: loading all specialists for every task.
- **Missing proof**: stopping after a design or fix without fresh verification.
- **Hidden shipping**: allowing a squad to deploy or write production data without named authorization.

## Project Ownership

The starter squads are examples. A project should derive its own squads from repeated outcomes and failure boundaries. A payments repository may need billing and reconciliation guards; a design-heavy client may need UX and visual-system specialists; an LLM product may need prompt-contract and parsing specialists.

The framework is successful when the project team can explain why each squad exists, not when it has copied every public Skill.
