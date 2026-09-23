#!/usr/bin/env python3
"""Optionally scaffold neutral framework files after project analysis."""

from __future__ import annotations

import argparse
import difflib
import re
import shutil
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
TEMPLATE_FILES = {
    ROOT / "templates" / "AGENTS.md": Path("AGENTS.md"),
    ROOT / "templates" / "AI_ENGINEERING_PLAYBOOK.md": Path("AI_ENGINEERING_PLAYBOOK.md"),
    ROOT / "templates" / "IDC.md": Path("IDC.md"),
    ROOT / "templates" / "IDC_TASK.md": Path("templates") / "IDC_TASK.md",
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
GUIDANCE_FILES = {
    ROOT / "docs" / "TASK_SCENARIOS.md": Path("docs") / "TASK_SCENARIOS.md",
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
ENTRY_PATHS = {
    "codex": Path("AGENTS.md"),
    "opencode": Path("AGENTS.md"),
    "claude-code": Path("CLAUDE.md"),
}
ENTRY_BEGIN = "<!-- IDC:BEGIN -->"
ENTRY_END = "<!-- IDC:END -->"
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
        choices=("neutral", "codex", "opencode", "claude-code"),
        default="neutral",
        help="Generated layout: neutral (default), Codex, OpenCode, or Claude Code",
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
    text = source.read_text(encoding="utf-8").replace("{{PROJECT_NAME}}", project_name)
    if source.name == "AI_ENGINEERING_PLAYBOOK.md":
        text = text.replace("../docs/TASK_SCENARIOS.md", "docs/TASK_SCENARIOS.md")
        text = text.replace("(IDC_TASK.md)", "(templates/IDC_TASK.md)")
    return text


def render_platform_skill(source: Path) -> str:
    text = re.sub(r"(?m)^allowed-tools:.*\n", "", source.read_text(encoding="utf-8"))
    text = text.replace("../../docs/TASK_SCENARIOS.md", "../../../docs/TASK_SCENARIOS.md")
    text = text.replace("../../templates/IDC_TASK.md", "../../../templates/IDC_TASK.md")
    return text


def planned_files(platform: str) -> list[tuple[Path, Path, bool]]:
    files = [(source, destination, True) for source, destination in TEMPLATE_FILES.items()]
    files.extend((source, destination, False) for source, destination in GUIDANCE_FILES.items())
    if platform == "neutral":
        files.extend((source, destination, False) for source, destination in RESOURCE_FILES.items())
        skill_root = Path(".agent") / "skills"
    elif platform == "codex":
        files.extend(
            (source, Path(".agents") / "evals" / destination.name, False)
            for source, destination in RESOURCE_FILES.items()
        )
        files = [
            (source, Path(".agents") / "templates" / destination.name, is_template)
            if destination == Path(".agent") / "templates" / "SQUAD.md"
            else (source, destination, is_template)
            for source, destination, is_template in files
            if destination != Path(".agent") / "AGENT_ENTRY.md"
        ]
        skill_root = Path(".agents") / "skills"
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
        files.append((ROOT / "templates" / "claude" / "CLAUDE.md", Path("CLAUDE.md"), False))
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


def integrate_entry(existing: str, template: str) -> str:
    """Insert or update the managed IDC block while preserving surrounding text."""
    starts = [match.start() for match in re.finditer(re.escape(ENTRY_BEGIN), existing)]
    ends = [match.start() for match in re.finditer(re.escape(ENTRY_END), existing)]
    if len(starts) != len(ends) or len(starts) > 1:
        raise ValueError("existing IDC entry markers are incomplete or duplicated")

    newline = "\r\n" if "\r\n" in existing else "\n"
    block = template.replace("\r\n", "\n").replace("\n", newline).rstrip("\r\n")
    if starts:
        end = ends[0] + len(ENTRY_END)
        if starts[0] > ends[0]:
            raise ValueError("existing IDC entry markers are out of order")
        return existing[:starts[0]] + block + existing[end:]

    if existing.startswith("\ufeff"):
        return "\ufeff" + block + newline + newline + existing[1:]
    return block + newline + newline + existing


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

    entry_destination = ENTRY_PATHS.get(args.platform)
    entry_template_path = (
        ROOT / "templates" / "claude" / "CLAUDE.md"
        if args.platform == "claude-code"
        else ROOT / "templates" / "IDC_ENTRY.md"
    )
    try:
        entry_template = entry_template_path.read_text(encoding="utf-8") if entry_destination else ""
        if entry_destination and (ENTRY_BEGIN not in entry_template or ENTRY_END not in entry_template):
            raise ValueError(f"entry template must contain {ENTRY_BEGIN} and {ENTRY_END}")
    except (OSError, UnicodeError, ValueError) as exc:
        print(f"ERROR: unable to load host entry template: {exc}", file=sys.stderr)
        return 1

    actions: list[tuple[Path, Path, bool, str]] = []
    entry_previews: dict[Path, tuple[str, str]] = {}
    blocked = False
    for source, relative_destination, is_template in planned_files(args.platform):
        destination = target / relative_destination
        if not is_inside_target(target, destination):
            status = "ERROR destination escapes target"
            blocked = True
        elif relative_destination == entry_destination and destination.exists():
            try:
                existing = destination.read_bytes().decode("utf-8")
                updated = integrate_entry(existing, entry_template)
                if updated == existing:
                    status = "IDC ENTRY CURRENT"
                else:
                    status = "INTEGRATE IDC ENTRY"
                    entry_previews[destination] = (existing, updated)
            except (OSError, UnicodeError, ValueError) as exc:
                status = "ERROR unable to integrate IDC entry"
                print(f"ERROR: {destination}: {exc}", file=sys.stderr)
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
        if not apply_changes and destination in entry_previews:
            original, updated = entry_previews[destination]
            for line in difflib.unified_diff(
                original.splitlines(keepends=True),
                updated.splitlines(keepends=True),
                fromfile=str(destination),
                tofile=f"{destination} (IDC entry)",
            ):
                print(line, end="" if line.endswith(("\n", "\r")) else "\n")

    if blocked:
        return 1
    if not apply_changes:
        print("未写入任何文件。确认目标项目和生成计划后，可使用 --apply 创建骨架。")
        return 0

    written = 0
    for source, destination, is_template, status in actions:
        relative_destination = destination.relative_to(target)
        if status in {"SKIP existing", "IDC ENTRY CURRENT"}:
            continue
        destination.parent.mkdir(parents=True, exist_ok=True)
        if relative_destination == entry_destination:
            if status == "INTEGRATE IDC ENTRY":
                existing = destination.read_bytes().decode("utf-8")
            elif is_template:
                existing = render_template(source, args.project_name)
            else:
                existing = source.read_bytes().decode("utf-8")
            destination.write_bytes(integrate_entry(existing, entry_template).encode("utf-8"))
        elif is_template:
            destination.write_text(render_template(source, args.project_name), encoding="utf-8")
        elif args.platform in {"codex", "opencode", "claude-code"} and source.parent.parent == ROOT / "skills":
            destination.write_text(render_platform_skill(source), encoding="utf-8")
        else:
            shutil.copyfile(source, destination)
        written += 1

    print(f"已写入 {written} 个文件。脚手架不等于适配完成，请基于目标项目裁剪内容并替换所有 {{{{...}}}} 占位符。")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
