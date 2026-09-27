"""Rebuildable summary index for progressive task event streams."""

from __future__ import annotations

import json
import os
import tempfile
from collections import Counter
from pathlib import Path
from typing import Any


INDEX_VERSION = 1


def index_path(project: Path) -> Path:
    return project.resolve() / ".idc" / "index" / "tasks.json"


def load_index(project: Path) -> dict[str, Any] | None:
    path = index_path(project)
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError):
        return None
    if not isinstance(value, dict) or value.get("version") != INDEX_VERSION:
        return None
    records = value.get("records")
    return value if isinstance(records, dict) else None


def save_index(project: Path, index: dict[str, Any]) -> None:
    path = index_path(project)
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, temporary = tempfile.mkstemp(prefix="tasks-", suffix=".json", dir=path.parent)
    try:
        with os.fdopen(fd, "w", encoding="utf-8", newline="\n") as stream:
            json.dump(index, stream, ensure_ascii=False, indent=2, sort_keys=True)
            stream.write("\n")
            stream.flush()
            os.fsync(stream.fileno())
        Path(temporary).replace(path)
    finally:
        if os.path.exists(temporary):
            os.unlink(temporary)


def empty_index() -> dict[str, Any]:
    return {"version": INDEX_VERSION, "records": {}}


def update_index(project: Path, event: dict[str, Any]) -> None:
    index = load_index(project) or empty_index()
    record_id = event["record_id"]
    record = index["records"].setdefault(record_id, _empty_record(record_id))
    _apply_event(record, event)
    save_index(project, index)


def rebuild_index(project: Path) -> dict[str, Any]:
    index = empty_index()
    root = project.resolve() / ".idc" / "work-items"
    if root.is_dir():
        for path in sorted(root.glob("*/events.jsonl")):
            try:
                lines = path.read_text(encoding="utf-8").splitlines()
                for line in lines:
                    if line.strip():
                        event = json.loads(line)
                        if isinstance(event, dict):
                            record_id = event.get("record_id")
                            if isinstance(record_id, str):
                                record = index["records"].setdefault(record_id, _empty_record(record_id))
                                _apply_event(record, event)
            except (OSError, UnicodeError, json.JSONDecodeError):
                continue
    save_index(project, index)
    return index


def get_index(project: Path) -> dict[str, Any]:
    return load_index(project) or rebuild_index(project)


def _empty_record(record_id: str) -> dict[str, Any]:
    return {
        "record_id": record_id, "task_id": None, "summary": "", "lifecycle": "captured",
        "outcome": None, "capture_mode": "durable", "capture_disposition": "open",
        "event_count": 0, "event_types": {}, "first_event_at": None, "last_event_at": None,
        "promoted_at": None, "closed_at": None, "requirement_changes": 0, "gate_blocks": 0,
        "acceptance": [], "passing_acceptance": [], "manual_backfills": 0,
    }


def _apply_event(record: dict[str, Any], event: dict[str, Any]) -> None:
    event_type = event.get("type")
    payload = event.get("payload") if isinstance(event.get("payload"), dict) else {}
    timestamp = event.get("timestamp")
    record["event_count"] += 1
    record["event_types"][str(event_type)] = record["event_types"].get(str(event_type), 0) + 1
    if record["first_event_at"] is None and isinstance(timestamp, str):
        record["first_event_at"] = timestamp
    if isinstance(timestamp, str):
        record["last_event_at"] = timestamp
    if event_type == "request.captured":
        record["summary"] = str(payload.get("summary", ""))
        record["capture_mode"] = str(payload.get("capture_mode", "durable"))
    elif event_type == "task.promoted":
        record["task_id"] = payload.get("task_id")
        record["promoted_at"] = timestamp
        record["capture_disposition"] = "promoted"
        record["lifecycle"] = "promoted"
    elif event_type == "capture.discarded":
        record["capture_disposition"] = "discarded"
    elif event_type == "capture.expired":
        record["capture_disposition"] = "expired"
    elif event_type == "lifecycle.changed":
        record["lifecycle"] = payload.get("to", record["lifecycle"])
    elif event_type == "task.closed":
        record["lifecycle"] = "closed"
        record["outcome"] = payload.get("outcome")
        record["closed_at"] = timestamp
    elif event_type == "requirement.changed":
        record["requirement_changes"] += 1
    elif event_type == "acceptance.changed":
        record["acceptance"] = list(payload.get("to") or [])
    elif event_type == "evidence.recorded" and payload.get("result") == "pass":
        record["passing_acceptance"] = sorted(set(record["passing_acceptance"]) | set(payload.get("acceptance_ids") or []))
    elif event_type == "legacy.snapshot-imported":
        record["manual_backfills"] += 1
    if event_type in {"gate.blocked", "obligation.blocked", "check.blocked"}:
        record["gate_blocks"] += 1
    elif isinstance(payload.get("hard_blocks"), list):
        record["gate_blocks"] += len(payload["hard_blocks"])


def record_metrics(record: dict[str, Any]) -> dict[str, Any]:
    acceptance = record.get("acceptance", [])
    passing = set(record.get("passing_acceptance", []))
    counts = Counter(record.get("event_types", {}))
    return {
        "record_id": record["record_id"], "task_id": record["task_id"], "summary": record["summary"],
        "lifecycle": record["lifecycle"], "outcome": record["outcome"], "capture_mode": record["capture_mode"],
        "capture_disposition": record["capture_disposition"], "event_count": record["event_count"],
        "event_types": dict(sorted(counts.items())), "requirement_changes": record["requirement_changes"],
        "gate_blocks": record["gate_blocks"], "first_event_at": record["first_event_at"],
        "last_event_at": record["last_event_at"], "promoted_at": record["promoted_at"],
        "closed_at": record["closed_at"], "acceptance_count": len(acceptance),
        "uncompleted_acceptance": sum(1 for item in acceptance if item.get("id") not in passing),
        "capture_to_promote_hours": _elapsed_hours(record["first_event_at"], record["promoted_at"]),
        "manual_backfills": record["manual_backfills"],
    }


def _elapsed_hours(start: str | None, end: str | None) -> float | None:
    if not start or not end:
        return None
    try:
        from datetime import datetime
        delta = datetime.fromisoformat(end) - datetime.fromisoformat(start)
    except (TypeError, ValueError):
        return None
    return round(delta.total_seconds() / 3600, 3)
