#!/usr/bin/env python3
"""Compatibility local entry point; the implementation lives in idc_core.inspect_cli."""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from idc_core.inspect_cli import main

if __name__ == "__main__":
    raise SystemExit(main())
