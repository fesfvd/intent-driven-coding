from __future__ import annotations

import json
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import orchestrate_squad
from validate_contracts import DEFAULT_SCHEMA, validate as validate_contracts


def squad_contract(
    acceptance: dict[str, str] | None = None,
    commands: list[dict[str, object]] | None = None,
) -> dict[str, object]:
    payload: dict[str, object] = {
        "schema_version": 1,
        "kind": "squad-contract",
        "id": "acceptance-fixture",
        "outcome": "Prove the acceptance policy fixture.",
        "routing": {
            "triggers": ["An acceptance policy fixture."],
            "exclusions": [],
            "precedence": "Use only as a structural fixture.",
        },
        "members": [
            {"skill": "debug", "role": "primary", "required_output": "diagnosis"},
            {"skill": "verify", "role": "proof", "required_output": "verification-report"},
        ],
        "handoffs": [
            {
                "from": "debug",
                "to": "verify",
                "artifact_id": "diagnosis",
                "consumer_requirements": ["The cause is named."],
            }
        ],
        "verification": {
            "claims": [
                {
                    "id": "claim-001",
                    "statement": "The fixture claim holds.",
                    "required_evidence": ["Focused check."],
                }
            ]
        },
        "authorization": {"required": False, "effects": [], "state": "not-required"},
    }
    if commands is not None:
        payload["verification"]["commands"] = commands
    if acceptance is not None:
        payload["verification"]["acceptance"] = acceptance
    return payload


def command_fixture() -> list[dict[str, object]]:
    return [{"id": "focused-check", "argv": ["python", "-m", "unittest"], "cwd": "."}]


def write_contract(payload: dict[str, object], directory: Path) -> Path:
    path = directory / "acceptance-fixture.squad.json"
    path.write_text(json.dumps(payload), encoding="utf-8")
    return path


class AcceptancePolicyTests(unittest.TestCase):
    def test_default_policy_applies_when_the_contract_omits_it(self) -> None:
        self.assertEqual(
            orchestrate_squad.acceptance_policy(squad_contract()),
            orchestrate_squad.DEFAULT_ACCEPTANCE,
        )

    def test_declared_policy_is_read_back_unchanged(self) -> None:
        declared = dict(orchestrate_squad.DEFAULT_ACCEPTANCE)
        self.assertEqual(
            orchestrate_squad.acceptance_policy(squad_contract(acceptance=declared)), declared
        )

    def test_an_undeclared_policy_is_accepted_and_a_deviating_one_is_not(self) -> None:
        self.assertEqual(orchestrate_squad.acceptance_errors(squad_contract()), [])
        weaker = dict(orchestrate_squad.DEFAULT_ACCEPTANCE, prose_report="blocking")
        errors = orchestrate_squad.acceptance_errors(squad_contract(acceptance=weaker))
        self.assertTrue(any("prose_report" in error for error in errors), errors)

    def test_policy_errors_block_a_deviating_contract_before_dispatch(self) -> None:
        weaker = dict(orchestrate_squad.DEFAULT_ACCEPTANCE, artifact_envelope="advisory")
        errors = orchestrate_squad.policy_errors(squad_contract(acceptance=weaker), ROOT, False)
        self.assertTrue(any("artifact_envelope" in error for error in errors), errors)

    def test_schema_accepts_the_supported_policy(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            path = write_contract(
                squad_contract(acceptance=dict(orchestrate_squad.DEFAULT_ACCEPTANCE)),
                Path(temp_dir),
            )
            self.assertEqual(validate_contracts(DEFAULT_SCHEMA, path), [])

    def test_schema_rejects_a_weaker_policy(self) -> None:
        weaker = dict(orchestrate_squad.DEFAULT_ACCEPTANCE, conflict_resolution="prose-wins")
        with tempfile.TemporaryDirectory() as temp_dir:
            path = write_contract(squad_contract(acceptance=weaker), Path(temp_dir))
            errors = validate_contracts(DEFAULT_SCHEMA, path)
        self.assertTrue(any("conflict_resolution" in error for error in errors), errors)


class CommandEvidenceDecidesAcceptanceTests(unittest.TestCase):
    def test_agent_output_alone_leaves_the_run_unproven(self) -> None:
        contract = squad_contract(commands=command_fixture())
        run = {
            "artifacts": [{"id": "verification-report", "path": "artifacts/verification-report.json"}],
            "verification": [],
        }
        self.assertEqual(orchestrate_squad.unproven_commands(run, contract), ["focused-check"])

    def test_passing_command_evidence_proves_the_run(self) -> None:
        contract = squad_contract(commands=command_fixture())
        run = {"verification": [{"kind": "command-evidence", "id": "focused-check", "returncode": 0}]}
        self.assertEqual(orchestrate_squad.unproven_commands(run, contract), [])

    def test_a_failing_command_stays_unproven(self) -> None:
        contract = squad_contract(commands=command_fixture())
        run = {"verification": [{"kind": "command-evidence", "id": "focused-check", "returncode": 1}]}
        self.assertEqual(orchestrate_squad.unproven_commands(run, contract), ["focused-check"])

    def test_a_timeout_record_is_not_command_evidence(self) -> None:
        contract = squad_contract(commands=command_fixture())
        run = {"verification": [{"kind": "command-timeout", "id": "focused-check"}]}
        self.assertEqual(orchestrate_squad.unproven_commands(run, contract), ["focused-check"])

    def test_undeclared_commands_are_never_required(self) -> None:
        self.assertEqual(orchestrate_squad.unproven_commands({"verification": []}, squad_contract()), [])


class AcceptanceDocumentationTests(unittest.TestCase):
    def test_example_contract_declares_the_acceptance_policy(self) -> None:
        payload = json.loads(
            (ROOT / "contracts" / "examples" / "cross-layer-feature.squad.json").read_text(
                encoding="utf-8"
            )
        )
        self.assertEqual(
            payload["verification"]["acceptance"], orchestrate_squad.DEFAULT_ACCEPTANCE
        )

    def test_orchestration_doc_states_the_three_rules(self) -> None:
        text = (ROOT / "docs" / "ORCHESTRATION.md").read_text(encoding="utf-8")
        self.assertIn("## Acceptance Rules", text)
        self.assertIn("Artifact envelope is strict", text)
        self.assertIn("Prose is advisory", text)
        self.assertIn("Command evidence wins", text)
        self.assertIn("acceptance-unproven", text)


if __name__ == "__main__":
    unittest.main()
