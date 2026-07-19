# {{PROJECT_NAME}} Professional Squads

This file registers reusable two- or three-Skill formations around project outcomes. The router selects a squad; it is not counted as a squad member.

Read `AGENTS.md` for current architecture and `AI_ENGINEERING_PLAYBOOK.md` for risk and permission rules.

## Formation Rules

- Prefer two Skills: primary judgment plus independent proof.
- Add a third only for a distinct material domain or risk boundary.
- Name the artifact passed at every handoff.
- Keep implementation with the main agent unless a project-specific implementation Skill is genuinely useful.
- Do not create a squad for obvious low-risk work that direct implementation and focused verification can close.

## Registered Squads

### Bug Resolution

| Field | Definition |
|---|---|
| Outcome | Locate an unknown root cause, implement the smallest fix, and prove the original symptom is resolved |
| Members | `debug` -> `verify` |
| Handoff | Reproduction, first broken layer, evidence, root cause, and regression target |
| Exit | Original symptom and relevant regressions have fresh evidence |
| Permission | Production evidence or writes follow project policy |

### Cross-Layer Feature

| Field | Definition |
|---|---|
| Outcome | Implement a feature that changes interfaces, persistence, routing, or multiple consumers |
| Members | `architecture` -> `code-review` -> `verify` |
| Handoff | Contract/impact map -> implementation diff and risks -> acceptance evidence |
| Exit | No blocking findings and acceptance checks are supported |
| Permission | Migration, external write, and release remain separately authorized |

### Skill System Design

| Field | Definition |
|---|---|
| Outcome | Derive or improve the project's professional roster and squads |
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
| Members | {{CUSTOM_SQUAD_MEMBERS}} |
| Handoff | {{CUSTOM_SQUAD_HANDOFF}} |
| Exit | {{CUSTOM_SQUAD_EXIT}} |
| Permission | {{CUSTOM_SQUAD_PERMISSION}} |

## Evaluation

For each registered squad maintain:

- positive selection cases;
- near misses that should route elsewhere;
- handoff usability cases;
- permission-boundary cases;
- one case proving the third member is necessary, when present.
