#!/usr/bin/env python3
"""Report which Tier-1 capabilities a task record permits skipping.

Read-only. Evaluates contracts/capability-skip-preconditions.json against one IDC
task record through the predicates in idc_core.routing, so the "Do not over-route
when" column of docs/CAPABILITY_TIERS.md is decided by evidence instead of read as
prose. Unknown is reported as unknown and never as permission to skip.
"""

from __future__ import annotations

import argparse
import dataclasses
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from idc_core.projector import fold_events
from idc_core.routing import (
    KEEP,
    KNOWN_ENVIRONMENT_FACTS,
    SKIP,
    UNKNOWN,
    evaluate_catalog,
    format_decisions,
    load_catalog,
)
from validate_contracts import DEFAULT_SCHEMA, validate as validate_contracts


DEFAULT_CATALOG = ROOT / "contracts" / "capability-skip-preconditions.json"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Check Tier-1 capability skip preconditions against one task record."
    )
    parser.add_argument("--project", required=True, type=Path, help="Project containing .idc")
    parser.add_argument("--record", help="Record id under .idc/work-items; defaults to the last one")
    parser.add_argument("--catalog", type=Path, default=DEFAULT_CATALOG, help="Skip catalog JSON")
    parser.add_argument(
        "--fact",
        action="append",
        choices=sorted(KNOWN_ENVIRONMENT_FACTS),
        default=None,
        help="Declared environment fact; repeatable. Omitting all facts leaves host predicates unknown.",
    )
    parser.add_argument("--json", action="store_true", help="Emit machine-readable decisions")
    return parser.parse_args()


def load_state(project: Path, record: str | None) -> tuple[str, object]:
    root = project.resolve() / ".idc" / "work-items"
    if record:
        events_path = root / record / "events.jsonl"
        if not events_path.is_file():
            raise ValueError(f"no event stream for record '{record}' under {root}")
    else:
        candidates = sorted(root.glob("*/events.jsonl"))
        if not candidates:
            raise ValueError(f"no event streams under {root}")
        events_path = candidates[-1]
    events = [
        json.loads(line)
        for line in events_path.read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]
    return events_path.parent.name, fold_events(events)


def main() -> int:
    args = parse_args()
    catalog_path = args.catalog.expanduser().resolve()
    if not catalog_path.is_file():
        print(f"ERROR: catalog does not exist: {catalog_path}", file=sys.stderr)
        return 2

    catalog_errors = validate_contracts(DEFAULT_SCHEMA, catalog_path)
    if catalog_errors:
        print("ERROR: the skip catalog is not a valid contract:", file=sys.stderr)
        for error in catalog_errors:
            print(f"- {error}", file=sys.stderr)
        return 1

    try:
        catalog = load_catalog(catalog_path)
        record_id, state = load_state(args.project, args.record)
    except (OSError, UnicodeError, ValueError, json.JSONDecodeError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1

    decisions = evaluate_catalog(catalog, state, facts=args.fact if args.fact else None)
    counts = {status: 0 for status in (SKIP, KEEP, UNKNOWN)}
    for decision in decisions:
        counts[decision.status] = counts.get(decision.status, 0) + 1

    if args.json:
        print(
            json.dumps(
                {
                    "record_id": record_id,
                    "catalog": str(catalog_path),
                    "facts": sorted(args.fact or []),
                    "counts": counts,
                    "decisions": [dataclasses.asdict(item) for item in decisions],
                },
                indent=2,
                sort_keys=True,
            )
        )
        return 0

    print(f"record: {record_id}")
    print(f"catalog: {catalog_path}")
    print(f"declared facts: {', '.join(sorted(args.fact or [])) or 'none'}")
    print()
    print(format_decisions(decisions))
    print()
    print(
        f"summary: skip={counts.get(SKIP, 0)} keep={counts.get(KEEP, 0)} "
        f"unknown={counts.get(UNKNOWN, 0)}"
    )
    print("Note: only 'skip' permits skipping a capability; 'unknown' does not.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
