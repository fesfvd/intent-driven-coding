"""Read-only summaries of progressive IDC event records."""

from __future__ import annotations

import json
from collections import Counter
from datetime import datetime
from pathlib import Path
from typing import Any

from .projector import fold_events


_GATE_BLOCK_TYPES = {
    "gate.blocked",
    "obligation.blocked",
    "check.blocked",
}


def build_progressive_metrics(project: Path) -> dict[str, Any]:
    """Build a deterministic, read-only metrics report for one explicit project."""

    project = project.resolve()
    records_root = project / ".idc" / "work-items"
    event_counts: Counter[str] = Counter()
    records: list[dict[str, Any]] = []
    errors: list[dict[str, str]] = []
    total_requirement_changes = 0
    total_gate_blocks = 0
    gate_blocks_available = False

    if records_root.is_dir():
        paths = sorted(records_root.glob("*/events.jsonl"))
    else:
        paths = []

    for events_path in paths:
        record_id = events_path.parent.name
        try:
            events = _read_events(events_path, record_id)
            state = fold_events(events)
        except (OSError, UnicodeError, ValueError, json.JSONDecodeError) as exc:
            errors.append({"record_id": record_id, "path": str(events_path), "error": str(exc)})
            continue

        counts = Counter(str(event.get("type")) for event in events)
        event_counts.update(counts)
        requirement_changes = counts.get("requirement.changed", 0)
        gate_blocks = _count_gate_blocks(events)
        total_requirement_changes += requirement_changes
        total_gate_blocks += gate_blocks
        if gate_blocks:
            gate_blocks_available = True
        timestamps = [event.get("timestamp") for event in events if isinstance(event.get("timestamp"), str)]
        first_timestamp = timestamps[0] if timestamps else None
        last_timestamp = timestamps[-1] if timestamps else None
        promoted_at = _first_event_timestamp(events, "task.promoted")
        closed_at = _first_event_timestamp(events, "task.closed")
        acceptance_items = list(state.acceptance)
        passing = {
            acceptance_id
            for evidence in state.evidence
            if evidence.get("result") == "pass"
            for acceptance_id in evidence.get("acceptance_ids", [])
        }
        uncompleted_acceptance = sum(
            1 for item in acceptance_items if item.get("id") not in passing
        )
        records.append(
            {
                "record_id": state.record_id,
                "task_id": state.task_id,
                "summary": state.summary,
                "lifecycle": state.lifecycle,
                "outcome": state.outcome,
                "capture_mode": state.capture_mode,
                "capture_disposition": state.capture_disposition,
                "event_count": len(events),
                "event_types": dict(sorted(counts.items())),
                "requirement_changes": requirement_changes,
                "gate_blocks": gate_blocks,
                "first_event_at": first_timestamp,
                "last_event_at": last_timestamp,
                "promoted_at": promoted_at,
                "closed_at": closed_at,
                "capture_to_promote_hours": _elapsed_hours(first_timestamp, promoted_at),
                "acceptance_count": len(acceptance_items),
                "uncompleted_acceptance": uncompleted_acceptance,
                "manual_backfills": counts.get("legacy.snapshot-imported", 0),
            }
        )

    records.sort(key=lambda item: item["record_id"])
    temporary = sum(item["capture_mode"] == "temporary" for item in records)
    durable = sum(item["capture_mode"] == "durable" for item in records)
    promoted = sum(item["task_id"] is not None for item in records)
    discarded = sum(item["capture_disposition"] == "discarded" for item in records)
    expired = sum(item["capture_disposition"] == "expired" for item in records)
    return {
        "project": str(project),
        "scope": ".idc progressive event log only",
        "records": records,
        "errors": errors,
        "totals": {
            "records": len(records),
            "events": sum(item["event_count"] for item in records),
            "temporary_captures": temporary,
            "durable_captures": durable,
            "promoted_tasks": promoted,
            "discarded_captures": discarded,
            "expired_captures": expired,
            "requirement_changes": total_requirement_changes,
            "gate_blocks": total_gate_blocks if gate_blocks_available else None,
            "acceptance_items": sum(item["acceptance_count"] for item in records),
            "uncompleted_acceptance": sum(item["uncompleted_acceptance"] for item in records),
            "manual_backfills": sum(item["manual_backfills"] for item in records),
            "event_types": dict(sorted(event_counts.items())),
        },
        "gate_blocks_available": gate_blocks_available,
        "availability": "available" if records else "unavailable",
    }


def _read_events(path: Path, record_id: str) -> list[dict[str, Any]]:
    events: list[dict[str, Any]] = []
    for line_number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), start=1):
        if not line.strip():
            continue
        event = json.loads(line)
        if not isinstance(event, dict):
            raise ValueError(f"{path}:{line_number}: event must be an object")
        if event.get("record_id") != record_id:
            raise ValueError(f"{path}:{line_number}: record_id mismatch")
        events.append(event)
    return events


def _first_event_timestamp(events: list[dict[str, Any]], event_type: str) -> str | None:
    for event in events:
        if event.get("type") == event_type and isinstance(event.get("timestamp"), str):
            return event["timestamp"]
    return None


def _elapsed_hours(start: str | None, end: str | None) -> float | None:
    if not start or not end:
        return None
    try:
        delta = datetime.fromisoformat(end) - datetime.fromisoformat(start)
    except (TypeError, ValueError):
        return None
    return round(delta.total_seconds() / 3600, 3)


def _count_gate_blocks(events: list[dict[str, Any]]) -> int:
    count = 0
    for event in events:
        event_type = event.get("type")
        payload = event.get("payload")
        if event_type in _GATE_BLOCK_TYPES or (
            isinstance(event_type, str)
            and event_type.endswith(".blocked")
            and (event_type.startswith("x.") or event_type in _GATE_BLOCK_TYPES)
        ):
            count += 1
        elif isinstance(payload, dict) and isinstance(payload.get("hard_blocks"), list):
            count += len(payload["hard_blocks"])
    return count


# Short alias for callers that do not need to distinguish progressive metrics
# from the legacy metadata portfolio report.
build_metrics = build_progressive_metrics
