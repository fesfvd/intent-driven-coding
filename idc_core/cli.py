from __future__ import annotations

import argparse
import importlib.resources
import json
import tempfile
from dataclasses import asdict
from pathlib import Path
from typing import Any

from jsonschema import Draft202012Validator

from .events import EventStore
from .legacy import import_legacy
from .metrics import build_progressive_metrics
from .context_health import inspect_context
from .commands import run_record_command
from .learning import check_learning_cadence, record_learning_session
from .workflow import GateBlocked, Workflow


VERSION = "1.2.0"
CONFIG_SCHEMA_VERSION = 2
EVENT_SCHEMA_VERSION = 2
PROGRESSIVE_COMMANDS = {
    "init",
    "start",
    "promote",
    "discard",
    "shape",
    "classify",
    "change",
    "resolve-decision",
    "condition",
    "transition",
    "activity",
    "add-evidence",
    "permission",
    "recovery",
    "close",
    "show",
    "render",
    "import-legacy",
    "doctor",
    "metrics",
    "migrate",
    "learn-review",
    "learn-dispose",
    "context-check",
    "learn-check",
    "learn-session",
}


def add_progressive_subcommands(subcommands: argparse._SubParsersAction) -> None:
    init = subcommands.add_parser("init", help="Initialize progressive IDC records in a project.")
    _project(init)
    init.add_argument("--project-key", required=True)
    init.add_argument(
        "--platform",
        choices=("neutral", "codex", "opencode", "claude-code"),
        default="neutral",
    )
    _json(init)

    start = subcommands.add_parser("start", help="Capture a request before work begins.")
    _project(start)
    start.add_argument("--summary", required=True)
    start.add_argument("--scene", dest="scenes", action="append", help="Initial scenario label read from the request; repeatable.")
    start.add_argument("--actor", choices=("human", "agent", "system"), default="agent")
    start.add_argument("--temporary", action="store_true")
    start.add_argument("--ttl-hours", type=int)
    _json(start)

    promote = subcommands.add_parser("promote", help="Promote a capture to a durable task.")
    _record(promote)
    _json(promote)

    discard = subcommands.add_parser("discard", help="Discard a capture without deleting its history.")
    _record(discard)
    discard.add_argument("--reason", required=True)
    _json(discard)

    shape = subcommands.add_parser("shape", help="Record translated intent and current task shape.")
    _record(shape)
    shape.add_argument("--goal", required=True)
    shape.add_argument("--explicit", action="append")
    shape.add_argument("--fact", action="append")
    shape.add_argument("--default", action="append")
    shape.add_argument("--decision", action="append")
    shape.add_argument("--scope", action="append")
    shape.add_argument("--acceptance", action="append")
    shape.add_argument("--class", dest="classifications", action="append")
    shape.add_argument("--uncertainty", action="append")
    shape.add_argument("--impact", action="append")
    _json(shape)

    classify = subcommands.add_parser("classify", help="Revise mutable scenario labels.")
    _record(classify)
    classify.add_argument("--class", dest="classifications", action="append", required=True)
    classify.add_argument("--reason", required=True)
    _json(classify)

    change = subcommands.add_parser("change", help="Record a requirement change without rewriting history.")
    _record(change)
    change.add_argument("--before", required=True)
    change.add_argument("--after", required=True)
    change.add_argument("--reason", required=True)
    change.add_argument("--actor", choices=("human", "agent"), default="agent")
    _json(change)

    decision = subcommands.add_parser("resolve-decision", help="Resolve one recorded open decision.")
    _record(decision)
    decision.add_argument("--decision", required=True)
    decision.add_argument("--resolution", required=True)
    decision.add_argument("--actor", choices=("human", "agent"), default="human")
    _json(decision)

    condition = subcommands.add_parser("condition", help="Set or clear an execution condition.")
    _record(condition)
    condition.add_argument("--name", required=True, choices=("emergency", "blocked", "waiting", "paused"))
    condition.add_argument("--state", required=True, choices=("active", "cleared"))
    condition.add_argument("--reason", required=True)
    _json(condition)

    transition = subcommands.add_parser("transition", help="Move the universal task lifecycle.")
    _record(transition)
    transition.add_argument("--to", required=True, choices=("shaped", "active", "validating"))
    _json(transition)

    activity = subcommands.add_parser("activity", help="Record a repeatable work activity.")
    _record(activity)
    activity.add_argument(
        "--name",
        required=True,
        choices=("discover", "design", "build", "verify", "review", "ship", "observe", "learn"),
    )
    _json(activity)

    evidence = subcommands.add_parser("add-evidence", help="Attach evidence to acceptance items.")
    _record(evidence)
    evidence.add_argument(
        "--kind",
        required=True,
        choices=("claimed", "host-observed", "command-evidence", "artifact-evidence", "human-confirmed"),
    )
    evidence.add_argument("--summary", required=True)
    evidence.add_argument("--result", required=True, choices=("pass", "fail", "inconclusive"))
    evidence.add_argument("--acceptance", action="append", default=[])
    evidence.add_argument("--reference")
    evidence.add_argument("--confirmation-ref")
    evidence.add_argument(
        "--failure-attribution",
        choices=("code-regression", "pre-existing", "environment-tool", "encoding-presentation", "inconclusive"),
    )
    evidence.add_argument("--actor", choices=("human", "agent", "system"), default="agent")
    _json(evidence)

    permission = subcommands.add_parser("permission", help="Record one exact permission effect and state.")
    _record(permission)
    permission.add_argument("--effect", required=True)
    permission.add_argument(
        "--state", required=True, choices=("requested", "granted", "rejected", "executed")
    )
    permission.add_argument("--actor", choices=("human", "agent", "system"), default="human")
    _json(permission)

    recovery = subcommands.add_parser("recovery", help="Record rollback or recovery information.")
    _record(recovery)
    recovery.add_argument("--summary", required=True)
    _json(recovery)

    close = subcommands.add_parser("close", help="Close a task with an explicit disposition.")
    _record(close)
    close.add_argument(
        "--outcome",
        required=True,
        choices=("completed", "cancelled", "superseded", "unresolved"),
    )
    close.add_argument("--summary", required=True)
    _json(close)

    show = subcommands.add_parser("show", help="Show projected state for one work record.")
    _record(show)
    _json(show)

    render = subcommands.add_parser("render", help="Rebuild a promoted task's Markdown view.")
    _record(render)
    _json(render)

    legacy = subcommands.add_parser("import-legacy", help="Import one legacy card as a reconstructed snapshot.")
    _project(legacy)
    legacy.add_argument("--path", required=True, type=Path)
    _json(legacy)

    doctor = subcommands.add_parser("doctor", help="Check config, schema, and an isolated event round trip.")
    _project(doctor)
    _json(doctor)

    context = subcommands.add_parser("context-check", help="Check the project's three IDC context layers.")
    _project(context)
    _json(context)

    metrics = subcommands.add_parser(
        "metrics", help="Read-only metrics for progressive event records."
    )
    _project(metrics)
    _json(metrics)

    migrate = subcommands.add_parser("migrate", help="Check or explicitly migrate an IDC project.")
    _project(migrate)
    migrate.add_argument("--check", action="store_true", help="Only inspect; never write files.")
    migrate.add_argument("--confirm", action="store_true", help="Write the reviewed migration.")
    _json(migrate)

    learning = subcommands.add_parser("learn-review", help="Review whether a closed task produced durable project knowledge.")
    _record(learning)
    learning.add_argument("--outcome", required=True, choices=("candidate", "none"))
    learning.add_argument("--candidate")
    learning.add_argument("--evidence-ref", action="append", default=[])
    learning.add_argument("--destination", choices=("architecture", "playbook", "skill", "squad", "test", "script"))
    learning.add_argument("--reason")
    learning.add_argument("--actor", choices=("human",), default="human")
    _json(learning)

    disposal = subcommands.add_parser("learn-dispose", help="Accept, reject, defer, or merge a learning candidate.")
    _record(disposal)
    disposal.add_argument("--disposition", required=True, choices=("accepted", "rejected", "deferred", "merged"))
    disposal.add_argument("--reason", required=True)
    disposal.add_argument("--actor", choices=("human",), default="human")
    _json(disposal)

    learning_check = subcommands.add_parser("learn-check", help="Check whether the project learning squad is due.")
    _project(learning_check)
    _json(learning_check)

    learning_session = subcommands.add_parser("learn-session", help="Record a completed project learning squad session.")
    _project(learning_session)
    learning_session.add_argument("--summary", required=True)
    _json(learning_session)


def run_progressive(args: argparse.Namespace) -> int:
    project = args.project.expanduser().resolve()
    if not project.is_dir():
        return _emit(args, {"error": f"project directory does not exist: {project}"}, 2)
    try:
        if args.command == "init":
            report = initialize(project, args.project_key, adapter=args.platform)
        elif args.command == "migrate":
            report = migrate_project(project, check_only=not args.confirm)
            if report.get("status") == "blocked":
                return _emit(args, {"error": "migration blocked", **report}, 3)
        elif args.command == "import-legacy":
            load_config(project)
            report = import_legacy(project, args.path)
        elif args.command == "doctor":
            report = doctor(project)
        elif args.command == "context-check":
            report = inspect_context(project)
            if not report["ready"]:
                return _emit(args, report, 1)
        elif args.command == "learn-check":
            report = check_learning_cadence(project)
        elif args.command == "learn-session":
            load_config(project)
            report = record_learning_session(project, summary=args.summary)
        elif args.command == "metrics":
            if not getattr(args, "json", False):
                return _emit(args, {"error": "metrics requires --json"}, 2)
            report = build_progressive_metrics(project)
        else:
            # Every mutating command must fail before opening the event store when
            # the project is on an incompatible protocol version.
            if args.command not in {"show", "render"}:
                assert_write_compatible(project)
            workflow = Workflow(project)
            if args.command in {"start", "promote", "discard", "shape", "classify", "change", "resolve-decision", "condition", "transition", "activity", "add-evidence", "permission", "recovery", "close", "learn-review", "learn-dispose", "show", "render"}:
                report = run_record_command(args, workflow, load_config, _acceptance_pairs, _pair_values)
    except GateBlocked as exc:
        return _emit(
            args,
            {"error": "gate blocked", "hard_blocks": exc.blocks, "explanations": exc.explanations},
            3,
        )
    except (FileExistsError, FileNotFoundError, KeyError, ValueError, json.JSONDecodeError) as exc:
        return _emit(args, {"error": str(exc)}, 2)
    return _emit(args, report, 0)


def initialize(project: Path, project_key: str, adapter: str = "neutral") -> dict[str, Any]:
    key = project_key.strip().upper()
    if not key or not key.isalnum() or not key[0].isalpha():
        raise ValueError("project_key must start with a letter and contain only letters and digits")
    root = project / ".idc"
    root.mkdir(exist_ok=True)
    config_path = root / "config.json"
    if config_path.exists():
        raise FileExistsError(f"IDC project is already initialized: {config_path}")
    config = {
        "schema_version": CONFIG_SCHEMA_VERSION,
        "idc_version": VERSION,
        "project_key": key,
        "record_policy": "local-private",
        "adapter": adapter,
        "capture_ttl_hours": 72,
    }
    config_path.write_text(json.dumps(config, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    (root / ".gitignore").write_text("*\n!.gitignore\n!config.json\n", encoding="utf-8")
    return config


def load_config(project: Path) -> dict[str, Any]:
    path = project / ".idc" / "config.json"
    if not path.is_file():
        raise FileNotFoundError(f"IDC is not initialized: {path}")
    config = json.loads(path.read_text(encoding="utf-8"))
    if config.get("schema_version") not in {1, CONFIG_SCHEMA_VERSION} or not config.get("project_key"):
        raise ValueError(f"invalid IDC config: {path}")
    ttl = config.get("capture_ttl_hours", 72)
    if not isinstance(ttl, int) or isinstance(ttl, bool) or ttl <= 0:
        raise ValueError(f"invalid capture_ttl_hours in IDC config: {path}")
    config["capture_ttl_hours"] = ttl
    return config


def assert_write_compatible(project: Path) -> dict[str, Any]:
    config = load_config(project)
    if config.get("schema_version") != CONFIG_SCHEMA_VERSION or config.get("idc_version") != VERSION:
        raise ValueError(
            "IDC protocol mismatch: project uses "
            f"schema {config.get('schema_version')} / IDC {config.get('idc_version')}; "
            f"this CLI writes schema {CONFIG_SCHEMA_VERSION} / IDC {VERSION}. "
            "Run `idc migrate --project <path> --check`, review the report, then use --confirm."
        )
    return config


def migrate_project(project: Path, *, check_only: bool = True) -> dict[str, Any]:
    config = load_config(project)
    if config.get("schema_version") == CONFIG_SCHEMA_VERSION and config.get("idc_version") == VERSION:
        return {"status": "current", "writes": [], "schema_version": CONFIG_SCHEMA_VERSION, "idc_version": VERSION}
    if config.get("schema_version") != 1:
        raise ValueError("unsupported config schema; migration report cannot infer a safe mapping")
    records_root = project / ".idc" / "work-items"
    historical_records = []
    for events_path in sorted(records_root.glob("*/events.jsonl")) if records_root.is_dir() else ():
        events = EventStore(project).read(events_path.parent.name)
        historical_records.append(
            {
                "record_id": events_path.parent.name,
                "event_schema": sorted({event.get("schema_version") for event in events}),
                "status": "read-only; no event rewrite",
            }
        )
    if not check_only and historical_records:
        return {
            "status": "blocked",
            "from": {"schema_version": config.get("schema_version"), "idc_version": config.get("idc_version")},
            "to": {"schema_version": CONFIG_SCHEMA_VERSION, "idc_version": VERSION},
            "writes": [],
            "historical_records": historical_records,
            "unresolved": ["historical schema 1 events require explicit record-by-record migration"],
        }
    report = {
        "status": "ready" if check_only else "migrated",
        "from": {"schema_version": config.get("schema_version"), "idc_version": config.get("idc_version")},
        "to": {"schema_version": CONFIG_SCHEMA_VERSION, "idc_version": VERSION},
        "writes": [] if check_only else [".idc/config.json"],
        "historical_records": historical_records or "read-only compatibility; review and migrate in batches",
        "unresolved": [
            "primary type/activity mappings are not inferred automatically",
            "schema 1 event streams are not mixed with schema 2 writes",
        ],
    }
    if not check_only:
        upgraded = dict(config)
        upgraded["schema_version"] = CONFIG_SCHEMA_VERSION
        upgraded["idc_version"] = VERSION
        path = project / ".idc" / "config.json"
        temporary = path.with_suffix(".json.migrating")
        temporary.write_text(json.dumps(upgraded, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        temporary.replace(path)
    return report


def doctor(project: Path) -> dict[str, Any]:
    config = load_config(project)
    schema_resource = importlib.resources.files("idc_core.resources").joinpath(
        "idc-task-event-v1.schema.json"
    )
    schema = json.loads(schema_resource.read_text(encoding="utf-8"))
    Draft202012Validator.check_schema(schema)
    with tempfile.TemporaryDirectory(prefix="idc-doctor-") as temp_dir:
        isolated_project = Path(temp_dir) / "project"
        isolated_project.mkdir()
        store = EventStore(isolated_project)
        record = store.capture("IDC doctor isolated round trip", actor="system")
        event = store.read(record.record_id)[0]
        errors = list(Draft202012Validator(schema).iter_errors(event))
        if errors:
            raise ValueError(f"event schema round trip failed: {errors[0].message}")
    return {
        "status": "pass",
        "project_key": config["project_key"],
        "idc_version": config["idc_version"],
        "supported": {"config_schema": CONFIG_SCHEMA_VERSION, "event_schema": EVENT_SCHEMA_VERSION},
        "checks": {
            "config": True,
            "event_schema": True,
            "event_round_trip": True,
        },
    }


def state_to_dict(state: Any) -> dict[str, Any]:
    result = asdict(state)
    result["conditions"] = sorted(state.conditions)
    return result


def _pairs(values: list[str], label: str, value_name: str) -> list[dict[str, str]]:
    parsed: list[dict[str, str]] = []
    next_id = 1
    used_ids: set[str] = set()
    for value in values:
        if "=" in value:
            key, item = _pair_values([value], label)[0]
        elif ":" in value and label == "acceptance":
            key, item = value.split(":", 1)
            key, item = key.strip(), item.strip()
            if not key or not item:
                raise ValueError(f"{label} must use non-empty ID:VALUE: {value}")
        elif label == "acceptance":
            while f"a-{next_id:03d}" in used_ids:
                next_id += 1
            key, item = f"a-{next_id:03d}", value.strip()
            if not item:
                raise ValueError(f"{label} must not be empty")
        else:
            raise ValueError(f"{label} must use NAME=VALUE: {value}")
        parsed.append({"id": key, value_name: item})
        used_ids.add(key)
        next_id += 1
    return parsed


def _acceptance_pairs(values: list[str], existing: list[dict[str, str]]) -> list[dict[str, str]]:
    """Merge CLI acceptance inputs into the current list without renumbering history."""
    merged = [dict(item) for item in existing]
    by_id = {item.get("id"): index for index, item in enumerate(merged) if item.get("id")}
    next_id = 1
    for value in values:
        if "=" in value:
            key, item = _pair_values([value], "acceptance")[0]
        elif ":" in value:
            key, item = value.split(":", 1)
            key, item = key.strip(), item.strip()
            if not key or not item:
                raise ValueError(f"acceptance must use non-empty ID:VALUE: {value}")
        else:
            item = value.strip()
            if not item:
                raise ValueError("acceptance must not be empty")
            matching = next((entry for entry in merged if entry.get("statement") == item), None)
            if matching:
                continue
            while f"a-{next_id:03d}" in by_id:
                next_id += 1
            key = f"a-{next_id:03d}"
            next_id += 1
        if key in by_id:
            merged[by_id[key]] = {"id": key, "statement": item}
        else:
            by_id[key] = len(merged)
            merged.append({"id": key, "statement": item})
    return merged


def _pair_values(values: list[str], label: str) -> list[tuple[str, str]]:
    parsed: list[tuple[str, str]] = []
    for value in values:
        if "=" not in value:
            raise ValueError(f"{label} must use NAME=VALUE: {value}")
        key, item = value.split("=", 1)
        if not key.strip() or not item.strip():
            raise ValueError(f"{label} must use non-empty NAME=VALUE: {value}")
        parsed.append((key.strip(), item.strip()))
    return parsed


def _emit(args: argparse.Namespace, report: dict[str, Any], code: int) -> int:
    if getattr(args, "json", False):
        print(json.dumps(report, ensure_ascii=False, indent=2) + "\n")
    elif code:
        print(f"ERROR: {report['error']}")
        for block in report.get("hard_blocks", []):
            print(f"- {block}")
    else:
        for key in (
            "record_id", "task_id", "lifecycle", "scenario", "outcome",
            "next_allowed_activity", "current_blockers",
        ):
            if report.get(key) is not None:
                value = report[key]
                if isinstance(value, list):
                    print(f"{key}:")
                    for item in value:
                        print(f"- {item}")
                else:
                    print(f"{key}: {value}")
        if report.get("outstanding_obligations"):
            print("outstanding_obligations:")
            for item in report["outstanding_obligations"]:
                print(f"- {item}")
        for scene in report.get("scenes", []):
            print(f"scene: {scene}")
        for warning in report.get("warnings", []):
            print(f"warning: {warning}")
        card = report.get("card")
        if card:
            print()
            print(card, end="" if card.endswith("\n") else "\n")
    return code


def _project(parser: argparse.ArgumentParser) -> None:
    parser.add_argument("--project", required=True, type=Path)


def _record(parser: argparse.ArgumentParser) -> None:
    _project(parser)
    parser.add_argument("--record", required=True)


def _json(parser: argparse.ArgumentParser) -> None:
    parser.add_argument("--json", action="store_true")
