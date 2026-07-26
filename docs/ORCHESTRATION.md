# Experimental Orchestration Controller

## Scope

`scripts/orchestrate_squad.py` is a local-only, experimental OpenCode controller for one explicitly selected v1 `squad-contract`. It derives the declared member order, starts the project `team` primary Agent for each worker, requires a host-observed Task call to the declared specialist, persists accepted handoffs, and executes declared verification commands without a shell.

It is not an Agent runtime, a dynamic router, a retry system, a host plugin, or a deployment system. The caller selects `--contract`; no model chooses a route in this MVP. It supports only serial two- or three-member contracts and OpenCode invocation.

## Run A Dry Run

Start without `--execute`. The controller validates the contract and policy, then creates `.idc/runs/<run-id>/run.json` and `events.jsonl` without invoking OpenCode or a verification command.

```powershell
python scripts/orchestrate_squad.py `
  --contract ../my-project/.idc/contracts/debug-verify.squad.json `
  --workspace ../my-project `
  --request "Investigate the failing report." `
  --run-id report-diagnosis
```

To permit the local, non-authorized execution path, repeat the command with `--execute`:

```powershell
python scripts/orchestrate_squad.py `
  --contract ../my-project/.idc/contracts/debug-verify.squad.json `
  --workspace ../my-project `
  --request "Investigate the failing report." `
  --run-id report-diagnosis `
  --verification-timeout-seconds 120 `
  --execute
```

The controller calls the configured `opencode` executable as `opencode run --agent team --format json`. OpenCode defines `debug`, `verify`, and the other specialists as subagents, so a primary Agent must invoke them through the host Task tool; a direct top-level `--agent debug` invocation is not treated as accepted dispatch. The controller rejects a worker unless its JSON event stream contains a completed Task event for the declared specialist and a child session ID. `--opencode-command` is a repeatable command-prefix override intended for local adapter tests; ordinary users should not need it. The controller never adds OpenCode's `--auto` flag.

## Contract Requirements

An executable run uses an otherwise normal v1 `squad-contract`, with an explicit `verification.commands` array. Each command has an ID, an argument vector, and a working directory relative to the workspace:

```json
{
  "verification": {
    "claims": [
      {
        "id": "fix-supported",
        "statement": "The defect has fresh supporting evidence.",
        "required_evidence": ["Focused command result."]
      }
    ],
    "commands": [
      {
        "id": "focused-check",
        "argv": ["python", "-m", "unittest"],
        "cwd": "."
      }
    ]
  }
}
```

`--execute` rejects contracts without at least one declared verification command. The controller accepts only these exact verification `argv` forms, with no additional arguments:

```text
pytest
python -m pytest
python -m unittest
```

The `python` entries require that exact literal executable name. Absolute interpreter paths, `python3`, and other interpreter aliases are not accepted. This bounded allowlist rejects direct invocation of Git, Docker, Kubernetes, Terraform, Twine, shell executables, package managers, and arbitrary interpreters. It blocks Git options and Git aliases, including declarations such as `git -C .. push` and `git -c alias.release=!git push release`. `python -c`, direct script paths, test path selection, and arbitrary runner flags are rejected before Agent dispatch. The selected test runner still executes workspace test code, so these local guardrails do not replace host permissions or an effect-specific production-policy language.

Each verification command is bounded by `--verification-timeout-seconds` (120 seconds by default; a non-positive value is rejected). On timeout, the controller terminates that command's process tree, records `command-timeout` with the captured bounded output paths, appends `verification-timed-out`, and fails the run. A timeout has no command exit status and is not `command-evidence`.

## State And Evidence

The controller records these states in order when the path succeeds:

```text
planned -> policy-checked -> approved -> dispatched
-> artifact-validated -> verified -> completed
```

`blocked` and `failed` are terminal states. Each run directory contains:

```text
.idc/runs/<run-id>/
|-- run.json
|-- events.jsonl
|-- artifacts/<artifact-id>.json
|-- host/<agent>.stdout.log
|-- host/<agent>.stderr.log
`-- verification/<command-id>.json
```

- `events.jsonl` is `controller-observed`: it proves the controller's decisions and subprocess results.
- Accepted worker artifacts retain `host_observation` with the primary `team` invocation, requested specialist, and host child-session ID. This is host-observed dispatch evidence, not proof that the specialist followed every instruction.
- Worker artifacts are `agent-declared`: the controller validates their JSON envelope and required upstream artifact IDs, but it cannot prove an Agent semantically read or followed the artifact.
- Completed verification records are `command-evidence`: they preserve the argv, working directory, exit code, and bounded stdout/stderr files. A `command-timeout` record is controller-observed timeout evidence, not a successful or failed command exit result.
- Raw OpenCode stdout and stderr are retained as controller-captured output. The completed Task event is evidence of named child-session dispatch, but neither it nor the JSON envelope proves semantic artifact consumption.

Workers must return exactly one JSON object with `artifact_id`, `summary`, `findings`, and `consumed_artifact_ids`. A downstream Worker must declare exactly the artifact IDs required by its registered handoff; otherwise the controller rejects the output before moving to the next member.

## Permission Boundary

`--execute` is only an explicit approval for the controller's local, low-risk path. A contract whose `authorization.required` is true is blocked because this MVP has no approval token bound to a contract version, workspace revision, requested effect, and command summary.

The controller does not enforce worker tool permissions inside OpenCode. Project-level OpenCode policy remains the authority for Bash, edits, commit, push, deployment, production access, paid calls, and other host-executed effects. Configure that policy before using `--execute`; do not infer sandboxing from the controller prompt.

No real OpenCode controller run is an acceptance result until [Host Acceptance](HOST_ACCEPTANCE.md) records the installed host, model, named dispatch evidence, artifact handoff, focused command result, and policy behavior. Unit tests use a harmless local stub and do not establish those host facts.

The first real OpenCode `1.18.5` controller acceptance remains [mismatched](../references/host-acceptance/opencode-1.18.5-controller-2026-07-26.md). A follow-up proved `team` can create a named `debug` Task child session, while the controller correctly rejected the run because the primary returned prose rather than the required artifact envelope. It therefore did not reach a persisted artifact, `verify`, or the verification command. Do not use `--execute` as a compatibility claim until the documented artifact-protocol and end-to-end gaps are resolved.

A separate manual host session did complete `team -> debug -> verify` with the debug result embedded in the verify Task prompt and a focused test invocation. That proves a narrow, in-session coordination path, not the controller protocol: no handoff was persisted, and the verify prose incorrectly described the failing command as exit code zero. The controller must continue to require independent event and command evidence.

## Deferred Work

- Candidate-route generation and dynamic routing.
- Parallel execution, retries, resume, cancellation recovery, and replanning.
- Approval tokens and effect-specific authorization.
- Host plugins or telemetry that independently prove native Agent/Skill dispatch.
- A self-hosted Agent runtime, remote service, accounts, or a web control plane.
