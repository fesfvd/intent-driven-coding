#!/usr/bin/env python3
"""Validate the public framework structure, links, templates, and Skill metadata."""

from __future__ import annotations

import re
import sys
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
REQUIRED_FILES = (
    "README.md",
    "AUTHOR.md",
    "AI_START_HERE.md",
    "QUICKSTART.md",
    "LICENSE",
    "docs/PROTOCOL.md",
    "docs/CONTEXT_ARCHITECTURE.md",
    "docs/TEAM_PLAYBOOK.md",
    "docs/SQUAD_METHOD.md",
    "docs/SQUAD_WORKSHOP.md",
    "docs/CAPABILITY_TIERS.md",
    "docs/PROJECT_ARCHETYPES.md",
    "docs/SQUAD_CATALOG.md",
    "docs/EVALUATION.md",
    "docs/PLATFORM_ADAPTERS.md",
    "docs/PERMISSIONS.md",
    "docs/ADAPTATION_GUIDE.md",
    "templates/AGENT_ENTRY.md",
    "templates/AGENTS.md",
    "templates/AI_ENGINEERING_PLAYBOOK.md",
    "templates/SQUADS.md",
    "templates/SQUAD.md",
    "skills/team/SKILL.md",
    "skills/architecture/SKILL.md",
    "skills/debug/SKILL.md",
    "skills/code-review/SKILL.md",
    "skills/verify/SKILL.md",
    "skills/meta-skill-designer/SKILL.md",
    "skills/skill-creator/SKILL.md",
    "evals/squad-routing.json",
    "evals/skill-design.json",
    "examples/requirement-translations.md",
    "scripts/bootstrap.py",
    "scripts/audit_skills.py",
    "scripts/validate_project.py",
)
ALLOWED_TEMPLATE_FILES = {
    Path("templates/AGENT_ENTRY.md"),
    Path("templates/AGENTS.md"),
    Path("templates/AI_ENGINEERING_PLAYBOOK.md"),
    Path("templates/SQUADS.md"),
    Path("templates/SQUAD.md"),
}
PRIVATE_PATTERNS = (
    ("private IPv4", re.compile(r"\b(?:10\.|192\.168\.|172\.(?:1[6-9]|2\d|3[01])\.)\d{1,3}\.\d{1,3}\b")),
    ("Windows user path", re.compile(r"[A-Za-z]:\\Users\\[^\\\s]+", re.IGNORECASE)),
    ("secret assignment", re.compile(r"(?i)(api[_-]?key|secret|token|password)\s*[:=]\s*['\"][^'\"]{8,}")),
)
LINK_PATTERN = re.compile(r"\[[^\]]+\]\(([^)]+)\)")


def markdown_files() -> list[Path]:
    return sorted(path for path in ROOT.rglob("*.md") if ".git" not in path.parts)


def parse_frontmatter(text: str) -> dict[str, str]:
    if not text.startswith("---\n"):
        return {}
    end = text.find("\n---\n", 4)
    if end == -1:
        return {}
    result: dict[str, str] = {}
    for line in text[4:end].splitlines():
        if ":" in line and not line.startswith((" ", "\t")):
            key, value = line.split(":", 1)
            result[key.strip()] = value.strip()
    return result


def validate() -> list[str]:
    errors: list[str] = []

    for relative in REQUIRED_FILES:
        if not (ROOT / relative).is_file():
            errors.append(f"Missing required file: {relative}")

    for path in sorted((ROOT / "skills").glob("*/SKILL.md")):
        text = path.read_text(encoding="utf-8")
        metadata = parse_frontmatter(text)
        expected_name = path.parent.name
        if metadata.get("name") != expected_name:
            errors.append(f"{path.relative_to(ROOT)}: name must be '{expected_name}'")
        if not metadata.get("description"):
            errors.append(f"{path.relative_to(ROOT)}: missing description")
        if "allowed-tools" not in metadata:
            errors.append(f"{path.relative_to(ROOT)}: missing allowed-tools")
        if "## Example Triggers" not in text:
            errors.append(f"{path.relative_to(ROOT)}: missing Example Triggers section")
        if "## Safety Statement" not in text:
            errors.append(f"{path.relative_to(ROOT)}: missing Safety Statement section")

    known_skills = {path.parent.name for path in (ROOT / "skills").glob("*/SKILL.md")}
    for path in sorted((ROOT / "evals").glob("*.json")):
        try:
            payload = json.loads(path.read_text(encoding="utf-8"))
        except json.JSONDecodeError as exc:
            errors.append(f"{path.relative_to(ROOT)}: invalid JSON ({exc})")
            continue
        if payload.get("schema_version") != 1:
            errors.append(f"{path.relative_to(ROOT)}: unsupported or missing schema_version")
        cases = payload.get("cases")
        if not isinstance(cases, list) or not cases:
            errors.append(f"{path.relative_to(ROOT)}: cases must be a non-empty list")
            continue
        for case in cases:
            if not case.get("id") or not case.get("prompt"):
                errors.append(f"{path.relative_to(ROOT)}: every case needs id and prompt")
            for member in case.get("expected_squad", []):
                if member.startswith("project-specific-"):
                    continue
                if member not in known_skills:
                    errors.append(
                        f"{path.relative_to(ROOT)}: case '{case.get('id')}' references unknown Skill '{member}'"
                    )

    for path in markdown_files():
        relative = path.relative_to(ROOT)
        text = path.read_text(encoding="utf-8")
        if "{{" in text and relative not in ALLOWED_TEMPLATE_FILES:
            errors.append(f"{relative}: unresolved template token outside templates/")
        for label, pattern in PRIVATE_PATTERNS:
            if pattern.search(text):
                errors.append(f"{relative}: possible {label}")
        for target in LINK_PATTERN.findall(text):
            if target.startswith(("http://", "https://", "mailto:", "#", "<")):
                continue
            link_path = target.split("#", 1)[0]
            if not link_path:
                continue
            destination = (path.parent / link_path).resolve()
            if not destination.exists():
                errors.append(f"{relative}: broken local link '{target}'")

    return errors


def main() -> int:
    errors = validate()
    if errors:
        print("Repository validation failed:")
        for error in errors:
            print(f"- {error}")
        return 1
    print(f"Repository validation passed ({len(REQUIRED_FILES)} required files, {len(markdown_files())} Markdown files).")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
