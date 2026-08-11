---
name: team
description: Routes ordinary-language software requests into the smallest safe two- or three-Skill squad registered by the project. Use for "build this", "fix it", "continue", "optimize", bugs, cross-layer features, reviews, verification, release preparation, Skill-team design, and other non-trivial work when the user should not need to name Skills, files, tests, or risk levels.
allowed-tools: [Read, Grep, Glob, Skill]
---

# Team Router

Translate natural language, classify risk, and select the minimum outcome-oriented squad. This router is the control plane, not a squad member. Do not copy specialist procedures into it.

The router owns one control-plane decision: select the next smallest safe route from user intent, repository evidence, workflow state, risk traits, and permission boundaries. Requirement translation, risk classification, state tracking, and permission checks are inputs and constraints to that decision, not separate specialist conclusions.

## Requirement Translation Gate

Classify information as:

| Class | Treatment |
|---|---|
| Explicit intent | Convert to observable behavior without changing meaning |
| Repository fact | Discover from current evidence and add to scope/preservation |
| Proposed default | Recommend the simplest valid approach and label it |
| Open decision | Ask only when alternatives change behavior, data, permissions, privacy, cost, or irreversible effects |

Proceed without asking when no open decision remains. Never ask the user to choose files, Skills, tests, architecture patterns, or risk labels that the repository can establish.

### Presentation Language

Resolve Presentation language before producing a user-facing final response, report, status update, or handoff intended for the user. Use an explicit user language preference first, then the current user language, then an explicitly established target-audience language. Preserve code, commands, identifiers, APIs, and maintainer-only document conventions unless the user asks to translate them.

Pass the resolved Presentation language to every specialist whose artifact will be shown to the user. Ask only when mixed-language input leaves a material user-visible choice unresolved.

## Adoption Mode: Collaborative Learning Mode

When this framework is new to the target repository, deliver the current safe task before proposing a full operating system. Use available base methods directly, investigate only the relevant path, and keep framework setup out of the critical path.

While working, collect lightweight evidence of repeated corrections, missing context, recurring risk checks, duplicated investigation, and useful handoff artifacts. Ask for the user's observed pain, prior experience, objections, and priorities when they can change whether a pattern is real or worth formalizing. Route to `meta-skill-designer -> skill-creator` only when progressive evidence and human judgment pass the creation gate or the user explicitly asks to design the system.

Teach through brief decisions: explain why a specialist, question, verification step, or permission gate matters at the point it changes the work. Include the relevant concept, evidence, uncertainty, or tradeoff so the user can evaluate and correct the route. Do not assign the user a framework reading curriculum, but do not hide system-design reasoning from them either.

## Squad Selection

| Outcome | Squad | Phase path |
|---|---|---|
| Exact low-risk edit | Main agent -> `verify` | INTAKE → BUILD → VERIFY |
| Cross-layer feature or contract | `architecture` -> `verify`; add `code-review` only for a distinct material risk boundary | INTAKE → DESIGN → BUILD → VERIFY (+ REVIEW) |
| Unknown-root-cause bug | `debug` -> `verify`; add `code-review` only when the fix creates a distinct regression boundary | INTAKE → DESIGN(debug) → BUILD → VERIFY (+ REVIEW) |
| Explicit review | `code-review` -> report verification gaps | INTAKE → REVIEW → VERIFY |
| Release preparation | `verify` -> `code-review` -> project-specific release process | INTAKE → VERIFY → REVIEW → SHIP |
| Skill roster or squad design | `meta-skill-designer` -> `skill-creator` | INTAKE → DESIGN(meta) → BUILD(meta) |

Read the project's `SQUADS.md` when present. Prefer two Skills: primary judgment plus independent proof. A third Skill must guard a distinct domain or risk and must produce a distinct artifact. Use project-specific specialists when their expertise changes the result. Do not load a long chain because many files are involved.

## Risk

| Risk | Boundary | Process |
|---|---|---|
| Low | Local and reversible; no persistent/API/permission/production impact | Read -> edit -> focused check -> verify |
| Medium | Cross-module, UI flow, API adaptation, generated artifact | Contract -> specialist if needed -> implement -> test -> review -> verify |
| High | Auth, persisted schema, billing, privacy, destructive or production effect | Contract -> test/contract -> implement -> security/review -> verify -> explicit permission |

## Pipeline Phases

Every non-trivial task flows through a subset of these phases. The router determines which phases apply, then gates each transition.

| Phase | Trigger | Squad activated |
|---|---|---|
| **INTAKE** | Every non-trivial request | Router classifies task type and risk |
| **DESIGN** | Cross-boundary change or unknown root cause | `architecture` (contract/impact) or `debug` (root cause) |
| **PLAN** | User explicitly requests a plan, or safe execution requires multi-step coordination | `architecture` (optional) |
| **BUILD** | All implementation tasks | Main agent implements from the DESIGN handoff |
| **VERIFY** | Every implementation task (not skippable) | `verify` |
| **REVIEW** | Medium/high risk or explicit review request | `code-review` |
| **SHIP** | Explicit deploy/release authorization | Permission gate only (not a squad member) |
| **LEARN** | Repeated failures or workflow friction | `meta-skill-designer` |

**Phase paths by task type:**

| Task type | Phase path | Force level |
|---|---|---|
| Typo / low-risk edit | INTAKE → BUILD → VERIFY | Minimal (2 phases) |
| Unknown-root-cause bug | INTAKE → DESIGN(debug) → BUILD → VERIFY | Standard (4 phases) |
| Security-sensitive bug | INTAKE → DESIGN(debug) → BUILD → VERIFY → REVIEW | Reinforced (5 phases) |
| Cross-layer feature | INTAKE → DESIGN(architecture) → BUILD → VERIFY → REVIEW | Reinforced (5 phases) |
| Explicit review request | INTAKE → REVIEW → VERIFY | Special (3 phases) |
| Release preparation | INTAKE → VERIFY → REVIEW → SHIP | Full (4 phases) |
| Skill system design | INTAKE → DESIGN(meta) → BUILD(meta) | Meta (3 phases) |

**Phase gates:**

<PHASE-GATE phase="BUILD">
Do NOT enter BUILD until:
- [ ] DESIGN phase is complete (if required for this task type)
- [ ] All DESIGN handoff artifacts are produced and reviewed
- [ ] Open decisions (if any) are resolved by the user
</PHASE-GATE>

<PHASE-GATE phase="SHIP">
Do NOT enter SHIP without explicit user authorization naming the exact side effect (commit, push, deploy, migration, production write). Local implementation success does not imply SHIP authorization.
</PHASE-GATE>

## State

The pipeline phases above map to this state machine:

```text
Intake -> Design? -> Plan? -> Build -> Verify -> Review? -> Ship? -> Learn?
```

"Continue" resumes the latest unfinished safe stage. It never bypasses a permission gate.

## Permission Gate

Do not infer authorization for commit, push, PR, deployment, production writes, external submissions, paid calls, destructive actions, or credential changes.

## Output

Keep routing internal unless the user asks. When visible detail is useful:

```markdown
- Task type:
- Risk:
- Current stage:
- Specialist chain:
- Permission gate:
- Presentation language:
```

## Execution Checklist

You **MUST** complete these in order:

- [ ] 1. Classify user intent into the 4 information classes (explicit intent, repository fact, proposed default, open decision).
- [ ] 2. Determine the task type (typo / bug / feature / review / release / meta).
- [ ] 3. Map task type to required pipeline phases using the Phase paths table.
- [ ] 4. Select the smallest squad for the active phase from the Squad Selection table.
- [ ] 5. Verify no open decision blocks execution; ask the user only for blocking decisions.
- [ ] 6. Hand off to the first squad member with a named artifact contract.

<HARD-GATE>
Do NOT enter BUILD phase until DESIGN phase gate is satisfied (if DESIGN is required). Do NOT enter SHIP phase without explicit user authorization. Do NOT infer commit, push, deploy, or production write authorization from local implementation success. A router selects expertise; it does not make the expert's conclusion.
</HARD-GATE>

## Constraints

- Query volatile repository facts; do not freeze routes, versions, service names, or thresholds here.
- Every implementation step must trace to explicit intent, repository evidence, an accepted default, or required verification.
- A router selects expertise; it does not make the expert's conclusion.
- A router does not count itself as a squad member.
- Every sequential handoff must name an artifact the next member consumes.
- Every user-facing handoff must preserve the resolved Presentation language.

## Example Triggers

1. "The report is blank. Find the cause and fix it."
2. "Add filtering to this list without breaking the existing API."
3. "Continue with the release checks."

## Safety Statement

This Skill only classifies and orchestrates. Side effects remain governed by the project playbook and the responsible specialist.
