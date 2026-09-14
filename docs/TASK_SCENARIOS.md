# IDC Task Scenarios
## Purpose

Scenario codes are a **mutable label** vocabulary for search, routing hypotheses,
and later comparison. They do not form the task identity and do not select a
fixed Phase path. A task may begin unclassified, hold several candidate labels,
or append `classification.changed` when repository evidence changes the meaning.

All tasks use the universal `captured -> shaped -> active -> validating -> closed`
lifecycle from [Progressive Task Records](PROGRESSIVE_TASKS.md). Risk and evidence
produce **dynamic obligations** independently of labels.

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

## Orthogonal Dimensions

Record only dimensions relevant to the current work. Unknown material impact is
itself a reason to investigate.

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

Uncertainty remains separate: `known-target`, `unknown-cause`,
`unknown-contract`, `cross-boundary`, and `irreversible`. Conditions such as
`emergency`, `blocked`, `waiting`, and `paused` can change during execution.

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

These are composable. New domains normally add a trait, evidence rule, or project
Skill rather than another global scenario code.

## Progressive Task Contents

The Agent owns translation from ordinary language. Users do not fill a form.

- **Task ID**: `IDC-<PROJECT>-<YYYYMMDD>-<NNN>` after promotion; legacy IDs remain readable.
- **Intent**: explicit request, repository facts, proposed defaults, and open decisions.
- **Scope**: current included boundary and preserved behavior.
- **Impact**: only assessed dimensions, with unknown retained honestly.
- **Acceptance**: observable outcome IDs that evidence can reference.
- **Verification**: actual evidence, result, provenance, and omitted checks.
- **Permission gate**: exact external effect and its requested/granted/executed state.
- **Classification**: zero or more revisable scenario labels.

The initial `captured` event needs only a request summary. Shaping is progressive:
low-risk omissions warn, while material open decisions and effectful operations
create hard gates. The generated card in `templates/IDC_TASK.md` is a projection,
not a form that must be completed before investigation.

## Compatibility Vocabulary

Older IDC material calls activities `INTAKE`, `DESIGN`, `PLAN`, `BUILD`, `VERIFY`,
`REVIEW`, `SHIP`, and `LEARN`. Adapters may display these names, but the Phase path
is no longer a fixed state machine:

- `INTAKE` maps to `captured` and early shaping.
- `DESIGN/PLAN/BUILD/VERIFY/REVIEW/SHIP/LEARN` map to repeatable activity events.
- Requirement changes can return current work to `shaped` without erasing work.
- `closed` records an explicit outcome rather than implying successful completion.
