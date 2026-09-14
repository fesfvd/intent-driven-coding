# Project Progress

This is the chronological record of Intent-Driven Coding itself. It answers
what changed, why it changed, what evidence supports it, and what remains
unproven. It is different from `CURRENT_STATE.md` (a snapshot) and
`ROADMAP.md` (future gates).

## Maintenance Rules

- Add an entry when a meaningful implementation, experiment, user decision, or
  evidence result changes the project's direction.
- Record outcomes, not activity. Link to the artifact or command that supports
  the entry.
- Keep unverified claims explicit. A plan is not an implementation and a
  structural check is not host acceptance.
- Prefer one entry per decision or evidence event. Do not turn this into a
  commit dump.
- Update the current snapshot and roadmap when an entry changes a phase status
  or an open risk.

## Current Focus

- Date: 2026-09-14
- Focus: validate event-first progressive records in real LAS work, then make
  the same core portable through a host-neutral CLI and thin adapters.
- Success condition: work is captured before substantial action, changes remain
  append-only, scenario labels can evolve without changing identity, and current
  risk plus evidence derive the obligations for closure or external effects.
- Not yet proven: that a supported host automatically maintains the event stream
  across a full real-work session without explicit CLI calls.

## Timeline

### 2026-09-14: Progressive task runtime

- **Change:** replaced task-card-first identity with append-only event records,
  a universal `captured -> shaped -> active -> validating -> closed` lifecycle,
  mutable scenario labels, and risk-adaptive dynamic obligations.
- **Change:** added the installable `idc` CLI and `idc_core` package, generated
  Markdown projections, legacy snapshot import, Codex `.agents/skills`
  scaffolding, JSON Schema validation, and concurrency-safe task IDs.
- **Reason:** real work changes during investigation and emergencies; requiring
  a complete card before work or reconstructing it afterward loses causality.
- **Boundary:** structural and local CLI tests do not prove automatic host event
  capture. LAS remains the first real-project pilot.
- **Evidence:** full `python -m unittest discover -s tests` suite reached 178
  passing tests, including temporary capture TTL configuration, stable acceptance
  merging, strict human confirmation, modular obligations, and read-only metrics;
  repository, contract, offline evaluation, and Skill audits pass.

### 2026-09-12: Self-use layer completed and a validator false positive fixed

- **Change:** completed the untracked `self-use/` layer that ships a
  lightweight, path-based personal profile: added `self-use/skills/architecture.md`,
  `self-use/skills/verify.md`, `self-use/templates/task-card-lite.md`, and
  `self-use/templates/task-card-decision.md`, and rewrote the README
  "next step" section into a file inventory plus an explicit unverified-status
  note.
- **Reason:** `self-use/README.md` promised three Skill files and two task-card
  templates that did not exist, so the layer was unusable as documented.
- **Change:** `scripts/validate_repository.py` now skips fenced code blocks when
  checking local Markdown links (`strip_fenced_code`, `broken_local_links`). The
  template-token and private-data checks still run on the raw text.
- **Reason:** the three suite assertions that require a clean repository were
  failing with `self-use/CLAUDE.md: broken local link` because illustrative
  example links inside ```markdown fences were treated as navigational links.
  Repository-wide validation was red, which violates the "evidence before
  claims" discipline this framework asks other projects to follow.
- **Evidence:** `python scripts/validate_repository.py` passes (97 required
  files, 379 Markdown files); `audit_skills.py`, `validate_contracts.py`, and
  `evaluate_contracts.py` pass with no warnings; `python -m unittest discover -s
  tests` reports `Ran 124 tests ... OK` (previously 122 with 3 failures); `git
  diff --check` passes. Two new tests cover the fenced-example link rule and the
  self-use file inventory.
- **Boundary:** this is structural evidence only. The self-use layer has no
  real-project execution record, and the framework still makes no claim about
  host routing, Skill discovery, or permission behavior.

### 2026-09-05: Installation identity and product positioning

- **Change:** added `docs/INSTALLATION.md` as the canonical clone-to-first-task
  guide and added the generated project-root `IDC.md` marker.
- **Reason:** users needed a clear distinction between the IDC source repository,
  the installed target-project guidance, and the assistant's first file to read.
- **Change:** documented IDC's difference from prompt packs, Skill collections,
  fixed Agent teams, generic orchestrators, and task-management tools.
- **Boundary:** this is a positioning and installation contract, not proof of
  automatic host discovery or routing.
- **Evidence:** the bootstrap, target validation, repository validation, and
  full unit-test suite pass after the change.

### 2026-09-05: Task scenarios and task identity (superseded in 1.1)

- **Change:** added `docs/TASK_SCENARIOS.md` with primary scenario codes for
  repair, security, feature, behavior change, refactor, review, operations,
  exploration, and project-system evolution.
- **Reason:** the existing router described Skills and phases but did not give
  users a stable way to recognize the shape and boundary of the task itself.
- **Change:** added the first generated-card predecessor and a scenario-encoded
  identity. Version 1.1 superseded that identity with scenario-neutral task IDs;
  old cards are accepted only as reconstructed legacy snapshots.
- **Reason:** every non-trivial task needs a durable reference for its intent,
  scope, impact, route, acceptance, evidence, and permission gate.
- **Evidence:** `python scripts/validate_repository.py` passed; `python -m
  unittest discover -s tests -v` passed all 122 tests (1 skipped) as of 2026-09-07; `git diff --check` passed.
  These checks validate local structure and tests, not host adoption.
- **Status:** implemented in this working change; adoption and usability remain
  to be tested with real tasks.

### 2026-08-14: DeepSeek Harness host pilots

- **Evidence:** two `0.1.0-rc.6` cohorts recorded host-observed routing results,
  including matched runs, a real three-member dispatch, a diff review that
  caught a planted regression, and a human-confirmed ambiguity loop.
- **Boundary:** neither cohort established stable routing accuracy or full
  security-route behavior. Details remain in the two records under
  `references/host-acceptance/`.

### 2026-07-26: Portable foundation and local controller

- **Change:** the repository had working structural validators, Skill audits,
  contract examples, native adapter templates, and an experimental explicit
  OpenCode controller.
- **Evidence:** the repository snapshot recorded passing unit, contract,
  evaluator, structure, and diff checks.
- **Boundary:** host discovery, named dispatch, semantic handoff consumption,
  and permission behavior remained unproven.

### 2026-09-07: Host self-bootstrap FIX of stale evidence numbers

- **Change:** corrected the unit-test count in `plans/CURRENT_STATE.md`
  (106) and `plans/PROJECT_PROGRESS.md` (120), which had drifted from the
  repository's actual test suite.
- **Reason:** a TraeCode-hosted Agent applied the framework's own FIX path to
  the IDC repository itself. The two plan documents contradicted each other and
  both disagreed with a fresh test run, violating the "evidence before claims"
  discipline the framework asks other projects to follow.
- **Evidence:** a fresh `python -m unittest discover -s tests -v` run recorded
  `Ran 122 tests ... OK (skipped=1)`; after the correction the four structural
  scripts (`validate_repository.py`, `audit_skills.py`, `validate_contracts.py`,
  `evaluate_contracts.py`) all pass with no warnings.
- **Boundary:** this corrects documented numbers; it is not evidence of host
  routing or Agent execution.

## Next Evidence To Collect

1. Use the task card on one low-risk `FIX`, one cross-boundary `FEAT`, one
   `SEC`, and one `REF` task in a real project.
2. Record whether the fixed fields reduce clarification, scope drift, or false
   completion claims.
3. Add or remove fields only after those observations and a human decision.
4. Run the `self-use` layer end to end on one real task in another project
   and record whether its absolute
   `/d/intent-driven-coding/self-use/skills/...` paths actually block reuse on a
   different machine or checkout.
5. Do not add a task database, web dashboard, or automatic ID service before
   local task cards demonstrate a concrete need.
