import json
from datetime import datetime
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
IDC = ROOT / "scripts" / "idc.py"


class ProgressiveCliTests(unittest.TestCase):
    def run_idc(self, *args: str) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            [sys.executable, str(IDC), *args],
            cwd=ROOT,
            capture_output=True,
            text=True,
            check=False,
        )

    def test_cli_runs_a_progressive_task_from_capture_to_completion(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            project = Path(temp_dir) / "project"
            project.mkdir()

            initialized = self.run_idc(
                "init", "--project", str(project), "--project-key", "LAS", "--json"
            )
            self.assertEqual(initialized.returncode, 0, initialized.stderr)
            self.assertEqual(json.loads(initialized.stdout)["project_key"], "LAS")

            started = self.run_idc(
                "start",
                "--project",
                str(project),
                "--summary",
                "Add PDF export",
                "--actor",
                "human",
                "--json",
            )
            self.assertEqual(started.returncode, 0, started.stderr)
            record_id = json.loads(started.stdout)["record_id"]

            promoted = self.run_idc(
                "promote", "--project", str(project), "--record", record_id, "--json"
            )
            self.assertEqual(promoted.returncode, 0, promoted.stderr)
            task_id = json.loads(promoted.stdout)["task_id"]
            self.assertRegex(task_id, r"^IDC-LAS-\d{8}-001$")

            shaped = self.run_idc(
                "shape",
                "--project",
                str(project),
                "--record",
                record_id,
                "--goal",
                "Users can download a PDF report",
                "--explicit",
                "Add PDF export",
                "--fact",
                "Reports have a print view",
                "--default",
                "Reuse the print layout",
                "--scope",
                "report export",
                "--acceptance",
                "pdf=PDF downloads",
                "--class",
                "FEAT",
                "--impact",
                "behavior=medium",
                "--json",
            )
            self.assertEqual(shaped.returncode, 0, shaped.stderr)
            self.assertEqual(json.loads(shaped.stdout)["lifecycle"], "shaped")

            for target in ("active", "validating"):
                transitioned = self.run_idc(
                    "transition",
                    "--project",
                    str(project),
                    "--record",
                    record_id,
                    "--to",
                    target,
                    "--json",
                )
                self.assertEqual(transitioned.returncode, 0, transitioned.stderr)

            evidence = self.run_idc(
                "add-evidence",
                "--project",
                str(project),
                "--record",
                record_id,
                "--kind",
                "command-evidence",
                "--summary",
                "Export regression passed",
                "--result",
                "pass",
                "--acceptance",
                "pdf",
                "--json",
            )
            self.assertEqual(evidence.returncode, 0, evidence.stderr)

            closed = self.run_idc(
                "close",
                "--project",
                str(project),
                "--record",
                record_id,
                "--outcome",
                "completed",
                "--summary",
                "PDF export implemented",
                "--json",
            )
            self.assertEqual(closed.returncode, 0, closed.stderr)
            self.assertEqual(json.loads(closed.stdout)["lifecycle"], "closed")

            shown = self.run_idc(
                "show", "--project", str(project), "--record", record_id, "--json"
            )
            state = json.loads(shown.stdout)
            self.assertEqual(state["task_id"], task_id)
            self.assertEqual(state["outcome"], "completed")
            self.assertTrue((project / ".idc" / "tasks" / f"{task_id}.md").is_file())

    def test_init_records_the_selected_thin_host_adapter(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            project = Path(temp_dir) / "project"
            project.mkdir()

            initialized = self.run_idc(
                "init",
                "--project",
                str(project),
                "--project-key",
                "sample",
                "--platform",
                "codex",
                "--json",
            )

            self.assertEqual(initialized.returncode, 0, initialized.stderr)
            self.assertEqual(json.loads(initialized.stdout)["adapter"], "codex")
            config = json.loads((project / ".idc" / "config.json").read_text(encoding="utf-8"))
            self.assertEqual(config["adapter"], "codex")

    def test_shape_auto_numbers_plain_text_acceptance_items(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            project = Path(temp_dir) / "project"
            project.mkdir()
            self.run_idc("init", "--project", str(project), "--project-key", "LAS")
            started = self.run_idc("start", "--project", str(project), "--summary", "Plain acceptance", "--json")
            record_id = json.loads(started.stdout)["record_id"]
            self.run_idc("promote", "--project", str(project), "--record", record_id)
            result = self.run_idc(
                "shape", "--project", str(project), "--record", record_id,
                "--goal", "Do the thing", "--acceptance", "Thing works",
                "--acceptance", "Nothing leaks", "--json",
            )
            self.assertEqual(result.returncode, 0, result.stderr)
            acceptance = json.loads(result.stdout)["acceptance"]
            self.assertEqual(acceptance, [
                {"id": "a-001", "statement": "Thing works"},
                {"id": "a-002", "statement": "Nothing leaks"},
            ])

    def test_new_plain_acceptance_items_do_not_renumber_existing_items(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            project = Path(temp_dir) / "project"
            project.mkdir()
            self.run_idc("init", "--project", str(project), "--project-key", "LAS")
            record_id = json.loads(self.run_idc(
                "start", "--project", str(project), "--summary", "Stable acceptance", "--json"
            ).stdout)["record_id"]
            self.run_idc("promote", "--project", str(project), "--record", record_id)
            base = self.run_idc(
                "shape", "--project", str(project), "--record", record_id,
                "--goal", "Goal", "--acceptance", "First", "--json"
            )
            self.assertEqual(json.loads(base.stdout)["acceptance"][0]["id"], "a-001")
            revised = self.run_idc(
                "shape", "--project", str(project), "--record", record_id,
                "--goal", "Goal", "--acceptance", "First", "--acceptance", "Second", "--json"
            )
            self.assertEqual(revised.returncode, 0, revised.stderr)
            self.assertEqual([item["id"] for item in json.loads(revised.stdout)["acceptance"]], ["a-001", "a-002"])

    def test_plain_acceptance_append_preserves_existing_items(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            project = Path(temp_dir) / "project"
            project.mkdir()
            self.run_idc("init", "--project", str(project), "--project-key", "LAS")
            record_id = json.loads(self.run_idc(
                "start", "--project", str(project), "--summary", "Append acceptance", "--json"
            ).stdout)["record_id"]
            self.run_idc("promote", "--project", str(project), "--record", record_id)
            self.run_idc(
                "shape", "--project", str(project), "--record", record_id,
                "--goal", "Goal", "--acceptance", "First", "--json",
            )
            revised = self.run_idc(
                "shape", "--project", str(project), "--record", record_id,
                "--goal", "Goal", "--acceptance", "Second", "--json",
            )
            self.assertEqual(revised.returncode, 0, revised.stderr)
            self.assertEqual(json.loads(revised.stdout)["acceptance"], [
                {"id": "a-001", "statement": "First"},
                {"id": "a-002", "statement": "Second"},
            ])


    def test_temporary_capture_can_be_discarded_from_cli(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            project = Path(temp_dir) / "project"
            project.mkdir()
            self.run_idc("init", "--project", str(project), "--project-key", "LAS")
            started = self.run_idc(
                "start", "--project", str(project), "--summary", "Temporary", "--temporary", "--json"
            )
            record_id = json.loads(started.stdout)["record_id"]
            discarded = self.run_idc(
                "discard", "--project", str(project), "--record", record_id,
                "--reason", "Not needed", "--json"
            )
            self.assertEqual(discarded.returncode, 0, discarded.stderr)
            self.assertEqual(json.loads(discarded.stdout)["capture_disposition"], "discarded")

    def test_temporary_capture_uses_project_ttl_configuration(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            project = Path(temp_dir) / "project"
            project.mkdir()
            self.run_idc("init", "--project", str(project), "--project-key", "LAS")
            config_path = project / ".idc" / "config.json"
            config = json.loads(config_path.read_text(encoding="utf-8"))
            config["capture_ttl_hours"] = 5
            config_path.write_text(json.dumps(config), encoding="utf-8")
            started = self.run_idc(
                "start", "--project", str(project), "--summary", "Configured", "--temporary", "--json"
            )
            self.assertEqual(started.returncode, 0, started.stderr)
            record_id = json.loads(started.stdout)["record_id"]
            shown = self.run_idc("show", "--project", str(project), "--record", record_id, "--json")
            state = json.loads(shown.stdout)
            events = json.loads((project / ".idc" / "work-items" / record_id / "events.jsonl").read_text(encoding="utf-8").splitlines()[0])
            delta = datetime.fromisoformat(state["expires_at"]) - datetime.fromisoformat(events["timestamp"])
            self.assertAlmostEqual(delta.total_seconds(), 5 * 3600, delta=2)

    def test_explicit_temporary_ttl_overrides_project_configuration(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            project = Path(temp_dir) / "project"
            project.mkdir()
            self.run_idc("init", "--project", str(project), "--project-key", "LAS")
            config_path = project / ".idc" / "config.json"
            config = json.loads(config_path.read_text(encoding="utf-8"))
            config["capture_ttl_hours"] = 5
            config_path.write_text(json.dumps(config), encoding="utf-8")
            started = self.run_idc(
                "start", "--project", str(project), "--summary", "Override", "--temporary",
                "--ttl-hours", "2", "--json",
            )
            record_id = json.loads(started.stdout)["record_id"]
            shown = self.run_idc("show", "--project", str(project), "--record", record_id, "--json")
            state = json.loads(shown.stdout)
            events = json.loads((project / ".idc" / "work-items" / record_id / "events.jsonl").read_text(encoding="utf-8").splitlines()[0])
            delta = datetime.fromisoformat(state["expires_at"]) - datetime.fromisoformat(events["timestamp"])
            self.assertAlmostEqual(delta.total_seconds(), 2 * 3600, delta=2)

    def test_temporary_capture_rejects_nonpositive_ttl(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            project = Path(temp_dir) / "project"
            project.mkdir()
            self.run_idc("init", "--project", str(project), "--project-key", "LAS")
            result = self.run_idc(
                "start", "--project", str(project), "--summary", "Invalid", "--temporary",
                "--ttl-hours", "0", "--json",
            )
            self.assertEqual(result.returncode, 2)
            self.assertIn("ttl", json.loads(result.stdout)["error"])

    def test_cli_cannot_self_declare_human_confirmation(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            project = Path(temp_dir) / "project"
            project.mkdir()
            self.run_idc("init", "--project", str(project), "--project-key", "LAS")
            record_id = json.loads(self.run_idc("start", "--project", str(project), "--summary", "Evidence", "--json").stdout)["record_id"]
            result = self.run_idc(
                "add-evidence", "--project", str(project), "--record", record_id,
                "--kind", "human-confirmed", "--summary", "Claim", "--result", "pass",
                "--confirmation-ref", "fake", "--json"
            )
            self.assertEqual(result.returncode, 2)
            self.assertIn("human actor", json.loads(result.stdout)["error"])

    def test_cli_reports_gate_blocks_without_writing_transition(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            project = Path(temp_dir) / "project"
            project.mkdir()
            self.run_idc("init", "--project", str(project), "--project-key", "LAS")
            started = self.run_idc(
                "start", "--project", str(project), "--summary", "Publish private report", "--json"
            )
            record_id = json.loads(started.stdout)["record_id"]
            self.run_idc("promote", "--project", str(project), "--record", record_id)
            self.run_idc(
                "shape",
                "--project",
                str(project),
                "--record",
                record_id,
                "--goal",
                "Publish report",
                "--decision",
                "Whether source text becomes public",
                "--scope",
                "publication",
                "--acceptance",
                "publish=Report is public",
                "--impact",
                "privacy=high",
            )

            result = self.run_idc(
                "transition",
                "--project",
                str(project),
                "--record",
                record_id,
                "--to",
                "active",
                "--json",
            )

            self.assertEqual(result.returncode, 3)
            self.assertIn("decision:open", json.loads(result.stdout)["hard_blocks"])
            shown = self.run_idc(
                "show", "--project", str(project), "--record", record_id, "--json"
            )
            self.assertEqual(json.loads(shown.stdout)["lifecycle"], "shaped")

    def test_cli_records_change_and_permissioned_ship_as_events(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            project = Path(temp_dir) / "project"
            project.mkdir()
            self.run_idc("init", "--project", str(project), "--project-key", "LAS")
            started = self.run_idc(
                "start", "--project", str(project), "--summary", "Deploy report update", "--json"
            )
            record_id = json.loads(started.stdout)["record_id"]
            self.run_idc("promote", "--project", str(project), "--record", record_id)
            self.run_idc("transition", "--project", str(project), "--record", record_id, "--to", "active")

            changed = self.run_idc(
                "change",
                "--project",
                str(project),
                "--record",
                record_id,
                "--before",
                "Deploy Web",
                "--after",
                "Deploy Web and Worker",
                "--reason",
                "Worker uses the changed contract",
                "--actor",
                "human",
                "--json",
            )
            self.assertEqual(changed.returncode, 0, changed.stderr)
            self.assertEqual(json.loads(changed.stdout)["lifecycle"], "shaped")

            self.run_idc(
                "shape",
                "--project",
                str(project),
                "--record",
                record_id,
                "--goal",
                "Deploy Web and Worker",
                "--scope",
                "production",
                "--acceptance",
                "health=Both services are healthy",
                "--impact",
                "external_effect=high",
                "--impact",
                "reversibility=medium",
            )
            blocked = self.run_idc(
                "activity",
                "--project",
                str(project),
                "--record",
                record_id,
                "--name",
                "ship",
                "--json",
            )
            self.assertEqual(blocked.returncode, 3)

            granted = self.run_idc(
                "permission",
                "--project",
                str(project),
                "--record",
                record_id,
                "--effect",
                "deploy:production",
                "--state",
                "granted",
                "--json",
            )
            self.assertEqual(granted.returncode, 0, granted.stderr)
            self.run_idc(
                "recovery",
                "--project",
                str(project),
                "--record",
                record_id,
                "--summary",
                "Roll back both services",
            )
            shipped = self.run_idc(
                "activity",
                "--project",
                str(project),
                "--record",
                record_id,
                "--name",
                "ship",
                "--json",
            )
            self.assertEqual(shipped.returncode, 0, shipped.stderr)
            self.assertEqual(json.loads(shipped.stdout)["activities"], ["ship"])

    def test_cli_reclassifies_and_resolves_a_blocking_decision(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            project = Path(temp_dir) / "project"
            project.mkdir()
            self.run_idc("init", "--project", str(project), "--project-key", "LAS")
            started = self.run_idc(
                "start", "--project", str(project), "--summary", "Investigate access failure", "--json"
            )
            record_id = json.loads(started.stdout)["record_id"]
            self.run_idc("promote", "--project", str(project), "--record", record_id)
            self.run_idc(
                "shape",
                "--project",
                str(project),
                "--record",
                record_id,
                "--goal",
                "Restore valid access",
                "--decision",
                "Whether anonymous access is intended",
                "--scope",
                "access policy",
                "--acceptance",
                "allowed=Allowed users retain access",
                "--class",
                "FIX",
            )

            classified = self.run_idc(
                "classify",
                "--project",
                str(project),
                "--record",
                record_id,
                "--class",
                "SEC",
                "--reason",
                "Repository evidence shows a trust boundary",
                "--json",
            )
            self.assertEqual(classified.returncode, 0, classified.stderr)
            self.assertEqual(json.loads(classified.stdout)["classifications"], ["SEC"])

            resolved = self.run_idc(
                "resolve-decision",
                "--project",
                str(project),
                "--record",
                record_id,
                "--decision",
                "Whether anonymous access is intended",
                "--resolution",
                "Anonymous access is denied",
                "--actor",
                "human",
                "--json",
            )
            self.assertEqual(resolved.returncode, 0, resolved.stderr)
            self.assertEqual(json.loads(resolved.stdout)["open_decisions"], [])
            active = self.run_idc(
                "transition",
                "--project",
                str(project),
                "--record",
                record_id,
                "--to",
                "active",
            )
            self.assertEqual(active.returncode, 0, active.stderr)

    def test_cli_records_and_clears_an_emergency_condition(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            project = Path(temp_dir) / "project"
            project.mkdir()
            self.run_idc("init", "--project", str(project), "--project-key", "LAS")
            started = self.run_idc(
                "start", "--project", str(project), "--summary", "Restore production", "--json"
            )
            record_id = json.loads(started.stdout)["record_id"]

            active = self.run_idc(
                "condition",
                "--project",
                str(project),
                "--record",
                record_id,
                "--name",
                "emergency",
                "--state",
                "active",
                "--reason",
                "Production unavailable",
                "--json",
            )
            self.assertEqual(active.returncode, 0, active.stderr)
            self.assertEqual(json.loads(active.stdout)["conditions"], ["emergency"])

            cleared = self.run_idc(
                "condition",
                "--project",
                str(project),
                "--record",
                record_id,
                "--name",
                "emergency",
                "--state",
                "cleared",
                "--reason",
                "Service restored",
                "--json",
            )
            self.assertEqual(cleared.returncode, 0, cleared.stderr)
            self.assertEqual(json.loads(cleared.stdout)["conditions"], [])


if __name__ == "__main__":
    unittest.main()
