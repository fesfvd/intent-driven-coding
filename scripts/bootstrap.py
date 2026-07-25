#!/usr/bin/env python3
"""Optionally scaffold neutral framework files after project analysis."""

from __future__ import annotations

import argparse
import re
import shutil
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
TEMPLATE_FILES = {
    ROOT / "templates" / "AGENTS.md": Path("AGENTS.md"),
    ROOT / "templates" / "AI_ENGINEERING_PLAYBOOK.md": Path("AI_ENGINEERING_PLAYBOOK.md"),
    ROOT / "templates" / "SQUADS.md": Path("SQUADS.md"),
    ROOT / "templates" / "AGENT_ENTRY.md": Path(".agent") / "AGENT_ENTRY.md",
    ROOT / "templates" / "SQUAD.md": Path(".agent") / "templates" / "SQUAD.md",
}
OPENCODE_AGENT_FILES = {
    ROOT / "templates" / "opencode" / "agents" / "team.md": Path(".opencode") / "agents" / "team.md",
    ROOT / "templates" / "opencode" / "agents" / "architecture.md": Path(".opencode") / "agents" / "architecture.md",
    ROOT / "templates" / "opencode" / "agents" / "debug.md": Path(".opencode") / "agents" / "debug.md",
    ROOT / "templates" / "opencode" / "agents" / "code-review.md": Path(".opencode") / "agents" / "code-review.md",
    ROOT / "templates" / "opencode" / "agents" / "verify.md": Path(".opencode") / "agents" / "verify.md",
    ROOT / "templates" / "opencode" / "agents" / "meta-skill-designer.md": Path(".opencode") / "agents" / "meta-skill-designer.md",
    ROOT / "templates" / "opencode" / "agents" / "skill-creator.md": Path(".opencode") / "agents" / "skill-creator.md",
}
CLAUDE_AGENT_FILES = {
    ROOT / "templates" / "claude" / "agents" / "architecture.md": Path(".claude") / "agents" / "architecture.md",
    ROOT / "templates" / "claude" / "agents" / "debug.md": Path(".claude") / "agents" / "debug.md",
    ROOT / "templates" / "claude" / "agents" / "code-review.md": Path(".claude") / "agents" / "code-review.md",
    ROOT / "templates" / "claude" / "agents" / "verify.md": Path(".claude") / "agents" / "verify.md",
    ROOT / "templates" / "claude" / "agents" / "meta-skill-designer.md": Path(".claude") / "agents" / "meta-skill-designer.md",
    ROOT / "templates" / "claude" / "agents" / "skill-creator.md": Path(".claude") / "agents" / "skill-creator.md",
}
RESOURCE_FILES = {
    ROOT / "evals" / "squad-routing.json": Path(".agent") / "evals" / "squad-routing.json",
    ROOT / "evals" / "skill-design.json": Path(".agent") / "evals" / "skill-design.json",
}
SKILL_NAMES = (
    "team",
    "architecture",
    "debug",
    "code-review",
    "verify",
    "meta-skill-designer",
    "skill-creator",
)
OPENCODE_COMPATIBLE_SKILL_ROOTS = (
    Path(".claude") / "skills",
    Path(".agents") / "skills",
)
OPENCODE_ANCESTOR_SKILL_ROOT = Path(".opencode") / "skills"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="预览或生成工具中立的框架骨架；不会分析项目或完成平台适配。"
    )
    parser.add_argument("--target", required=True, type=Path, help="Existing project directory")
    parser.add_argument("--project-name", required=True, help="Name used in generated headings")
    parser.add_argument(
        "--platform",
        choices=("neutral", "opencode", "claude-code"),
        default="neutral",
        help="Generated layout: neutral (default) or OpenCode",
    )
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument("--apply", action="store_true", help="Write the planned files")
    mode.add_argument("--dry-run", action="store_true", help="Preview only (default)")
    parser.add_argument(
        "--force",
        action="store_true",
        help="Overwrite existing destination files; valid only with --apply",
    )
    return parser.parse_args()


def render_template(source: Path, project_name: str) -> str:
    return source.read_text(encoding="utf-8").replace("{{PROJECT_NAME}}", project_name)


def render_platform_skill(source: Path) -> str:
    return re.sub(r"(?m)^allowed-tools:.*\n", "", source.read_text(encoding="utf-8"))


def planned_files(platform: str) -> list[tuple[Path, Path, bool]]:
    files = [(source, destination, True) for source, destination in TEMPLATE_FILES.items()]
    if platform == "neutral":
        files.extend((source, destination, False) for source, destination in RESOURCE_FILES.items())
        skill_root = Path(".agent") / "skills"
    elif platform == "opencode":
        files.extend(
            (source, Path(".opencode") / "evals" / destination.name, False)
            for source, destination in RESOURCE_FILES.items()
        )
        files.extend((source, destination, False) for source, destination in OPENCODE_AGENT_FILES.items())
        files = [
            (source, Path(".opencode") / "templates" / destination.name, is_template)
            if destination == Path(".agent") / "templates" / "SQUAD.md"
            else (source, destination, is_template)
            for source, destination, is_template in files
            if destination != Path(".agent") / "AGENT_ENTRY.md"
        ]
        skill_root = Path(".opencode") / "skills"
    else:
        files.extend(
            (source, Path(".claude") / "evals" / destination.name, False)
            for source, destination in RESOURCE_FILES.items()
        )
        files.extend((source, destination, False) for source, destination in CLAUDE_AGENT_FILES.items())
        files.append(
            (ROOT / "templates" / "claude" / "CLAUDE.md", Path(".claude") / "CLAUDE.md", True)
        )
        files = [
            (source, Path(".claude") / "templates" / destination.name, is_template)
            if destination == Path(".agent") / "templates" / "SQUAD.md"
            else (source, destination, is_template)
            for source, destination, is_template in files
            if destination != Path(".agent") / "AGENT_ENTRY.md"
        ]
        skill_root = Path(".claude") / "skills"
    for name in SKILL_NAMES:
        source = ROOT / "skills" / name / "SKILL.md"
        destination = skill_root / name / "SKILL.md"
        files.append((source, destination, False))
    return files


def is_inside_target(target: Path, destination: Path) -> bool:
    try:
        destination.resolve().relative_to(target)
    except ValueError:
        return False
    return True


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


def opencode_skill_collisions(target: Path) -> list[Path]:
    collisions: list[Path] = []
    for root in opencode_search_roots(target):
        skill_roots = OPENCODE_COMPATIBLE_SKILL_ROOTS
        if root != target:
            skill_roots = (*skill_roots, OPENCODE_ANCESTOR_SKILL_ROOT)
        for skill_root in skill_roots:
            for name in SKILL_NAMES:
                path = root / skill_root / name / "SKILL.md"
                if path.is_file():
                    collisions.append(path)
    return collisions


def main() -> int:
    args = parse_args()
    target = args.target.expanduser().resolve()
    apply_changes = args.apply

    if args.force and not apply_changes:
        print("ERROR: --force is valid only with --apply.", file=sys.stderr)
        return 2
    if not target.exists() or not target.is_dir():
        print(f"ERROR: target directory does not exist: {target}", file=sys.stderr)
        return 2
    if args.platform == "opencode":
        collisions = opencode_skill_collisions(target)
        if collisions:
            print("ERROR: conflicting OpenCode skill discovery paths:", file=sys.stderr)
            for path in collisions:
                print(f"- {path}", file=sys.stderr)
            return 1

    actions: list[tuple[Path, Path, bool, str]] = []
    blocked = False
    for source, relative_destination, is_template in planned_files(args.platform):
        destination = target / relative_destination
        if not is_inside_target(target, destination):
            status = "ERROR destination escapes target"
            blocked = True
        elif destination.exists() and not args.force:
            status = "SKIP existing"
        elif destination.exists():
            status = "OVERWRITE"
        else:
            status = "CREATE"
        if not source.exists():
            status = "ERROR missing source"
            blocked = True
        actions.append((source, destination, is_template, status))

    mode = "APPLY" if apply_changes else "DRY RUN"
    print(f"Intent-Driven Coding 可选脚手架: {mode}")
    print(f"Target: {target}")
    for _, destination, _, status in actions:
        print(f"[{status}] {destination}")

    if blocked:
        return 1
    if not apply_changes:
        print("未写入任何文件。确认目标项目和生成计划后，可使用 --apply 创建骨架。")
        return 0

    written = 0
    for source, destination, is_template, status in actions:
        if status == "SKIP existing":
            continue
        destination.parent.mkdir(parents=True, exist_ok=True)
        if is_template:
            destination.write_text(render_template(source, args.project_name), encoding="utf-8")
        elif args.platform in {"opencode", "claude-code"} and source.parent.parent == ROOT / "skills":
            destination.write_text(render_platform_skill(source), encoding="utf-8")
        else:
            shutil.copyfile(source, destination)
        written += 1

    print(f"已写入 {written} 个文件。脚手架不等于适配完成，请基于目标项目裁剪内容并替换所有 {{{{...}}}} 占位符。")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
