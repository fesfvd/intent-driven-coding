import json
import tempfile
import unittest
from datetime import datetime, timezone
from pathlib import Path

from idc_core.learning import check_learning_cadence, record_learning_session


class LearningCadenceTests(unittest.TestCase):
    def test_learning_check_is_quiet_before_the_project_review_window(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            project = Path(temp_dir)
            (project / ".idc").mkdir()
            (project / ".idc" / "config.json").write_text(json.dumps({"project_key": "X"}), encoding="utf-8")

            report = check_learning_cadence(project, now=datetime(2026, 9, 27, tzinfo=timezone.utc))

            self.assertEqual(report["status"], "quiet")
            self.assertEqual(report["reason"], "no completed work since the last review")

    def test_learning_check_becomes_due_after_completed_work_accumulates(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            project = Path(temp_dir)
            work_items = project / ".idc" / "work-items"
            work_items.mkdir(parents=True)
            (project / ".idc" / "config.json").write_text(
                json.dumps({"project_key": "X", "learning": {"completed_task_threshold": 2, "max_days": 30}}),
                encoding="utf-8",
            )
            for number in (1, 2):
                record = work_items / f"work-{number}"
                record.mkdir()
                events = [
                    {"record_id": f"work-{number}", "seq": 0, "type": "request.captured", "payload": {"summary": "done"}, "timestamp": "2026-09-20T00:00:00+00:00"},
                    {"record_id": f"work-{number}", "seq": 1, "type": "task.closed", "payload": {"outcome": "completed"}, "timestamp": "2026-09-21T00:00:00+00:00"},
                ]
                (record / "events.jsonl").write_text("\n".join(json.dumps(item) for item in events) + "\n", encoding="utf-8")

            report = check_learning_cadence(project, now=datetime(2026, 9, 27, tzinfo=timezone.utc))

            self.assertEqual(report["status"], "due")
            self.assertEqual(report["completed_since_review"], 2)
            self.assertIn("completed task threshold", report["reason"])

    def test_recording_a_learning_session_resets_the_window(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            project = Path(temp_dir)
            (project / ".idc").mkdir()

            report = record_learning_session(
                project,
                now=datetime(2026, 9, 27, tzinfo=timezone.utc),
                summary="Merged repeated export lessons and retired stale guidance",
            )

            self.assertEqual(report["status"], "recorded")
            self.assertEqual(check_learning_cadence(project, now=datetime(2026, 9, 27, tzinfo=timezone.utc))["status"], "quiet")

    def test_learning_session_keeps_minimal_previous_session_history(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            project = Path(temp_dir)
            (project / ".idc").mkdir()
            first = datetime(2026, 9, 20, tzinfo=timezone.utc)
            second = datetime(2026, 9, 27, tzinfo=timezone.utc)

            record_learning_session(project, now=first, summary="First review")
            report = record_learning_session(project, now=second, summary="Second review")

            self.assertEqual(report["session_count"], 2)
            self.assertEqual(report["previous_review_at"], first.isoformat())
            state = json.loads((project / ".idc" / "learning-state.json").read_text(encoding="utf-8"))
            self.assertEqual(state["summary"], "Second review")
