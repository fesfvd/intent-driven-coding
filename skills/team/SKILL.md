---
name: team
description: Route ordinary-language software requests into the smallest safe specialist chain with progressive IDC records and dynamic obligations. Use for "build this", "fix it", "continue", "optimize", bugs, cross-layer features, reviews, verification, release preparation, Skill-team design, and other non-trivial work when the user should not need to name Skills, files, tests, or risk levels.
allowed-tools: [Read, Grep, Glob, Skill]
---

# Progressive Team Router

## Purpose

Translate natural language, open a progressive record before work, and select
the minimum outcome-oriented squad. This router is the control plane, not a
squad member. Do not copy specialist procedures into it.

The router owns one control-plane decision: select the next smallest safe route
from user intent, repository evidence, workflow state, risk traits, and
permission boundaries. Requirement translation, risk classification, state
tracking, and permission checks are inputs and constraints to that decision,
not separate specialist conclusions.

<!-- DESIGN TENSION (T5): Router classification is itself a guess. The Router
must classify user intent (e.g., "unknown-root-cause bug" vs "cross-layer
feature") from minimal input — often a single sentence. This classification
determines the route, but the user may know the root cause and simply not have
stated it. Mitigation: state the classification explicitly and invite
correction ("I'm treating this as an unknown-root-cause bug. If you already
know the cause, tell me and I'll route differently.").
See docs/KNOWN_TENSIONS.md. -->

## First Work Report

Open every actionable request with a work report, not a silent setup:

1. Run `idc start --summary "<request>" --scene <initial-label>` before
   investigation or mutation. The command prints the provisional card (header,
   current state, initial scene, outstanding obligations) and writes
   `.idc/work-items/<record-id>/CARD.md`.
2. Show that card header to the user as the first report: what was captured,
   the initial scene read, and what must be proven next.
3. Promote with `idc promote` when investigation, a material decision, or a
   change begins; the durable card moves to `.idc/tasks/<task-id>.md`.

Scene labels are mutable routing hints, not identity. Reclassify through an
event (`idc classify`) when repository evidence changes the task meaning.

## Progressive Lifecycle

```text
captured -> shaped -> active -> validating -> closed
                ^         |
                `---------` requirement or scope change
```

- `captured`: preserve the request before investigation or mutation.
- `shaped`: current intent, boundaries, decisions, and acceptance are visible.
- `active`: investigation, design, implementation, or review is happening.
- `validating`: current claims are being checked against acceptance.
- `closed`: one explicit outcome was recorded.

Low-risk shaping gaps warn. Material open decisions, external effects, and
completion evidence use hard gates. Emergency mode may defer shaping but cannot
waive permission, recovery, or completion obligations.

## Pipeline Phases (Legacy Vocabulary)

`INTAKE`, `DESIGN`, `PLAN`, `BUILD`, `VERIFY`, `REVIEW`, `SHIP`, and `LEARN`
remain useful names for activities and old records. They are not a mandatory
Phase path. Activities can repeat, be skipped when irrelevant, or return the
task to `shaped` when facts or requirements change. Promoted work uses
`IDC-<PROJECT>-<YYYYMMDD>-<NNN>`; legacy scenario-bearing IDs remain readable,
and classification never changes the identity.

| Activity | Use when it changes the result |
|---|---|
| discover/debug | Current behavior or cause is uncertain |
| design/plan | A contract, boundary, or multi-step dependency needs judgment |
| build | The accepted outcome requires an implementation change |
| verify | A claim must be supported by fresh evidence |
| review | An independent risk boundary is material |
| ship | An explicitly authorized external effect is requested |
| observe | Post-change behavior must be checked |
| learn | Repeated evidence may justify a durable method change |

<PHASE-GATE phase="DYNAMIC">
Do not use a scenario label to justify a transition. Evaluate current dynamic
obligations. Do not record `ship` without authorization for the exact effect, and
do not close as `completed` without passing evidence mapped to acceptance.
</PHASE-GATE>

**Artifact discipline:** Even when a single model handles multiple activities,
require an explicit handoff artifact at material boundaries. An
`impact-contract` (even a five-line structured note) before build. A
`verification-report` (even a checklist) before a completion claim. The
artifact, not the model's confidence, carries the proof.

## Requirement Translation Gate

Classify information as:

| Class | Treatment |
|---|---|
| Explicit intent | Convert to observable behavior without changing meaning |
| Repository fact | Discover from current evidence and add to scope/preservation |
| Proposed default | Recommend the simplest valid approach and label it |
| Open decision | Ask only when alternatives change behavior, data, permissions, privacy, cost, or irreversible effects |

Proceed without asking when no open decision remains. Never ask the user to
choose files, Skills, tests, architecture patterns, or risk labels that the
repository can establish. When information is merely incomplete and low risk,
record the warning and take the next smallest safe route. Append later
corrections instead of rewriting the original request.

### Presentation Language

Presentation language follows an explicit user preference first, then the
current user language, then an explicitly established target-audience
language. Resolve it before producing a user-facing final
response, report, status update, or handoff. Preserve code, commands,
identifiers, APIs, and maintainer-only document conventions unless the user
asks to translate them. Pass the resolved language to every specialist whose
artifact will be shown to the user.

## Squad Selection

Read the project's `SQUADS.md` when present. Prefer two Skills: primary
judgment plus independent proof. A third Skill must guard a distinct domain or
risk and must produce a distinct artifact. Do not load a long chain because
many files are involved.

Typical outcome-to-route hints (activities, not a mandatory path):

| Outcome | Route hint |
|---|---|
| Exact low-risk edit | main agent + `verify` |
| Cross-layer feature or contract | `architecture` -> `verify`; add `code-review` only for a distinct material risk boundary |
| Unknown-root-cause bug | `debug` -> `verify`; add `code-review` only when the fix creates a distinct regression boundary |
| Explicit review | `code-review`, then report verification gaps |
| Release preparation | `verify` -> `code-review` -> project-specific release process |
| Skill roster or squad design | `meta-skill-designer` -> `skill-creator` |

## Adoption Mode

On first use, deliver the current safe task before trying to install or
customize the whole framework. Capture progressive evidence from real friction,
corrections, handoffs, and risk boundaries. Propose durable guidance, Skills,
or squads only when repeated evidence and human judgment show that they will
improve later work.

## Collaborative Learning Mode

The Agent investigates, explains relevant evidence and tradeoffs, and makes a
concrete recommendation. The human contributes lived pain, priorities, domain
experience, objections, and decisions about durable practice. Teach through
brief decisions during real work; do not turn framework study into a
prerequisite.

## Risk

| Risk | Boundary | Process |
|---|---|---|
| Low | Local and reversible; no persistent/API/permission/production impact | Read -> edit -> focused check -> verify |
| Medium | Cross-module, UI flow, API adaptation, generated artifact | Contract -> specialist if needed -> implement -> test -> review -> verify |
| High | Auth, persisted schema, billing, privacy, destructive or production effect | Contract -> test/contract -> implement -> security/review -> verify -> explicit permission |

## Permission Gate

Do not infer authorization for commit, push, PR, deployment, production writes,
external submissions, paid calls, destructive actions, or credential changes.
A recorded authorization describes scope; it does not grant it.

## Execution Checklist

- [ ] 1. Open the request with `idc start --summary ... --scene <initial-read>` and show the printed card as the first work report.
- [ ] 2. Classify user intent into the four information classes (explicit intent, repository fact, proposed default, open decision).
- [ ] 3. Assign initial scenario labels and impact/uncertainty readings using `docs/TASK_SCENARIOS.md`; state them and invite correction.
- [ ] 4. Promote the record when investigation, a material decision, or a change begins.
- [ ] 5. Select the smallest useful specialist chain and name any handoff artifact.
- [ ] 6. Append requirement, scope, risk, route, and decision changes as events.
- [ ] 7. Map fresh evidence to acceptance before a completion claim.

<HARD-GATE>
Never reconstruct a normal task only after completion. Never infer commit, push,
deployment, production write, paid call, publication, or destructive
authorization from local work. A router selects expertise; it does not make the
expert's conclusion.
</HARD-GATE>

## Output

Keep routing mechanics internal unless they help a human decision. The first
work report is the printed provisional card; later visible summaries stay
short:

```text
IDC <task-id or capture-id>: <current observable goal>
State: <lifecycle>; labels: <current labels or unclassified>
Open decision or hard gate: <only when present>
```

## Example Triggers

1. "The report is blank. Find the cause and fix it."
2. "Add filtering without breaking the existing API."
3. "The requirement changed: deploy both Web and Worker."

## Safety Statement

This Skill coordinates records and professional judgment. It does not broaden
the requested scope or authorize external effects.
