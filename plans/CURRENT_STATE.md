# Current State

Status date: 2026-07-26

## Product Position

Intent-Driven Coding is a portable AI engineering method and optional scaffold for project-specific Skills, two- or three-Skill Squads, contracts, verification, and host adapters. It now also contains an experimental, local-only OpenCode orchestration controller for explicitly selected contracts. It is not an Agent runtime, a general workflow engine, a task board, or a deployment system.

The intended value is to help a developer and a coding Agent derive a small, evidence-based project system from repeated work instead of copying a fixed team or a large Skill catalog unchanged.

## Implemented

- Requirement translation, progressive context, human decision boundaries, and the small-Squad method.
- Seven starter capabilities: `team`, `architecture`, `debug`, `code-review`, `verify`, `meta-skill-designer`, and `skill-creator`.
- Neutral, OpenCode, and Claude Code scaffold layouts.
- Project structure validation, Skill auditing, bootstrap safety checks, and platform-specific template validation.
- JSON Schema v1 for Squad contracts, evaluation cases, and evaluation records.
- Offline contract validation and offline comparison of evaluation records with contract expectations.
- An experimental `scripts/orchestrate_squad.py` controller that records a serial, explicit OpenCode route; validates declared artifact consumption; captures command evidence; and blocks unsupported authorization and selected effectful verification commands.
- Experimental `scripts/idc.py status`, `scripts/idc.py evidence`, and `scripts/idc.py portfolio` local CLI commands that read only explicitly supplied projects' `.idc` contracts, evaluations, and controller runs; they have stable JSON output and explicit Chinese or English terminal output.
- A design language for a future read-only multi-project Observatory in `DESIGN.md`.

## Latest Local Evidence

The latest repository verification and first host pilot provide the following evidence:

- 106 unit tests passed.
- Contract validation passed for 2 example contract documents.
- Offline evaluation passed for 1 evaluation record.
- Repository validation and Skill audit passed.
- `git diff --check` passed.
- A disposable OpenCode `1.18.5` fixture passed structural validation and exposed its project `team` Agent plus seven project Skills.
- The OpenCode `1.18.5` pilot ran 10 routing prompts with `opencode/deepseek-v4-flash-free`. It produced only partial, mismatched, or unobservable runs; it did not establish route accuracy, usable handoffs, or permission acceptance. See `references/host-acceptance/opencode-1.18.5-2026-07-26.md`.
- The versioned non-leaking host-acceptance fixture is prepared by `scripts/prepare_host_acceptance_fixture.py`; its OpenCode and Claude Code layouts pass structural validation before model runs.
- The Claude Code `2.1.154` pilot ran the same 10 prompts with its default `deepseek-v4-pro` model. It produced only partial, mismatched, or unobservable runs; it did not establish named project subagent selection, persisted handoffs, focused verification, or deployment-policy behavior. See `references/host-acceptance/claude-code-2.1.154-2026-07-26.md`.
- The first real OpenCode controller run is `mismatched`: project `debug` and `verify` Agents were listed, but an exported session recorded generic `build` after the controller requested `debug`; it produced no artifact, command evidence, tokens, or cost. The Windows npm-shim launch defect and process-tree timeout cleanup now have local regression coverage.
- A Phase 1R follow-up observed `opencode run --agent team` create a named `debug` child through the host Task tool. The controller safely rejected its prose response because it did not match the required artifact envelope, so no persisted artifact, `verify`, or focused command evidence exists. See `references/host-acceptance/opencode-1.18.5-controller-2026-07-26.md`.
- A separate manual OpenCode fixture session completed `team -> debug -> verify`; the parent embedded the debug result in the verify Task input, both child sessions were exported, and the verify child ran the focused report test. The host Bash event and an independent rerun recorded exit code `1`, while the verify prose incorrectly stated exit code `0`. This is evidence for distinguishing host observations, command evidence, and Agent claims; it is not a persisted handoff or controller acceptance.
- An authorized LAS `5.2.3` local-project case observed OpenCode `1.18.5` discover only built-in `build` and `plan`, not the project's LAS specialist Skills as named Agents. A read-only `plan` session claimed `backend/tests/test_project_map.py` would fail; independent `uv run python -m pytest backend/tests/test_project_map.py -q` command evidence reported `4 passed`. The session made no source changes, but it read beyond the requested file scope. See `references/host-acceptance/las-5.2.3-opencode-1.18.5-2026-07-26.md`.
- `idc status --project "D:\LAS 5.2.3" --language zh` reported only `unavailable` `.idc` categories, as expected because that project has no `.idc` metadata. It did not infer information from source, host configuration, or Git data.

These checks prove repository structure, scripts, fixtures, and documented constraints. They do not prove actual Agent routing, host discovery, permission behavior, or user value.

## Confirmed Boundaries

- A JSON contract can validate structure and cross-document consistency; it cannot prove that an Agent selected the declared route.
- An evaluation record is Agent-declared unless it is linked to independent host, command, artifact, or human evidence. The documented taxonomy is `claimed`, `host-observed`, `command-evidence`, `artifact-evidence`, and `human-confirmed`; the designated project owner confirmed one personal-project Evidence Card. The local CLI can display available `.idc` classes, but the taxonomy is not yet a contract Schema field.
- The controller's JSONL trace proves controller decisions and captured subprocess results, not host-native Agent dispatch or semantic artifact consumption.
- A generated native adapter layout is structurally valid only after `validate_project.py`; host discovery and permission behavior still require host-specific acceptance checks.
- `idc status` is a bounded local observation tool, not an Agent chat client, task dispatcher, workflow engine, source scanner, or authority that replaces human judgment.

## Open Risks

1. Neither host pilot nor the controller acceptance produced a fully matched route with independently usable handoff and verification evidence.
2. Claude Code selected user-level or generic capabilities in some observed cases; OpenCode accepts named child dispatch through `team` Task calls, but the current controller cannot rely on a general primary Agent to return its strict artifact envelope. A manual Task chain also showed that an Agent's prose can contradict the command exit recorded by the host.
3. Current contract examples cover only one three-member cross-layer Squad.
4. Provenance taxonomy is documented and has one real-project case plus designated-owner review, but it has not been added to evaluation records or independently shown to improve reviewability.
5. The value of cross-project visualization remains a hypothesis; the local metadata portfolio has not established that a web dashboard is needed.

## Current Decisions

- Keep the controller restricted to explicit, serial local contracts; do not add dynamic routing, retries, parallelism, an Agent runtime, or a general workflow engine before its host evidence exists.
- Do not begin Web Observatory implementation until local CLI users identify information a terminal report cannot express adequately.
- Pause CLI expansion after `status`, `evidence`, and `portfolio`; do not implement `diff` or add Git reads until a concrete same-project history-comparison question arises.
- Treat `DESIGN.md` as an experimental design constitution for the Observatory direction, not a promise that a web product exists.
- Use raw independent reviews as input, then record repository decisions separately in this directory.

## Immediate Next Gate

The project owner found the initial label-only LAS provenance record unclear and requested context, a short comparison, and source references; the record now begins with a Chinese Evidence Card. The owner confirmed that the revised card identifies the contradiction and is the designated human reviewer for this personal-project evidence case. Explicit user decisions authorized the bounded `idc status`, `idc evidence`, and `idc portfolio` CLI slices, then chose to pause expansion. Do not add Schema fields, `diff`, Git reads, or a dedicated controller primary Agent without a new separate user decision grounded in a concrete need. Do not report routing accuracy or controller compatibility until named dispatch, persisted handoffs, focused verification, and a policy-controlled release attempt hold in both hosts.
