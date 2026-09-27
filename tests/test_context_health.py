import tempfile
import unittest
from pathlib import Path

from idc_core.context_health import inspect_context


class ContextHealthTests(unittest.TestCase):
    def test_initialized_project_reports_missing_context_layers(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            project = Path(temp_dir)
            (project / ".idc").mkdir()
            (project / ".idc" / "config.json").write_text("{}", encoding="utf-8")

            report = inspect_context(project)

            self.assertFalse(report["ready"])
            self.assertEqual(report["layers"]["persistent_entry"]["status"], "missing")
            self.assertEqual(report["layers"]["on_demand_methods"]["status"], "missing")
            self.assertEqual(report["layers"]["task_evidence"]["status"], "missing")

    def test_context_health_accepts_a_project_specific_three_layer_setup(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            project = Path(temp_dir)
            (project / ".idc" / "work-items").mkdir(parents=True)
            (project / ".idc" / "tasks").mkdir()
            (project / ".agents" / "skills").mkdir(parents=True)
            (project / "AGENTS.md").write_text("Project architecture and boundaries\n", encoding="utf-8")
            (project / "IDC.md").write_text("Read AGENTS.md and the playbook.\n", encoding="utf-8")
            (project / "AI_ENGINEERING_PLAYBOOK.md").write_text("Verification and workflow rules.\n", encoding="utf-8")
            (project / "SQUADS.md").write_text("Accepted squads and handoffs.\n", encoding="utf-8")
            (project / ".idc" / "config.json").write_text("{}", encoding="utf-8")

            report = inspect_context(project)

            self.assertTrue(report["ready"])
            self.assertTrue(all(layer["status"] == "ready" for layer in report["layers"].values()))


if __name__ == "__main__":
    unittest.main()
