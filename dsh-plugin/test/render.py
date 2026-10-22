"""Render one record written by the JS plugin using the Python reference core.

Usage: python render.py <project-dir> <record-id>

This is the interoperability direction that matters: a log written by the
plugin must be readable and renderable by the reference implementation.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

from idc_core.events import EventStore
from idc_core.projector import fold_events
from idc_core.render import render_card


def main() -> int:
    project = Path(sys.argv[1])
    record_id = sys.argv[2]
    events = EventStore(project).read(record_id)
    state = fold_events(events)
    print(json.dumps({"card": render_card(state), "lifecycle": state.lifecycle}, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
