import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from idc_core.metrics import build_progressive_metrics


ROOT = Path(__file__).resolve().parents[1]
IDC = ROOT / "scripts" / "idc.py"


class ProgressiveMetricsTests(unittest.TestCase):
    def run_idc(self, *args: str) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            [sys.executable, str(IDC), *args],
            cwd=ROOT,
            capture_output=True,
            text=True,
            check=False,
        )

    def test_metrics_summarize_event_first_records_without_mutating_them(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            project = Path(temp_dir) / "project"
            project.mkdir()
            self.run_idc("init", "--project", str(project), "--project-key", "LAS")
            started = self.run_idc(
                "start", "--project", str(project), "--summary", "Metrics task", "--json"
            )
            record_id = json.loads(started.stdout)["record_id"]
            self.run_idc("promote", "--project", str(project), "--record", record_id)
            self.run_idc(
                "shape", "--project", str(project), "--record", record_id,
                "--goal", "Measure work", "--acceptance", "Report exists",
            )
            self.run_idc(
                "change", "--project", str(project), "--record", record_id,
                "--before", "Report", "--after", "Report and trend", "--reason", "Need trend",
            )
            events_path = project / ".idc" / "work-items" / record_id / "events.jsonl"
            before = events_path.read_text(encoding="utf-8")

            report = build_progressive_metrics(project)

            self.assertEqual(report["scope"], ".idc progressive event log only")
            self.assertEqual(report["totals"]["records"], 1)
            self.assertGreaterEqual(report["totals"]["events"], 4)
            self.assertEqual(report["totals"]["requirement_changes"], 1)
            self.assertEqual(report["records"][0]["record_id"], record_id)
            self.assertEqual(report["records"][0]["capture_mode"], "durable")
            self.assertEqual(report["records"][0]["task_id"].startswith("IDC-LAS-"), True)
            self.assertEqual(events_path.read_text(encoding="utf-8"), before)

    def test_metrics_cli_emits_json_for_one_explicit_project(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            project = Path(temp_dir) / "project"
            project.mkdir()
            self.run_idc("init", "--project", str(project), "--project-key", "LAS")
            result = self.run_idc(
                "metrics", "--project", str(project), "--json"
            )

            self.assertEqual(result.returncode, 0, result.stderr)
            report = json.loads(result.stdout)
            self.assertEqual(report["project"], str(project.resolve()))
            self.assertEqual(report["totals"]["records"], 0)

    def test_portfolio_progressive_metrics_accepts_project_alias(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            project = Path(temp_dir) / "project"
            project.mkdir()
            self.run_idc("init", "--project", str(project), "--project-key", "LAS")
            result = self.run_idc(
                "portfolio", "--progressive-metrics", "--project", str(project), "--json"
            )

            self.assertEqual(result.returncode, 0, result.stderr)
            report = json.loads(result.stdout)
            self.assertEqual(report["totals"]["records"], 0)

