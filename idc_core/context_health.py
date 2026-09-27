from __future__ import annotations

from pathlib import Path
from typing import Any


def inspect_context(project: Path) -> dict[str, Any]:
    project = project.resolve()
    persistent = _persistent_entry(project)
    methods = _on_demand_methods(project)
    evidence = _task_evidence(project)
    layers = {
        "persistent_entry": persistent,
        "on_demand_methods": methods,
        "task_evidence": evidence,
    }
    return {"ready": all(item["status"] == "ready" for item in layers.values()), "layers": layers}


def _persistent_entry(project: Path) -> dict[str, Any]:
    entry_paths = [project / "IDC.md", project / "AGENTS.md", project / "CLAUDE.md"]
    existing = [path.name for path in entry_paths if _usable(path)]
    if not existing:
        return {"status": "missing", "paths": [path.name for path in entry_paths]}
    return {"status": "ready", "paths": existing}


def _on_demand_methods(project: Path) -> dict[str, Any]:
    required = [project / "AI_ENGINEERING_PLAYBOOK.md", project / "SQUADS.md"]
    skill_dirs = [project / ".agents" / "skills", project / ".opencode" / "skills", project / ".claude" / "skills"]
    existing = [path.name for path in required if _usable(path)]
    skill_dir = next((path for path in skill_dirs if path.is_dir()), None)
    if skill_dir:
        existing.append(str(skill_dir.relative_to(project)))
    if len(existing) < 3:
        return {"status": "missing", "paths": existing, "required": [path.name for path in required]}
    return {"status": "ready", "paths": existing}


def _task_evidence(project: Path) -> dict[str, Any]:
    idc = project / ".idc"
    required = [idc / "config.json", idc / "work-items", idc / "tasks"]
    existing = [str(path.relative_to(project)) for path in required if path.exists()]
    if len(existing) != len(required):
        return {"status": "missing", "paths": existing}
    return {"status": "ready", "paths": existing}


def _usable(path: Path) -> bool:
    if not path.is_file():
        return False
    try:
        text = path.read_text(encoding="utf-8")
    except (OSError, UnicodeError):
        return False
    return bool(text.strip()) and "{{" not in text
