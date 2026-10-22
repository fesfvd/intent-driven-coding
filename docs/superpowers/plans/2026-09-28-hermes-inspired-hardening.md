# Hermes-Inspired Hardening Implementation Plan (Reviewed)

> **For agentic workers:** Execute the checked tasks in order; write a failing behavior test before implementation. This plan replaces the earlier draft after review against the current repository.

**Goal:** Strengthen evidence-backed learning, make bootstrap outcomes auditable, and assert that tests use isolated temporary projects without claiming process-wide write isolation.

**Architecture:** The learning-curator Skill retains human disposition as the gate to durable guidance. `bootstrap.py` adds an optional JSON report of planned versus actually applied per-file outcomes; no completion stamp is created because skipped user-owned files and a stale manifest cannot prove scaffold completeness. Tests check their real project destinations before invoking CLI writers or subprocesses. These three increments are independently verifiable.

**Tech stack:** Python stdlib, unittest, existing repository validators.

## Review Findings Resolved

- Former Task 2 reported preflight statuses as completed actions and set `ok` solely from preflight. Revised report has `planned`, `outcome`, `reason`, `written`, `ok`, and `error`, with failures recorded after completed writes and nonzero exit.
- Former stamp would hash skipped arbitrary user files and might survive a failed subsequent run. Defer it. `validate_project.py` remains the structural check, and live host acceptance remains separate.
- Former monkeypatch missed `Path.open`, `os.*`, and subprocess writes. No global patch or process-wide safety claim; check actual test project paths at call sites and document the boundary.
- Document the CLI contract in `docs/INSTALLATION.md`, register changed source in `scripts/validate_repository.py` only if adding a new repository script (this revision does not).

## Task 0: Record Work

- [x] Inspect `python scripts/idc.py start --help` and `promote --help`.
- [x] Capture and promote record `work-20260928t061848z-fefafa32` (`IDC-IDC-20260928-001`).
- [x] Update the record as work progresses; close with an accurate verified outcome.

## Task 1: Learning-Curator Contract

**Files:** `skills/learning-curator/SKILL.md`, `tests/test_repository.py`.

- [x] Add a failing test that checks a concrete candidate example: a rule stated imperatively with a causal mechanism, a distinct unresolved open question, and merge provenance requiring either `absorbed-into` or a falsifying reason. Check the text of these examples/contracts, not just section headings.
- [x] Run focused test and observe expected failure.
- [x] In the Skill, require rule + mechanism without incident narration; unresolved attempts stay open questions, never validated practice. Preference order: strengthen current rule, merge umbrella, add support reference, finally propose a class-level new Skill. Require human disposition before any change; retiring knowledge requires `absorbed-into` or a falsifying reason. Keep the existing table and removal test.
- [x] Run the focused test and `python scripts/audit_skills.py`.

## Task 2: Bootstrap JSON Report

**Files:** `scripts/bootstrap.py`, `tests/test_repository.py`, `docs/INSTALLATION.md`.

**Contract:** `--report-json PATH` is optional. A JSON document contains `schema_version: 1`, `mode`, `platform`, `ok`, `written`, `error` (null or short failure), and `actions`, each with target-relative `destination`, `planned`, `outcome`, and `reason`. Outcomes: `planned` for dry-run actions, `created`/`overwritten`/`entry-integrated` for successful writes, `skipped`/`unchanged` for intentional no-ops, `blocked` on preflight error, `not-applied` for otherwise writable files in a blocked or interrupted run, and `failed` for the failing write. Reasons are explicit for skips/errors. A dry-run is `ok: true` if preflight succeeded but `written: 0`; an apply is `ok: true` only after all actions completed. No report is published if the report path is invalid or would overlap a scaffold destination/source; reject it before writing the scaffold. The report is outside the target tree by default in examples to avoid confusing validation. No stamp.

- [x] Test first: dry-run with report shows `planned`, writes no scaffold; apply with pre-existing file shows actual `skipped` and `created`, accurate `written`; blocked preflight reports `blocked` and `not-applied`; injected mid-apply write error reports prior successes, `failed` and remaining `not-applied`, exits nonzero; a report path equal to a planned scaffold destination is rejected without modifying that destination. Test mid-apply by calling `bootstrap.main()` with patched `sys.argv` and `shutil.copyfile` on a temporary target, rather than manipulating real source files.
- [x] Run focused tests and observe failures from missing option/behavior.
- [x] Implement atomic JSON write with a temporary sibling + `os.replace`, creating report parent only after validation; reject aliases to any source or target destination (including symlinks), target root as a directory, and the report path itself if it resolves to a planned destination. Do not swallow report-writing failure: exit nonzero and describe it. Catch file-write errors in apply to record a failure before returning nonzero. Preserve existing human-readable CLI output and default behavior.
- [x] Run focused and existing bootstrap tests; update `docs/INSTALLATION.md` to show `--report-json` and explain planned vs applied statuses, skipped files, and the continued role of `validate_project.py` and host acceptance.

## Task 3: Focused Test Sandbox Assertions

**Files:** `tests/test_repository.py`, `tests/test_progressive_distribution.py` (and only other test modules with a concrete risky destination found in review).

- [x] Identify project roots passed to writing commands or in-process event stores. Write a failing unit test for a reusable `assert_test_project_path` helper: reject repository root, children, symlink aliases, and paths in an unexpected location; accept a `TemporaryDirectory()` project. No monkeypatch.
- [x] Implement helper in `tests/_project_paths.py` that checks resolved paths against the repository root and the explicit temporary root. Add it at actual CLI writer/subprocess entry points (e.g. `RepositoryTests.run_script` only where arguments include `--target`/`--project`, and distribution smoke tests). Do not claim it catches arbitrary writes or override subprocess behavior.
- [x] Run focused helper and test-module checks, then full suite. If a particular test has no target path, leave it alone and report that limit.

## Task 4: Verification and Closure

- [ ] `python -m unittest discover -s tests -v`
- [ ] `python scripts/validate_repository.py`
- [ ] `python scripts/validate_contracts.py`
- [ ] `python scripts/evaluate_contracts.py`
- [ ] `python scripts/audit_skills.py`
- [ ] `ruff check idc_core scripts tests` and `python -m compileall -q idc_core scripts`.
- [ ] Close IDC record with accurate tests and limitations; do not commit/push/publish without explicit authorization.
