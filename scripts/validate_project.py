#!/usr/bin/env python3
"""Validate an installed Intent-Driven Coding project without modifying it."""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path


COMMON_REQUIRED_FILES = (
    Path("AGENTS.md"),
    Path("AI_ENGINEERING_PLAYBOOK.md"),
    Path("SQUADS.md"),
)
PLATFORM_REQUIRED_FILES = {
    "neutral": (Path(".agent/AGENT_ENTRY.md"),),
    "opencode": (Path(".opencode/templates/SQUAD.md"),),
    "claude-code": (Path(".claude/CLAUDE.md"), Path(".claude/templates/SQUAD.md")),
}
PLATFORM_SKILL_ROOTS = {
    "neutral": Path(".agent/skills"),
    "opencode": Path(".opencode/skills"),
    "claude-code": Path(".claude/skills"),
}
PLATFORM_EVAL_ROOTS = {
    "neutral": Path(".agent/evals"),
    "opencode": Path(".opencode/evals"),
    "claude-code": Path(".claude/evals"),
}
PLATFORM_FRAMEWORK_ROOTS = {
    "neutral": Path(".agent"),
    "opencode": Path(".opencode"),
    "claude-code": Path(".claude"),
}
OPENCODE_AGENT_MODES = {
    "team": "primary",
    "architecture": "subagent",
    "debug": "subagent",
    "code-review": "subagent",
    "verify": "subagent",
    "meta-skill-designer": "subagent",
    "skill-creator": "subagent",
}
OPENCODE_AGENT_REQUIRED_PERMISSIONS = {
    "architecture": {"edit": "deny", "bash": "deny", "task": "deny"},
    "debug": {"edit": "deny", "task": "deny"},
    "code-review": {"edit": "deny", "bash": "deny", "task": "deny"},
    "verify": {"edit": "deny", "task": "deny"},
    "meta-skill-designer": {"edit": "deny", "bash": "deny", "task": "deny"},
    "skill-creator": {"task": "deny"},
}
OPENCODE_SKILL_NAME = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
OPENCODE_COMPATIBLE_SKILL_ROOTS = (
    Path(".claude/skills"),
    Path(".agents/skills"),
)
OPENCODE_ANCESTOR_SKILL_ROOT = Path(".opencode/skills")
CLAUDE_AGENT_NAMES = (
    "architecture",
    "debug",
    "code-review",
    "verify",
    "meta-skill-designer",
    "skill-creator",
)
CLAUDE_AGENT_TOOLS = {
    "architecture": {"Read", "Grep", "Glob", "Skill"},
    "debug": {"Read", "Grep", "Glob", "Bash", "Skill"},
    "code-review": {"Read", "Grep", "Glob", "Skill"},
    "verify": {"Read", "Grep", "Glob", "Bash", "Skill"},
    "meta-skill-designer": {"Read", "Grep", "Glob", "Skill"},
    "skill-creator": {"Read", "Grep", "Glob", "Edit", "Write", "Skill"},
}
PLATFORM_REQUIRED_SKILLS = {
    "neutral": ("team",),
    "opencode": ("team",),
    "claude-code": ("team",),
}
PLACEHOLDER = re.compile(r"\{\{[^{}]+\}\}")
SQUAD_MEMBERS = re.compile(r"\|\s*Members\s*\|\s*([^|]+)\|", re.IGNORECASE)
PRIVATE_PATTERNS = (
    ("本机用户路径", re.compile(r"[A-Za-z]:\\Users\\[^\\\s]+", re.IGNORECASE)),
    ("私有 IPv4", re.compile(r"\b(?:10\.|192\.168\.|172\.(?:1[6-9]|2\d|3[01])\.)\d{1,3}\.\d{1,3}\b")),
    ("疑似密钥赋值", re.compile(r"(?i)(api[_-]?key|secret|token|password)\s*[:=]\s*['\"][^'\"]{8,}")),
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="检查已安装的 Intent-Driven Coding 项目配置。")
    parser.add_argument("--target", required=True, type=Path, help="目标项目目录")
    parser.add_argument(
        "--platform",
        choices=("neutral", "opencode", "claude-code"),
        default="neutral",
        help="已安装的框架布局",
    )
    return parser.parse_args()


def parse_frontmatter(text: str) -> dict[str, str]:
    if not text.startswith("---\n"):
        return {}
    end = text.find("\n---\n", 4)
    if end == -1:
        return {}
    values: dict[str, str] = {}
    for line in text[4:end].splitlines():
        if ":" in line and not line.startswith((" ", "\t")):
            key, value = line.split(":", 1)
            value = value.strip()
            if len(value) >= 2 and value[0] == value[-1] and value[0] in {"'", '"'}:
                value = value[1:-1]
            values[key.strip()] = value
    return values


def has_frontmatter_permission(text: str, name: str, value: str) -> bool:
    end = text.find("\n---\n", 4)
    if not text.startswith("---\n") or end == -1:
        return False
    return bool(re.search(rf"(?m)^  {re.escape(name)}:\s*{re.escape(value)}\s*$", text[4:end]))


def opencode_permission_entries(text: str) -> tuple[dict[str, str], bool]:
    end = text.find("\n---\n", 4)
    if not text.startswith("---\n") or end == -1:
        return {}, False
    lines = text[4:end].splitlines()
    for index, line in enumerate(lines):
        if not line.startswith("permission:"):
            continue
        if line != "permission:":
            return {}, False
        entries: dict[str, str] = {}
        for entry in lines[index + 1:]:
            if not entry.startswith("  "):
                break
            match = re.fullmatch(r"  ([a-z]+): ([a-z]+)", entry)
            if match is None or match.group(1) in entries:
                return entries, False
            entries[match.group(1)] = match.group(2)
        return entries, True
    return {}, True


def opencode_search_roots(target: Path) -> list[Path]:
    current = target
    while not (current / ".git").exists():
        if current.parent == current:
            return [target]
        current = current.parent
    roots = [target]
    while roots[-1] != current:
        roots.append(roots[-1].parent)
    return roots


def collect_skills(
    target: Path, skill_root: Path, require_opencode_names: bool, use_directory_names: bool
) -> tuple[set[str], list[str]]:
    skills: set[str] = set()
    errors: list[str] = []
    for path in sorted((target / skill_root).glob("*/SKILL.md")):
        text = path.read_text(encoding="utf-8")
        metadata = parse_frontmatter(text)
        name = path.parent.name if use_directory_names else metadata.get("name")
        if not name:
            errors.append(f"{path.relative_to(target)} 缺少 frontmatter name")
            continue
        if require_opencode_names:
            if name != path.parent.name:
                errors.append(
                    f"{path.relative_to(target)} frontmatter name 必须与目录名 {path.parent.name} 一致"
                )
            if not OPENCODE_SKILL_NAME.fullmatch(name):
                errors.append(f"{path.relative_to(target)} name 不符合 OpenCode 命名规则: {name}")
            if not 1 <= len(name) <= 64:
                errors.append(f"{path.relative_to(target)} name 长度必须为 1-64: {len(name)}")
            description = metadata.get("description", "")
            if not 1 <= len(description) <= 1024:
                errors.append(
                    f"{path.relative_to(target)} description 长度必须为 1-1024: {len(description)}"
                )
        if name in skills:
            errors.append(f"Skill 名称重复: {name}")
        skills.add(name)
        if not metadata.get("description"):
            errors.append(f"{path.relative_to(target)} 缺少 description")
        if "## Safety Statement" not in text:
            errors.append(f"{path.relative_to(target)} 缺少 Safety Statement")
    if not skills:
        errors.append(".agent/skills/ 下没有找到 Skill")
    return skills, errors


def validate_opencode_skill_collisions(target: Path, skills: set[str]) -> list[str]:
    errors: list[str] = []
    for root in opencode_search_roots(target):
        skill_roots = OPENCODE_COMPATIBLE_SKILL_ROOTS
        if root != target:
            skill_roots = (*skill_roots, OPENCODE_ANCESTOR_SKILL_ROOT)
        for skill_root in skill_roots:
            for name in skills:
                path = root / skill_root / name / "SKILL.md"
                if path.is_file():
                    errors.append(f"OpenCode 兼容 Skill 路径冲突: {path}")
    return errors


def validate_opencode_agents(target: Path, skills: set[str]) -> list[str]:
    errors: list[str] = []
    agent_root = target / ".opencode" / "agents"
    for name, expected_mode in OPENCODE_AGENT_MODES.items():
        path = agent_root / f"{name}.md"
        if name != "team" and name not in skills:
            if path.is_file():
                errors.append(f"{path.relative_to(target)} Agent requires matching Skill: {name}")
            continue
        if not path.is_file():
            errors.append(f"缺少 OpenCode Agent: {path.relative_to(target)}")
            continue
        text = path.read_text(encoding="utf-8")
        metadata = parse_frontmatter(text)
        for field in sorted(set(metadata) - {"description", "mode", "permission"}):
            errors.append(f"{path.relative_to(target)} unexpected frontmatter field: {field}")
        if not metadata.get("description"):
            errors.append(f"{path.relative_to(target)} 缺少 frontmatter description")
        if metadata.get("mode") != expected_mode:
            errors.append(
                f"{path.relative_to(target)} mode 必须为 {expected_mode}"
            )
        for permission, value in OPENCODE_AGENT_REQUIRED_PERMISSIONS.get(name, {}).items():
            if not has_frontmatter_permission(text, permission, value):
                errors.append(f"{path.relative_to(target)} permission {permission} must be {value}")
        permissions, valid_permissions = opencode_permission_entries(text)
        expected_permissions = OPENCODE_AGENT_REQUIRED_PERMISSIONS.get(name, {})
        if not valid_permissions or permissions != expected_permissions:
            errors.append(f"{path.relative_to(target)} permission entries must exactly match the approved set")
    return errors


def validate_claude_agents(target: Path, skills: set[str]) -> list[str]:
    errors: list[str] = []
    agent_root = target / ".claude" / "agents"
    for name in CLAUDE_AGENT_NAMES:
        path = agent_root / f"{name}.md"
        if name not in skills:
            if path.is_file():
                errors.append(f"{path.relative_to(target)} Agent requires matching Skill: {name}")
            continue
        if not path.is_file():
            errors.append(f"缺少 Claude Code Agent: {path.relative_to(target)}")
            continue
        metadata = parse_frontmatter(path.read_text(encoding="utf-8"))
        for field in sorted(set(metadata) - {"name", "description", "tools"}):
            errors.append(f"{path.relative_to(target)} unexpected frontmatter field: {field}")
        if metadata.get("name") != name:
            errors.append(f"{path.relative_to(target)} frontmatter name 必须为 {name}")
        if not metadata.get("description"):
            errors.append(f"{path.relative_to(target)} 缺少 frontmatter description")
        if not metadata.get("tools"):
            errors.append(f"{path.relative_to(target)} 缺少 frontmatter tools")
            continue
        tools = {tool.strip() for tool in metadata["tools"].split(",") if tool.strip()}
        if tools != CLAUDE_AGENT_TOOLS[name]:
            errors.append(f"{path.relative_to(target)} tools must be exactly the approved set")
    return errors


def validate_squads(target: Path, skills: set[str]) -> tuple[list[str], list[str]]:
    errors: list[str] = []
    warnings: list[str] = []
    path = target / "SQUADS.md"
    if not path.is_file():
        return errors, warnings
    text = path.read_text(encoding="utf-8")
    for raw_members in SQUAD_MEMBERS.findall(text):
        members = re.findall(r"`([^`]+)`", raw_members)
        if not members and "{{" not in raw_members:
            warnings.append(f"无法解析小队成员: {raw_members.strip()}")
            continue
        if members and not 2 <= len(members) <= 3:
            errors.append(f"小队应由 2-3 个 Skill 组成: {', '.join(members)}")
        for member in members:
            if member.startswith("project-specific-"):
                continue
            if member not in skills:
                errors.append(f"SQUADS.md 引用了不存在的 Skill: {member}")
    return errors, warnings


def validate_evals(target: Path, skills: set[str], eval_root: Path) -> list[str]:
    errors: list[str] = []
    for path in sorted((target / eval_root).glob("*.json")):
        try:
            payload = json.loads(path.read_text(encoding="utf-8"))
        except json.JSONDecodeError as exc:
            errors.append(f"{path.relative_to(target)} JSON 无效: {exc}")
            continue
        for case in payload.get("cases", []):
            for member in case.get("expected_squad", []):
                if member.startswith("project-specific-"):
                    continue
                if member not in skills:
                    errors.append(
                        f"{path.relative_to(target)} 的案例 {case.get('id')} 引用了不存在的 Skill: {member}"
                    )
    return errors


def validate(target: Path, platform: str) -> tuple[list[str], list[str]]:
    errors: list[str] = []
    warnings: list[str] = []
    for relative in (*COMMON_REQUIRED_FILES, *PLATFORM_REQUIRED_FILES[platform]):
        if not (target / relative).is_file():
            errors.append(f"缺少必需文件: {relative}")

    skill_root = PLATFORM_SKILL_ROOTS[platform]
    skills, skill_errors = collect_skills(
        target,
        skill_root,
        require_opencode_names=platform == "opencode",
        use_directory_names=platform == "claude-code",
    )
    errors.extend(skill_errors)
    for name in PLATFORM_REQUIRED_SKILLS[platform]:
        if name not in skills:
            errors.append(f"missing required Skill: {name}")
    if platform == "opencode":
        errors.extend(validate_opencode_agents(target, skills))
        errors.extend(validate_opencode_skill_collisions(target, skills))
    elif platform == "claude-code":
        errors.extend(validate_claude_agents(target, skills))

    framework_markdown = [
        target / "AGENTS.md",
        target / "AI_ENGINEERING_PLAYBOOK.md",
        target / "SQUADS.md",
    ]
    framework_root = target / PLATFORM_FRAMEWORK_ROOTS[platform]
    framework_markdown.extend(sorted(framework_root.rglob("*.md")))
    for path in framework_markdown:
        if not path.is_file():
            continue
        text = path.read_text(encoding="utf-8")
        tokens = PLACEHOLDER.findall(text)
        if tokens:
            errors.append(f"{path.relative_to(target)} 仍有 {len(tokens)} 个模板占位符")
        for label, pattern in PRIVATE_PATTERNS:
            if pattern.search(text):
                warnings.append(f"{path.relative_to(target)} 包含{label}，发布前请确认")

    squad_errors, squad_warnings = validate_squads(target, skills)
    errors.extend(squad_errors)
    warnings.extend(squad_warnings)
    errors.extend(validate_evals(target, skills, PLATFORM_EVAL_ROOTS[platform]))
    return errors, warnings


def main() -> int:
    args = parse_args()
    target = args.target.expanduser().resolve()
    if not target.is_dir():
        print(f"错误：目标目录不存在: {target}")
        return 2
    errors, warnings = validate(target, args.platform)
    for warning in warnings:
        print(f"警告：{warning}")
    if errors:
        print("项目验证失败：")
        for error in errors:
            print(f"- {error}")
        return 1
    skill_root = target / PLATFORM_SKILL_ROOTS[args.platform]
    print(f"项目验证通过：发现 {len(list(skill_root.glob('*/SKILL.md')))} 个 Skill，{len(warnings)} 个警告。")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
