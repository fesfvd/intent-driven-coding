#!/usr/bin/env python3
"""Optionally scaffold neutral framework files after project analysis."""

from __future__ import annotations

import argparse
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


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="预览或生成工具中立的框架骨架；不会分析项目或完成平台适配。"
    )
    parser.add_argument("--target", required=True, type=Path, help="Existing project directory")
    parser.add_argument("--project-name", required=True, help="Name used in generated headings")
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


def planned_files() -> list[tuple[Path, Path, bool]]:
    files = [(source, destination, True) for source, destination in TEMPLATE_FILES.items()]
    files.extend((source, destination, False) for source, destination in RESOURCE_FILES.items())
    for name in SKILL_NAMES:
        source = ROOT / "skills" / name / "SKILL.md"
        destination = Path(".agent") / "skills" / name / "SKILL.md"
        files.append((source, destination, False))
    return files


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

    actions: list[tuple[Path, Path, bool, str]] = []
    blocked = False
    for source, relative_destination, is_template in planned_files():
        destination = target / relative_destination
        if destination.exists() and not args.force:
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
        else:
            shutil.copyfile(source, destination)
        written += 1

    print(f"已写入 {written} 个文件。脚手架不等于适配完成，请基于目标项目裁剪内容并替换所有 {{{{...}}}} 占位符。")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
