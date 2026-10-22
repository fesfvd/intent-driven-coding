"""Generate reference projections with the Python IDC implementation.

Usage:
    python oracle.py --now 2026-10-18T00:00:00+00:00 --out out.json --project <dir> [--project <dir> ...]

The script never writes to the inspected projects. Index rebuilds happen on a
temporary copy that contains only `.idc/work-items`.
"""

from __future__ import annotations

import argparse
import json
import shutil
import tempfile
from dataclasses import asdict
from datetime import datetime
from pathlib import Path

from idc_core.obligations import evaluate_obligations
from idc_core.projector import fold_events
from idc_core.render import render_card
from idc_core.task_index import rebuild_index

TARGETS = ("shaped", "active", "validating", "build", "completed", "ship")


def read_events(path: Path) -> list[dict]:
    events: list[dict] = []
    for line in path.read_text(encoding="utf-8").splitlines():
        if line.strip():
            events.append(json.loads(line))
    return events


def state_dict(state) -> dict:
    result = asdict(state)
    result["conditions"] = sorted(state.conditions)
    return result


def dump_project(project: Path, now: datetime) -> dict:
    root = project / ".idc" / "work-items"
    records = []
    if root.is_dir():
        for record_dir in sorted(path for path in root.iterdir() if path.is_dir()):
            events = read_events(record_dir / "events.jsonl")
            if not events:
                continue
            try:
                state = fold_events(events, now=now)
                records.append(
                    {
                        "record_id": record_dir.name,
                        "state": state_dict(state),
                        "card": render_card(state),
                        "gates": {
                            target: asdict(evaluate_obligations(state, target))
                            for target in TARGETS
                        },
                    }
                )
            except Exception as error:  # the reference implementation itself rejects this record
                records.append(
                    {
                        "record_id": record_dir.name,
                        "error": f"{type(error).__name__}: {error}",
                    }
                )
    index = None
    if root.is_dir():
        with tempfile.TemporaryDirectory() as temporary:
            copy = Path(temporary) / "project"
            (copy / ".idc").mkdir(parents=True)
            shutil.copytree(root, copy / ".idc" / "work-items")
            index = rebuild_index(copy)
    return {"records": records, "index": index}


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--now", required=True)
    parser.add_argument("--out", required=True, type=Path)
    parser.add_argument("--project", action="append", required=True, type=Path)
    args = parser.parse_args()
    now = datetime.fromisoformat(args.now)
    report = {
        "now": args.now,
        "projects": [
            {"project": str(project.resolve()), "data": dump_project(project.resolve(), now)}
            for project in args.project
        ],
    }
    args.out.write_text(json.dumps(report, ensure_ascii=False), encoding="utf-8")
    print(f"wrote {args.out} ({sum(len(item['data']['records']) for item in report['projects'])} records)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
