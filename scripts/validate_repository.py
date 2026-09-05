#!/usr/bin/env python3
"""Validate the public framework structure, links, templates, and Skill metadata."""

from __future__ import annotations

import re
import sys
import json
from pathlib import Path

from validate_contracts import DEFAULT_CONTRACTS, DEFAULT_SCHEMA, validate as validate_contracts
from evaluate_contracts import DEFAULT_RECORDS, evaluate as evaluate_contracts


ROOT = Path(__file__).resolve().parents[1]
REQUIRED_FILES = (
    "README.md",
    "AUTHOR.md",
    "AI_START_HERE.md",
    "QUICKSTART.md",
    "DESIGN.md",
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
    "docs/HOST_ACCEPTANCE.md",
    "docs/MINIMAL.md",
    "docs/TASK_SCENARIOS.md",
    "docs/ORCHESTRATION.md",
    "docs/PLATFORM_ADAPTERS.md",
    "docs/OPENCODE_ADAPTER.md",
    "docs/CLAUDE_CODE_ADAPTER.md",
    "docs/CONTRACTS.md",
    "docs/CLI.md",
    "docs/PERMISSIONS.md",
    "docs/ADAPTATION_GUIDE.md",
    "docs/INSTALLATION.md",
    "plans/CURRENT_STATE.md",
    "plans/ROADMAP.md",
    "plans/PROJECT_PROGRESS.md",
    "references/README.md",
    "references/host-acceptance/README.md",
    "references/host-acceptance/opencode-1.18.5-2026-07-26.md",
    "references/host-acceptance/opencode-1.18.5-controller-2026-07-26.md",
    "references/host-acceptance/claude-code-2.1.154-2026-07-26.md",
    "references/host-acceptance/las-5.2.3-opencode-1.18.5-2026-07-26.md",
    "fixtures/host-acceptance/README.md",
    "fixtures/host-acceptance/AGENTS.md",
    "fixtures/host-acceptance/AI_ENGINEERING_PLAYBOOK.md",
    "fixtures/host-acceptance/SQUADS.md",
    "fixtures/host-acceptance/SQUAD.md",
    "fixtures/host-acceptance/fixture_app.py",
    "fixtures/host-acceptance/tests/test_report.py",
    "fixtures/host-acceptance/tests/test_invoice.py",
    "fixtures/host-acceptance/tests/test_approval.py",
    "fixtures/host-acceptance/opencode.json",
    "templates/AGENT_ENTRY.md",
    "templates/AGENTS.md",
    "templates/AI_ENGINEERING_PLAYBOOK.md",
    "templates/IDC.md",
    "templates/IDC_TASK.md",
    "templates/SQUADS.md",
    "templates/SQUAD.md",
    "templates/opencode/agents/team.md",
    "templates/opencode/agents/architecture.md",
    "templates/opencode/agents/debug.md",
    "templates/opencode/agents/code-review.md",
    "templates/opencode/agents/verify.md",
    "templates/opencode/agents/meta-skill-designer.md",
    "templates/opencode/agents/skill-creator.md",
    "templates/claude/CLAUDE.md",
    "templates/claude/agents/architecture.md",
    "templates/claude/agents/debug.md",
    "templates/claude/agents/code-review.md",
    "templates/claude/agents/verify.md",
    "templates/claude/agents/meta-skill-designer.md",
    "templates/claude/agents/skill-creator.md",
    "skills/team/SKILL.md",
    "skills/architecture/SKILL.md",
    "skills/debug/SKILL.md",
    "skills/code-review/SKILL.md",
    "skills/verify/SKILL.md",
    "skills/meta-skill-designer/SKILL.md",
    "skills/skill-creator/SKILL.md",
    "evals/squad-routing.json",
    "evals/skill-design.json",
    "evals/fixtures/cross-layer-feature.record.json",
    "schemas/intent-driven-coding-contract-v1.schema.json",
    "contracts/examples/cross-layer-feature.squad.json",
    "contracts/examples/cross-layer-feature.evaluation.json",
    "examples/requirement-translations.md",
    "requirements.txt",
    "scripts/bootstrap.py",
    "scripts/audit_skills.py",
    "scripts/validate_project.py",
    "scripts/validate_contracts.py",
    "scripts/evaluate_contracts.py",
    "scripts/orchestrate_squad.py",
    "scripts/idc.py",
    "scripts/prepare_host_acceptance_fixture.py",
    ".claude-plugin/plugin.json",
    ".claude-plugin/marketplace.json",
    "hooks/hooks.json",
    "hooks/run-hook.cmd",
    "hooks/session-start",
    ".opencode/plugins/intent-driven-coding.js",
    ".opencode/INSTALL.md",
)
ALLOWED_TEMPLATE_FILES = {
    Path("templates/AGENT_ENTRY.md"),
    Path("templates/AGENTS.md"),
    Path("templates/AI_ENGINEERING_PLAYBOOK.md"),
    Path("templates/SQUADS.md"),
    Path("templates/SQUAD.md"),
    Path("templates/IDC_TASK.md"),
    Path("templates/claude/CLAUDE.md"),
}
REFERENCE_DIRECTORY = Path("references")
PRIVATE_PATTERNS = (
    ("private IPv4", re.compile(r"\b(?:10\.|192\.168\.|172\.(?:1[6-9]|2\d|3[01])\.)\d{1,3}\.\d{1,3}\b")),
    ("Windows user path", re.compile(r"[A-Za-z]:\\Users\\[^\\\s]+", re.IGNORECASE)),
    ("secret assignment", re.compile(r"(?i)(api[_-]?key|secret|token|password)\s*[:=]\s*['\"][^'\"]{8,}")),
)
OPENCODE_AGENT_MODES = {
    "team": "primary",
    "architecture": "subagent",
    "debug": "subagent",
    "code-review": "subagent",
    "verify": "subagent",
    "meta-skill-designer": "subagent",
    "skill-creator": "subagent",
}
CLAUDE_AGENT_NAMES = (
    "architecture",
    "debug",
    "code-review",
    "verify",
    "meta-skill-designer",
    "skill-creator",
)
LINK_PATTERN = re.compile(r"\[[^\]]+\]\(([^)]+)\)")


# Dependency caches can contain arbitrary third-party Markdown and links. They
# are neither framework source nor generated artifacts we publish, so public
# documentation validation must not recurse through them.
MARKDOWN_EXCLUDED_PARTS = {".git", "node_modules", ".venv", "venv"}


def markdown_files() -> list[Path]:
    return sorted(
        path
        for path in ROOT.rglob("*.md")
        if not any(part in MARKDOWN_EXCLUDED_PARTS for part in path.parts)
    )


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
        if "## Execution Checklist" not in text:
            errors.append(f"{path.relative_to(ROOT)}: missing Execution Checklist section")
        if "<HARD-GATE>" not in text:
            errors.append(f"{path.relative_to(ROOT)}: missing <HARD-GATE> block")

    for name, expected_mode in OPENCODE_AGENT_MODES.items():
        path = ROOT / "templates" / "opencode" / "agents" / f"{name}.md"
        if not path.is_file():
            continue
        text = path.read_text(encoding="utf-8")
        metadata = parse_frontmatter(text)
        if not metadata.get("description"):
            errors.append(f"{path.relative_to(ROOT)}: missing description")
        if metadata.get("mode") != expected_mode:
            errors.append(
                f"{path.relative_to(ROOT)}: mode must be '{expected_mode}'"
            )
        if name == "team" and "permission:" in text:
            errors.append(f"{path.relative_to(ROOT)}: must not override target permissions")
        if name in {"architecture", "code-review", "meta-skill-designer"} and "bash: deny" not in text:
            errors.append(f"{path.relative_to(ROOT)}: must deny Bash")

    for name in CLAUDE_AGENT_NAMES:
        path = ROOT / "templates" / "claude" / "agents" / f"{name}.md"
        if not path.is_file():
            continue
        metadata = parse_frontmatter(path.read_text(encoding="utf-8"))
        if metadata.get("name") != name:
            errors.append(f"{path.relative_to(ROOT)}: name must be '{name}'")
        if not metadata.get("description"):
            errors.append(f"{path.relative_to(ROOT)}: missing description")
        if not metadata.get("tools"):
            errors.append(f"{path.relative_to(ROOT)}: missing tools")

    errors.extend(validate_contracts(DEFAULT_SCHEMA, DEFAULT_CONTRACTS))
    errors.extend(evaluate_contracts(DEFAULT_CONTRACTS, DEFAULT_RECORDS))

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
        if (
            "{{" in text
            and relative not in ALLOWED_TEMPLATE_FILES
            and not relative.is_relative_to(REFERENCE_DIRECTORY)
        ):
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
    print("Note: structural checks do not prove host routing or permission behavior.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
