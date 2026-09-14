# Progressive Task Records

IDC records real work as it develops. It does not require a complete plan before
investigation, and it does not reconstruct normal tasks after completion.

## Operating Model

Every actionable request can begin as a lightweight `captured` record. It becomes
a durable task only when investigation, a material decision, or a change begins.
The record then grows through append-only events:

Use `idc start --temporary` for exploratory thoughts that may be discarded. The
default temporary TTL is 72 hours; expiry appends an event and never deletes
history. `idc discard` closes an unpromoted capture without creating a task card.
The default can be changed per project with `capture_ttl_hours` in `.idc/config.json`; an
explicit `--ttl-hours` on `start` takes precedence. `idc metrics --project <path> --json`
reports read-only counts and timing derived from the event log. It never mutates records.

```text
captured -> shaped -> active -> validating -> closed
                ^         |
                `---------` requirement or scope change
```

This lifecycle is deliberately small. Discovery, design, build, verification,
review, ship, observation, and learning are repeatable activities, not positions
that every task must visit in one fixed order.

## Dynamic Obligations

Dynamic obligations determine what the current work must prove next. They are
derived from the current intent, impact, uncertainty, conditions, evidence, and
requested external effects.

- Low-risk incomplete shaping produces warnings and work may continue.
- An unresolved product, privacy, data, permission, cost, or irreversible
  decision blocks ordinary execution.
- Emergency mode may defer shaping, but it does not waive permission, recovery,
  verification, or completion obligations.
- External effects require authorization for the exact named effect.
- `completed` requires passing evidence mapped to every acceptance item.

The task type does not select a fixed process. Scenario labels are mutable search
and routing hints. The obligation engine, not the label, controls hard gates.

## Record Layers

```text
.idc/
|-- config.json
|-- work-items/<record-id>/events.jsonl   # authoritative append-only facts
|-- task-ids/<task-id>                    # atomic identity reservation
`-- tasks/<task-id>.md                    # generated human-readable projection
```

An event states who recorded what, when, and with which provenance. The Markdown
card is always rebuilt from events and must not be edited directly.

Evidence provenance uses `claimed`, `host-observed`, `command-evidence`,
`artifact-evidence`, `human-confirmed`, or `reconstructed`. A label describes the
source; it does not upgrade a claim into proof.

`human-confirmed` requires a human actor and a non-empty `confirmation_ref`.
Agents must keep their own claims separate from explicit human confirmation.

## Host-Neutral Commands

```text
idc init        initialize project identity and record policy
idc start       capture the request before work
idc start --temporary --ttl-hours 24
idc promote     assign a durable task ID when work begins
idc discard     retain history while discarding an unpromoted capture
idc shape       record translated intent, scope, acceptance, and current labels
idc classify    add or replace mutable scenario labels
idc change      append a requirement change without rewriting history
idc resolve-decision
idc condition   record emergency, backfill, or other operating conditions
idc transition  move the universal lifecycle
idc activity    record discovery/design/build/verify/review/ship/observe/learn
idc add-evidence
idc permission
idc recovery
idc close
idc show
idc render
idc import-legacy
idc doctor
idc metrics

Acceptance values may be free text (auto-numbered `a-001`, `a-002`), `id=value`, or
`id:statement`. Repeated `shape --acceptance` calls merge items: existing IDs remain
stable, explicit IDs replace their statement, and omitted items are retained. A
`human-confirmed` evidence event requires `--actor human --confirmation-ref <ref>`.
```

Host adapters may trigger these commands, but they must not implement another
state model. Structural installation is not proof that a host actually captured
or maintained a task; host acceptance remains separate.

## Legacy Boundary

`import-legacy` reads an old Markdown card as one `reconstructed` snapshot. It
preserves the source file and does not invent historical lifecycle, decision, or
verification events. `BACKFILLED` is an audit-recovery condition, never the
normal path for new work.
