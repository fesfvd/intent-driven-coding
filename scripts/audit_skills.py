#!/usr/bin/env python3
"""Audit Skill structure and squad references without modifying files."""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path


FRONTMATTER_END = re.compile(r"\n---\n")
VOLATILE_PATTERNS = {
    "absolute Windows path": re.compile(r"[A-Za-z]:\\[^\s`]+"),
    "private IPv4": re.compile(r"\b(?:10\.|192\.168\.|172\.(?:1[6-9]|2\d|3[01])\.)\d{1,3}\.\d{1,3}\b"),
    "hard-coded API route": re.compile(r"`?/(?:api|v\d+)/[A-Za-z0-9_/{}/.-]+`?"),
    "version snapshot": re.compile(r"\bv?\d+\.\d+(?:\.\d+)?\b", re.IGNORECASE),
}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Audit a directory of SKILL.md files.")
    parser.add_argument("--skills", type=Path, default=Path("skills"), help="Skill root directory")
    parser.add_argument("--evals", type=Path, default=Path("evals"), help="Evaluation directory")
    return parser.parse_args()


def frontmatter(text: str) -> dict[str, str]:
    if not text.startswith("---\n"):
        return {}
    match = FRONTMATTER_END.search(text, 4)
    if not match:
        return {}
    values: dict[str, str] = {}
    for line in text[4:match.start()].splitlines():
        if ":" in line and not line.startswith((" ", "\t")):
            key, value = line.split(":", 1)
            values[key.strip()] = value.strip()
    return values


def audit(skills_root: Path, evals_root: Path) -> tuple[list[str], list[str]]:
    errors: list[str] = []
    warnings: list[str] = []
    skill_paths = sorted(skills_root.glob("*/SKILL.md"))
    known = {path.parent.name for path in skill_paths}

    if not skill_paths:
        errors.append(f"No SKILL.md files found under {skills_root}")
        return errors, warnings

    for path in skill_paths:
        text = path.read_text(encoding="utf-8")
        metadata = frontmatter(text)
        name = path.parent.name
        if metadata.get("name") != name:
            errors.append(f"{path}: frontmatter name must be '{name}'")
        description = metadata.get("description", "")
        if len(description) < 60:
            warnings.append(f"{path}: description may not explain both what and when")
        if "allowed-tools" not in metadata:
            errors.append(f"{path}: missing allowed-tools")
        for section in ("## Example Triggers", "## Safety Statement"):
            if section not in text:
                errors.append(f"{path}: missing {section}")
        if text.count("\n") > 500:
            warnings.append(f"{path}: over 500 lines; consider progressive disclosure")
        for label, pattern in VOLATILE_PATTERNS.items():
            if pattern.search(text):
                warnings.append(f"{path}: possible {label}; confirm it belongs in a stable Skill")

    for eval_path in sorted(evals_root.glob("*.json")):
        try:
            payload = json.loads(eval_path.read_text(encoding="utf-8"))
        except json.JSONDecodeError as exc:
            errors.append(f"{eval_path}: invalid JSON ({exc})")
            continue
        for case in payload.get("cases", []):
            for member in case.get("expected_squad", []):
                if member.startswith("project-specific-"):
                    continue
                if member not in known:
                    errors.append(f"{eval_path}: case '{case.get('id')}' references unknown Skill '{member}'")

    return errors, warnings


def main() -> int:
    args = parse_args()
    errors, warnings = audit(args.skills, args.evals)
    for warning in warnings:
        print(f"WARNING: {warning}")
    if errors:
        print("Skill audit failed:")
        for error in errors:
            print(f"- {error}")
        return 1
    print(f"Skill audit passed with {len(warnings)} warning(s).")
    print("Note: Skill structure does not prove host routing or Agent execution.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
