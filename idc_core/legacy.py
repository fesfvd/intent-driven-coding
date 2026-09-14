from __future__ import annotations

import hashlib
import re
from pathlib import Path
from typing import Any

from .events import EventStore


FIELD_PATTERNS = {
    "legacy_task_id": re.compile(r"^-\s*(?:Task ID|任务 ID):\s*`?([^`\s]+)`?", re.MULTILINE),
    "title": re.compile(r"^-\s*Title:\s*(.+)$", re.MULTILINE),
    "status": re.compile(r"^-\s*Status:\s*`?([^`\r\n]+)`?", re.MULTILINE),
    "scenario": re.compile(r"^-\s*Scenario:\s*`?([^`\r\n]+)`?", re.MULTILINE),
    "current_phase": re.compile(r"^-\s*Current phase:\s*`?([^`\r\n]+)`?", re.MULTILINE),
}


def import_legacy(project: Path, source: Path) -> dict[str, Any]:
    project = project.resolve()
    source = source.resolve()
    try:
        relative = source.relative_to(project)
    except ValueError as exc:
        raise ValueError("legacy task must be inside the project") from exc
    if not source.is_file() or source.suffix.lower() != ".md":
        raise ValueError(f"legacy task is not a Markdown file: {source}")
    text = source.read_text(encoding="utf-8-sig")
    parsed: dict[str, str | None] = {}
    for name, pattern in FIELD_PATTERNS.items():
        match = pattern.search(text)
        parsed[name] = match.group(1).strip() if match else None
    if not parsed["title"]:
        heading = re.search(r"^#\s+(.+)$", text, re.MULTILINE)
        parsed["title"] = heading.group(1).strip() if heading else source.stem
    contradictions: list[str] = []
    if str(parsed["status"]).upper() == "COMPLETE" and re.search(r"^-\s*\[ \]", text, re.MULTILINE):
        contradictions.append("complete-with-unchecked-items")
    payload: dict[str, Any] = {
        **parsed,
        "source": relative.as_posix(),
        "source_sha256": hashlib.sha256(source.read_bytes()).hexdigest(),
        "contradictions": contradictions,
    }
    record = EventStore(project).create_with_event(
        "legacy.snapshot-imported",
        payload,
        actor="system",
        provenance="reconstructed",
    )
    return {"record_id": record.record_id, **payload}

