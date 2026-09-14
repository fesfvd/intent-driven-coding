---
name: team
description: Route ordinary development requests through progressive IDC records, dynamic obligations, and the smallest useful specialist chain.
allowed-tools: Read, Grep, Glob
---

# Progressive Team Router

## Purpose

Translate ordinary user intent, start a lightweight record before work, and select
only the professional judgment that changes the result. Scenario labels are
mutable routing hints. Risk, uncertainty, evidence, and requested effects produce
dynamic obligations.

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
Phase path. Activities can repeat, be skipped when irrelevant, or return the task to
`shaped` when facts or requirements change.

Promoted work uses `IDC-<PROJECT>-<YYYYMMDD>-<NNN>`; classification never changes
that identity.

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

## Requirement Translation

Maintain four distinct information classes:

- Explicit intent: preserve the user's meaning as observable behavior.
- Repository fact: investigate source, configuration, tests, and runtime evidence.
- Proposed default: label the Agent's simplest recommendation as a proposal.
- Open decision: ask only when alternatives materially change behavior, data,
  privacy, permission, cost, or an irreversible effect.

Do not ask users to choose files, tests, Skills, or internal implementation details
that the repository can establish.

### Requirement Translation Gate

Before `active`, resolve only decisions that materially change behavior, data,
privacy, permission, cost, or irreversible effects. When information is merely
incomplete and low risk, record the warning and take the next smallest safe route.
Append later corrections instead of rewriting the original request.

Presentation language follows the user's explicit language preference, then the
current user language. Preserve code, commands, identifiers, and maintainer-only
conventions unless translation is requested.

## Adoption Mode

On first use, deliver the current safe task before trying to install or customize
the whole framework. Capture progressive evidence from real friction, corrections,
handoffs, and risk boundaries. Propose durable guidance, Skills, or squads only
when repeated evidence and human judgment show that they will improve later work.

## Collaborative Learning Mode

The Agent investigates, explains relevant evidence and tradeoffs, and makes a
concrete recommendation. The human contributes lived pain, priorities, domain
experience, objections, and decisions about durable practice. Teach through brief
decisions during real work; do not turn framework study into a prerequisite.

## Routing

1. Read `docs/TASK_SCENARIOS.md` when a label helps search or specialist choice.
2. Prefer direct work plus verification for local, reversible changes.
3. Add `debug` for unknown causes, `architecture` for material cross-boundary
   contracts, `code-review` for an independent risk boundary, and `verify` when
   implementation claims need proof.
4. Use two or three members only when distinct judgments and named handoffs exist.
5. Reclassify through an event when evidence changes the task meaning.

## Execution Checklist

- [ ] 1. Capture the actionable request with `idc start` before investigation or mutation.
- [ ] 2. Promote it when investigation, a material decision, or a change begins.
- [ ] 3. Translate intent progressively; do not invent missing product meaning.
- [ ] 4. Evaluate current impact, uncertainty, conditions, and dynamic obligations.
- [ ] 5. Select the smallest useful specialist chain and name any handoff artifact.
- [ ] 6. Append requirement, scope, risk, route, and decision changes as events.
- [ ] 7. Map fresh evidence to acceptance before a completion claim.

<HARD-GATE>
Never reconstruct a normal task only after completion. Never infer commit, push,
deployment, production write, paid call, publication, or destructive authorization
from local work. A recorded authorization describes scope; it does not grant it.
</HARD-GATE>

## Output

Keep routing mechanics internal unless they help a human decision. The ordinary
user-facing start is short:

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

This Skill coordinates records and professional judgment. It does not broaden the
requested scope or authorize external effects.
