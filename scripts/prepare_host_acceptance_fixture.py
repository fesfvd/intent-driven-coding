#!/usr/bin/env python3
"""Prepare a disposable, non-leaking target for manual host acceptance runs."""

from __future__ import annotations

import argparse
import shutil
import sys
from pathlib import Path

import bootstrap


ROOT = Path(__file__).resolve().parents[1]
FIXTURE_ROOT = ROOT / "fixtures" / "host-acceptance"
COMMON_FIXTURE_FILES = (
    Path("AGENTS.md"),
    Path("AI_ENGINEERING_PLAYBOOK.md"),
    Path("SQUADS.md"),
    Path("SQUAD.md"),
    Path("fixture_app.py"),
    Path("tests/test_report.py"),
    Path("tests/test_invoice.py"),
    Path("tests/test_approval.py"),
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Prepare a disposable Intent-Driven Coding host-acceptance fixture."
    )
    parser.add_argument("--target", required=True, type=Path, help="Existing empty directory")
    parser.add_argument(
        "--platform",
        required=True,
        choices=("opencode", "claude-code"),
        help="Native layout to prepare",
    )
    parser.add_argument("--apply", action="store_true", help="Write the fixture")
    return parser.parse_args()


def copy_bootstrap_layout(target: Path, platform: str) -> None:
    for source, relative_destination, is_template in bootstrap.planned_files(platform):
        destination = target / relative_destination
        destination.parent.mkdir(parents=True, exist_ok=True)
        if is_template:
            destination.write_text(
                bootstrap.render_template(source, "IDC Host Acceptance Fixture"), encoding="utf-8"
            )
        elif source.parent.parent == bootstrap.ROOT / "skills":
            destination.write_text(bootstrap.render_platform_skill(source), encoding="utf-8")
        else:
            shutil.copyfile(source, destination)


def copy_fixture_files(target: Path, platform: str) -> None:
    for relative in COMMON_FIXTURE_FILES:
        source = FIXTURE_ROOT / relative
        destination = target / relative
        destination.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(source, destination)

    template_root = target / (".opencode" if platform == "opencode" else ".claude") / "templates"
    shutil.copyfile(FIXTURE_ROOT / "SQUAD.md", template_root / "SQUAD.md")

    if platform == "opencode":
        shutil.copyfile(FIXTURE_ROOT / "opencode.json", target / "opencode.json")

    # Acceptance prompts remain outside the target so the model cannot route by reading answers.
    shutil.rmtree(target / (".opencode" if platform == "opencode" else ".claude") / "evals")

    entry_relative = bootstrap.ENTRY_PATHS[platform]
    entry_destination = target / entry_relative
    entry_template = (
        ROOT / "templates" / "claude" / "CLAUDE.md"
        if platform == "claude-code"
        else ROOT / "templates" / "IDC_ENTRY.md"
    )
    existing = entry_destination.read_text(encoding="utf-8") if entry_destination.exists() else ""
    entry_destination.write_text(
        bootstrap.integrate_entry(existing, entry_template.read_text(encoding="utf-8")),
        encoding="utf-8",
    )


def main() -> int:
    args = parse_args()
    target = args.target.expanduser().resolve()
    if not target.is_dir():
        print(f"ERROR: target directory does not exist: {target}", file=sys.stderr)
        return 2
    if any(target.iterdir()):
        print("ERROR: target directory must be empty.", file=sys.stderr)
        return 2

    print(f"Host acceptance fixture: {'APPLY' if args.apply else 'DRY RUN'}")
    print(f"Target: {target}")
    print(f"Platform: {args.platform}")
    print("No routing evaluation prompts will be copied into the target.")
    if not args.apply:
        return 0

    copy_bootstrap_layout(target, args.platform)
    copy_fixture_files(target, args.platform)
    print("Fixture prepared. Initialize a disposable Git baseline explicitly before a diff-based run.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
