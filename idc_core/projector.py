from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Iterable
from datetime import datetime, timezone


@dataclass
class TaskState:
    record_id: str
    task_id: str | None = None
    summary: str = ""
    lifecycle: str = "captured"
    outcome: str | None = None
    goal: str = ""
    explicit: list[str] = field(default_factory=list)
    repository_facts: list[str] = field(default_factory=list)
    proposed_defaults: list[str] = field(default_factory=list)
    open_decisions: list[str] = field(default_factory=list)
    decisions: list[dict[str, Any]] = field(default_factory=list)
    scope: list[str] = field(default_factory=list)
    acceptance: list[dict[str, str]] = field(default_factory=list)
    uncertainty: list[str] = field(default_factory=list)
    classifications: list[str] = field(default_factory=list)
    classification_history: list[dict[str, Any]] = field(default_factory=list)
    requirement_changes: list[dict[str, Any]] = field(default_factory=list)
    impacts: dict[str, str] = field(default_factory=dict)
    permissions: dict[str, str] = field(default_factory=dict)
    recovery: str | None = None
    conditions: set[str] = field(default_factory=set)
    evidence: list[dict[str, Any]] = field(default_factory=list)
    activities: list[str] = field(default_factory=list)
    events: list[dict[str, Any]] = field(default_factory=list)
    legacy_snapshot: dict[str, Any] | None = None
    capture_mode: str = "durable"
    expires_at: str | None = None
    capture_disposition: str = "open"


def fold_events(events: Iterable[dict[str, Any]], *, now: datetime | None = None) -> TaskState:
    materialized = list(events)
    if not materialized:
        raise ValueError("at least one event is required")
    record_id = materialized[0].get("record_id")
    if not isinstance(record_id, str):
        raise ValueError("event record_id is required")
    state = TaskState(record_id=record_id)
    for expected_seq, event in enumerate(materialized):
        if event.get("record_id") != record_id or event.get("seq") != expected_seq:
            raise ValueError("events must have one record_id and contiguous sequence numbers")
        payload = event.get("payload")
        if not isinstance(payload, dict):
            raise ValueError("event payload must be an object")
        event_type = event.get("type")
        state.events.append(event)
        if event_type == "request.captured":
            state.summary = str(payload.get("summary", ""))
            state.capture_mode = str(payload.get("capture_mode", "durable"))
            state.expires_at = payload.get("expires_at")
        elif event_type == "task.promoted":
            state.task_id = str(payload["task_id"])
            state.capture_disposition = "promoted"
        elif event_type == "capture.discarded":
            state.capture_disposition = "discarded"
        elif event_type == "capture.expired":
            state.capture_disposition = "expired"
        elif event_type == "intent.translated":
            state.goal = str(payload.get("goal", ""))
            state.explicit = list(payload.get("explicit") or [])
            state.repository_facts = list(payload.get("repository_facts") or [])
            state.proposed_defaults = list(payload.get("proposed_defaults") or [])
            state.open_decisions = list(payload.get("open_decisions") or [])
        elif event_type == "scope.changed":
            state.scope = list(payload.get("to") or [])
        elif event_type == "acceptance.changed":
            state.acceptance = list(payload.get("to") or [])
        elif event_type == "uncertainty.changed":
            state.uncertainty = list(payload.get("to") or [])
        elif event_type == "classification.changed":
            state.classifications = list(payload.get("to") or [])
            state.classification_history.append(dict(payload))
        elif event_type == "lifecycle.changed":
            state.lifecycle = str(payload["to"])
        elif event_type == "requirement.changed":
            state.requirement_changes.append(dict(payload))
            if state.lifecycle in {"active", "validating"}:
                state.lifecycle = "shaped"
        elif event_type == "impact.assessed":
            state.impacts.update(payload.get("dimensions") or {})
        elif event_type == "permission.requested":
            state.permissions[str(payload["effect"])] = "requested"
        elif event_type == "permission.granted":
            state.permissions[str(payload["effect"])] = "granted"
        elif event_type == "permission.rejected":
            state.permissions[str(payload["effect"])] = "rejected"
        elif event_type == "permission.executed":
            state.permissions[str(payload["effect"])] = "executed"
        elif event_type == "recovery.recorded":
            state.recovery = str(payload["summary"])
        elif event_type == "condition.changed":
            name = str(payload["name"])
            if payload.get("active"):
                state.conditions.add(name)
            else:
                state.conditions.discard(name)
        elif event_type == "evidence.recorded":
            state.evidence.append(dict(payload))
        elif event_type == "activity.recorded":
            state.activities.append(str(payload["name"]))
        elif event_type == "decision.resolved":
            decision = str(payload["decision"])
            state.open_decisions = [item for item in state.open_decisions if item != decision]
            state.decisions.append(dict(payload))
        elif event_type == "task.closed":
            state.lifecycle = "closed"
            state.outcome = str(payload["outcome"])
        elif event_type == "legacy.snapshot-imported":
            state.legacy_snapshot = dict(payload)
            state.summary = str(payload.get("title", "Legacy task snapshot"))
    if state.capture_mode == "temporary" and state.capture_disposition == "open" and state.expires_at:
        expires = datetime.fromisoformat(state.expires_at)
        if expires <= (now or datetime.now(timezone.utc)):
            state.capture_disposition = "expired"
    return state
