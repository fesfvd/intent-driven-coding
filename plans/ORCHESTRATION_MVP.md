# OpenCode Orchestration Controller MVP Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Execute this plan task-by-task with tests before implementation. Steps use the repository test suite as the completion record.

**Goal:** Add a local-only controller that executes an explicit OpenCode Squad contract with auditable handoffs, command evidence, and policy gates.

**Architecture:** The controller owns a fixed local state machine and invokes OpenCode only through an adapter boundary. It persists controller-observed events, agent-declared artifacts, and command evidence without claiming host-native dispatch proof.

**Tech Stack:** Python 3.9+, standard library subprocess/JSON/JSONL, `jsonschema`, and `unittest`.

---

## Goal

Add a local-only controller that executes one explicitly selected, registered OpenCode Squad contract as a serial state machine. It must capture agent-declared handoffs, controller-observed command results, and policy decisions without becoming an Agent runtime or granting host permissions.

## Architecture

`scripts/orchestrate_squad.py` will load an existing v1 Squad contract, derive its ordered route from `members`, and write a per-run directory below `.idc/runs/`. The controller invokes OpenCode with `opencode run --agent team --format json` only when `--execute` is supplied; the project `team` primary must create the declared specialist through the host Task tool. The default mode is a non-dispatching dry run. Each worker must return a strict JSON envelope, and the controller creates the persisted artifact, validates required upstream artifact IDs, then advances the state.

The controller owns the fixed states `planned`, `policy-checked`, `approved`, `dispatched`, `artifact-validated`, `verified`, and `completed`, with `blocked`, `failed`, and `cancelled` terminal alternatives. `events.jsonl` is append-only controller evidence; `run.json` is the current snapshot. Raw host stdout and stderr are stored separately and are not treated as proof that a named host event occurred.

## Scope

- Support only `--host opencode` and sequential two- or three-member v1 Squad contracts.
- Add optional verification command declarations to the existing contract schema; commands are executed without a shell, bounded by a timeout, and restricted to a small test-runner allowlist.
- Require `--execute` as explicit human confirmation; contracts requiring authorization remain blocked because approval tokens are not implemented in this MVP.
- Keep model route selection, parallelism, retries, resume, dynamic replanning, host-plugin event telemetry, and self-hosted Agent execution out of scope.

## Files

- Modify: `schemas/intent-driven-coding-contract-v1.schema.json`
  - Add optional `verification.commands` declarations with identifier, argv, and relative working directory.
- Modify: `scripts/validate_contracts.py`
  - Reject duplicate verification command IDs. The controller checks workspace containment at execution because it owns the workspace path.
- Create: `scripts/orchestrate_squad.py`
  - Implement contract loading, fixed state transitions, policy checks, OpenCode subprocess adapter, strict agent-output parsing, artifact persistence, command evidence, and CLI exit codes.
- Modify: `tests/test_repository.py`
  - Add CLI-level tests for dry-run evidence, artifact dependency enforcement, verification command evidence, authorization blocking, and unsafe verification command rejection.
- Modify: `docs/CONTRACTS.md`
  - Document execution declarations, run records, provenance labels, and the precise policy boundary.
- Create: `docs/ORCHESTRATION.md`
  - Document the controller contract, CLI, state model, stored artifacts, and experimental OpenCode boundary.
- Modify: `plans/CURRENT_STATE.md` and `plans/ROADMAP.md`
  - Record the intentional shift from a deferred workflow engine to a tightly scoped, experimental controller MVP.
- Modify: `scripts/validate_repository.py`
  - Register new public documentation and controller script.

## Implementation Steps

### 1. Contract Verification

1. Add a failing test that a contract with duplicate verification command IDs is rejected.
2. Run the test and confirm the validator reports the duplicate ID.
3. Extend the schema and semantic validator with `verification.commands`.
4. Re-run the focused test and existing contract validation.

### 2. Dry-Run State Record

1. Add a failing CLI test that invokes a temporary two-member contract without `--execute`.
2. Assert that `run.json` contains the derived route and `events.jsonl` records `planned` then `policy-checked`, without an OpenCode invocation.
3. Implement contract loading, run ID creation, append-only event writing, state snapshots, and dry-run output.
4. Re-run the focused test.

### 3. Worker Handoffs

1. Add a failing test using a harmless fake OpenCode executable that returns strict JSON envelopes for `debug` and `verify`.
2. Assert that the second prompt contains the first artifact reference and that both artifact envelopes record the declared producer and consumed artifact IDs.
3. Implement the OpenCode adapter and strict output/artifact validation.
4. Re-run the focused test.

### 4. Verification And Policy Gates

1. Add failing tests for a successful verification command, an unsafe verification command, and a contract requiring authorization.
2. Implement no-shell command execution, stdout/stderr evidence capture, the unsafe-command denial list, and the authorization block.
3. Re-run focused tests and the complete test suite.

### 5. Public Contract

1. Update documentation and roadmap language to describe the MVP's actual guarantees and remaining host-policy limitation.
2. Register public files with repository validation.
3. Run repository validation, contract validation, offline evaluation, Skill audit, unit tests, and `git diff --check`.
