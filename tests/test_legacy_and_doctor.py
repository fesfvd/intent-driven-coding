import hashlib
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
IDC = ROOT / "scripts" / "idc.py"


class LegacyAndDoctorTests(unittest.TestCase):
    def run_idc(self, *args: str) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            [sys.executable, str(IDC), *args],
            cwd=ROOT,
            capture_output=True,
            text=True,
            check=False,
        )

    def test_legacy_import_preserves_source_and_creates_one_reconstructed_snapshot(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            project = Path(temp_dir) / "project"
            tasks = project / ".idc" / "tasks"
            tasks.mkdir(parents=True)
            source = tasks / "IDC-LAS-FEAT-20260911-001.md"
            source.write_text(
                """# IDC Task Card

- Task ID: `IDC-LAS-FEAT-20260911-001`
- Title: Add sponsor tier
- Status: `COMPLETE`
- Scenario: `FEAT`
- Current phase: `VERIFY`

- [ ] Price confirmed
""",
                encoding="utf-8",
            )
            before = hashlib.sha256(source.read_bytes()).hexdigest()
            self.run_idc("init", "--project", str(project), "--project-key", "LAS")

            imported = self.run_idc(
                "import-legacy", "--project", str(project), "--path", str(source), "--json"
            )

            self.assertEqual(imported.returncode, 0, imported.stderr)
            report = json.loads(imported.stdout)
            self.assertEqual(report["legacy_task_id"], "IDC-LAS-FEAT-20260911-001")
            self.assertIn("complete-with-unchecked-items", report["contradictions"])
            self.assertEqual(hashlib.sha256(source.read_bytes()).hexdigest(), before)
            events_path = (
                project / ".idc" / "work-items" / report["record_id"] / "events.jsonl"
            )
            events = [json.loads(line) for line in events_path.read_text(encoding="utf-8").splitlines()]
            self.assertEqual([event["type"] for event in events], ["legacy.snapshot-imported"])
            self.assertEqual(events[0]["provenance"], "reconstructed")

    def test_doctor_uses_an_isolated_round_trip_and_leaves_no_work_item(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            project = Path(temp_dir) / "project"
            project.mkdir()
            self.run_idc("init", "--project", str(project), "--project-key", "LAS")

            checked = self.run_idc("doctor", "--project", str(project), "--json")

            self.assertEqual(checked.returncode, 0, checked.stderr)
            report = json.loads(checked.stdout)
            self.assertEqual(report["status"], "pass")
            self.assertTrue(report["checks"]["event_round_trip"])
            work_items = project / ".idc" / "work-items"
            self.assertFalse(work_items.exists() and any(work_items.iterdir()))


if __name__ == "__main__":
    unittest.main()
