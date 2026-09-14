# {{PROJECT_NAME}} Professional Squads

This file registers reusable two- or three-Skill formations around project outcomes. The router selects a squad; it is not counted as a squad member.

Read `AGENTS.md` for current architecture and `AI_ENGINEERING_PLAYBOOK.md` for risk and permission rules.

## Formation Rules

- Prefer two Skills: primary judgment plus independent proof.
- Add a third only for a distinct material domain or risk boundary.
- Name the artifact passed at every handoff.
- Keep implementation with the main agent unless a project-specific implementation Skill is genuinely useful.
- Do not create a squad for obvious low-risk work that direct implementation and focused verification can close.
- Derive dynamic obligations from current risk and evidence; activities may repeat in any safe order. Legacy compatibility note: a pipeline phase path per task type is an import hint, not the current lifecycle.

## Registered Squads

### Bug Resolution

| Field | Definition |
|---|---|
| Outcome | Locate an unknown root cause, implement the smallest fix, and prove the original symptom is resolved |
| Activity hints | discover/debug -> build -> verify |
| Members | `debug` -> `verify` |
| Handoff | Reproduction, first broken layer, evidence, root cause, and regression target |
| Exit | Original symptom and relevant regressions have fresh evidence |
| Permission | Production evidence or writes follow project policy |

### Cross-Layer Feature

| Field | Definition |
|---|---|
| Outcome | Implement a feature that changes interfaces, persistence, routing, or multiple consumers |
| Activity hints | design/architecture -> build -> verify -> review when obligated |
| Members | `architecture` -> `code-review` -> `verify` |
| Handoff | Contract/impact map -> implementation diff and risks -> acceptance evidence |
| Exit | No blocking findings and acceptance checks are supported |
| Permission | Migration, external write, and release remain separately authorized |

### Skill System Design

| Field | Definition |
|---|---|
| Outcome | Derive or improve the project's professional roster and squads |
| Activity hints | learn/design -> build |
| Members | `meta-skill-designer` -> `skill-creator` |
| Handoff | Role map, squad contracts, trigger hypotheses, and evaluation plan |
| Exit | Candidate Skills have realistic positive, near-miss, handoff, and safety evaluations |
| Permission | Installation and publication remain explicitly authorized |

## Project-Specific Squads

Add formations using `.agent/templates/SQUAD.md`. Replace this section with outcomes derived from repeated project work.

### {{CUSTOM_SQUAD_NAME}}

| Field | Definition |
|---|---|
| Outcome | {{CUSTOM_SQUAD_OUTCOME}} |
| Activity hints | {{CUSTOM_SQUAD_PHASE_ROUTE}} |
| Members | {{CUSTOM_SQUAD_MEMBERS}} |
| Handoff | {{CUSTOM_SQUAD_HANDOFF}} |
| Exit | {{CUSTOM_SQUAD_EXIT}} |
| Permission | {{CUSTOM_SQUAD_PERMISSION}} |

## Evaluation

For each registered squad maintain:

Legacy templates called the activity-hint field `Phase route`; retain that name
only when importing an old contract. It is not a fixed state machine.

- positive selection cases;
- near misses that should route elsewhere;
- handoff usability cases;
- permission-boundary cases;
- one case proving the third member is necessary, when present.
