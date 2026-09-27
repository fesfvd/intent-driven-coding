from __future__ import annotations

import json
import os
import tempfile
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from .task_index import get_index


DEFAULT_THRESHOLD = 5
DEFAULT_MAX_DAYS = 14


def check_learning_cadence(project: Path, *, now: datetime | None = None) -> dict[str, Any]:
    project = project.resolve()
    current = _ensure_aware(now or datetime.now(timezone.utc))
    config = _read_json(project / ".idc" / "config.json")
    learning = config.get("learning") if isinstance(config.get("learning"), dict) else {}
    threshold = _positive_int(learning.get("completed_task_threshold"), DEFAULT_THRESHOLD)
    max_days = _positive_int(learning.get("max_days"), DEFAULT_MAX_DAYS)
    state = _read_json(project / ".idc" / "learning-state.json")
    last_review = _parse_time(state.get("last_review_at"))
    completed = _completed_tasks(project)
    completed_since = [item for item in completed if last_review is None or item < last_review]
    age_days = (current - last_review).days if last_review else None
    if not completed_since:
        status = "quiet"
        reason = "no completed work since the last review"
    elif len(completed_since) >= threshold:
        status = "due"
        reason = f"completed task threshold reached ({len(completed_since)} >= {threshold})"
    elif age_days is not None and age_days >= max_days:
        status = "due"
        reason = f"review window elapsed ({age_days} >= {max_days} days)"
    else:
        status = "quiet"
        reason = "review window has not opened"
    return {
        "status": status,
        "reason": reason,
        "completed_since_review": len(completed_since),
        "completed_total": len(completed),
        "threshold": threshold,
        "max_days": max_days,
        "last_review_at": state.get("last_review_at"),
        "suggested_squad": "learning-curator" if status == "due" else None,
    }


def record_learning_session(project: Path, *, now: datetime | None = None, summary: str) -> dict[str, Any]:
    if not summary.strip():
        raise ValueError("learning session summary must not be empty")
    current = _ensure_aware(now or datetime.now(timezone.utc))
    path = project.resolve() / ".idc" / "learning-state.json"
    path.parent.mkdir(parents=True, exist_ok=True)
    previous = _read_json(path)
    state = {
        "last_review_at": current.isoformat(),
        "summary": summary.strip(),
        "session_count": (
            previous.get("session_count", 0)
            if isinstance(previous.get("session_count", 0), int)
            and not isinstance(previous.get("session_count", 0), bool)
            and previous.get("session_count", 0) >= 0
            else 0
        ) + 1,
        "previous_review_at": previous.get("last_review_at"),
    }
    fd, temporary = tempfile.mkstemp(prefix="learning-state-", suffix=".json", dir=path.parent)
    try:
        with os.fdopen(fd, "w", encoding="utf-8", newline="\n") as stream:
            stream.write(json.dumps(state, ensure_ascii=False, indent=2) + "\n")
            stream.flush()
            os.fsync(stream.fileno())
        Path(temporary).replace(path)
    finally:
        if os.path.exists(temporary):
            os.unlink(temporary)
    return {"status": "recorded", **state}


def _completed_tasks(project: Path) -> list[datetime]:
    indexed = get_index(project)
    if indexed is not None:
        return sorted(
            timestamp for record in indexed["records"].values()
            if record.get("outcome") == "completed"
            for timestamp in [_parse_time(record.get("closed_at"))]
            if timestamp is not None
        )
    result: list[datetime] = []
    root = project / ".idc" / "work-items"
    if not root.is_dir():
        return result
    for path in root.glob("*/events.jsonl"):
        try:
            events = [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]
        except (OSError, json.JSONDecodeError):
            continue
        for event in events:
            if event.get("type") == "task.closed" and event.get("payload", {}).get("outcome") == "completed":
                timestamp = _parse_time(event.get("timestamp"))
                if timestamp:
                    result.append(timestamp)
                break
    return sorted(result)


def _read_json(path: Path) -> dict[str, Any]:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {}
    return value if isinstance(value, dict) else {}


def _parse_time(value: Any) -> datetime | None:
    if not isinstance(value, str):
        return None
    try:
        return _ensure_aware(datetime.fromisoformat(value))
    except ValueError:
        return None


def _ensure_aware(value: datetime) -> datetime:
    return value.astimezone(timezone.utc) if value.tzinfo else value.replace(tzinfo=timezone.utc)


def _positive_int(value: Any, fallback: int) -> int:
    return value if isinstance(value, int) and not isinstance(value, bool) and value > 0 else fallback
