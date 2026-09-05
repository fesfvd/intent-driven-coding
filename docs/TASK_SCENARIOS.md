# IDC Task Scenarios

## Purpose

`team` decides which professional judgment is needed. This document defines the
task shape that decision starts from. It prevents every request from being
treated as either a generic "bug" or a generic "feature".

The framework uses two separate questions:

1. **What kind of work is this?** Choose one primary scenario code.
2. **What can this work affect?** Record impact dimensions and risk modifiers.

"The user has a clear goal" is not a scenario. It is an intake fact that can
reduce uncertainty, but a clear goal may still be a high-risk `FEAT`, `CHG`, or
`OPS` task.

## Scenario Codes

Choose the code whose primary outcome matches the request. Do not choose a code
because it sounds more sophisticated, and do not create a new code for every
domain noun. Apply these precedence rules when a request has more than one
possible label:

1. `REVIEW` wins when the requested outcome is findings and no code change.
2. `OPS` wins when the requested outcome is an environment, release, migration,
   or external operation, even if code changes are needed to prepare it.
3. `META` wins when the subject is the project's AI engineering system itself.
4. `EXP` wins when the requested outcome is knowledge or a feasibility decision,
   not a committed product change.
5. `SEC` wins over `FIX` when the primary defect is a trust-boundary, access,
   disclosure, privacy, or unsafe-execution failure.
6. Otherwise choose `FEAT`, `CHG`, `REF`, or `FIX` by the intended outcome.

| Code | Scenario | Outcome | Typical route |
|---|---|---|---|
| `FIX` | Known defect repair | Restore an established behavior or invariant that is wrong | INTAKE -> BUILD -> VERIFY; add `debug` when the cause is uncertain |
| `SEC` | Security or trust-boundary correction | Prevent unauthorized access, disclosure, privilege escalation, unsafe execution, or privacy failure | INTAKE -> DESIGN(debug) -> BUILD -> REVIEW -> VERIFY |
| `FEAT` | New capability | Introduce behavior, interface, data, or workflow that did not previously exist | INTAKE -> DESIGN(architecture) -> BUILD -> REVIEW -> VERIFY |
| `CHG` | Existing behavior adjustment | Deliberately change a current rule, output, flow, policy, or configuration | INTAKE -> DESIGN(architecture) when boundaries change -> BUILD -> VERIFY |
| `REF` | Structural refactor | Change internal structure while preserving externally relevant behavior | INTAKE -> DESIGN(architecture) -> BUILD -> VERIFY; add REVIEW for a material boundary |
| `REVIEW` | Assessment or audit | Produce an evidence-backed finding about code, architecture, security, or a diff without changing the subject | INTAKE -> REVIEW -> VERIFY |
| `OPS` | Release, migration, or operational action | Move a known change across an environment, alter deployed state, or perform a controlled maintenance operation | INTAKE -> VERIFY -> REVIEW -> SHIP |
| `EXP` | Investigation or feasibility study | Reduce uncertainty and record a decision, measurement, prototype result, or recommendation | INTAKE -> DESIGN/PLAN -> VERIFY; no implementation claim unless the task changes class |
| `META` | Project-system evolution | Change Skills, Squads, contracts, evaluation, host adapters, or IDC operating rules | INTAKE -> DESIGN(meta) -> BUILD(meta) -> VERIFY |

Documentation-only work normally uses `CHG` when it changes project guidance,
`META` when it changes the IDC system itself, or `REVIEW` when it only audits
existing documentation. Use `FEAT` only when the documentation is a user-facing
capability with its own acceptance behavior.

## Orthogonal Impact Dimensions

Scenario code describes intent. The task card must also score the possible
impact of the change. Use `none`, `low`, `medium`, `high`, or `unknown` and
explain every `medium` or higher value.

| Dimension | Question |
|---|---|
| Behavior | Can users or callers observe a different result or workflow? |
| Data | Can data be created, transformed, migrated, deleted, or exposed? |
| Security | Can identity, authorization, isolation, secrets, or trust boundaries change? |
| Privacy | Can personal, private, or sensitive information become more or less visible? |
| Permission | Can a user, service, or operator gain or lose an action? |
| Cost | Can this change consume money, quota, provider capacity, or significant compute? |
| Availability | Can it affect uptime, latency, concurrency, recovery, or operational capacity? |
| External effect | Can it send, deploy, publish, commit, push, or write outside the local workspace? |
| Reversibility | How difficult is it to undo if the assumption is wrong? |

The highest impact dimension determines the minimum process. A local `FEAT`
with no persistent or external effect may use a short route. A small-looking
`CHG` that changes authorization or deletion policy is high risk and must use a
reinforced route.

## Uncertainty Modifiers

Record these independently from impact:

| Modifier | Meaning | Consequence |
|---|---|---|
| `known-target` | The affected behavior and likely production path are already established | Skip exploratory design only when repository evidence confirms the boundary |
| `unknown-cause` | The symptom is clear but the first broken layer is not | Reproduce and diagnose before implementation; use `debug` |
| `unknown-contract` | The desired product or data meaning is not established | Stop at INTAKE/DESIGN and ask a focused question |
| `cross-boundary` | Multiple modules, services, artifacts, or teams must stay aligned | Produce an impact contract before BUILD |
| `irreversible` | An incorrect action is destructive or expensive to undo | Require explicit authorization and a recovery or rollback condition |

These modifiers are not extra members of a Squad. They select gates and
evidence requirements.

## Scenario-Specific Start Fields

The common task card is mandatory, but each scenario adds a small set of fields
that makes its acceptance testable. These fields are shown before BUILD.

| Scenario | Add before implementation | Minimum completion proof |
|---|---|---|
| `FIX` | Expected behavior, observed behavior, reproduction, suspected cause, and preserved regressions | Reproduction passes after the fix and the relevant invariant remains true |
| `SEC` | Asset, threat/actor, trust boundary, allowed path, denied path, exposure scope, and containment plan | Unauthorized path is denied, legitimate path works, and no sensitive data is exposed in evidence |
| `FEAT` | User/stakeholder, new capability boundary, state transitions, compatibility expectations, and out-of-scope variants | New acceptance behavior passes plus existing consumers remain compatible |
| `CHG` | Current rule, requested new rule, migration/compatibility impact, and rollback meaning | New rule passes, intentionally changed old behavior is recorded, and unrelated behavior is preserved |
| `REF` | Behavior invariants, structural target, dependency/consumer map, and proof that semantics should not change | Focused characterization checks and relevant suite pass with no unexplained behavior change |
| `REVIEW` | Review subject/revision, review question, scope, excluded files, and severity threshold | Findings cite concrete evidence; no safety claim exceeds the inspected scope |
| `OPS` | Exact revision, environment, preconditions, external effects, observability, rollback/recovery, and approver | Preflight and postflight evidence exist; execution occurs only after named authorization |
| `EXP` | Question, hypotheses, time/resource budget, measurement method, and stop/decision rule | Results answer the question or explicitly leave it unresolved; no prototype is mistaken for production work |
| `META` | Repeated observation, proposed rule/Skill/Squad change, affected users, evaluation cases, and retirement condition | The framework change passes structural checks and a focused evaluation or real-task review |

## Mandatory Task Start Card

Every non-trivial task starts with an IDC task card. The agent should present a
short version before implementation and maintain the full version in
`.idc/tasks/` when the project uses that directory. The card contains:

- **Task ID**: `IDC-<PROJECT>-<SCENARIO>-<YYYYMMDD>-<NNN>`; uppercase project key,
  one scenario code, UTC date, and a per-project sequence.
- **Intent**: the user's requested outcome in observable language.
- **Classification**: scenario code, uncertainty modifiers, and why nearby
  scenarios were rejected.
- **Scope**: included paths or boundaries, explicit exclusions, and preserved
  behavior.
- **Baseline**: repository facts, current behavior, reproduction, or diff that
  establishes where the task starts.
- **Impact**: the nine dimensions above, with rationale for medium or high
  values.
- **Route**: phases, Skills/Squad, handoff artifacts, and phase gates.
- **Acceptance**: success criteria, regression invariants, and user-visible or
  operational result expected at the end.
- **Verification**: exact checks, evidence owner, and omitted checks.
- **Permission gate**: any commit, push, deploy, migration, production write,
  paid call, destructive action, or publication still requiring approval.
- **Open decisions**: only decisions that change behavior, data, privacy,
  permission, cost, or irreversible scope.

The task ID identifies one piece of work; it is not a claim that the work
passed. Status and evidence must be recorded separately.

## Fixed Phase Gate Expectations

| Stage | Must be known before moving on |
|---|---|
| `INTAKE` | Task ID, scenario, intent, initial scope, impact, uncertainty, and open decisions |
| `DESIGN` | Current path, preservation rules, impact contract, proposed route, and resolved blocking decisions |
| `BUILD` | Approved scope, explicit acceptance criteria, and no unmet design gate |
| `VERIFY` | Fresh checks mapped to acceptance criteria, actual results, and omitted-check explanation |
| `REVIEW` | Independent findings or explicit reason the review boundary does not apply |
| `SHIP` | Exact side effect, target revision/environment, rollback or recovery condition, and explicit authorization |
| `LEARN` | Repeated friction or risk worth turning into a project rule, Skill, Squad, or evaluation case |

## Short User-Facing Format

For ordinary work, the agent can show this compact card:

```markdown
IDC Task: IDC-MYPROJECT-FEAT-20260905-001
Scenario: FEAT / cross-boundary
Intent: [observable result]
Scope: [included] / Excludes: [not included]
Impact: behavior=medium, data=low, security=none, external=none
Route: INTAKE -> DESIGN(architecture) -> BUILD -> VERIFY
Acceptance: [what must be true]
Permission gate: none / [exact action requiring approval]
Open decision: none / [one focused question]
```

For an obvious one-file, low-risk correction, use the compact format rather than
creating a durable file. The visible line still carries the IDC identity,
scenario, outcome, and verification; the full card is reserved for work with
meaningful scope, impact, handoffs, or decisions.
