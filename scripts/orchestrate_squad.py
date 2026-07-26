#!/usr/bin/env python3
"""Run a registered Squad contract as a local, evidence-recording state machine."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import shutil
import signal
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from validate_contracts import DEFAULT_SCHEMA, validate as validate_contracts


RUN_ID_PATTERN = re.compile(r"^[a-z][a-z0-9-]{0,63}$")
ALLOWED_VERIFICATION_COMMANDS = (
    ("pytest",),
    ("python", "-m", "pytest"),
    ("python", "-m", "unittest"),
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Record or execute a registered Squad contract with local evidence."
    )
    parser.add_argument("--contract", required=True, type=Path, help="Squad contract JSON file")
    parser.add_argument("--workspace", required=True, type=Path, help="Target project directory")
    parser.add_argument("--request", required=True, help="User request recorded with the run")
    parser.add_argument("--host", choices=("opencode",), default="opencode")
    parser.add_argument("--run-id", help="Lowercase identifier for this run")
    parser.add_argument(
        "--execute",
        action="store_true",
        help="Explicitly approve local, non-authorized controller execution.",
    )
    parser.add_argument(
        "--opencode-command",
        action="append",
        help="OpenCode executable or command prefix argument; repeat to provide a test adapter.",
    )
    parser.add_argument(
        "--worker-timeout-seconds",
        type=int,
        default=600,
        help="Maximum seconds for a single OpenCode worker invocation.",
    )
    parser.add_argument(
        "--verification-timeout-seconds",
        type=int,
        default=120,
        help="Maximum seconds for a single declared verification command.",
    )
    return parser.parse_args()


def now() -> str:
    return datetime.now(timezone.utc).isoformat()


def generated_run_id(contract_id: str) -> str:
    timestamp = datetime.now(timezone.utc).strftime("%Y%m%dt%H%M%Sz").lower()
    return f"{contract_id}-{timestamp}"


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def write_snapshot(path: Path, payload: dict[str, Any]) -> None:
    path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")


def append_event(
    path: Path,
    sequence: int,
    event_type: str,
    state: str,
    details: dict[str, Any] | None = None,
) -> None:
    event = {
        "sequence": sequence,
        "timestamp": now(),
        "type": event_type,
        "state": state,
        "provenance": "controller-observed",
    }
    if details:
        event["details"] = details
    with path.open("a", encoding="utf-8", newline="\n") as handle:
        handle.write(json.dumps(event, separators=(",", ":")) + "\n")


def load_contract(path: Path) -> tuple[dict[str, Any] | None, list[str]]:
    errors = validate_contracts(DEFAULT_SCHEMA, path)
    if errors:
        return None, errors
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        return None, [f"cannot read contract: {exc}"]
    if payload.get("kind") != "squad-contract":
        return None, ["contract must have kind 'squad-contract'"]
    return payload, []


def resolve_opencode_command(command: list[str] | None) -> list[str]:
    if command:
        return command
    return [shutil.which("opencode") or "opencode"]


def command_is_unsafe(argv: list[str]) -> bool:
    return tuple(argv) not in ALLOWED_VERIFICATION_COMMANDS


def command_working_directory(workspace: Path, value: str) -> Path | None:
    candidate = (workspace / value).resolve()
    try:
        candidate.relative_to(workspace)
    except ValueError:
        return None
    return candidate


def policy_errors(
    contract: dict[str, Any], workspace: Path, execution_requested: bool
) -> list[str]:
    errors: list[str] = []
    commands = contract["verification"].get("commands", [])
    for command in commands:
        if command_working_directory(workspace, command["cwd"]) is None:
            errors.append(f"verification command '{command['id']}' escapes the workspace")
        if command_is_unsafe(command["argv"]):
            errors.append(f"verification command '{command['id']}' has a blocked effect")
    if execution_requested and not commands:
        errors.append("execution requires at least one declared verification command")
    return errors


def agent_prompt(
    contract: dict[str, Any],
    member: dict[str, Any],
    run_dir: Path,
    required_artifacts: list[dict[str, str]],
) -> str:
    dependencies = "none"
    if required_artifacts:
        dependencies = "\n".join(
            "\n".join(
                (
                    f"- {artifact['id']}: {artifact['path']} (sha256 {artifact['sha256']})",
                    Path(artifact["path"]).read_text(encoding="utf-8"),
                )
            )
            for artifact in required_artifacts
        )
    required_ids = [artifact["id"] for artifact in required_artifacts]
    subagent_instructions = "\n".join(
        (
            f"Execute the registered '{member['skill']}' judgment for Squad contract '{contract['id']}'.",
            "Do not edit files, commit, push, deploy, or perform external actions.",
            "Do not store files; the controller owns the persisted run artifacts.",
            "Use every required upstream artifact supplied below before responding:",
            dependencies,
            "Return exactly one JSON object, with no Markdown or surrounding text:",
            json.dumps(
                {
                    "artifact_id": member["required_output"],
                    "summary": "non-empty result summary",
                    "findings": ["evidence-backed finding"],
                    "consumed_artifact_ids": required_ids,
                }
            ),
        )
    )
    return "\n".join(
        (
            f"Use the {member['skill']} subagent through the Task tool exactly once.",
            "Do not read files, use other tools, classify the request, or perform the delegated judgment yourself.",
            "Tell the subagent:",
            subagent_instructions,
            "After the Task completes, return its exact JSON response with no Markdown or surrounding text.",
        )
    )


def parse_agent_output(
    stdout: str, expected_artifact: str, required_artifact_ids: list[str], expected_subagent: str
) -> tuple[dict[str, Any] | None, dict[str, str] | None, str | None]:
    task_observation: dict[str, str] | None = None
    final_text: str | None = None
    for line in stdout.splitlines():
        try:
            event = json.loads(line)
        except json.JSONDecodeError:
            return None, None, "worker output is not valid OpenCode JSON events"
        if not isinstance(event, dict):
            return None, None, "worker output contains a non-object OpenCode event"
        part = event.get("part")
        if not isinstance(part, dict):
            continue
        if event.get("type") == "tool_use" and part.get("tool") == "task":
            state = part.get("state")
            if not isinstance(state, dict) or state.get("status") != "completed":
                continue
            task_input = state.get("input")
            metadata = state.get("metadata")
            if (
                isinstance(task_input, dict)
                and task_input.get("subagent_type") == expected_subagent
                and isinstance(metadata, dict)
                and isinstance(metadata.get("sessionId"), str)
            ):
                task_observation = {
                    "invocation_agent": "team",
                    "subagent": expected_subagent,
                    "child_session_id": metadata["sessionId"],
                }
        if event.get("type") == "text" and isinstance(part.get("text"), str):
            final_text = part["text"]
    if task_observation is None:
        return None, None, f"worker output has no completed Task event for '{expected_subagent}'"
    if final_text is None:
        return None, None, "worker output has no final text event"
    try:
        output = json.loads(final_text)
    except json.JSONDecodeError:
        return None, None, "worker final text is not a single JSON object"
    if not isinstance(output, dict) or set(output) != {
        "artifact_id",
        "summary",
        "findings",
        "consumed_artifact_ids",
    }:
        return None, None, "worker output does not match the required artifact envelope"
    if output["artifact_id"] != expected_artifact:
        return None, None, f"worker output must produce '{expected_artifact}'"
    if not isinstance(output["summary"], str) or not output["summary"].strip():
        return None, None, "worker output needs a non-empty summary"
    if not isinstance(output["findings"], list) or not output["findings"] or not all(
        isinstance(finding, str) and finding.strip() for finding in output["findings"]
    ):
        return None, None, "worker output needs at least one non-empty finding"
    consumed = output["consumed_artifact_ids"]
    if not isinstance(consumed, list) or consumed != required_artifact_ids:
        return None, None, "worker output does not declare the required upstream artifacts"
    return output, task_observation, None


def write_command_output(directory: Path, name: str, stdout: str, stderr: str) -> tuple[Path, Path]:
    directory.mkdir(exist_ok=True)
    stdout_path = directory / f"{name}.stdout.log"
    stderr_path = directory / f"{name}.stderr.log"
    stdout_path.write_text(stdout, encoding="utf-8")
    stderr_path.write_text(stderr, encoding="utf-8")
    return stdout_path, stderr_path


def terminate_process_tree(process: subprocess.Popen[str]) -> None:
    if os.name == "nt":
        result = subprocess.run(
            ["taskkill", "/PID", str(process.pid), "/T", "/F"],
            text=True,
            capture_output=True,
            check=False,
        )
        if result.returncode != 0 and process.poll() is None:
            process.kill()
        return
    try:
        os.killpg(process.pid, signal.SIGKILL)
    except ProcessLookupError:
        pass


def run_command(
    command: list[str], working_directory: Path, timeout_seconds: int
) -> subprocess.CompletedProcess[str]:
    process = subprocess.Popen(
        command,
        cwd=working_directory,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        start_new_session=os.name != "nt",
        creationflags=subprocess.CREATE_NEW_PROCESS_GROUP if os.name == "nt" else 0,
    )
    try:
        stdout, stderr = process.communicate(timeout=timeout_seconds)
    except subprocess.TimeoutExpired as exc:
        terminate_process_tree(process)
        stdout, stderr = process.communicate()
        raise subprocess.TimeoutExpired(command, timeout_seconds, output=stdout, stderr=stderr) from exc
    return subprocess.CompletedProcess(command, process.returncode, stdout, stderr)


def run_worker(
    command: list[str], workspace: Path, timeout_seconds: int
) -> subprocess.CompletedProcess[str]:
    return run_command(command, workspace, timeout_seconds)


def transition(
    run: dict[str, Any],
    snapshot_path: Path,
    events_path: Path,
    sequence: int,
    state: str,
    event_type: str,
    details: dict[str, Any] | None = None,
) -> int:
    run["state"] = state
    write_snapshot(snapshot_path, run)
    append_event(events_path, sequence, event_type, state, details)
    return sequence + 1


def main() -> int:
    args = parse_args()
    workspace = args.workspace.expanduser().resolve()
    contract_path = args.contract.expanduser().resolve()
    if not workspace.is_dir():
        print(f"ERROR: workspace directory does not exist: {workspace}", file=sys.stderr)
        return 2
    if not contract_path.is_file():
        print(f"ERROR: contract file does not exist: {contract_path}", file=sys.stderr)
        return 2
    if args.worker_timeout_seconds <= 0:
        print("ERROR: --worker-timeout-seconds must be positive.", file=sys.stderr)
        return 2
    if args.verification_timeout_seconds <= 0:
        print("ERROR: --verification-timeout-seconds must be positive.", file=sys.stderr)
        return 2

    contract, errors = load_contract(contract_path)
    if errors:
        print("ERROR: invalid Squad contract:", file=sys.stderr)
        for error in errors:
            print(f"- {error}", file=sys.stderr)
        return 1
    assert contract is not None

    run_id = args.run_id or generated_run_id(contract["id"])
    if not RUN_ID_PATTERN.fullmatch(run_id):
        print("ERROR: --run-id must be a lowercase identifier.", file=sys.stderr)
        return 2
    run_dir = workspace / ".idc" / "runs" / run_id
    if run_dir.exists():
        print(f"ERROR: run directory already exists: {run_dir}", file=sys.stderr)
        return 1
    run_dir.mkdir(parents=True)

    route = [member["skill"] for member in contract["members"]]
    run: dict[str, Any] = {
        "schema_version": 1,
        "kind": "orchestration-run",
        "id": run_id,
        "state": "planned",
        "host": args.host,
        "workspace": str(workspace),
        "request": args.request,
        "contract": {
            "id": contract["id"],
            "path": str(contract_path),
            "sha256": sha256(contract_path),
        },
        "route": route,
        "authorization": contract["authorization"],
        "artifacts": [],
        "verification": [],
        "timeouts": {
            "worker_seconds": args.worker_timeout_seconds,
            "verification_seconds": args.verification_timeout_seconds,
        },
    }
    snapshot_path = run_dir / "run.json"
    events_path = run_dir / "events.jsonl"
    write_snapshot(snapshot_path, run)
    append_event(events_path, 1, "run-planned", run["state"])
    sequence = 2

    errors = policy_errors(contract, workspace, args.execute)
    if errors:
        transition(
            run,
            snapshot_path,
            events_path,
            sequence,
            "blocked",
            "policy-blocked",
            {"errors": errors},
        )
        print("ERROR: policy blocked the run:", file=sys.stderr)
        for error in errors:
            print(f"- {error}", file=sys.stderr)
        return 1

    sequence = transition(
        run, snapshot_path, events_path, sequence, "policy-checked", "policy-checked"
    )
    if not args.execute:
        print(f"Dry run recorded: {run_dir}")
        return 0

    if contract["authorization"]["required"]:
        transition(
            run,
            snapshot_path,
            events_path,
            sequence,
            "blocked",
            "authorization-required",
            {"effects": contract["authorization"]["effects"]},
        )
        print(
            "ERROR: this contract requires an approval token, which this MVP does not support.",
            file=sys.stderr,
        )
        return 1

    sequence = transition(
        run, snapshot_path, events_path, sequence, "approved", "execution-approved"
    )
    opencode_command = resolve_opencode_command(args.opencode_command)
    artifacts: dict[str, dict[str, str]] = {}
    handoffs_by_consumer = {handoff["to"]: handoff for handoff in contract["handoffs"]}
    host_directory = run_dir / "host"

    for member in contract["members"]:
        handoff = handoffs_by_consumer.get(member["skill"])
        required_artifact_ids = [] if handoff is None else [handoff["artifact_id"]]
        required_artifacts = [artifacts[artifact_id] for artifact_id in required_artifact_ids]
        sequence = transition(
            run,
            snapshot_path,
            events_path,
            sequence,
            "dispatched",
            "agent-dispatched",
            {"agent": member["skill"], "required_artifacts": required_artifact_ids},
        )
        command = [
            *opencode_command,
            "run",
            "--agent",
            "team",
            "--format",
            "json",
            "--dir",
            str(workspace),
            agent_prompt(contract, member, run_dir, required_artifacts),
        ]
        try:
            result = run_worker(command, workspace, args.worker_timeout_seconds)
        except (OSError, subprocess.TimeoutExpired) as exc:
            transition(
                run,
                snapshot_path,
                events_path,
                sequence,
                "failed",
                "agent-failed",
                {"agent": member["skill"], "error": str(exc)},
            )
            print(f"ERROR: OpenCode worker failed: {exc}", file=sys.stderr)
            return 1
        stdout_path, stderr_path = write_command_output(
            host_directory, member["skill"], result.stdout, result.stderr
        )
        if result.returncode != 0:
            transition(
                run,
                snapshot_path,
                events_path,
                sequence,
                "failed",
                "agent-failed",
                {"agent": member["skill"], "returncode": result.returncode},
            )
            print(f"ERROR: OpenCode worker '{member['skill']}' exited {result.returncode}.", file=sys.stderr)
            return 1
        output, task_observation, output_error = parse_agent_output(
            result.stdout,
            member["required_output"],
            required_artifact_ids,
            member["skill"],
        )
        if output_error:
            transition(
                run,
                snapshot_path,
                events_path,
                sequence,
                "failed",
                "artifact-rejected",
                {"agent": member["skill"], "error": output_error},
            )
            print(f"ERROR: OpenCode worker '{member['skill']}': {output_error}", file=sys.stderr)
            return 1
        assert output is not None
        artifact_directory = run_dir / "artifacts"
        artifact_directory.mkdir(exist_ok=True)
        artifact_path = artifact_directory / f"{member['required_output']}.json"
        artifact = {
            "schema_version": 1,
            "kind": "agent-artifact",
            "id": member["required_output"],
            "run_id": run_id,
            "producer": member["skill"],
            "provenance": "agent-declared",
            "output": output,
            "host_output": {
                "stdout": str(stdout_path.relative_to(run_dir)),
                "stderr": str(stderr_path.relative_to(run_dir)),
            },
            "host_observation": task_observation,
        }
        write_snapshot(artifact_path, artifact)
        artifact_reference = {
            "id": member["required_output"],
            "path": str(artifact_path),
            "sha256": sha256(artifact_path),
        }
        artifacts[member["required_output"]] = artifact_reference
        run["artifacts"].append(artifact_reference)
        sequence = transition(
            run,
            snapshot_path,
            events_path,
            sequence,
            "artifact-validated",
            "artifact-validated",
            {"agent": member["skill"], "artifact_id": member["required_output"]},
        )

    verification_directory = run_dir / "verification"
    for command in contract["verification"]["commands"]:
        command_cwd = command_working_directory(workspace, command["cwd"])
        assert command_cwd is not None
        try:
            result = run_command(
                command["argv"],
                command_cwd,
                args.verification_timeout_seconds,
            )
        except subprocess.TimeoutExpired as exc:
            stdout_path, stderr_path = write_command_output(
                verification_directory,
                command["id"],
                exc.stdout or "",
                exc.stderr or "",
            )
            timeout_evidence = {
                "schema_version": 1,
                "kind": "command-timeout",
                "id": command["id"],
                "provenance": "controller-observed",
                "argv": command["argv"],
                "cwd": str(command_cwd),
                "timeout_seconds": args.verification_timeout_seconds,
                "stdout": str(stdout_path.relative_to(run_dir)),
                "stderr": str(stderr_path.relative_to(run_dir)),
            }
            write_snapshot(verification_directory / f"{command['id']}.json", timeout_evidence)
            run["verification"].append(timeout_evidence)
            transition(
                run,
                snapshot_path,
                events_path,
                sequence,
                "failed",
                "verification-timed-out",
                {"command": command["id"], "timeout_seconds": args.verification_timeout_seconds},
            )
            print(f"ERROR: verification command '{command['id']}' timed out.", file=sys.stderr)
            return 1
        except OSError as exc:
            transition(
                run,
                snapshot_path,
                events_path,
                sequence,
                "failed",
                "verification-failed",
                {"command": command["id"], "error": str(exc)},
            )
            print(f"ERROR: verification command '{command['id']}' failed: {exc}", file=sys.stderr)
            return 1
        stdout_path, stderr_path = write_command_output(
            verification_directory, command["id"], result.stdout, result.stderr
        )
        evidence = {
            "schema_version": 1,
            "kind": "command-evidence",
            "id": command["id"],
            "provenance": "command-evidence",
            "argv": command["argv"],
            "cwd": str(command_cwd),
            "returncode": result.returncode,
            "stdout": str(stdout_path.relative_to(run_dir)),
            "stderr": str(stderr_path.relative_to(run_dir)),
        }
        write_snapshot(verification_directory / f"{command['id']}.json", evidence)
        run["verification"].append(evidence)
        if result.returncode != 0:
            transition(
                run,
                snapshot_path,
                events_path,
                sequence,
                "failed",
                "verification-failed",
                {"command": command["id"], "returncode": result.returncode},
            )
            print(f"ERROR: verification command '{command['id']}' exited {result.returncode}.", file=sys.stderr)
            return 1
        sequence = transition(
            run,
            snapshot_path,
            events_path,
            sequence,
            "verified",
            "verification-succeeded",
            {"command": command["id"]},
        )

    transition(run, snapshot_path, events_path, sequence, "completed", "run-completed")
    print(f"Run completed: {run_dir}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
