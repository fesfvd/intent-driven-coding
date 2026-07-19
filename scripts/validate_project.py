#!/usr/bin/env python3
"""Validate an installed Intent-Driven Coding project without modifying it."""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path


REQUIRED_FILES = (
    Path("AGENTS.md"),
    Path("AI_ENGINEERING_PLAYBOOK.md"),
    Path("SQUADS.md"),
    Path(".agent/AGENT_ENTRY.md"),
)
PLACEHOLDER = re.compile(r"\{\{[^{}]+\}\}")
SKILL_NAME = re.compile(r"^name:\s*([^\s]+)\s*$", re.MULTILINE)
SQUAD_MEMBERS = re.compile(r"\|\s*Members\s*\|\s*([^|]+)\|", re.IGNORECASE)
PRIVATE_PATTERNS = (
    ("本机用户路径", re.compile(r"[A-Za-z]:\\Users\\[^\\\s]+", re.IGNORECASE)),
    ("私有 IPv4", re.compile(r"\b(?:10\.|192\.168\.|172\.(?:1[6-9]|2\d|3[01])\.)\d{1,3}\.\d{1,3}\b")),
    ("疑似密钥赋值", re.compile(r"(?i)(api[_-]?key|secret|token|password)\s*[:=]\s*['\"][^'\"]{8,}")),
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="检查已安装的 Intent-Driven Coding 项目配置。")
    parser.add_argument("--target", required=True, type=Path, help="目标项目目录")
    return parser.parse_args()


def collect_skills(target: Path) -> tuple[set[str], list[str]]:
    skills: set[str] = set()
    errors: list[str] = []
    for path in sorted((target / ".agent" / "skills").glob("*/SKILL.md")):
        text = path.read_text(encoding="utf-8")
        match = SKILL_NAME.search(text)
        if not match:
            errors.append(f"{path.relative_to(target)} 缺少 frontmatter name")
            continue
        name = match.group(1)
        if name in skills:
            errors.append(f"Skill 名称重复: {name}")
        skills.add(name)
        if "description:" not in text:
            errors.append(f"{path.relative_to(target)} 缺少 description")
        if "## Safety Statement" not in text:
            errors.append(f"{path.relative_to(target)} 缺少 Safety Statement")
    if not skills:
        errors.append(".agent/skills/ 下没有找到 Skill")
    return skills, errors


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


def validate_evals(target: Path, skills: set[str]) -> list[str]:
    errors: list[str] = []
    for path in sorted((target / ".agent" / "evals").glob("*.json")):
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


def validate(target: Path) -> tuple[list[str], list[str]]:
    errors: list[str] = []
    warnings: list[str] = []
    for relative in REQUIRED_FILES:
        if not (target / relative).is_file():
            errors.append(f"缺少必需文件: {relative}")

    skills, skill_errors = collect_skills(target)
    errors.extend(skill_errors)

    framework_markdown = [
        target / "AGENTS.md",
        target / "AI_ENGINEERING_PLAYBOOK.md",
        target / "SQUADS.md",
    ]
    framework_markdown.extend(sorted((target / ".agent").rglob("*.md")))
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
    errors.extend(validate_evals(target, skills))
    return errors, warnings


def main() -> int:
    args = parse_args()
    target = args.target.expanduser().resolve()
    if not target.is_dir():
        print(f"错误：目标目录不存在: {target}")
        return 2
    errors, warnings = validate(target)
    for warning in warnings:
        print(f"警告：{warning}")
    if errors:
        print("项目验证失败：")
        for error in errors:
            print(f"- {error}")
        return 1
    print(f"项目验证通过：发现 {len(list((target / '.agent' / 'skills').glob('*/SKILL.md')))} 个 Skill，{len(warnings)} 个警告。")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
