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

- Date: 2026-09-05
- Focus: establish a task-scenario model and a recognizable IDC task-start card
  so users can understand the work route before implementation begins.
- Success condition: the framework distinguishes task intent from impact and
  uncertainty, gives each non-trivial task an `IDC-...` identity, and records
  scope, acceptance, verification, and permission boundaries in one place.
- Not yet proven: that users consistently complete tasks faster or that any host
  automatically creates or maintains these cards.

## Timeline

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

### 2026-09-05: Task scenarios and task identity

- **Change:** added `docs/TASK_SCENARIOS.md` with primary scenario codes for
  repair, security, feature, behavior change, refactor, review, operations,
  exploration, and project-system evolution.
- **Reason:** the existing router described Skills and phases but did not give
  users a stable way to recognize the shape and boundary of the task itself.
- **Change:** added `templates/IDC_TASK.md` and the identity format
  `IDC-<PROJECT>-<SCENARIO>-<YYYYMMDD>-<NNN>`.
- **Reason:** every non-trivial task needs a durable reference for its intent,
  scope, impact, route, acceptance, evidence, and permission gate.
- **Evidence:** `python scripts/validate_repository.py` passed; `python -m
  unittest discover -s tests -v` passed all 120 tests; `git diff --check` passed.
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

## Next Evidence To Collect

1. Use the task card on one low-risk `FIX`, one cross-boundary `FEAT`, one
   `SEC`, and one `REF` task in a real project.
2. Record whether the fixed fields reduce clarification, scope drift, or false
   completion claims.
3. Add or remove fields only after those observations and a human decision.
4. Do not add a task database, web dashboard, or automatic ID service before
   local task cards demonstrate a concrete need.
