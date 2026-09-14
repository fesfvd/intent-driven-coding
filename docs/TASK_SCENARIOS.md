# IDC Task Scenarios

## Purpose

`team` decides which professional judgment is needed. This document defines the
task shape that decision starts from, so a request is never treated as a
generic "bug" or a generic "feature".

Scenario codes are a **mutable label** vocabulary for search, routing
hypotheses, and later comparison. They do not form the task identity and do not
select a fixed phase path. A task may begin unclassified, hold several
candidate labels, or append `classification.changed` when repository evidence
changes the meaning.

The framework uses two separate questions:

1. **What kind of work is this?** Hold one or more primary scenario labels.
2. **What can this work affect?** Record impact dimensions and uncertainty
   modifiers separately.

"The user has a clear goal" is not a scenario. It is an intake fact that can
reduce uncertainty, but a clear goal may still be a high-risk `FEAT`, `CHG`, or
`OPS` task.

All tasks use the universal `captured -> shaped -> active -> validating ->
closed` lifecycle from [Progressive Task Records](PROGRESSIVE_TASKS.md). Risk
and evidence produce **dynamic obligations** independently of labels.

## Outcome Labels

| Label | Current intended outcome |
|---|---|
| `FIX` | Restore established behavior or an invariant |
| `SEC` | Correct a security, privacy, isolation, or trust-boundary failure |
| `FEAT` | Introduce a new user-visible or system capability |
| `CHG` | Deliberately change an existing rule, output, policy, or flow |
| `REF` | Change internal structure while preserving relevant behavior |
| `REVIEW` | Produce evidence-backed findings without changing the subject |
| `OPS` | Perform or prepare a release, migration, or operational action |
| `EXP` | Reduce uncertainty and produce knowledge or a feasibility decision |
| `META` | Change the project's AI engineering or IDC operating system |

Do not force an early choice. Classification is useful only when it changes the
next investigation, specialist method, evidence requirement, or later query.

When a request could carry several labels, these precedence rules pick the
primary reading:

1. `REVIEW` wins when the requested outcome is findings and no code change.
2. `OPS` wins when the requested outcome is an environment, release, migration,
   or external operation, even if code changes are needed to prepare it.
3. `META` wins when the subject is the project's AI engineering system itself.
4. `EXP` wins when the requested outcome is knowledge or a feasibility decision,
   not a committed product change.
5. `SEC` wins over `FIX` when the primary defect is a trust-boundary, access,
   disclosure, privacy, or unsafe-execution failure.
6. Otherwise choose `FEAT`, `CHG`, `REF`, or `FIX` by the intended outcome.

Documentation-only work normally uses `CHG` when it changes project guidance,
`META` when it changes the IDC system itself, or `REVIEW` when it only audits
existing documentation. Use `FEAT` only when the documentation is a user-facing
capability with its own acceptance behavior.

## Typical Route Hints

Routes are repeatable activity hints, not a mandatory path. Activities can
repeat, be skipped, or return the task to shaping when facts change.

| Label | Typical route hint |
|---|---|
| `FIX` | build + verify; add `debug` when the cause is uncertain |
| `SEC` | design(debug) -> build -> review -> verify |
| `FEAT` | design(architecture) -> build -> review -> verify |
| `CHG` | design(architecture) when boundaries change -> build -> verify |
| `REF` | design(architecture) -> build -> verify; add review for a material boundary |
| `REVIEW` | review -> verify |
| `OPS` | verify -> review -> ship |
| `EXP` | design/plan -> verify; no implementation claim unless the task changes class |
| `META` | design(meta) -> build(meta) -> verify |

## Orthogonal Impact Dimensions

Record only dimensions relevant to the current work. Unknown material impact is
itself a reason to investigate. Use `none`, `low`, `medium`, `high`, or
`unknown` and explain every `medium` or higher value.

| Dimension | Question |
|---|---|
| Behavior | Can a user or caller observe a different result? |
| Data | Can data be created, transformed, migrated, deleted, or exposed? |
| Security | Can identity, trust, authorization, or secret handling change? |
| Privacy | Can private information become more or less visible? |
| Permission | Can an actor gain or lose an action? |
| Cost | Can the task consume money, quota, capacity, or significant compute? |
| Availability | Can uptime, latency, concurrency, or recovery change? |
| External effect | Can it commit, push, publish, deploy, send, or write remotely? |
| Reversibility | How difficult is it to undo a wrong assumption? |

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
| `unknown-contract` | The desired product or data meaning is not established | Stop at shaping and ask a focused question |
| `cross-boundary` | Multiple modules, services, artifacts, or teams must stay aligned | Produce an impact contract before affected work |
| `irreversible` | An incorrect action is destructive or expensive to undo | Require explicit authorization and a recovery or rollback condition |

These modifiers are not extra members of a Squad. They select gates and
evidence requirements. Conditions such as `emergency`, `blocked`, `waiting`,
and `paused` are separate and can change during execution.

## Dynamic Obligations By Trait

| Current trait | Obligation added |
|---|---|
| Unknown cause | Reproduction or falsifiable diagnosis before a repair claim |
| Unknown contract | Human decision before ordinary implementation |
| Cross-boundary | Current impact/consumer contract before affected work |
| Security or privacy impact | Allowed and denied paths plus focused review evidence |
| Persistent data impact | Compatibility, migration, and recovery meaning |
| External effect | Exact effect authorization before `ship` activity |
| Medium/high reversibility risk | Recovery or rollback record |
| Completion requested | Passing evidence mapped to every Acceptance item |
| Emergency | Deferred-shaping warnings; no waiver of ship or completion gates |

These are composable. New domains normally add a trait, evidence rule, or
project Skill rather than another global scenario label.

## Scenario-Specific Start Fields

The progressive record is mandatory, but each scenario adds a small set of
fields that makes its acceptance testable. These fields are shown before build
work begins.

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

## Progressive Task Contents

The Agent owns translation from ordinary language. Users do not fill a form.

- **Task ID**: `IDC-<PROJECT>-<YYYYMMDD>-<NNN>` after promotion; legacy IDs
  that embed a scenario code remain readable.
- **Intent**: explicit request, repository facts, proposed defaults, and open
  decisions.
- **Scope**: current included boundary, explicit exclusions, and preserved
  behavior.
- **Baseline**: repository facts, current behavior, reproduction, or diff that
  establishes where the task starts.
- **Impact**: only assessed dimensions, with unknown retained honestly.
- **Acceptance**: observable outcome IDs that evidence can reference.
- **Verification**: actual evidence, result, provenance, and omitted checks.
- **Permission gate**: exact external effect and its requested/granted/executed
  state.
- **Classification**: zero or more revisable scenario labels.

The initial `captured` event needs only a request summary; `idc start --scene`
can also record the initial scene read. Shaping is progressive: low-risk
omissions warn, while material open decisions and effectful operations create
hard gates. The generated card in `templates/IDC_TASK.md` is a projection,
not a form that must be completed before investigation.

## Compatibility Vocabulary

Older IDC material calls activities `INTAKE`, `DESIGN`, `PLAN`, `BUILD`,
`VERIFY`, `REVIEW`, `SHIP`, and `LEARN`. Adapters may display these names, but
the phase path is no longer a fixed state machine:

- `INTAKE` maps to `captured` and early shaping.
- `DESIGN/PLAN/BUILD/VERIFY/REVIEW/SHIP/LEARN` map to repeatable activity events.
- Requirement changes can return current work to `shaped` without erasing work.
- `closed` records an explicit outcome rather than implying successful completion.

## Short User-Facing Format

The first work report is printed automatically: `idc start` emits the
provisional card (header, current state, initial scene, outstanding
obligations). For later summaries, keep this compact shape:

```markdown
IDC Task: IDC-MYPROJECT-20260905-001
State: active; labels: FEAT / cross-boundary
Intent: [observable result]
Scope: [included] / Excludes: [not included]
Impact: behavior=medium, data=low, security=none, external=none
Acceptance: [what must be true]
Permission gate: none / [exact action requiring approval]
Open decision: none / [one focused question]
```

For an obvious one-file, low-risk correction, the printed card plus a compact
summary is the whole record. Durable files are reserved for work with
meaningful scope, impact, handoffs, or decisions. The task ID identifies one
piece of work; it is not a claim that the work passed. Status and evidence must
be recorded separately.
