import json
import tempfile
import unittest
from pathlib import Path

from idc_core.cli import initialize, load_config, migrate_project
from idc_core.events import EventStore
from idc_core.workflow import GateBlocked, Workflow


class ProtocolV12Tests(unittest.TestCase):
    def test_initialize_writes_v12_config_and_v2_events(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            project = Path(temp_dir)
            initialize(project, "LAS", adapter="opencode")

            config = json.loads((project / ".idc" / "config.json").read_text(encoding="utf-8"))
            record = EventStore(project).capture("Protocol check")
            event = EventStore(project).read(record.record_id)[0]

            self.assertEqual(config["idc_version"], "1.2.0")
            self.assertEqual(config["schema_version"], 2)
            self.assertEqual(event["schema_version"], 2)

    def test_old_config_is_readable_only_and_rejects_writes(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            project = Path(temp_dir)
            (project / ".idc").mkdir()
            (project / ".idc" / "config.json").write_text(
                json.dumps({"schema_version": 1, "idc_version": "1.1.1", "project_key": "LAS"}),
                encoding="utf-8",
            )

            report = migrate_project(project, check_only=True)

            self.assertEqual(report["status"], "ready")
            self.assertEqual(load_config(project)["schema_version"], 1)
            self.assertEqual(
                json.loads((project / ".idc" / "config.json").read_text(encoding="utf-8"))["schema_version"],
                1,
            )

    def test_captured_task_cannot_enter_implementation_lifecycle(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            workflow = Workflow(Path(temp_dir))
            record = workflow.start("Implement the report export")
            with self.assertRaisesRegex(GateBlocked, "lifecycle:captured->active"):
                workflow.transition(record, "active")

    def test_confirmed_migration_does_not_mix_schema_one_history(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            project = Path(temp_dir)
            (project / ".idc" / "work-items" / "work-old").mkdir(parents=True)
            (project / ".idc" / "config.json").write_text(
                json.dumps({"schema_version": 1, "idc_version": "1.1.1", "project_key": "LAS"}),
                encoding="utf-8",
            )
            (project / ".idc" / "work-items" / "work-old" / "events.jsonl").write_text(
                json.dumps({"schema_version": 1, "record_id": "work-old", "seq": 0, "payload": {}}) + "\n",
                encoding="utf-8",
            )

            report = migrate_project(project, check_only=False)

            self.assertEqual(report["status"], "blocked")
            self.assertEqual(load_config(project)["schema_version"], 1)


if __name__ == "__main__":
    unittest.main()
