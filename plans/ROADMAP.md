# Roadmap

Status date: 2026-07-26

## Operating Rule

Each phase exists to reduce a specific uncertainty. Do not start a later phase because its output is attractive. Start it only when the prior phase exit criteria are supported by recorded evidence.

## Phase 0: Portable Foundation

Status: implemented, with execution claims still unproven.

Scope:

- Portable method, starter Skills, Squad templates, contracts, offline validators, and native adapter templates.
- Documentation that keeps progressive adoption and human judgment central.

Evidence held:

- Repository, contract, evaluator, bootstrap, and adapter-structure tests.

Exit criteria:

- Satisfied for structural correctness.
- Not satisfied for real host behavior; Phase 1 owns that gap.

## Phase 1: Empirical Routing And Host Acceptance

Goal: determine whether real coding Agents select and use the intended smallest route in actual supported hosts.

Status: in progress. Partial OpenCode `1.18.5` and Claude Code `2.1.154` pilots are recorded in `references/host-acceptance/`; both found route and evidence gaps, so neither is an acceptance result. A later OpenCode fixture manually completed `team -> debug -> verify`, but only through an in-session handoff and with a false agent-reported command exit status; it supports the Phase 2 provenance need, not a compatibility claim.

Minimum experiment:

1. Select Claude Code and OpenCode versions available to the evaluator.
2. Run 10-20 ordinary-language requests covering direct work, unknown-root-cause debugging, cross-layer change, meta design, permission boundaries, and near misses.
3. Record the project, host version, model, prompt, discovered entry files, actual loaded Skills or Agents, selected route, handoff artifacts, verification result, and permission behavior.
4. Compare actual routes with explicit expected routes. Classify every mismatch as a framework issue, host limitation, model behavior, or ambiguous case.

Exit criteria:

- A versioned manual acceptance record exists for both hosts.
- Route accuracy and handoff usability are reported without benchmark language.
- Unsupported or unstable behavior is labeled `experimental` or `guidance-only` in documentation.

Do not build:

- A general LLM benchmark service.
- General dynamic multi-Agent orchestration.
- New broad capability packs before the routing evidence is understood.

## Phase 1B: Experimental Local Orchestration Controller

Goal: test whether an explicit, local controller can make declared routes, artifact dependencies, command evidence, and authorization boundaries observable without replacing a coding host runtime.

Status: implementation and Windows timeout cleanup are covered by local tests; real-host acceptance is mismatched. A follow-up observed `team -> Task(debug)` host dispatch but not the required structured artifact protocol, downstream `verify`, or focused command evidence. See `references/host-acceptance/opencode-1.18.5-controller-2026-07-26.md`.

Scope:

- Explicit v1 Squad-contract selection for serial OpenCode execution.
- Local run snapshots, JSONL controller events, persisted artifact envelopes, and command evidence.
- No-shell verification commands with workspace containment and a limited blocked-effect guard.
- A hard block for authorization-required contracts until effect-specific approval tokens exist.

Exit criteria:

- A real OpenCode fixture run records the selected named Agents, persisted handoffs, focused command evidence, and policy behavior.
- The record distinguishes controller-observed facts, Agent-declared content, command evidence, and host-native evidence.
- At least one user can identify a repeated coordination failure that the controller prevented or made reviewable.

Do not build:

- Model-selected routes, parallel Workers, retries, resume, dynamic replanning, or a remote control service.
- A self-hosted Agent runtime or a claim that the controller enforces OpenCode internal tool permissions.
- Further controller or adapter features until a stable artifact protocol, downstream handoff, and focused command evidence have host evidence.

## Phase 2: Evidence And Contract Provenance

Goal: make the difference between claimed, observed, verified, and human-confirmed behavior explicit.

Status: completed for the personal-project documentation scope. One authorized LAS `5.2.3` local-project case records a `plan` claim that a focused test would fail, host discovery that exposed no named LAS specialist Agent, and independent command evidence that all four tests passed. The project owner confirmed the Chinese Evidence Card made the contradiction clear. The taxonomy is documented only and has not been added to the JSON Schema.

Scope:

- Define a provenance taxonomy for evaluation records and host acceptance records.
- Add a visible contract boundary explaining what structural validation cannot prove.
- Test the taxonomy in one real project before expanding the Schema broadly.

Required evidence classes:

- `claimed`: Agent-authored statement only.
- `host-observed`: host or adapter log indicates a Skill, Agent, or tool event.
- `command-evidence`: reproducible command, exit status, and bounded output reference.
- `artifact-evidence`: persisted artifact or diff reference.
- `human-confirmed`: a named human decision or approval record; a personal project may explicitly designate its owner as the human reviewer.

Exit criteria:

- At least one real evaluation can distinguish claimed data from independent evidence.
- Provenance improves reviewability without forcing users to collect full telemetry.
- The contract docs make no implication that JSON consistency proves execution behavior.

Do not build:

- A mandatory central log server.
- A synthetic health score.
- A provenance field that is only another unchecked Agent self-report.

## Phase 3: Multi-Project Local Index And CLI

Goal: validate whether developers need a cross-project view before building a web application.

Status: paused after the bounded `idc status --project <path>`, `idc evidence --project <path>`, and `idc portfolio --paths <path-a> <path-b> ...` slices. They are explicit-path, read-only `.idc` metadata reports with JSON output and an explicit terminal language preference. Portfolio requires at least two distinct resolved project paths and compares their metadata coverage. The project owner chose not to implement `diff` until a concrete same-project history-comparison question arises; current evidence does not justify a historical diff or web application.

Implemented slice:

- Explicit single-project path, with no project registration or implicit discovery.
- Read-only summary of contracts, evaluation cases and records, controller-recorded runs, and each run's latest valid event.
- Evidence display that labels evaluation records as `claimed`, recorded verification return codes as `command-evidence`, and persisted controller records as `artifact-evidence`; it reports `host-observed` and `human-confirmed` as unavailable when no explicit local record exists.
- Multi-project coverage report for contracts and evaluation records across only the explicitly supplied paths, with no registration or implicit discovery.
- Machine-readable JSON plus a concise terminal report in an explicit `zh` or `en` language.
- No project source, host configuration, personal configuration, Git history, or session export reads.

Deferred candidate commands:

```text
idc diff --project <path> --from <revision> --to <revision>
```

Exit criteria:

- At least three independent users can answer their current project-team question faster with the CLI than by opening project files manually.
- Users identify concrete information that a terminal report cannot express adequately.
- The index remains local-first and never reads source code or personal configuration without explicit scope.

Do not build:

- A web server, database, accounts, authentication, task board, or Agent command surface.

## Phase 4: Local HTML Report

Goal: test visual comparison and evolution comprehension without introducing a persistent web platform.

Minimum scope:

- Generate a self-contained local HTML report from the Phase 3 JSON model.
- Include project overview, Squad chains, evidence freshness, and evolution timeline.
- Follow `DESIGN.md` while preserving graph/list/table alternatives.

Exit criteria:

- Users can identify cross-project differences or historical changes more accurately than with CLI output alone.
- The report reveals a specific visual workflow that requires persistence or interactivity.

Do not build:

- Live Agent monitoring, task creation, chat, deployment controls, or a fake real-time dashboard.

## Phase 5: Read-Only Web Observatory

Goal: provide a local-first, multi-project observation surface only after the local index and report prove their value.

Scope:

- Portfolio, project, evolution, evidence, and settings views defined by `DESIGN.md`.
- Read-only project state, source links, freshness, and provenance labels.
- Host adapters as metadata sources, never as hidden authority over project files or permissions.

Entry criteria:

- Phase 1 host records exist.
- Phase 2 provenance model is tested in a real project.
- Phase 3 and Phase 4 show repeated unmet user needs.
- A privacy and local-data boundary is written before implementation.

Success criteria:

- Users can inspect what changed, why it changed, what evidence supports it, and what remains unverified.
- The application does not dispatch tasks, send prompts, run Agents, commit code, or replace human decisions.

## Deferred Or Explicitly Excluded

- Agent runtime and general workflow engine.
- Agent chat, task assignment, Kanban, and team messaging.
- Deployment, commit, push, or production control surfaces.
- Marketplace for generic Skills or large prebuilt teams.
- Cross-project code editing or repository search.
- Composite "team health" scores without transparent raw evidence.
- Claims of benchmarked routing quality before repeated published runs.

## Plan Maintenance

- Update `CURRENT_STATE.md` after a phase changes status.
- Add versioned acceptance records to `references/`.
- Keep raw external reviews separate from project decisions.
- Remove or revise a phase when evidence invalidates its premise.
