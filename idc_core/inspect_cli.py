"""Read explicitly scoped Intent-Driven Coding metadata without touching project source."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

from idc_core.cli import PROGRESSIVE_COMMANDS, add_progressive_subcommands, run_progressive
from idc_core.metrics import build_progressive_metrics


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Summarize explicitly scoped local Intent-Driven Coding metadata."
    )
    subcommands = parser.add_subparsers(dest="command", required=True)
    for name, help_text in (
        ("status", "Summarize one project's .idc metadata."),
        ("evidence", "Classify one project's recorded .idc evidence."),
    ):
        command = subcommands.add_parser(name, help=help_text)
        command.add_argument("--project", required=True, type=Path, help="Explicit project directory")
        command.add_argument("--json", action="store_true", help="Emit machine-readable JSON")
        command.add_argument(
            "--language",
            choices=("en", "zh"),
            default="en",
            help="Language for terminal output; JSON field names remain stable.",
        )
    portfolio = subcommands.add_parser("portfolio", help="Compare explicit projects' .idc metadata.")
    portfolio.add_argument(
        "--paths",
        required=False,
        type=Path,
        nargs="+",
        help="Two or more explicit project directories",
    )
    portfolio.add_argument(
        "--project",
        type=Path,
        help="One explicit project directory for --progressive-metrics",
    )
    portfolio.add_argument(
        "--progressive-metrics",
        action="store_true",
        help="Read-only metrics from one project's progressive event log",
    )
    portfolio.add_argument("--json", action="store_true", help="Emit machine-readable JSON")
    portfolio.add_argument(
        "--language",
        choices=("en", "zh"),
        default="en",
        help="Language for terminal output; JSON field names remain stable.",
    )
    add_progressive_subcommands(subcommands)
    return parser.parse_args()


def load_json_files(directory: Path) -> list[tuple[Path, dict[str, Any]]]:
    if not directory.is_dir():
        return []
    documents: list[tuple[Path, dict[str, Any]]] = []
    for path in sorted(directory.rglob("*.json")):
        try:
            payload = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, UnicodeError, json.JSONDecodeError):
            continue
        if isinstance(payload, dict):
            documents.append((path, payload))
    return documents


def latest_event(events_path: Path) -> str:
    if not events_path.is_file():
        return "unavailable"
    latest = "unavailable"
    try:
        lines = events_path.read_text(encoding="utf-8").splitlines()
    except (OSError, UnicodeError):
        return latest
    for line in lines:
        try:
            event = json.loads(line)
        except json.JSONDecodeError:
            continue
        if isinstance(event, dict) and isinstance(event.get("type"), str):
            latest = event["type"]
    return latest


def build_status(project: Path) -> dict[str, Any]:
    idc_root = project / ".idc"
    contract_documents = load_json_files(idc_root / "contracts")
    evaluation_documents = load_json_files(idc_root / "evals")
    contracts = sorted(
        payload["id"]
        for _, payload in contract_documents
        if payload.get("kind") == "squad-contract" and isinstance(payload.get("id"), str)
    )
    evaluation_cases = sorted(
        payload["id"]
        for _, payload in contract_documents
        if payload.get("kind") == "evaluation-case" and isinstance(payload.get("id"), str)
    )
    evaluation_records = sorted(
        payload["id"]
        for _, payload in evaluation_documents
        if payload.get("kind") == "evaluation-record" and isinstance(payload.get("id"), str)
    )
    runs: list[dict[str, Any]] = []
    runs_root = idc_root / "runs"
    if runs_root.is_dir():
        for path in sorted(runs_root.glob("*/run.json")):
            try:
                run = json.loads(path.read_text(encoding="utf-8"))
            except (OSError, UnicodeError, json.JSONDecodeError):
                continue
            if not isinstance(run, dict) or run.get("kind") != "orchestration-run":
                continue
            run_id = run.get("id")
            if not isinstance(run_id, str):
                continue
            runs.append(
                {
                    "id": run_id,
                    "state": run.get("state", "unavailable"),
                    "host": run.get("host", "unavailable"),
                    "route": run.get("route", []),
                    "latest_event": latest_event(path.with_name("events.jsonl")),
                }
            )
    return {
        "project": str(project),
        "scope": ".idc metadata only",
        "contracts": contracts,
        "evaluation_cases": evaluation_cases,
        "evaluation_records": evaluation_records,
        "runs": runs,
        "availability": {
            "contracts": "available" if contracts or evaluation_cases else "unavailable",
            "evaluations": "available" if evaluation_records else "unavailable",
            "runs": "available" if runs else "unavailable",
        },
    }


def relative_to_project(path: Path, project: Path) -> str:
    return path.relative_to(project).as_posix()


def string_list(value: Any) -> list[str]:
    if not isinstance(value, list):
        return []
    return [item for item in value if isinstance(item, str)]


def dictionary_list(value: Any) -> list[dict[str, Any]]:
    if not isinstance(value, list):
        return []
    return [item for item in value if isinstance(item, dict)]


def build_evidence(project: Path) -> dict[str, Any]:
    idc_root = project / ".idc"
    claimed: list[dict[str, Any]] = []
    for path, record in load_json_files(idc_root / "evals"):
        if record.get("kind") != "evaluation-record" or not isinstance(record.get("id"), str):
            continue
        claimed.append(
            {
                "class": "claimed",
                "id": record["id"],
                "source": relative_to_project(path, project),
                "case_id": record.get("case_id", "unavailable"),
                "contract_id": record.get("contract_id", "unavailable"),
                "selected_route": string_list(record.get("selected_route")),
                "verification_claims": string_list(record.get("verification_claims")),
                "artifacts": string_list(record.get("artifacts")),
            }
        )
    claimed.sort(key=lambda record: record["id"])

    command_evidence: list[dict[str, Any]] = []
    artifact_evidence: list[dict[str, Any]] = []
    runs_root = idc_root / "runs"
    if runs_root.is_dir():
        for path in sorted(runs_root.glob("*/run.json")):
            try:
                run = json.loads(path.read_text(encoding="utf-8"))
            except (OSError, UnicodeError, json.JSONDecodeError):
                continue
            if not isinstance(run, dict) or run.get("kind") != "orchestration-run":
                continue
            run_id = run.get("id")
            if not isinstance(run_id, str):
                continue
            source = relative_to_project(path, project)
            artifact_evidence.append(
                {
                    "class": "artifact-evidence",
                    "id": run_id,
                    "source": source,
                    "state": run.get("state", "unavailable"),
                    "host": run.get("host", "unavailable"),
                    "route": string_list(run.get("route")),
                    "artifacts": string_list(
                        [artifact.get("id") for artifact in dictionary_list(run.get("artifacts"))]
                    ),
                    "latest_event": latest_event(path.with_name("events.jsonl")),
                }
            )
            for verification in dictionary_list(run.get("verification")):
                if (
                    verification.get("kind") != "command-evidence"
                    or not isinstance(verification.get("id"), str)
                    or not isinstance(verification.get("returncode"), int)
                ):
                    continue
                command_evidence.append(
                    {
                        "class": "command-evidence",
                        "id": verification["id"],
                        "run_id": run_id,
                        "source": source,
                        "argv": string_list(verification.get("argv")),
                        "cwd": verification.get("cwd", "unavailable"),
                        "returncode": verification["returncode"],
                        "stdout": verification.get("stdout", "unavailable"),
                        "stderr": verification.get("stderr", "unavailable"),
                    }
                )
    artifact_evidence.sort(key=lambda record: record["id"])
    command_evidence.sort(key=lambda record: (record["run_id"], record["id"]))
    return {
        "project": str(project),
        "scope": ".idc metadata only",
        "claimed": claimed,
        "command_evidence": command_evidence,
        "artifact_evidence": artifact_evidence,
        "availability": {
            "claimed": "available" if claimed else "unavailable",
            "host-observed": "unavailable",
            "command-evidence": "available" if command_evidence else "unavailable",
            "artifact-evidence": "available" if artifact_evidence else "unavailable",
            "human-confirmed": "unavailable",
        },
    }


def build_portfolio(projects: list[Path]) -> dict[str, Any]:
    summaries: list[dict[str, Any]] = []
    contract_coverage: dict[str, list[str]] = {}
    evaluation_record_coverage: dict[str, list[str]] = {}
    for project in projects:
        status = build_status(project)
        evidence = build_evidence(project)
        summaries.append(
            {
                "project": str(project),
                "contracts": status["contracts"],
                "evaluation_cases": status["evaluation_cases"],
                "evaluation_records": status["evaluation_records"],
                "run_count": len(status["runs"]),
                "evidence_availability": evidence["availability"],
            }
        )
        for contract_id in status["contracts"]:
            contract_coverage.setdefault(contract_id, []).append(str(project))
        for record_id in status["evaluation_records"]:
            evaluation_record_coverage.setdefault(record_id, []).append(str(project))
    return {
        "scope": ".idc metadata only",
        "projects": summaries,
        "coverage": {
            "contracts": contract_coverage,
            "evaluation_records": evaluation_record_coverage,
        },
    }


def render_terminal(status: dict[str, Any], language: str) -> str:
    if language == "zh":
        labels = {
            "project": "项目",
            "scope": "范围",
            "contracts": "合同",
            "evaluation_cases": "评估案例",
            "evaluation_records": "评估记录",
            "runs": "运行记录",
            "unavailable": "不可用",
            "run": "通过",
            "latest": "最后事件",
            "scope_value": "仅 .idc 元数据",
        }
    else:
        labels = {
            "project": "Project",
            "scope": "Scope",
            "contracts": "Contracts",
            "evaluation_cases": "Evaluation cases",
            "evaluation_records": "Evaluation records",
            "runs": "Runs",
            "unavailable": "unavailable",
            "run": "via",
            "latest": "latest event",
            "scope_value": ".idc metadata only",
        }
    lines = [
        f"{labels['project']}: {status['project']}",
        f"{labels['scope']}: {labels['scope_value']}",
        f"{labels['contracts']}: {', '.join(status['contracts']) or labels['unavailable']}",
        f"{labels['evaluation_cases']}: {', '.join(status['evaluation_cases']) or labels['unavailable']}",
        f"{labels['evaluation_records']}: {', '.join(status['evaluation_records']) or labels['unavailable']}",
        f"{labels['runs']}: {len(status['runs'])}",
    ]
    for run in status["runs"]:
        lines.append(
            f"- {run['id']}: {run['state']} {labels['run']} {run['host']}; "
            f"{labels['latest']} {run['latest_event']}"
        )
    return "\n".join(lines)


def render_evidence(evidence: dict[str, Any], language: str) -> str:
    if language == "zh":
        labels = {
            "project": "项目",
            "scope": "范围",
            "scope_value": "仅 .idc 元数据",
            "claimed": "Agent 声称",
            "command": "命令证据",
            "artifact": "持久化记录",
            "host": "宿主观察",
            "human": "人工确认",
            "unavailable": "不可用",
            "returncode": "退出码",
            "state": "状态",
        }
    else:
        labels = {
            "project": "Project",
            "scope": "Scope",
            "scope_value": ".idc metadata only",
            "claimed": "Agent claims",
            "command": "Command evidence",
            "artifact": "Persisted records",
            "host": "Host-observed",
            "human": "Human-confirmed",
            "unavailable": "unavailable",
            "returncode": "return code",
            "state": "state",
        }
    availability = evidence["availability"]
    lines = [
        f"{labels['project']}: {evidence['project']}",
        f"{labels['scope']}: {labels['scope_value']}",
        f"{labels['claimed']}: {len(evidence['claimed'])}",
    ]
    for claim in evidence["claimed"]:
        lines.append(f"- {claim['id']}: {', '.join(claim['verification_claims']) or labels['unavailable']}")
    lines.append(f"{labels['command']}: {len(evidence['command_evidence'])}")
    for command in evidence["command_evidence"]:
        lines.append(f"- {command['id']}: {labels['returncode']} {command['returncode']}")
    lines.append(f"{labels['artifact']}: {len(evidence['artifact_evidence'])}")
    for artifact in evidence["artifact_evidence"]:
        lines.append(f"- {artifact['id']}: {labels['state']} {artifact['state']}")
    lines.append(f"{labels['host']}: {availability['host-observed']}")
    lines.append(f"{labels['human']}: {availability['human-confirmed']}")
    return "\n".join(lines)


def render_portfolio(portfolio: dict[str, Any], language: str) -> str:
    if language == "zh":
        labels = {
            "projects": "项目数",
            "scope": "范围",
            "scope_value": "仅 .idc 元数据",
            "contracts": "合同",
            "evaluation_cases": "评估案例",
            "evaluation_records": "评估记录",
            "runs": "运行记录",
            "unavailable": "不可用",
            "coverage": "合同覆盖",
        }
    else:
        labels = {
            "projects": "Projects",
            "scope": "Scope",
            "scope_value": ".idc metadata only",
            "contracts": "Contracts",
            "evaluation_cases": "Evaluation cases",
            "evaluation_records": "Evaluation records",
            "runs": "Runs",
            "unavailable": "unavailable",
            "coverage": "Contract coverage",
        }
    lines = [
        f"{labels['projects']}: {len(portfolio['projects'])}",
        f"{labels['scope']}: {labels['scope_value']}",
    ]
    for project in portfolio["projects"]:
        lines.extend(
            (
                f"- {project['project']}",
                f"  {labels['contracts']}: {', '.join(project['contracts']) or labels['unavailable']}",
                f"  {labels['evaluation_cases']}: {', '.join(project['evaluation_cases']) or labels['unavailable']}",
                f"  {labels['evaluation_records']}: {', '.join(project['evaluation_records']) or labels['unavailable']}",
                f"  {labels['runs']}: {project['run_count']}",
            )
        )
    lines.append(f"{labels['coverage']}:")
    for contract_id, project_paths in portfolio["coverage"]["contracts"].items():
        lines.append(f"- {contract_id}: {len(project_paths)}/{len(portfolio['projects'])}")
    return "\n".join(lines)


def main() -> int:
    args = parse_args()
    if args.command in PROGRESSIVE_COMMANDS:
        return run_progressive(args)
    if args.command == "portfolio":
        if args.progressive_metrics:
            if args.project is not None and args.paths:
                print("ERROR: --project cannot be combined with --paths.", file=sys.stderr)
                return 2
            project_arg = args.project or (args.paths[0] if args.paths and len(args.paths) == 1 else None)
            if project_arg is None:
                print("ERROR: --progressive-metrics requires one --project directory.", file=sys.stderr)
                return 2
            project = project_arg.expanduser().resolve()
            if not project.is_dir():
                print(f"ERROR: project directory does not exist: {project}", file=sys.stderr)
                return 2
            report = build_progressive_metrics(project)
            if not args.json:
                print("ERROR: --progressive-metrics requires --json.", file=sys.stderr)
                return 2
            print(json.dumps(report, ensure_ascii=False, indent=2) + "\n")
            return 0
        if not args.paths or len(args.paths) < 2:
            print("ERROR: --paths requires at least two project directories.", file=sys.stderr)
            return 2
        projects = [path.expanduser().resolve() for path in args.paths]
        if len(set(projects)) != len(projects):
            print("ERROR: --paths requires distinct project directories.", file=sys.stderr)
            return 2
        for project in projects:
            if not project.is_dir():
                print(f"ERROR: project directory does not exist: {project}", file=sys.stderr)
                return 2
        report = build_portfolio(projects)
        terminal_report = render_portfolio(report, args.language)
    else:
        project = args.project.expanduser().resolve()
        if not project.is_dir():
            print(f"ERROR: project directory does not exist: {project}", file=sys.stderr)
            return 2
        if args.command == "status":
            report = build_status(project)
            terminal_report = render_terminal(report, args.language)
        else:
            report = build_evidence(project)
            terminal_report = render_evidence(report, args.language)
    if args.json:
        print(json.dumps(report, indent=2) + "\n")
    else:
        print(terminal_report)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
