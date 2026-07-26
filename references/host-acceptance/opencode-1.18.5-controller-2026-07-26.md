# OpenCode Controller Acceptance: 2026-07-26

## Status

Status: `mismatched`

This is one disposable-fixture observation for the experimental controller. It is not a compatibility claim for OpenCode, a model, or another project.

## Scope

| Field | Record |
|---|---|
| Date and run ID | 2026-07-26; `controller-real-opencode-rerun` |
| Host version | OpenCode `1.18.5` |
| Model | `epstein-gpt56/gpt-5.6-sol`, as reported by the exported host session |
| Target revision | Disposable generated fixture; no Git baseline was initialized |
| Contract | `fixture-diagnosis`, SHA-256 `a263ed921a047a4f5c881bc9b84c20e0332be770963ee6d6c5e2cceb003c16ee` |
| Request | Diagnose the intentionally failing fixture report without applying a patch. |
| Expected route | `debug` -> `verify` |
| Verification command | Local source parse only; no edit, commit, push, deployment, paid call, or production access was requested |

## Preconditions

1. `prepare_host_acceptance_fixture.py --platform opencode --apply` prepared an empty disposable target.
2. `validate_project.py --platform opencode` passed.
3. `opencode agent list` listed the project-local `debug` and `verify` subagents.
4. Controller dry run `controller-dry-run` reached `policy-checked` with the expected `debug`, `verify` route and no worker invocation.
5. The controller did not pass OpenCode `--auto`. The fixture policy retained its `ask`/`deny` boundaries.

## Observed Execution

The first execute run failed before model invocation because Python could not resolve the PowerShell-visible npm command by its bare `opencode` name. The controller was corrected to resolve the executable with `shutil.which`; this is a Windows launcher fix, not host-routing evidence.

The rerun launched a real OpenCode session. Its controller record reached `agent-dispatched` for requested agent `debug`. The exported host session, however, reported:

```text
agent: build
tokens: input 0, output 0, reasoning 0
cost: 0
assistant parts: []
```

No `debug` response, persisted artifact, downstream `verify` invocation, or verification command result occurred. The outer acceptance process exceeded 620 seconds while the spawned OpenCode process remained alive; the acceptance process stopped only that known child process after exporting the session. The run snapshot therefore remains `dispatched`, rather than a controller-recorded terminal state.

## Evidence Classification

| Concern | Observation |
|---|---|
| Project Agent discovery | `opencode agent list` observed `debug` and `verify`. |
| Named dispatch | Mismatched: exported session recorded generic `build`, not requested `debug`. |
| Handoff | Unobservable: no worker output or artifact was produced. |
| Command evidence | Unobservable: route did not reach the declared local command. |
| Permission behavior | Unobservable: no model tool call or permission prompt occurred. |
| External effect | None requested or executed. |

## Decision

Do not claim controller compatibility or named OpenCode dispatch. Before another paid or long-running attempt, determine the correct non-interactive OpenCode invocation for a project subagent and make controller worker timeout terminate the full Windows shim process tree. Keep raw session evidence local and bounded; this record retains only the session ID-independent facts above.

## Phase 1R Follow-Up

### Scope

This follow-up used a second disposable fixture with OpenCode `1.18.5` and `opencode/deepseek-v4-flash-free`. It did not request edits, commits, pushes, deployment, production access, paid effects, or external actions.

The installed CLI help and OpenCode Agent documentation distinguish a top-level primary Agent from a subagent. The observed non-interactive shape is therefore `opencode run --agent team`, followed by a host Task call with `subagent_type: debug`; a direct top-level `--agent debug` request remains mismatched.

### Observations

1. A minimal `opencode run --agent team --format json` session exported `agent: team` and returned the requested marker with no file changes or tool calls.
2. Putting `@debug` in a one-shot CLI message did not create a child session. The exported session remained `team` only.
3. A `team` session explicitly instructed to use the Task tool produced a completed Task event with `subagent_type: debug`, a child session ID, and an exported child session whose agent was `debug`.
4. The revised controller starts `team`, requires that completed Task event, and records the child-session observation only after the event is present. Its Windows timeout cleanup has a local regression test that proves a spawned child process is terminated.
5. In the final controller fixture run, `debug` was host-observed and performed a read-only diagnosis of the intentional failures. The primary response summarized that diagnosis as prose rather than the controller's strict JSON artifact envelope. The controller rejected it, persisted no artifact, did not invoke `verify`, and did not run the declared focused command.

### Follow-Up Classification

| Concern | Observation |
|---|---|
| Primary Agent selection | Observed: exported session recorded project `team`. |
| Named subagent dispatch | Observed: host Task event and child export recorded `debug`. |
| Artifact protocol | Mismatched: primary prose did not satisfy the required JSON envelope. |
| Handoff to `verify` | Unobservable: no accepted debug artifact existed. |
| Command evidence | Unobservable: the controller stopped before the declared command. |
| Permission behavior | Partial: the debug child performed only local reads and a focused local test; no external effect was requested. |
| Windows timeout cleanup | Local-test evidence only; not a real-host route result. |

### Decision Update

Named OpenCode child dispatch is now an observed host fact under this exact fixture, host version, model, and configuration. It does not make the controller compatible: the end-to-end artifact, handoff, verification, and permission path remains unproven. Do not add a dedicated controller primary Agent, automatic artifact transformation, retries, or orchestration features until a repeated real coordination failure justifies that investment.

## Manual Task Handoff Observation

### Status

Status: `partial`

This was a separate, bounded host session rather than a controller run. It confirms a narrow manual coordination path in the same disposable fixture; it is not a general compatibility, quality, or controller claim.

### Observed Route

The project `team` primary Agent created a `debug` Task child, received its diagnosis, then created a `verify` Task child. The parent Task event supplied the full debug diagnosis inside the verify Task prompt. Both child session exports recorded the expected project Agent names and no file additions or deletions.

The verify child ran only `python -m unittest discover -s tests -p test_report.py -v`. Its host Bash event recorded exit code `1` and the intentional report assertion failure. An independent local rerun produced the same failing result.

### Evidence Boundary

The verify child correctly described the assertion failure, but its final prose also stated that the command completed with exit code `0`. That statement conflicts with the host Bash event and independent rerun. The Task completion status means the child session completed; it does not mean the focused command passed.

| Concern | Observation |
|---|---|
| `team -> debug -> verify` Task route | Host-observed in one disposable fixture session. |
| Debug-to-verify handoff | Host-observed as transient Task prompt content, not a persisted artifact. |
| Focused command | Host Bash event and independent rerun both recorded the intentional failure and exit code `1`. |
| Verify prose | Agent claim only; its exit-code statement was contradicted by command evidence. |
| Source changes and external effects | None observed or requested. |

### Decision Update

This result supports explicit manual coordination for bounded work and makes the evidence-provenance distinction concrete. It does not justify a dedicated controller primary Agent or moving the controller to accepted status. Test the provenance taxonomy in a real project before adding it to contracts or building Phase 3 CLI features.
