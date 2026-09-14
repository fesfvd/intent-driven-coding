import tempfile
import unittest
from datetime import datetime, timedelta, timezone
from pathlib import Path


from idc_core.workflow import GateBlocked, Workflow


NOW = datetime(2026, 9, 14, 5, 0, tzinfo=timezone.utc)


class ProgressiveWorkflowTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp_dir = tempfile.TemporaryDirectory()
        self.project = Path(self.temp_dir.name)
        self.workflow = Workflow(self.project, clock=lambda: NOW)
        self.record = self.workflow.start("Add report export", actor="human")
        self.task_id = self.workflow.promote(self.record, project_key="LAS")

    def tearDown(self) -> None:
        self.temp_dir.cleanup()

    def test_low_risk_work_can_start_with_progressive_warnings(self) -> None:
        result = self.workflow.transition(self.record, "active")

        self.assertEqual(result.state.lifecycle, "active")
        self.assertIn("intent:goal", result.warnings)
        self.assertIn("acceptance", result.warnings)

    def test_temporary_capture_expires_without_creating_a_task_card(self) -> None:
        current = [NOW]
        workflow = Workflow(self.project, clock=lambda: current[0])
        record = workflow.start("Temporary thought", actor="human", temporary=True, ttl_hours=1)
        state = workflow.state(record)
        self.assertEqual(state.capture_mode, "temporary")
        self.assertIsNone(state.task_id)
        self.assertEqual(list((self.project / ".idc" / "tasks").glob("*.md")), [
            self.project / ".idc" / "tasks" / f"{self.task_id}.md"
        ])
        current[0] = NOW + timedelta(hours=2)
        expired = workflow.state(record)
        self.assertEqual(expired.capture_disposition, "expired")
        self.assertEqual(expired.events[-1]["type"], "capture.expired")

    def test_discarded_temporary_capture_cannot_be_promoted(self) -> None:
        workflow = Workflow(self.project, clock=lambda: NOW)
        record = workflow.start("Discard me", temporary=True)
        workflow.discard(record, reason="No longer needed")
        with self.assertRaisesRegex(ValueError, "discarded"):
            workflow.promote(record, project_key="LAS")

    def test_temporary_capture_rejects_nonpositive_ttl_at_api_boundary(self) -> None:
        with self.assertRaisesRegex(ValueError, "ttl"):
            self.workflow.start("Invalid temporary", temporary=True, ttl_hours=0)

    def test_human_confirmed_evidence_requires_human_actor_and_reference(self) -> None:
        workflow = Workflow(self.project, clock=lambda: NOW)
        record = workflow.start("Confirm evidence")
        with self.assertRaisesRegex(ValueError, "human-confirmed"):
            workflow.add_evidence(
                record,
                kind="human-confirmed",
                summary="Agent claim",
                result="pass",
                actor="agent",
            )
        with self.assertRaisesRegex(ValueError, "confirmation"):
            workflow.add_evidence(
                record,
                kind="human-confirmed",
                summary="Human confirmed",
                result="pass",
                actor="human",
            )
        state = workflow.add_evidence(
            record,
            kind="human-confirmed",
            summary="Human confirmed",
            result="pass",
            actor="human",
            confirmation_ref="user-message-1",
        )
        self.assertEqual(state.evidence[-1]["confirmation_ref"], "user-message-1")

    def test_open_product_decision_blocks_active_work_unless_emergency(self) -> None:
        self.workflow.shape(
            self.record,
            goal="Users can export reports",
            explicit=["Add export"],
            open_decisions=["Should private source text be included?"],
            scope=["report export"],
            acceptance=[{"id": "export", "statement": "An export file is downloaded"}],
            impacts={"privacy": "high"},
        )

        with self.assertRaisesRegex(GateBlocked, "decision:open"):
            self.workflow.transition(self.record, "active")

        self.workflow.set_condition(self.record, "emergency", True, reason="Restore production")
        result = self.workflow.transition(self.record, "active")
        self.assertIn("decision:open", result.warnings)

    def test_completed_requires_evidence_for_each_acceptance_item(self) -> None:
        self.workflow.shape(
            self.record,
            goal="Users can export reports",
            explicit=["Add export"],
            scope=["report export"],
            acceptance=[
                {"id": "pdf", "statement": "PDF downloads"},
                {"id": "private", "statement": "Private source remains excluded"},
            ],
            impacts={"behavior": "medium", "privacy": "medium"},
        )
        self.workflow.transition(self.record, "active")
        self.workflow.transition(self.record, "validating")
        self.workflow.add_evidence(
            self.record,
            kind="command-evidence",
            summary="PDF regression test passed",
            result="pass",
            acceptance_ids=["pdf"],
        )

        with self.assertRaisesRegex(GateBlocked, "acceptance:private"):
            self.workflow.close(self.record, outcome="completed", summary="Implemented export")

        self.workflow.add_evidence(
            self.record,
            kind="command-evidence",
            summary="Privacy regression passed",
            result="pass",
            acceptance_ids=["private"],
        )
        result = self.workflow.close(self.record, outcome="completed", summary="Implemented export")
        self.assertEqual(result.state.lifecycle, "closed")
        self.assertEqual(result.state.outcome, "completed")

    def test_promoted_record_is_rendered_as_generated_markdown(self) -> None:
        self.workflow.shape(
            self.record,
            goal="Users can export reports",
            explicit=["Add export"],
            repository_facts=["Reports already have a print view"],
            proposed_defaults=["Use PDF first"],
            scope=["report export"],
            acceptance=[{"id": "pdf", "statement": "PDF downloads"}],
            classifications=["FEAT"],
            impacts={"behavior": "medium"},
        )

        card = self.project / ".idc" / "tasks" / f"{self.task_id}.md"
        text = card.read_text(encoding="utf-8")
        self.assertIn("AUTO-GENERATED", text)
        self.assertIn("Users can export reports", text)
        self.assertIn("FEAT", text)
        self.assertIn("Reports already have a print view", text)

    def test_closed_projection_marks_passing_acceptance_and_clears_obligations(self) -> None:
        self.workflow.shape(
            self.record,
            goal="Answer feasibility question",
            scope=["local experiment"],
            acceptance=[{"id": "answer", "statement": "Question is answered"}],
        )
        self.workflow.add_evidence(
            self.record,
            kind="command-evidence",
            summary="Feasibility check passed",
            result="pass",
            acceptance_ids=["answer"],
        )
        self.workflow.close(self.record, outcome="completed", summary="Answered")

        card = (self.project / ".idc" / "tasks" / f"{self.task_id}.md").read_text(encoding="utf-8")
        self.assertIn("- [x] `answer`", card)
        self.assertIn("- None\n\n## Event Log", card)

    def test_requirement_change_is_an_event_and_returns_work_to_shaping(self) -> None:
        self.workflow.transition(self.record, "active")

        state = self.workflow.change_requirement(
            self.record,
            before="Export PDF",
            after="Export PDF and DOCX",
            reason="User expanded the required formats",
            actor="human",
        )

        self.assertEqual(state.lifecycle, "shaped")
        self.assertEqual(state.requirement_changes[-1]["before"], "Export PDF")
        self.assertEqual(state.events[-1]["provenance"], "human-confirmed")

    def test_ship_activity_uses_permission_and_recovery_gates(self) -> None:
        self.workflow.shape(
            self.record,
            goal="Deploy release",
            scope=["production"],
            acceptance=[{"id": "live", "statement": "Service is healthy"}],
            impacts={"external_effect": "high", "reversibility": "medium"},
        )

        with self.assertRaisesRegex(GateBlocked, "permission:external-effect"):
            self.workflow.record_activity(self.record, "ship")

        self.workflow.permission(self.record, effect="deploy:production", state="granted", actor="human")
        self.workflow.record_recovery(self.record, "Roll back to the previous image")
        state = self.workflow.record_activity(self.record, "ship")
        self.assertEqual(state.activities[-1], "ship")

    def test_closed_task_cannot_reenter_active_lifecycle(self) -> None:
        self.workflow.shape(
            self.record,
            goal="Answer feasibility question",
            scope=["local experiment"],
            acceptance=[{"id": "answer", "statement": "Question is answered"}],
        )
        self.workflow.add_evidence(
            self.record,
            kind="artifact-evidence",
            summary="Experiment report",
            result="pass",
            acceptance_ids=["answer"],
        )
        self.workflow.close(self.record, outcome="completed", summary="Answered")

        with self.assertRaisesRegex(GateBlocked, "lifecycle:closed"):
            self.workflow.transition(self.record, "active")

    def test_partial_reshape_preserves_fields_that_are_not_supplied(self) -> None:
        self.workflow.shape(
            self.record,
            goal="Export PDF",
            explicit=["Add export"],
            repository_facts=["Print layout exists"],
            scope=["report export"],
            acceptance=[{"id": "pdf", "statement": "PDF downloads"}],
            classifications=["FEAT"],
            impacts={"behavior": "medium"},
        )

        state = self.workflow.shape(self.record, goal="Export PDF with page numbers")

        self.assertEqual(state.repository_facts, ["Print layout exists"])
        self.assertEqual(state.scope, ["report export"])
        self.assertEqual(state.acceptance[0]["id"], "pdf")
        self.assertEqual(state.classifications, ["FEAT"])
        self.assertEqual(state.impacts, {"behavior": "medium"})

    def test_lifecycle_allows_rework_but_rejects_meaningless_jumps(self) -> None:
        with self.assertRaisesRegex(GateBlocked, "lifecycle:captured->validating"):
            self.workflow.transition(self.record, "validating")

        self.workflow.transition(self.record, "active")
        self.workflow.transition(self.record, "validating")
        result = self.workflow.transition(self.record, "shaped")

        self.assertEqual(result.state.lifecycle, "shaped")

    def test_build_activity_derives_obligations_from_uncertainty_traits(self) -> None:
        self.workflow.shape(
            self.record,
            goal="Repair report pipeline",
            scope=["report producer", "report renderer"],
            acceptance=[{"id": "report", "statement": "Report renders"}],
            uncertainty=["unknown-cause", "cross-boundary"],
        )

        with self.assertRaisesRegex(GateBlocked, "activity:discover"):
            self.workflow.record_activity(self.record, "build")

        self.workflow.record_activity(self.record, "discover")
        with self.assertRaisesRegex(GateBlocked, "activity:design"):
            self.workflow.record_activity(self.record, "build")

        self.workflow.record_activity(self.record, "design")
        state = self.workflow.record_activity(self.record, "build")
        self.assertEqual(state.activities, ["discover", "design", "build"])

    def test_high_security_impact_requires_review_before_completion(self) -> None:
        self.workflow.shape(
            self.record,
            goal="Deny unauthorized report access",
            scope=["report access"],
            acceptance=[{"id": "denied", "statement": "Unauthorized access is denied"}],
            impacts={"security": "high"},
        )
        self.workflow.add_evidence(
            self.record,
            kind="command-evidence",
            summary="Access regression passed",
            result="pass",
            acceptance_ids=["denied"],
        )

        with self.assertRaisesRegex(GateBlocked, "activity:review"):
            self.workflow.close(self.record, outcome="completed", summary="Access fixed")

        self.workflow.record_activity(self.record, "review")
        result = self.workflow.close(self.record, outcome="completed", summary="Access fixed")
        self.assertEqual(result.state.outcome, "completed")


if __name__ == "__main__":
    unittest.main()
