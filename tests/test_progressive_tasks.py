import tempfile
import unittest
import json
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timezone
from pathlib import Path

from jsonschema import Draft202012Validator


from idc_core.events import EventStore
from idc_core.obligations import evaluate_obligations
from idc_core.projector import fold_events


NOW = datetime(2026, 9, 14, 4, 30, tzinfo=timezone.utc)


class ProgressiveTaskTests(unittest.TestCase):
    def test_promoted_task_id_does_not_embed_mutable_scenario(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            project = Path(temp_dir)
            store = EventStore(project, clock=lambda: NOW)

            record = store.capture("Report becomes blank after saving", actor="human")
            task_id = store.promote(record.record_id, project_key="LAS")

            self.assertEqual(task_id, "IDC-LAS-20260914-001")
            self.assertNotIn("FIX", task_id)

    def test_classification_is_revised_without_changing_task_identity(self) -> None:
        events = [
            {
                "schema_version": 1,
                "record_id": "work-1",
                "seq": 0,
                "timestamp": "2026-09-14T04:30:00+00:00",
                "actor": {"kind": "human"},
                "type": "request.captured",
                "provenance": "human-confirmed",
                "payload": {"summary": "Investigate an access failure"},
            },
            {
                "schema_version": 1,
                "record_id": "work-1",
                "seq": 1,
                "timestamp": "2026-09-14T04:31:00+00:00",
                "actor": {"kind": "agent"},
                "type": "task.promoted",
                "provenance": "artifact-evidence",
                "payload": {"task_id": "IDC-LAS-20260914-001"},
            },
            {
                "schema_version": 1,
                "record_id": "work-1",
                "seq": 2,
                "timestamp": "2026-09-14T04:32:00+00:00",
                "actor": {"kind": "agent"},
                "type": "classification.changed",
                "provenance": "claimed",
                "payload": {"from": None, "to": ["FIX"], "reason": "Initial symptom"},
            },
            {
                "schema_version": 1,
                "record_id": "work-1",
                "seq": 3,
                "timestamp": "2026-09-14T04:33:00+00:00",
                "actor": {"kind": "agent"},
                "type": "classification.changed",
                "provenance": "command-evidence",
                "payload": {
                    "from": ["FIX"],
                    "to": ["SEC"],
                    "reason": "Reproduction crossed a trust boundary",
                },
            },
        ]

        state = fold_events(events)

        self.assertEqual(state.task_id, "IDC-LAS-20260914-001")
        self.assertEqual(state.classifications, ["SEC"])
        self.assertEqual(len(state.classification_history), 2)

    def test_requirement_change_returns_active_work_to_shaped(self) -> None:
        events = [
            self.event(0, "request.captured", {"summary": "Change report export"}),
            self.event(1, "lifecycle.changed", {"from": "captured", "to": "shaped"}),
            self.event(2, "lifecycle.changed", {"from": "shaped", "to": "active"}),
            self.event(
                3,
                "requirement.changed",
                {"before": "Export PDF", "after": "Export PDF and DOCX", "reason": "User correction"},
            ),
        ]

        state = fold_events(events)

        self.assertEqual(state.lifecycle, "shaped")
        self.assertEqual(state.requirement_changes[0]["after"], "Export PDF and DOCX")

    def test_external_effect_is_hard_blocked_until_exact_permission_is_granted(self) -> None:
        state = fold_events(
            [
                self.event(0, "request.captured", {"summary": "Deploy release"}),
                self.event(
                    1,
                    "impact.assessed",
                    {"dimensions": {"external_effect": "high", "reversibility": "medium"}},
                ),
                self.event(2, "permission.requested", {"effect": "deploy:production"}),
            ]
        )

        blocked = evaluate_obligations(state, target="ship")
        self.assertIn("permission:deploy:production", blocked.hard_blocks)

        state = fold_events(
            [
                self.event(0, "request.captured", {"summary": "Deploy release"}),
                self.event(
                    1,
                    "impact.assessed",
                    {"dimensions": {"external_effect": "high", "reversibility": "medium"}},
                ),
                self.event(2, "permission.requested", {"effect": "deploy:production"}),
                self.event(3, "permission.granted", {"effect": "deploy:production"}),
                self.event(4, "recovery.recorded", {"summary": "Roll back to prior image"}),
            ]
        )
        allowed = evaluate_obligations(state, target="ship")
        self.assertEqual(allowed.hard_blocks, [])

    def test_parallel_promotions_reserve_distinct_task_ids(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            project = Path(temp_dir)
            store = EventStore(project, clock=lambda: NOW)
            records = [store.capture(f"Task {number}").record_id for number in range(2)]

            with ThreadPoolExecutor(max_workers=2) as executor:
                task_ids = list(executor.map(lambda record: store.promote(record, "LAS"), records))

            self.assertEqual(
                sorted(task_ids),
                ["IDC-LAS-20260914-001", "IDC-LAS-20260914-002"],
            )

    def test_emitted_events_match_the_public_event_schema(self) -> None:
        schema_path = Path(__file__).resolve().parents[1] / "schemas" / "idc-task-event-v1.schema.json"
        schema = json.loads(schema_path.read_text(encoding="utf-8"))
        validator = Draft202012Validator(schema)
        with tempfile.TemporaryDirectory() as temp_dir:
            store = EventStore(Path(temp_dir), clock=lambda: NOW)
            record = store.capture("Investigate report")

            errors = list(validator.iter_errors(store.read(record.record_id)[0]))

        self.assertEqual(errors, [])

    def test_unknown_core_event_and_provenance_are_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            store = EventStore(Path(temp_dir), clock=lambda: NOW)
            record = store.capture("Investigate report")

            with self.assertRaisesRegex(ValueError, "unsupported event type"):
                store.append(record.record_id, "made.up", {})
            with self.assertRaisesRegex(ValueError, "unsupported provenance"):
                store.append(record.record_id, "x.project-note", {}, provenance="memory")

    def test_corrupt_event_line_reports_path_and_line_number(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            store = EventStore(Path(temp_dir), clock=lambda: NOW)
            record = store.capture("Investigate report")
            events_path = record.path / "events.jsonl"
            with events_path.open("a", encoding="utf-8") as stream:
                stream.write("{broken\n")

            with self.assertRaisesRegex(ValueError, r"events\.jsonl:2"):
                store.read(record.record_id)

    def test_parallel_event_appends_keep_contiguous_unique_sequence_numbers(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            project = Path(temp_dir)
            store = EventStore(project, clock=lambda: NOW)
            record = store.capture("Coordinate parallel work")

            def append_note(number: int) -> None:
                EventStore(project, clock=lambda: NOW).append(
                    record.record_id,
                    "x.parallel-note",
                    {"number": number},
                )

            with ThreadPoolExecutor(max_workers=8) as executor:
                list(executor.map(append_note, range(20)))

            events = store.read(record.record_id)
            self.assertEqual([event["seq"] for event in events], list(range(21)))

    @staticmethod
    def event(seq: int, event_type: str, payload: dict) -> dict:
        return {
            "schema_version": 1,
            "record_id": "work-1",
            "seq": seq,
            "timestamp": f"2026-09-14T04:{30 + seq:02d}:00+00:00",
            "actor": {"kind": "agent"},
            "type": event_type,
            "provenance": "claimed",
            "payload": payload,
        }


if __name__ == "__main__":
    unittest.main()
