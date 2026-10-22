from __future__ import annotations

import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch


ROOT = Path(__file__).resolve().parents[1]
CATALOG = ROOT / "contracts" / "capability-skip-preconditions.json"
CHECKER = ROOT / "scripts" / "check_skip_preconditions.py"
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "scripts"))

import validate_repository
from idc_core.projector import TaskState
from idc_core.routing import (
    KEEP,
    PREDICATE_KINDS,
    SKIP,
    UNKNOWN,
    evaluate_catalog,
    load_catalog,
)


def state(**kwargs: object) -> TaskState:
    return TaskState(record_id="work-test", **kwargs)


def passing_acceptance(acceptance_id: str = "a-001") -> dict[str, object]:
    return {
        "acceptance": [{"id": acceptance_id, "statement": "the behavior holds"}],
        "evidence": [{"result": "pass", "acceptance_ids": [acceptance_id]}],
    }


class SkipCatalogShapeTests(unittest.TestCase):
    def setUp(self) -> None:
        self.catalog = load_catalog(CATALOG)

    def test_catalog_uses_only_the_closed_predicate_vocabulary(self) -> None:
        for entry in self.catalog["capabilities"]:
            for precondition in entry.get("skip_when", []):
                for condition in precondition["requires"]:
                    self.assertIn(condition["kind"], PREDICATE_KINDS)

    def test_verification_has_no_skip_precondition(self) -> None:
        entry = next(
            item for item in self.catalog["capabilities"] if item["capability"] == "verification"
        )
        self.assertFalse(entry["skippable"])
        self.assertNotIn("skip_when", entry)

    def test_document_binding_passes_for_the_shipped_catalog(self) -> None:
        self.assertEqual(validate_repository.capability_skip_catalog_errors(), [])

    def test_document_binding_rejects_prose_drift(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            (root / "contracts").mkdir()
            (root / "docs").mkdir()
            catalog = json.loads(CATALOG.read_text(encoding="utf-8"))
            catalog["capabilities"][1]["over_route_when_prose"] = "drifted prose"
            (root / "contracts" / "capability-skip-preconditions.json").write_text(
                json.dumps(catalog), encoding="utf-8"
            )
            (root / "docs" / "CAPABILITY_TIERS.md").write_text(
                (ROOT / "docs" / "CAPABILITY_TIERS.md").read_text(encoding="utf-8"),
                encoding="utf-8",
            )
            with patch.object(validate_repository, "ROOT", root):
                errors = validate_repository.capability_skip_catalog_errors()
        self.assertTrue(any("prose does not match" in error for error in errors), errors)

    def test_document_binding_rejects_a_missing_tier_one_row(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            (root / "contracts").mkdir()
            (root / "docs").mkdir()
            catalog = json.loads(CATALOG.read_text(encoding="utf-8"))
            catalog["capabilities"] = catalog["capabilities"][:-1]
            (root / "contracts" / "capability-skip-preconditions.json").write_text(
                json.dumps(catalog), encoding="utf-8"
            )
            (root / "docs" / "CAPABILITY_TIERS.md").write_text(
                (ROOT / "docs" / "CAPABILITY_TIERS.md").read_text(encoding="utf-8"),
                encoding="utf-8",
            )
            with patch.object(validate_repository, "ROOT", root):
                errors = validate_repository.capability_skip_catalog_errors()
        self.assertTrue(any("has no catalog entry" in error for error in errors), errors)


class SkipEvaluationTests(unittest.TestCase):
    def setUp(self) -> None:
        self.catalog = load_catalog(CATALOG)

    def decision(self, value: TaskState, capability: str, facts: object = None):
        decisions = evaluate_catalog(self.catalog, value, facts=facts)
        return next(item for item in decisions if item.capability == capability)

    def test_host_exclusion_is_unknown_until_the_fact_is_declared(self) -> None:
        undecided = self.decision(state(), "intent-routing")
        self.assertEqual(undecided.status, UNKNOWN)
        self.assertFalse(undecided.skipped)
        declared = self.decision(state(), "intent-routing", facts={"host_thin_control_plane"})
        self.assertEqual(declared.status, SKIP)
        self.assertTrue(declared.skipped)

    def test_debugging_skips_only_after_the_cause_is_discovered(self) -> None:
        unknown_cause = self.decision(state(uncertainty=["unknown-cause"]), "debugging")
        self.assertEqual(unknown_cause.status, KEEP)
        discovered = self.decision(state(activities=["discover"]), "debugging")
        self.assertEqual(discovered.status, SKIP)

    def test_code_review_requires_all_three_clauses(self) -> None:
        covered = self.decision(state(scope=["app.py"], **passing_acceptance()), "code-review")
        self.assertEqual(covered.status, SKIP)
        uncovered = self.decision(
            state(scope=["app.py"], acceptance=[{"id": "a-001", "statement": "holds"}]),
            "code-review",
        )
        self.assertEqual(uncovered.status, KEEP)
        wide = self.decision(state(scope=["app.py", "api.py"], **passing_acceptance()), "code-review")
        self.assertEqual(wide.status, KEEP)

    def test_acceptance_coverage_is_not_vacuous(self) -> None:
        decision = self.decision(state(scope=["app.py"]), "code-review")
        statuses = {
            condition.kind: condition.status
            for precondition in decision.preconditions
            for condition in precondition.conditions
        }
        self.assertEqual(statuses["acceptance_covered"], "unsatisfied")

    def test_an_empty_record_cannot_skip_by_saying_nothing(self) -> None:
        decision = self.decision(state(), "architecture-impact")
        self.assertEqual(decision.status, KEEP)
        statuses = {
            condition.kind: condition.status
            for precondition in decision.preconditions
            for condition in precondition.conditions
        }
        self.assertEqual(statuses["scope_at_most"], "unsatisfied")
        self.assertEqual(statuses["impact_absent"], "unsatisfied")

    def test_a_recorded_clean_assessment_permits_the_architecture_skip(self) -> None:
        decision = self.decision(
            state(scope=["app.py"], impacts={"security": "none"}), "architecture-impact"
        )
        self.assertEqual(decision.status, SKIP)

    def test_verification_is_never_skipped(self) -> None:
        decision = self.decision(state(activities=["discover"]), "verification")
        self.assertEqual(decision.status, KEEP)
        self.assertFalse(decision.skipped)


class SkipCheckerCliTests(unittest.TestCase):
    def write_record(self, project: Path, events: list[tuple[str, dict[str, object]]]) -> str:
        directory = project / ".idc" / "work-items" / "work-20260101t000000z-00000000"
        directory.mkdir(parents=True)
        lines = [
            json.dumps(
                {
                    "record_id": directory.name,
                    "seq": sequence,
                    "type": event_type,
                    "payload": payload,
                    "timestamp": "2026-01-01T00:00:00+00:00",
                }
            )
            for sequence, (event_type, payload) in enumerate(events)
        ]
        (directory / "events.jsonl").write_text("\n".join(lines) + "\n", encoding="utf-8")
        return directory.name

    def run_checker(self, *args: str) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            [sys.executable, str(CHECKER), *args],
            cwd=ROOT,
            text=True,
            capture_output=True,
            check=False,
        )

    def test_checker_reports_unknown_then_skip_for_a_declared_fact(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            project = Path(temp_dir)
            self.write_record(project, [("request.captured", {"summary": "Investigate"})])
            undecided = self.run_checker("--project", str(project))
            self.assertEqual(undecided.returncode, 0, undecided.stderr)
            self.assertIn("intent-routing", undecided.stdout)
            self.assertIn("unknown=1", undecided.stdout)
            self.assertIn("only 'skip' permits skipping", undecided.stdout)
            declared = self.run_checker(
                "--project", str(project), "--fact", "host_thin_control_plane"
            )
            self.assertEqual(declared.returncode, 0, declared.stderr)
            self.assertIn("skip=1", declared.stdout)

    def test_checker_skips_debugging_when_discover_is_recorded(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            project = Path(temp_dir)
            self.write_record(
                project,
                [
                    ("request.captured", {"summary": "Investigate"}),
                    ("activity.recorded", {"name": "discover"}),
                ],
            )
            result = self.run_checker("--project", str(project), "--json")
            self.assertEqual(result.returncode, 0, result.stderr)
            payload = json.loads(result.stdout)
            statuses = {item["capability"]: item["status"] for item in payload["decisions"]}
            self.assertEqual(statuses["debugging"], "skip")
            self.assertEqual(payload["counts"]["skip"], 1)

    def test_checker_rejects_an_unknown_environment_fact(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            project = Path(temp_dir)
            self.write_record(project, [("request.captured", {"summary": "Investigate"})])
            result = self.run_checker("--project", str(project), "--fact", "not_a_declared_fact")
            self.assertNotEqual(result.returncode, 0)


if __name__ == "__main__":
    unittest.main()
