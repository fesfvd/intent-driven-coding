# IDC Repository Guide

This file describes the IDC framework repository itself. Current source,
tests, schemas, templates, and recorded host evidence are authoritative over
this summary. Keep this map concise and update it when repository boundaries or
verification commands change.

## Product And Scope

Intent-Driven Coding is a portable method, documentation set, host scaffold,
and local task-record CLI for deriving evidence-based AI engineering practice
from real work. It is not a general Agent runtime, automatic routing guarantee,
project task board, or deployment system.

The repository also contains an experimental OpenCode contract controller.
Its subprocess traces prove controller-observed behavior, not native host
dispatch or permission enforcement.

## Repository Map

| Path | Responsibility | Boundary |
|---|---|---|
| `idc_core/events.py`, `projector.py`, `workflow.py`, `obligations.py` | Event store, state projection, task workflow, dynamic gates | `events.jsonl` is the per-task source of truth; Markdown and task index are rebuildable projections |
| `idc_core/cli.py`, `commands.py`, `inspect_cli.py`, `learning.py`, `metrics.py`, `task_index.py` | CLI parsing/dispatch, command handlers, cadence, summaries, rebuildable index | Project paths must be explicit; index state never overrides event history |
| `schemas/`, `idc_core/resources/` | Public contract/event schemas and packaged schema resources | Keep packaged and public event schemas synchronized |
| `templates/`, `skills/`, `evals/`, `contracts/` | Installable guidance, platform agents, routing/evaluation inputs, examples | Bootstrap outputs are structural scaffolds, not proof of host behavior |
| `scripts/bootstrap.py`, `validate_project.py` | Platform file manifest, safe scaffold, generated-project checks | Keep planned files, docs, and manifest tests aligned |
| `scripts/validate_repository.py`, `validate_contracts.py`, `evaluate_contracts.py`, `audit_skills.py` | Repository, schema, offline evaluation, and Skill checks | These do not establish live host routing acceptance |
| `references/host-acceptance/`, `fixtures/host-acceptance/` | Versioned observations and non-leaking test targets | Preserve evidence status; do not generalize one run into compatibility claims |
| `docs/`, `README.md`, `QUICKSTART.md`, `AI_START_HERE.md` | Public product, install, protocol, and adoption guidance | Verify operational claims against code and current evidence |

## Critical Flows

Task record:

```text
CLI -> Workflow -> EventStore -> .idc/work-items/<record-id>/events.jsonl
                         |-> task index cache
                         `-> projector -> Markdown view
```

The JSONL event stream is authoritative. Markdown cards and
`.idc/index/tasks.json` are derived data. The index must be rebuildable and its
failure or staleness must not silently change event truth.

Host scaffold:

```text
templates + skills + evals -> scripts/bootstrap.py planned_files(platform)
                            -> target project files
                            -> scripts/validate_project.py structural checks
```

The installer does not install the `idc` Python package or initialize the
target's `.idc/config.json`; those are separate operations. Structural checks
do not prove runtime host discovery, routing, handoff, or permission behavior.

## Change Rules

- For an actionable change in this repository, use IDC's own task flow: capture
  with `idc start`, promote durable work when substantive investigation or
  implementation begins, and maintain the event record as the work changes.
- Inspect current source, tests, and host evidence before changing public claims.
- When changing an event contract, keep `schemas/idc-task-event-v1.schema.json`
  and `idc_core/resources/idc-task-event-v1.schema.json` synchronized.
- When changing Skills, Agent templates, or bootstrap destinations, update
  `scripts/validate_repository.py`, platform manifest tests, and public install
  docs as applicable.
- Keep `README.md` concise; `QUICKSTART.md` explains first use; `AI_START_HERE.md`
  guides an agent's bounded adoption; detailed contracts belong under `docs/`.
- Do not claim host support from templates, generated files, or structural
  validation alone. Cite versioned acceptance evidence and retain its status.
- Keep user-facing changes and release actions within explicit user
  authorization. Do not commit, push, publish, deploy, or make external calls
  unless asked.

## Verification

Run focused tests for changed behavior, then the repository checks appropriate
to the change. The CI baseline is:

```powershell
python -m unittest discover -s tests -v
python scripts/validate_repository.py
python scripts/validate_contracts.py
python scripts/evaluate_contracts.py
python scripts/audit_skills.py
```

For Python changes, also run `ruff check idc_core scripts tests` and
`python -m compileall -q idc_core scripts`. For generated host layouts, run
`scripts/validate_project.py --target <target> --platform <platform>` after
resolving scaffold placeholders; report structural and live-host results
separately.
