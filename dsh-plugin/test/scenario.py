"""Run a deterministic IDC workflow with the Python reference implementation.

Usage: python scenario.py <project-dir>

Prints one JSON object with the resulting events, card and index. The project
must be empty (the script creates `.idc` through the normal write path).
"""

from __future__ import annotations

import json
import sys
from datetime import datetime, timezone
from pathlib import Path

from idc_core.render import render_card
from idc_core.workflow import Workflow


def main() -> int:
    project = Path(sys.argv[1])
    now = datetime(2026, 10, 18, 6, 0, 0, tzinfo=timezone.utc)
    workflow = Workflow(project, clock=lambda: now)
    record_id = workflow.start("Port the IDC protocol", scenes=["META"])
    task_id = workflow.promote(record_id, "IDC")
    workflow.shape(
        record_id,
        goal="Port the IDC protocol to a DSH plugin",
        explicit=["No Python runtime dependency"],
        scope=["dsh-plugin/"],
        acceptance=[{"id": "a1", "statement": "JS and Python produce the same card"}],
        classifications=["META"],
        uncertainty=["cross-boundary"],
        impacts={"external_effect": "none", "reversibility": "low"},
        open_decisions=["d1", "d2"],
    )
    workflow.resolve_decision(record_id, decision="d1", resolution="Native port")
    workflow.resolve_decision(record_id, decision="d2", resolution="Single writer")
    workflow.record_activity(record_id, "design")
    workflow.transition(record_id, "active")
    workflow.record_activity(record_id, "build")
    workflow.add_evidence(
        record_id,
        kind="command-evidence",
        summary="node --test test/parity.test.mjs",
        result="pass",
        acceptance_ids=["a1"],
        reference="test/parity.test.mjs",
    )
    workflow.record_activity(record_id, "verify")
    workflow.transition(record_id, "validating")
    workflow.close(record_id, outcome="completed", summary="Parity recorded")
    workflow.review_learning(record_id, outcome="none", reason="No reusable lesson")
    state = workflow.state(record_id)
    index = json.loads((project / ".idc" / "index" / "tasks.json").read_text(encoding="utf-8"))
    print(
        json.dumps(
            {
                "record_id": record_id,
                "task_id": task_id,
                "events": [json.loads(line) for line in (project / ".idc" / "work-items" / record_id / "events.jsonl").read_text(encoding="utf-8").splitlines() if line.strip()],
                "card": render_card(state),
                "index": index,
            },
            ensure_ascii=False,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
