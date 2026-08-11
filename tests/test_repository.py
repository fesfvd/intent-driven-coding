from __future__ import annotations

import os
import json
import signal
import subprocess
import sys
import tempfile
import time
import unittest
import re
from unittest.mock import patch
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
BOOTSTRAP = ROOT / "scripts" / "bootstrap.py"
VALIDATOR = ROOT / "scripts" / "validate_repository.py"
AUDITOR = ROOT / "scripts" / "audit_skills.py"
PROJECT_VALIDATOR = ROOT / "scripts" / "validate_project.py"
CONTRACT_VALIDATOR = ROOT / "scripts" / "validate_contracts.py"
CONTRACT_EVALUATOR = ROOT / "scripts" / "evaluate_contracts.py"
HOST_FIXTURE_PREPARER = ROOT / "scripts" / "prepare_host_acceptance_fixture.py"
ORCHESTRATOR = ROOT / "scripts" / "orchestrate_squad.py"
IDC = ROOT / "scripts" / "idc.py"
sys.path.insert(0, str(ROOT / "scripts"))
import orchestrate_squad


class RepositoryTests(unittest.TestCase):
    def run_script(self, script: Path, *args: str) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            [sys.executable, str(script), *args],
            cwd=ROOT,
            text=True,
            capture_output=True,
            check=False,
        )

    def test_repository_validator_passes(self) -> None:
        result = self.run_script(VALIDATOR)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

    def test_repository_validator_allows_literal_template_tokens_in_references(self) -> None:
        reference = ROOT / "references" / "external-review-2026-07-25.md"
        self.assertIn("{{PROJECT_NAME}}", reference.read_text(encoding="utf-8"))
        result = self.run_script(VALIDATOR)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

    def test_phase_one_routing_fixture_supports_manual_host_acceptance(self) -> None:
        routing_fixture = json.loads(
            (ROOT / "evals" / "squad-routing.json").read_text(encoding="utf-8")
        )
        cases = {case["id"]: case for case in routing_fixture["cases"]}
        required_cases = {
            "direct-low-risk-copy-fix",
            "unknown-root-cause",
            "cross-layer-feature",
            "publication-ambiguity",
            "skill-system-design",
            "release-permission",
            "diff-review",
            "security-regression",
            "retention-ambiguity",
            "scope-near-miss",
        }
        self.assertGreaterEqual(len(cases), 10)
        self.assertTrue(required_cases.issubset(cases))

        template = ROOT / "references" / "host-acceptance" / "README.md"
        self.assertTrue(template.is_file())
        template_text = template.read_text(encoding="utf-8")
        for required_field in (
            "Host version",
            "Model",
            "Target revision",
            "Expected route",
            "Actual route",
            "Host-observed evidence",
            "Permission behavior",
        ):
            self.assertIn(required_field, template_text)

    def test_evidence_roadmap_artifacts_are_registered_and_linked(self) -> None:
        validator = (ROOT / "scripts" / "validate_repository.py").read_text(encoding="utf-8")
        readme = (ROOT / "README.md").read_text(encoding="utf-8")
        for path in (
            "plans/CURRENT_STATE.md",
            "plans/ROADMAP.md",
            "docs/HOST_ACCEPTANCE.md",
            "references/README.md",
            "references/host-acceptance/README.md",
            "references/host-acceptance/opencode-1.18.5-2026-07-26.md",
            "references/host-acceptance/claude-code-2.1.154-2026-07-26.md",
            "references/host-acceptance/las-5.2.3-opencode-1.18.5-2026-07-26.md",
            "DESIGN.md",
        ):
            self.assertIn(f'"{path}"', validator)
        self.assertIn("[Current state](plans/CURRENT_STATE.md)", readme)
        self.assertIn("[Roadmap](plans/ROADMAP.md)", readme)
        self.assertIn("[experimental design constitution](DESIGN.md)", readme)

    def test_host_acceptance_record_discloses_partial_observations(self) -> None:
        record = (
            ROOT / "references" / "host-acceptance" / "opencode-1.18.5-2026-07-26.md"
        ).read_text(encoding="utf-8")
        current_state = (ROOT / "plans" / "CURRENT_STATE.md").read_text(encoding="utf-8")
        for required_text in (
            "OpenCode `1.18.5`",
            "`opencode/deepseek-v4-flash-free`",
            "Status: partial",
            "direct-low-risk-copy-fix",
            "security-regression",
            "unobservable",
            "not a general compatibility claim",
        ):
            self.assertIn(required_text, record)
        self.assertIn("OpenCode `1.18.5`", current_state)
        self.assertIn("Claude Code `2.1.154` pilot", current_state)
        self.assertIn("non-leaking host-acceptance fixture", current_state)
        self.assertIn("prepare_host_acceptance_fixture.py", current_state)

    def test_claude_host_acceptance_record_discloses_partial_observations(self) -> None:
        record = (
            ROOT / "references" / "host-acceptance" / "claude-code-2.1.154-2026-07-26.md"
        ).read_text(encoding="utf-8")
        for required_text in (
            "Claude Code `2.1.154`",
            "`deepseek-v4-pro`",
            "Status: partial",
            "direct-low-risk-copy-fix",
            "security-regression",
            "No persisted handoff artifact",
            "$0.25",
            "not a general compatibility claim",
        ):
            self.assertIn(required_text, record)

    def test_host_fixture_preparer_creates_a_nonleaking_opencode_target(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            target = Path(temp_dir)
            result = self.run_script(
                HOST_FIXTURE_PREPARER,
                "--target",
                str(target),
                "--platform",
                "opencode",
                "--apply",
            )
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            self.assertTrue((target / "fixture_app.py").is_file())
            self.assertTrue((target / "tests" / "test_report.py").is_file())
            self.assertFalse((target / ".opencode" / "evals" / "squad-routing.json").exists())

            config = json.loads((target / "opencode.json").read_text(encoding="utf-8"))
            self.assertEqual(config["permission"]["task"]["*"], "deny")
            self.assertEqual(config["permission"]["task"]["debug"], "allow")
            self.assertEqual(config["permission"]["task"]["verify"], "allow")

            validation = self.run_script(
                PROJECT_VALIDATOR,
                "--target",
                str(target),
                "--platform",
                "opencode",
            )
            self.assertEqual(validation.returncode, 0, validation.stdout + validation.stderr)

            baseline = subprocess.run(
                [sys.executable, "-m", "unittest", "discover", "-s", "tests", "-p", "test_report.py", "-v"],
                cwd=target,
                text=True,
                capture_output=True,
                check=False,
            )
            self.assertEqual(baseline.returncode, 1, baseline.stdout + baseline.stderr)
            self.assertIn("test_saved_report_renders_its_body", baseline.stderr)

            target_text = "\n".join(
                path.read_text(encoding="utf-8")
                for path in target.rglob("*")
                if path.is_file()
                and path.suffix in {".json", ".md", ".py", ".txt"}
                and ".git" not in path.parts
            )
            routing_cases = json.loads(
                (ROOT / "evals" / "squad-routing.json").read_text(encoding="utf-8")
            )["cases"]
            for case in routing_cases:
                self.assertNotIn(case["prompt"], target_text)

    def test_host_fixture_assets_are_registered_for_acceptance_runs(self) -> None:
        validator = (ROOT / "scripts" / "validate_repository.py").read_text(encoding="utf-8")
        template = (ROOT / "references" / "host-acceptance" / "README.md").read_text(encoding="utf-8")
        for path in (
            "scripts/prepare_host_acceptance_fixture.py",
            "fixtures/host-acceptance/README.md",
            "fixtures/host-acceptance/AGENTS.md",
            "fixtures/host-acceptance/AI_ENGINEERING_PLAYBOOK.md",
            "fixtures/host-acceptance/SQUADS.md",
            "fixtures/host-acceptance/SQUAD.md",
            "fixtures/host-acceptance/fixture_app.py",
            "fixtures/host-acceptance/tests/test_report.py",
            "fixtures/host-acceptance/tests/test_invoice.py",
            "fixtures/host-acceptance/tests/test_approval.py",
            "fixtures/host-acceptance/opencode.json",
        ):
            self.assertIn(f'"{path}"', validator)
        self.assertIn("prepare_host_acceptance_fixture.py", template)

    def test_public_docs_link_host_acceptance_evidence(self) -> None:
        guide = (ROOT / "docs" / "HOST_ACCEPTANCE.md").read_text(encoding="utf-8")
        platform_guide = (ROOT / "docs" / "PLATFORM_ADAPTERS.md").read_text(encoding="utf-8")
        opencode = (ROOT / "docs" / "OPENCODE_ADAPTER.md").read_text(encoding="utf-8")
        claude = (ROOT / "docs" / "CLAUDE_CODE_ADAPTER.md").read_text(encoding="utf-8")
        evaluation = (ROOT / "docs" / "EVALUATION.md").read_text(encoding="utf-8")
        readme = (ROOT / "README.md").read_text(encoding="utf-8")

        for required_text in (
            "OpenCode `1.18.5`",
            "Claude Code `2.1.154`",
            "partial",
            "prepare_host_acceptance_fixture.py",
            "No routing accuracy",
        ):
            self.assertIn(required_text, guide)
        for document in (platform_guide, opencode, claude, evaluation, readme):
            self.assertIn("HOST_ACCEPTANCE.md", document)

    def test_contract_validator_accepts_framework_examples(self) -> None:
        result = self.run_script(
            CONTRACT_VALIDATOR,
            "--contracts",
            str(ROOT / "contracts" / "examples"),
        )
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn("Contract validation passed", result.stdout)

    def test_contract_validator_rejects_invalid_contract(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            contract_root = Path(temp_dir)
            (contract_root / "invalid.json").write_text(
                '{"schema_version": 1, "kind": "squad-contract"}\n',
                encoding="utf-8",
            )
            result = self.run_script(
                CONTRACT_VALIDATOR,
                "--contracts",
                str(contract_root),
            )
            self.assertEqual(result.returncode, 1)
            self.assertIn("invalid.json", result.stdout)

    def test_contract_validator_reports_non_utf8_contract(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            contract_root = Path(temp_dir)
            (contract_root / "invalid-encoding.json").write_bytes(b"\xff")
            result = self.run_script(
                CONTRACT_VALIDATOR,
                "--contracts",
                str(contract_root),
            )
            self.assertEqual(result.returncode, 1)
            self.assertIn("cannot read JSON", result.stdout)

    def test_contract_validator_rejects_external_schema_references(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            schema = root / "schema.json"
            contracts = root / "contracts"
            contracts.mkdir()
            schema.write_text(
                json.dumps(
                    {
                        "$schema": "https://json-schema.org/draft/2020-12/schema",
                        "$ref": "http://127.0.0.1:1/contract-schema.json",
                    }
                ),
                encoding="utf-8",
            )
            (contracts / "contract.json").write_text("{}", encoding="utf-8")
            result = self.run_script(
                CONTRACT_VALIDATOR,
                "--schema",
                str(schema),
                "--contracts",
                str(contracts),
            )
            self.assertEqual(result.returncode, 1)
            self.assertIn("external schema reference", result.stdout)

    def test_offline_contract_evaluator_accepts_matching_record(self) -> None:
        result = self.run_script(
            CONTRACT_EVALUATOR,
            "--contracts",
            str(ROOT / "contracts" / "examples"),
            "--records",
            str(ROOT / "evals" / "fixtures"),
        )
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn("Offline evaluation passed", result.stdout)

    def test_offline_contract_evaluator_rejects_forbidden_behavior(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            contracts = root / "contracts"
            records = root / "records"
            contracts.mkdir()
            records.mkdir()
            for source in (ROOT / "contracts" / "examples").glob("*.json"):
                (contracts / source.name).write_text(source.read_text(encoding="utf-8"), encoding="utf-8")
            record = {
                "schema_version": 1,
                "kind": "evaluation-record",
                "id": "cross-layer-feature-record",
                "case_id": "cross-layer-feature-contract-route",
                "contract_id": "cross-layer-feature",
                "selected_route": ["architecture", "code-review", "verify"],
                "artifacts": ["impact-contract", "review-findings", "verification-report"],
                "verification_claims": ["acceptance-supported"],
                "authorization": {
                    "required": True,
                    "effects": ["Migration, release, and external write remain separately authorized."],
                    "state": "not-requested"
                },
                "observed_forbidden_behavior": ["Assume migration or deployment authorization."]
            }
            (records / "invalid-record.json").write_text(json.dumps(record), encoding="utf-8")

            result = self.run_script(
                CONTRACT_EVALUATOR,
                "--contracts",
                str(contracts),
                "--records",
                str(records),
            )
            self.assertEqual(result.returncode, 1)
            self.assertIn("forbidden behavior", result.stdout)

    def test_offline_contract_evaluator_rejects_authorization_effect_mismatch(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            contracts = root / "contracts"
            records = root / "records"
            contracts.mkdir()
            records.mkdir()
            for source in (ROOT / "contracts" / "examples").glob("*.json"):
                (contracts / source.name).write_text(source.read_text(encoding="utf-8"), encoding="utf-8")
            record = json.loads(
                (ROOT / "evals" / "fixtures" / "cross-layer-feature.record.json").read_text(encoding="utf-8")
            )
            record["authorization"]["effects"] = ["Deploy the current revision."]
            (records / "invalid-record.json").write_text(json.dumps(record), encoding="utf-8")
            result = self.run_script(
                CONTRACT_EVALUATOR,
                "--contracts",
                str(contracts),
                "--records",
                str(records),
            )
            self.assertEqual(result.returncode, 1)
            self.assertIn("authorization effects", result.stdout)

    def test_contract_validator_rejects_handoff_outside_squad_route(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            contract_root = Path(temp_dir)
            payload = json.loads(
                (ROOT / "contracts" / "examples" / "cross-layer-feature.squad.json").read_text(encoding="utf-8")
            )
            payload["handoffs"][0]["from"] = "debug"
            (contract_root / "invalid-handoff.json").write_text(
                json.dumps(payload),
                encoding="utf-8",
            )
            result = self.run_script(
                CONTRACT_VALIDATOR,
                "--contracts",
                str(contract_root),
            )
            self.assertEqual(result.returncode, 1)
            self.assertIn("not a squad member", result.stdout)

    def test_contract_validator_rejects_disconnected_handoff_route(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            contract_root = Path(temp_dir)
            payload = json.loads(
                (ROOT / "contracts" / "examples" / "cross-layer-feature.squad.json").read_text(encoding="utf-8")
            )
            payload["handoffs"] = [payload["handoffs"][0]]
            (contract_root / "invalid-handoff-route.json").write_text(
                json.dumps(payload),
                encoding="utf-8",
            )
            result = self.run_script(CONTRACT_VALIDATOR, "--contracts", str(contract_root))
            self.assertEqual(result.returncode, 1)
            self.assertIn("must connect each adjacent squad member", result.stdout)

    def test_contract_validator_rejects_contradictory_authorization_state(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            contract_root = Path(temp_dir)
            payload = json.loads(
                (ROOT / "contracts" / "examples" / "cross-layer-feature.squad.json").read_text(encoding="utf-8")
            )
            payload["authorization"]["state"] = "not-required"
            (contract_root / "invalid-authorization.json").write_text(json.dumps(payload), encoding="utf-8")
            result = self.run_script(CONTRACT_VALIDATOR, "--contracts", str(contract_root))
            self.assertEqual(result.returncode, 1)
            self.assertIn("not-required", result.stdout)

    def test_contract_validator_rejects_evaluation_with_unknown_contract(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            contract_root = Path(temp_dir)
            squad = (ROOT / "contracts" / "examples" / "cross-layer-feature.squad.json").read_text(encoding="utf-8")
            evaluation = json.loads(
                (ROOT / "contracts" / "examples" / "cross-layer-feature.evaluation.json").read_text(encoding="utf-8")
            )
            evaluation["contract_id"] = "missing-contract"
            (contract_root / "squad.json").write_text(squad, encoding="utf-8")
            (contract_root / "evaluation.json").write_text(json.dumps(evaluation), encoding="utf-8")
            result = self.run_script(CONTRACT_VALIDATOR, "--contracts", str(contract_root))
            self.assertEqual(result.returncode, 1)
            self.assertIn("unknown contract", result.stdout)

    def test_contract_validator_rejects_duplicate_evaluation_case_ids(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            contract_root = Path(temp_dir)
            squad = (ROOT / "contracts" / "examples" / "cross-layer-feature.squad.json").read_text(encoding="utf-8")
            evaluation = (ROOT / "contracts" / "examples" / "cross-layer-feature.evaluation.json").read_text(encoding="utf-8")
            (contract_root / "squad.json").write_text(squad, encoding="utf-8")
            (contract_root / "evaluation-one.json").write_text(evaluation, encoding="utf-8")
            (contract_root / "evaluation-two.json").write_text(evaluation, encoding="utf-8")
            result = self.run_script(CONTRACT_VALIDATOR, "--contracts", str(contract_root))
            self.assertEqual(result.returncode, 1)
            self.assertIn("duplicate evaluation case id", result.stdout)

    def test_contract_validator_rejects_evaluation_reference_mismatches(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            contract_root = Path(temp_dir)
            squad = (ROOT / "contracts" / "examples" / "cross-layer-feature.squad.json").read_text(encoding="utf-8")
            evaluation = json.loads(
                (ROOT / "contracts" / "examples" / "cross-layer-feature.evaluation.json").read_text(encoding="utf-8")
            )
            evaluation["expected_route"] = ["architecture", "verify"]
            evaluation["required_artifacts"] = ["missing-artifact"]
            evaluation["required_verification_claims"] = ["missing-claim"]
            evaluation["authorization"] = {
                "required": False,
                "effects": [],
                "state": "not-required"
            }
            (contract_root / "squad.json").write_text(squad, encoding="utf-8")
            (contract_root / "evaluation.json").write_text(json.dumps(evaluation), encoding="utf-8")
            result = self.run_script(CONTRACT_VALIDATOR, "--contracts", str(contract_root))
            self.assertEqual(result.returncode, 1)
            self.assertIn("expected route does not match", result.stdout)
            self.assertIn("required artifact", result.stdout)
            self.assertIn("unknown verification claim", result.stdout)
            self.assertIn("authorization requirement does not match", result.stdout)

    def test_contract_validator_rejects_evaluation_authorization_effect_mismatch(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            contract_root = Path(temp_dir)
            squad = (ROOT / "contracts" / "examples" / "cross-layer-feature.squad.json").read_text(encoding="utf-8")
            evaluation = json.loads(
                (ROOT / "contracts" / "examples" / "cross-layer-feature.evaluation.json").read_text(encoding="utf-8")
            )
            evaluation["authorization"]["effects"] = ["Deploy the current revision."]
            (contract_root / "squad.json").write_text(squad, encoding="utf-8")
            (contract_root / "evaluation.json").write_text(json.dumps(evaluation), encoding="utf-8")
            result = self.run_script(CONTRACT_VALIDATOR, "--contracts", str(contract_root))
            self.assertEqual(result.returncode, 1)
            self.assertIn("authorization effects", result.stdout)

    def test_contract_validator_rejects_duplicate_verification_claims(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            contract_root = Path(temp_dir)
            payload = json.loads(
                (ROOT / "contracts" / "examples" / "cross-layer-feature.squad.json").read_text(encoding="utf-8")
            )
            payload["verification"]["claims"].append(payload["verification"]["claims"][0].copy())
            (contract_root / "duplicate-claim.json").write_text(json.dumps(payload), encoding="utf-8")
            result = self.run_script(CONTRACT_VALIDATOR, "--contracts", str(contract_root))
            self.assertEqual(result.returncode, 1)
            self.assertIn("duplicate verification claim", result.stdout)

    def test_contract_validator_accepts_declared_verification_commands(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            contract_root = Path(temp_dir)
            payload = json.loads(
                (ROOT / "contracts" / "examples" / "cross-layer-feature.squad.json").read_text(encoding="utf-8")
            )
            payload["verification"]["commands"] = [
                {
                    "id": "focused-check",
                    "argv": [sys.executable, "-c", "raise SystemExit(0)"],
                    "cwd": ".",
                }
            ]
            (contract_root / "contract.json").write_text(json.dumps(payload), encoding="utf-8")

            result = self.run_script(CONTRACT_VALIDATOR, "--contracts", str(contract_root))

            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

    def test_contract_validator_rejects_duplicate_verification_command_ids(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            contract_root = Path(temp_dir)
            payload = json.loads(
                (ROOT / "contracts" / "examples" / "cross-layer-feature.squad.json").read_text(encoding="utf-8")
            )
            command = {
                "id": "focused-check",
                "argv": [sys.executable, "-c", "raise SystemExit(0)"],
                "cwd": ".",
            }
            payload["verification"]["commands"] = [command, command.copy()]
            (contract_root / "contract.json").write_text(json.dumps(payload), encoding="utf-8")

            result = self.run_script(CONTRACT_VALIDATOR, "--contracts", str(contract_root))

            self.assertEqual(result.returncode, 1)
            self.assertIn("duplicate verification command", result.stdout)

    def test_orchestrator_dry_run_records_a_policy_checked_route(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            workspace = Path(temp_dir) / "workspace"
            workspace.mkdir()
            contract = workspace / "debug-verify.squad.json"
            contract.write_text(
                json.dumps(
                    {
                        "schema_version": 1,
                        "kind": "squad-contract",
                        "id": "debug-verify",
                        "outcome": "Diagnose a defect and independently verify its fix.",
                        "routing": {
                            "triggers": ["Find the root cause of a failing report."],
                            "exclusions": [],
                            "precedence": "Use only when the root cause is unknown.",
                        },
                        "members": [
                            {
                                "skill": "debug",
                                "role": "primary",
                                "required_output": "root-cause-analysis",
                            },
                            {
                                "skill": "verify",
                                "role": "proof",
                                "required_output": "verification-report",
                            },
                        ],
                        "handoffs": [
                            {
                                "from": "debug",
                                "to": "verify",
                                "artifact_id": "root-cause-analysis",
                                "consumer_requirements": ["Read the diagnosis before verification."],
                            }
                        ],
                        "verification": {
                            "claims": [
                                {
                                    "id": "fix-supported",
                                    "statement": "The reported defect has fresh supporting evidence.",
                                    "required_evidence": ["Focused command result."],
                                }
                            ]
                        },
                        "authorization": {
                            "required": False,
                            "effects": [],
                            "state": "not-required",
                        },
                    }
                ),
                encoding="utf-8",
            )

            result = self.run_script(
                ORCHESTRATOR,
                "--contract",
                str(contract),
                "--workspace",
                str(workspace),
                "--request",
                "Investigate the failing report.",
                "--run-id",
                "dry-run",
            )

            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            run = json.loads((workspace / ".idc" / "runs" / "dry-run" / "run.json").read_text(encoding="utf-8"))
            self.assertEqual(run["state"], "policy-checked")
            self.assertEqual(run["route"], ["debug", "verify"])
            events = [
                json.loads(line)["type"]
                for line in (workspace / ".idc" / "runs" / "dry-run" / "events.jsonl").read_text(encoding="utf-8").splitlines()
            ]
            self.assertEqual(events, ["run-planned", "policy-checked"])

    def test_idc_status_reads_only_explicit_idc_metadata(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            project = Path(temp_dir) / "project"
            contract_dir = project / ".idc" / "contracts"
            evaluation_dir = project / ".idc" / "evals"
            run_dir = project / ".idc" / "runs" / "observed-run"
            contract_dir.mkdir(parents=True)
            evaluation_dir.mkdir()
            run_dir.mkdir(parents=True)
            (project / "app.py").write_bytes(b"\xffnot-readable-source")

            contract = json.loads(
                (ROOT / "contracts" / "examples" / "cross-layer-feature.squad.json").read_text(encoding="utf-8")
            )
            evaluation_case = json.loads(
                (ROOT / "contracts" / "examples" / "cross-layer-feature.evaluation.json").read_text(encoding="utf-8")
            )
            evaluation_record = json.loads(
                (ROOT / "evals" / "fixtures" / "cross-layer-feature.record.json").read_text(encoding="utf-8")
            )
            (contract_dir / "cross-layer-feature.squad.json").write_text(
                json.dumps(contract), encoding="utf-8"
            )
            (contract_dir / "cross-layer-feature.evaluation.json").write_text(
                json.dumps(evaluation_case), encoding="utf-8"
            )
            (evaluation_dir / "cross-layer-feature.record.json").write_text(
                json.dumps(evaluation_record), encoding="utf-8"
            )
            (run_dir / "run.json").write_text(
                json.dumps(
                    {
                        "schema_version": 1,
                        "kind": "orchestration-run",
                        "id": "observed-run",
                        "state": "completed",
                        "host": "opencode",
                        "route": ["architecture", "code-review", "verify"],
                        "contract": {"id": "cross-layer-feature"},
                        "artifacts": [],
                        "verification": [],
                    }
                ),
                encoding="utf-8",
            )
            (run_dir / "events.jsonl").write_text(
                "\n".join(
                    (
                        json.dumps({"timestamp": "2026-07-26T00:00:00+00:00", "type": "run-planned"}),
                        json.dumps({"timestamp": "2026-07-26T00:01:00+00:00", "type": "run-completed"}),
                    )
                )
                + "\n",
                encoding="utf-8",
            )

            result = self.run_script(IDC, "status", "--project", str(project), "--json")

            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            status = json.loads(result.stdout)
            self.assertEqual(status["project"], str(project.resolve()))
            self.assertEqual(status["scope"], ".idc metadata only")
            self.assertEqual(status["contracts"], ["cross-layer-feature"])
            self.assertEqual(status["evaluation_cases"], ["cross-layer-feature-contract-route"])
            self.assertEqual(status["evaluation_records"], ["cross-layer-feature-record"])
            self.assertEqual(status["runs"][0]["id"], "observed-run")
            self.assertEqual(status["runs"][0]["latest_event"], "run-completed")
            self.assertEqual(
                status["availability"],
                {"contracts": "available", "evaluations": "available", "runs": "available"},
            )

    def test_idc_status_rejects_a_missing_project_path(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            missing_project = Path(temp_dir) / "missing-project"

            result = self.run_script(IDC, "status", "--project", str(missing_project), "--json")

            self.assertEqual(result.returncode, 2)
            self.assertIn("project directory does not exist", result.stderr)

    def test_idc_status_renders_terminal_output_in_the_explicit_language(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            project = Path(temp_dir) / "project"
            (project / ".idc").mkdir(parents=True)

            result = self.run_script(IDC, "status", "--project", str(project), "--language", "zh")

            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            self.assertIn("项目:", result.stdout)
            self.assertIn("范围: 仅 .idc 元数据", result.stdout)

    def test_idc_evidence_distinguishes_claims_commands_and_persisted_runs(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            project = Path(temp_dir) / "project"
            evaluation_dir = project / ".idc" / "evals"
            run_dir = project / ".idc" / "runs" / "evidence-run"
            evaluation_dir.mkdir(parents=True)
            run_dir.mkdir(parents=True)
            (project / "app.py").write_bytes(b"\xffnot-readable-source")
            evaluation_record = json.loads(
                (ROOT / "evals" / "fixtures" / "cross-layer-feature.record.json").read_text(encoding="utf-8")
            )
            (evaluation_dir / "cross-layer-feature.record.json").write_text(
                json.dumps(evaluation_record), encoding="utf-8"
            )
            (run_dir / "run.json").write_text(
                json.dumps(
                    {
                        "schema_version": 1,
                        "kind": "orchestration-run",
                        "id": "evidence-run",
                        "state": "completed",
                        "host": "opencode",
                        "route": ["architecture", "code-review", "verify"],
                        "artifacts": [
                            {
                                "id": "verification-report",
                                "path": ".idc/runs/evidence-run/artifacts/verification-report.json",
                                "sha256": "test-only",
                            }
                        ],
                        "verification": [
                            {
                                "schema_version": 1,
                                "kind": "command-evidence",
                                "id": "focused-check",
                                "provenance": "command-evidence",
                                "argv": ["python", "-m", "pytest", "tests/test_report.py"],
                                "cwd": str(project),
                                "returncode": 0,
                                "stdout": "verification/focused-check.stdout.txt",
                                "stderr": "verification/focused-check.stderr.txt",
                            }
                        ],
                    }
                ),
                encoding="utf-8",
            )

            result = self.run_script(IDC, "evidence", "--project", str(project), "--json")

            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            evidence = json.loads(result.stdout)
            self.assertEqual(evidence["project"], str(project.resolve()))
            self.assertEqual(evidence["scope"], ".idc metadata only")
            self.assertEqual(evidence["claimed"][0]["id"], "cross-layer-feature-record")
            self.assertEqual(evidence["claimed"][0]["class"], "claimed")
            self.assertEqual(evidence["command_evidence"][0]["id"], "focused-check")
            self.assertEqual(evidence["command_evidence"][0]["returncode"], 0)
            self.assertEqual(evidence["artifact_evidence"][0]["id"], "evidence-run")
            self.assertEqual(evidence["artifact_evidence"][0]["class"], "artifact-evidence")
            self.assertEqual(
                evidence["availability"],
                {
                    "claimed": "available",
                    "host-observed": "unavailable",
                    "command-evidence": "available",
                    "artifact-evidence": "available",
                    "human-confirmed": "unavailable",
                },
            )

    def test_idc_evidence_renders_terminal_output_in_the_explicit_language(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            project = Path(temp_dir) / "project"
            (project / ".idc").mkdir(parents=True)

            result = self.run_script(IDC, "evidence", "--project", str(project), "--language", "zh")

            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            self.assertIn("项目:", result.stdout)
            self.assertIn("Agent 声称:", result.stdout)

    def test_idc_evidence_tolerates_incomplete_run_metadata(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            project = Path(temp_dir) / "project"
            run_dir = project / ".idc" / "runs" / "incomplete-run"
            run_dir.mkdir(parents=True)
            (run_dir / "run.json").write_text(
                json.dumps(
                    {
                        "schema_version": 1,
                        "kind": "orchestration-run",
                        "id": "incomplete-run",
                        "artifacts": None,
                        "verification": None,
                    }
                ),
                encoding="utf-8",
            )

            result = self.run_script(IDC, "evidence", "--project", str(project), "--json")

            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            evidence = json.loads(result.stdout)
            self.assertEqual(evidence["artifact_evidence"][0]["id"], "incomplete-run")
            self.assertEqual(evidence["artifact_evidence"][0]["artifacts"], [])
            self.assertEqual(evidence["command_evidence"], [])

    def test_idc_portfolio_compares_explicit_project_metadata(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            first_project = Path(temp_dir) / "first-project"
            second_project = Path(temp_dir) / "second-project"
            first_contract_dir = first_project / ".idc" / "contracts"
            second_evaluation_dir = second_project / ".idc" / "evals"
            first_contract_dir.mkdir(parents=True)
            second_evaluation_dir.mkdir(parents=True)
            (first_project / "app.py").write_bytes(b"\xfffirst-project-source")
            (second_project / "app.py").write_bytes(b"\xffsecond-project-source")
            contract = json.loads(
                (ROOT / "contracts" / "examples" / "cross-layer-feature.squad.json").read_text(encoding="utf-8")
            )
            evaluation_record = json.loads(
                (ROOT / "evals" / "fixtures" / "cross-layer-feature.record.json").read_text(encoding="utf-8")
            )
            (first_contract_dir / "cross-layer-feature.squad.json").write_text(
                json.dumps(contract), encoding="utf-8"
            )
            (second_evaluation_dir / "cross-layer-feature.record.json").write_text(
                json.dumps(evaluation_record), encoding="utf-8"
            )

            result = self.run_script(
                IDC,
                "portfolio",
                "--paths",
                str(first_project),
                str(second_project),
                "--json",
            )

            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            portfolio = json.loads(result.stdout)
            self.assertEqual(portfolio["scope"], ".idc metadata only")
            self.assertEqual(
                [project["project"] for project in portfolio["projects"]],
                [str(first_project.resolve()), str(second_project.resolve())],
            )
            self.assertEqual(portfolio["projects"][0]["contracts"], ["cross-layer-feature"])
            self.assertEqual(portfolio["projects"][1]["evaluation_records"], ["cross-layer-feature-record"])
            self.assertEqual(
                portfolio["coverage"],
                {
                    "contracts": {"cross-layer-feature": [str(first_project.resolve())]},
                    "evaluation_records": {"cross-layer-feature-record": [str(second_project.resolve())]},
                },
            )

    def test_idc_portfolio_requires_two_explicit_project_paths(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            project = Path(temp_dir) / "project"
            project.mkdir()

            result = self.run_script(IDC, "portfolio", "--paths", str(project), "--json")

            self.assertEqual(result.returncode, 2)
            self.assertIn("at least two project directories", result.stderr)

    def test_idc_portfolio_rejects_duplicate_project_paths(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            project = Path(temp_dir) / "project"
            project.mkdir()

            result = self.run_script(IDC, "portfolio", "--paths", str(project), str(project), "--json")

            self.assertEqual(result.returncode, 2)
            self.assertIn("distinct project directories", result.stderr)

    def test_idc_portfolio_renders_terminal_output_in_the_explicit_language(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            first_project = Path(temp_dir) / "first-project"
            second_project = Path(temp_dir) / "second-project"
            first_project.mkdir()
            second_project.mkdir()

            result = self.run_script(
                IDC,
                "portfolio",
                "--paths",
                str(first_project),
                str(second_project),
                "--language",
                "zh",
            )

            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            self.assertIn("项目数: 2", result.stdout)
            self.assertIn("合同:", result.stdout)

    def test_idc_cli_documents_its_explicit_scope_and_language_option(self) -> None:
        guide = ROOT / "docs" / "CLI.md"
        readme = (ROOT / "README.md").read_text(encoding="utf-8")
        validator = (ROOT / "scripts" / "validate_repository.py").read_text(encoding="utf-8")

        self.assertTrue(guide.is_file())
        guide_text = guide.read_text(encoding="utf-8")
        self.assertIn("idc.py status --project", guide_text)
        self.assertIn("idc.py evidence --project", guide_text)
        self.assertIn("idc.py portfolio --paths", guide_text)
        self.assertIn("--language zh", guide_text)
        self.assertIn(".idc/contracts", guide_text)
        self.assertIn("不读取项目源码", guide_text)
        self.assertIn("command-evidence", guide_text)
        self.assertIn("host-observed", guide_text)
        self.assertIn("portfolio", guide_text)
        self.assertIn("至少两个不同", guide_text)
        self.assertIn("[本地 CLI](docs/CLI.md)", readme)
        self.assertIn('"docs/CLI.md"', validator)

    def test_orchestrator_executes_registered_agents_with_artifact_handoffs(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            workspace = Path(temp_dir) / "workspace"
            workspace.mkdir()
            contract = workspace / "cross-layer-feature.squad.json"
            payload = json.loads(
                (ROOT / "contracts" / "examples" / "cross-layer-feature.squad.json").read_text(encoding="utf-8")
            )
            payload["authorization"] = {
                "required": False,
                "effects": [],
                "state": "not-required",
            }
            payload["verification"]["commands"] = [
                {
                    "id": "focused-check",
                    "argv": ["python", "-m", "unittest"],
                    "cwd": ".",
                }
            ]
            contract.write_text(json.dumps(payload), encoding="utf-8")
            (workspace / "test_focused_check.py").write_text(
                "\n".join(
                    (
                        "import unittest",
                        "",
                        "class FocusedCheck(unittest.TestCase):",
                        "    def test_check(self):",
                        "        print('focused check passed')",
                    )
                )
                + "\n",
                encoding="utf-8",
            )
            fake_opencode = workspace / "fake_opencode.py"
            fake_opencode.write_text(
                "\n".join(
                    (
                        "import json",
                        "import re",
                        "import sys",
                        "invocation_agent = sys.argv[sys.argv.index('--agent') + 1]",
                        "if invocation_agent != 'team':",
                        "    raise SystemExit(f'expected team, got {invocation_agent}')",
                        "agent = re.search(r\"registered '([^']+)' judgment\", sys.argv[-1]).group(1)",
                        "outputs = {",
                        "    'architecture': ('impact-contract', []),",
                        "    'code-review': ('review-findings', ['impact-contract']),",
                        "    'verify': ('verification-report', ['review-findings']),",
                        "}",
                        "artifact_id, consumed = outputs[agent]",
                        "output = {",
                        "    'artifact_id': artifact_id,",
                        "    'summary': f'{agent} result',",
                        "    'findings': [f'{agent} evidence'],",
                        "    'consumed_artifact_ids': consumed,",
                        "}",
                        "print(json.dumps({'type': 'tool_use', 'part': {'type': 'tool', 'tool': 'task', 'state': {'status': 'completed', 'input': {'subagent_type': agent}, 'metadata': {'sessionId': f'session-{agent}'}}}}))",
                        "print(json.dumps({'type': 'text', 'part': {'type': 'text', 'text': json.dumps(output)}}))",
                    )
                )
                + "\n",
                encoding="utf-8",
            )

            result = self.run_script(
                ORCHESTRATOR,
                "--contract",
                str(contract),
                "--workspace",
                str(workspace),
                "--request",
                "Add a field through every layer.",
                "--run-id",
                "executed-run",
                "--execute",
                "--opencode-command",
                sys.executable,
                "--opencode-command",
                str(fake_opencode),
            )

            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            run_dir = workspace / ".idc" / "runs" / "executed-run"
            run = json.loads((run_dir / "run.json").read_text(encoding="utf-8"))
            self.assertEqual(run["state"], "completed")
            review = json.loads((run_dir / "artifacts" / "review-findings.json").read_text(encoding="utf-8"))
            self.assertEqual(review["producer"], "code-review")
            self.assertEqual(review["output"]["consumed_artifact_ids"], ["impact-contract"])
            self.assertEqual(
                review["host_observation"],
                {
                    "invocation_agent": "team",
                    "subagent": "code-review",
                    "child_session_id": "session-code-review",
                },
            )
            command = json.loads((run_dir / "verification" / "focused-check.json").read_text(encoding="utf-8"))
            self.assertEqual(command["returncode"], 0)
            self.assertIn("focused check passed", (run_dir / "verification" / "focused-check.stdout.log").read_text(encoding="utf-8"))

    def test_orchestrator_rejects_worker_that_omits_required_handoff(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            workspace = Path(temp_dir) / "workspace"
            workspace.mkdir()
            contract = workspace / "cross-layer-feature.squad.json"
            payload = json.loads(
                (ROOT / "contracts" / "examples" / "cross-layer-feature.squad.json").read_text(encoding="utf-8")
            )
            payload["authorization"] = {
                "required": False,
                "effects": [],
                "state": "not-required",
            }
            payload["verification"]["commands"] = [
                {
                    "id": "focused-check",
                    "argv": ["python", "-m", "unittest"],
                    "cwd": ".",
                }
            ]
            contract.write_text(json.dumps(payload), encoding="utf-8")
            fake_opencode = workspace / "fake_opencode.py"
            fake_opencode.write_text(
                "\n".join(
                    (
                        "import json",
                        "import re",
                        "import sys",
                        "invocation_agent = sys.argv[sys.argv.index('--agent') + 1]",
                        "if invocation_agent != 'team':",
                        "    raise SystemExit(f'expected team, got {invocation_agent}')",
                        "agent = re.search(r\"registered '([^']+)' judgment\", sys.argv[-1]).group(1)",
                        "outputs = {",
                        "    'architecture': 'impact-contract',",
                        "    'code-review': 'review-findings',",
                        "    'verify': 'verification-report',",
                        "}",
                        "output = {",
                        "    'artifact_id': outputs[agent],",
                        "    'summary': f'{agent} result',",
                        "    'findings': [f'{agent} evidence'],",
                        "    'consumed_artifact_ids': [],",
                        "}",
                        "print(json.dumps({'type': 'tool_use', 'part': {'type': 'tool', 'tool': 'task', 'state': {'status': 'completed', 'input': {'subagent_type': agent}, 'metadata': {'sessionId': f'session-{agent}'}}}}))",
                        "print(json.dumps({'type': 'text', 'part': {'type': 'text', 'text': json.dumps(output)}}))",
                    )
                )
                + "\n",
                encoding="utf-8",
            )

            result = self.run_script(
                ORCHESTRATOR,
                "--contract",
                str(contract),
                "--workspace",
                str(workspace),
                "--request",
                "Add a field through every layer.",
                "--run-id",
                "missing-handoff",
                "--execute",
                "--opencode-command",
                sys.executable,
                "--opencode-command",
                str(fake_opencode),
            )

            self.assertEqual(result.returncode, 1)
            self.assertIn("required upstream artifacts", result.stderr)
            run_dir = workspace / ".idc" / "runs" / "missing-handoff"
            run = json.loads((run_dir / "run.json").read_text(encoding="utf-8"))
            self.assertEqual(run["state"], "failed")
            self.assertFalse((run_dir / "artifacts" / "review-findings.json").exists())

    def test_orchestrator_timeout_terminates_the_worker_process_tree(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            workspace = Path(temp_dir) / "workspace"
            workspace.mkdir()
            contract = workspace / "cross-layer-feature.squad.json"
            payload = json.loads(
                (ROOT / "contracts" / "examples" / "cross-layer-feature.squad.json").read_text(encoding="utf-8")
            )
            payload["authorization"] = {
                "required": False,
                "effects": [],
                "state": "not-required",
            }
            payload["verification"]["commands"] = [
                {
                    "id": "focused-check",
                    "argv": ["python", "-m", "unittest"],
                    "cwd": ".",
                }
            ]
            contract.write_text(json.dumps(payload), encoding="utf-8")
            worker = workspace / "worker_that_spawns_child.py"
            worker.write_text(
                "\n".join(
                    (
                        "import subprocess",
                        "import sys",
                        "import time",
                        "from pathlib import Path",
                        "workspace = Path(sys.argv[sys.argv.index('--dir') + 1])",
                        "child = subprocess.Popen([sys.executable, '-c', 'import time; time.sleep(30)'], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)",
                        "(workspace / 'child.pid').write_text(str(child.pid), encoding='utf-8')",
                        "time.sleep(30)",
                    )
                )
                + "\n",
                encoding="utf-8",
            )

            child_pid: int | None = None
            try:
                result = self.run_script(
                    ORCHESTRATOR,
                    "--contract",
                    str(contract),
                    "--workspace",
                    str(workspace),
                    "--request",
                    "Diagnose the fixture without edits.",
                    "--run-id",
                    "worker-timeout",
                    "--execute",
                    "--worker-timeout-seconds",
                    "1",
                    "--opencode-command",
                    sys.executable,
                    "--opencode-command",
                    str(worker),
                )

                self.assertEqual(result.returncode, 1, result.stdout + result.stderr)
                run_dir = workspace / ".idc" / "runs" / "worker-timeout"
                run = json.loads((run_dir / "run.json").read_text(encoding="utf-8"))
                self.assertEqual(run["state"], "failed")
                self.assertIn("agent-failed", (run_dir / "events.jsonl").read_text(encoding="utf-8"))

                child_pid = int((workspace / "child.pid").read_text(encoding="utf-8"))
                deadline = time.monotonic() + 3
                while time.monotonic() < deadline:
                    if os.name == "nt":
                        probe = subprocess.run(
                            ["tasklist", "/FI", f"PID eq {child_pid}", "/FO", "CSV", "/NH"],
                            text=True,
                            capture_output=True,
                            check=False,
                        )
                        is_running = str(child_pid) in probe.stdout
                    else:
                        try:
                            os.kill(child_pid, 0)
                            is_running = True
                        except ProcessLookupError:
                            is_running = False
                    if not is_running:
                        break
                    time.sleep(0.1)
                else:
                    self.fail("timed-out worker left a child process running")
            finally:
                if child_pid is not None:
                    try:
                        if os.name == "nt":
                            subprocess.run(
                                ["taskkill", "/PID", str(child_pid), "/T", "/F"],
                                capture_output=True,
                                check=False,
                            )
                        else:
                            os.kill(child_pid, signal.SIGKILL)
                    except ProcessLookupError:
                        pass

    def test_orchestrator_blocks_unsafe_verification_command_before_dispatch(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            workspace = Path(temp_dir) / "workspace"
            workspace.mkdir()
            contract = workspace / "cross-layer-feature.squad.json"
            payload = json.loads(
                (ROOT / "contracts" / "examples" / "cross-layer-feature.squad.json").read_text(encoding="utf-8")
            )
            payload["authorization"] = {
                "required": False,
                "effects": [],
                "state": "not-required",
            }
            payload["verification"]["commands"] = [
                {"id": "publish", "argv": ["git", "-C", "..", "push"], "cwd": "."}
            ]
            contract.write_text(json.dumps(payload), encoding="utf-8")

            result = self.run_script(
                ORCHESTRATOR,
                "--contract",
                str(contract),
                "--workspace",
                str(workspace),
                "--request",
                "Release the change.",
                "--run-id",
                "unsafe-command",
                "--execute",
                "--opencode-command",
                sys.executable,
                "--opencode-command",
                str(workspace / "not-run.py"),
            )

            self.assertEqual(result.returncode, 1)
            self.assertIn("blocked effect", result.stderr)
            run_dir = workspace / ".idc" / "runs" / "unsafe-command"
            run = json.loads((run_dir / "run.json").read_text(encoding="utf-8"))
            self.assertEqual(run["state"], "blocked")
            events = (run_dir / "events.jsonl").read_text(encoding="utf-8")
            self.assertNotIn("agent-dispatched", events)

    def test_orchestrator_blocks_git_alias_verification_commands(self) -> None:
        self.assertTrue(
            orchestrate_squad.command_is_unsafe(
                ["git", "-c", "alias.release=!git push", "release"]
            )
        )

    def test_orchestrator_allows_only_bounded_test_runner_commands(self) -> None:
        self.assertFalse(
            orchestrate_squad.command_is_unsafe(["python", "-m", "unittest"])
        )
        self.assertFalse(
            orchestrate_squad.command_is_unsafe(["python", "-m", "pytest"])
        )
        self.assertFalse(orchestrate_squad.command_is_unsafe(["pytest"]))
        self.assertTrue(
            orchestrate_squad.command_is_unsafe(
                ["python", "-c", "import subprocess; subprocess.run(['git', 'push'])"]
            )
        )
        self.assertTrue(
            orchestrate_squad.command_is_unsafe(["python", "-m", "pytest", "tests/test_one.py"])
        )
        self.assertTrue(
            orchestrate_squad.command_is_unsafe(["C:/untrusted/python.exe", "-m", "pytest"])
        )
        self.assertTrue(
            orchestrate_squad.command_is_unsafe(["python3", "-m", "unittest"])
        )

    def test_orchestrator_records_a_timed_out_verification_command(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            workspace = Path(temp_dir) / "workspace"
            workspace.mkdir()
            contract = workspace / "cross-layer-feature.squad.json"
            payload = json.loads(
                (ROOT / "contracts" / "examples" / "cross-layer-feature.squad.json").read_text(encoding="utf-8")
            )
            payload["authorization"] = {
                "required": False,
                "effects": [],
                "state": "not-required",
            }
            payload["verification"]["commands"] = [
                {
                    "id": "slow-check",
                    "argv": ["python", "-m", "unittest"],
                    "cwd": ".",
                }
            ]
            contract.write_text(json.dumps(payload), encoding="utf-8")
            (workspace / "test_slow_check.py").write_text(
                "\n".join(
                    (
                        "import time",
                        "import unittest",
                        "",
                        "class SlowCheck(unittest.TestCase):",
                        "    def test_wait(self):",
                        "        time.sleep(30)",
                    )
                )
                + "\n",
                encoding="utf-8",
            )
            fake_opencode = workspace / "fake_opencode.py"
            fake_opencode.write_text(
                "\n".join(
                    (
                        "import json",
                        "import re",
                        "import sys",
                        "agent = re.search(r\"registered '([^']+)' judgment\", sys.argv[-1]).group(1)",
                        "outputs = {",
                        "    'architecture': ('impact-contract', []),",
                        "    'code-review': ('review-findings', ['impact-contract']),",
                        "    'verify': ('verification-report', ['review-findings']),",
                        "}",
                        "artifact_id, consumed = outputs[agent]",
                        "output = {",
                        "    'artifact_id': artifact_id,",
                        "    'summary': f'{agent} result',",
                        "    'findings': [f'{agent} evidence'],",
                        "    'consumed_artifact_ids': consumed,",
                        "}",
                        "print(json.dumps({'type': 'tool_use', 'part': {'type': 'tool', 'tool': 'task', 'state': {'status': 'completed', 'input': {'subagent_type': agent}, 'metadata': {'sessionId': f'session-{agent}'}}}}))",
                        "print(json.dumps({'type': 'text', 'part': {'type': 'text', 'text': json.dumps(output)}}))",
                    )
                )
                + "\n",
                encoding="utf-8",
            )

            result = self.run_script(
                ORCHESTRATOR,
                "--contract",
                str(contract),
                "--workspace",
                str(workspace),
                "--request",
                "Verify the implementation without external effects.",
                "--run-id",
                "verification-timeout",
                "--execute",
                "--verification-timeout-seconds",
                "1",
                "--opencode-command",
                sys.executable,
                "--opencode-command",
                str(fake_opencode),
            )

            self.assertEqual(result.returncode, 1, result.stdout + result.stderr)
            self.assertIn("verification command 'slow-check' timed out", result.stderr)
            run_dir = workspace / ".idc" / "runs" / "verification-timeout"
            run = json.loads((run_dir / "run.json").read_text(encoding="utf-8"))
            self.assertEqual(run["state"], "failed")
            self.assertEqual(run["verification"][0]["kind"], "command-timeout")
            self.assertEqual(run["verification"][0]["timeout_seconds"], 1)
            self.assertIn("verification-timed-out", (run_dir / "events.jsonl").read_text(encoding="utf-8"))

    def test_orchestrator_blocks_contract_that_requires_authorization(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            workspace = Path(temp_dir) / "workspace"
            workspace.mkdir()
            contract = workspace / "cross-layer-feature.squad.json"
            payload = json.loads(
                (ROOT / "contracts" / "examples" / "cross-layer-feature.squad.json").read_text(encoding="utf-8")
            )
            payload["verification"]["commands"] = [
                {
                    "id": "focused-check",
                    "argv": ["python", "-m", "unittest"],
                    "cwd": ".",
                }
            ]
            contract.write_text(json.dumps(payload), encoding="utf-8")

            result = self.run_script(
                ORCHESTRATOR,
                "--contract",
                str(contract),
                "--workspace",
                str(workspace),
                "--request",
                "Release the change.",
                "--run-id",
                "authorization-required",
                "--execute",
                "--opencode-command",
                sys.executable,
                "--opencode-command",
                str(workspace / "not-run.py"),
            )

            self.assertEqual(result.returncode, 1)
            self.assertIn("approval token", result.stderr)
            run_dir = workspace / ".idc" / "runs" / "authorization-required"
            run = json.loads((run_dir / "run.json").read_text(encoding="utf-8"))
            self.assertEqual(run["state"], "blocked")
            self.assertIn("authorization-required", (run_dir / "events.jsonl").read_text(encoding="utf-8"))

    def test_orchestrator_blocks_execution_without_a_verification_command(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            workspace = Path(temp_dir) / "workspace"
            workspace.mkdir()
            contract = workspace / "cross-layer-feature.squad.json"
            payload = json.loads(
                (ROOT / "contracts" / "examples" / "cross-layer-feature.squad.json").read_text(encoding="utf-8")
            )
            payload["authorization"] = {
                "required": False,
                "effects": [],
                "state": "not-required",
            }
            contract.write_text(json.dumps(payload), encoding="utf-8")

            result = self.run_script(
                ORCHESTRATOR,
                "--contract",
                str(contract),
                "--workspace",
                str(workspace),
                "--request",
                "Implement the change.",
                "--run-id",
                "missing-verification-command",
                "--execute",
                "--opencode-command",
                sys.executable,
                "--opencode-command",
                str(workspace / "not-run.py"),
            )

            self.assertEqual(result.returncode, 1)
            self.assertIn("requires at least one declared verification command", result.stderr)
            run_dir = workspace / ".idc" / "runs" / "missing-verification-command"
            run = json.loads((run_dir / "run.json").read_text(encoding="utf-8"))
            self.assertEqual(run["state"], "blocked")
            self.assertNotIn("agent-dispatched", (run_dir / "events.jsonl").read_text(encoding="utf-8"))

    def test_orchestrator_blocks_verification_command_outside_workspace(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            workspace = Path(temp_dir) / "workspace"
            workspace.mkdir()
            contract = workspace / "cross-layer-feature.squad.json"
            payload = json.loads(
                (ROOT / "contracts" / "examples" / "cross-layer-feature.squad.json").read_text(encoding="utf-8")
            )
            payload["authorization"] = {
                "required": False,
                "effects": [],
                "state": "not-required",
            }
            payload["verification"]["commands"] = [
                {
                    "id": "outside-workspace",
                    "argv": ["python", "-m", "unittest"],
                    "cwd": "..",
                }
            ]
            contract.write_text(json.dumps(payload), encoding="utf-8")

            result = self.run_script(
                ORCHESTRATOR,
                "--contract",
                str(contract),
                "--workspace",
                str(workspace),
                "--request",
                "Verify the change.",
                "--run-id",
                "outside-workspace",
                "--execute",
                "--opencode-command",
                sys.executable,
                "--opencode-command",
                str(workspace / "not-run.py"),
            )

            self.assertEqual(result.returncode, 1)
            self.assertIn("escapes the workspace", result.stderr)
            run_dir = workspace / ".idc" / "runs" / "outside-workspace"
            run = json.loads((run_dir / "run.json").read_text(encoding="utf-8"))
            self.assertEqual(run["state"], "blocked")
            self.assertNotIn("agent-dispatched", (run_dir / "events.jsonl").read_text(encoding="utf-8"))

    def test_orchestration_controller_assets_are_registered_and_documented(self) -> None:
        guide = (ROOT / "docs" / "ORCHESTRATION.md").read_text(encoding="utf-8")
        contracts = (ROOT / "docs" / "CONTRACTS.md").read_text(encoding="utf-8")
        opencode = (ROOT / "docs" / "OPENCODE_ADAPTER.md").read_text(encoding="utf-8")
        permissions = (ROOT / "docs" / "PERMISSIONS.md").read_text(encoding="utf-8")
        validator = (ROOT / "scripts" / "validate_repository.py").read_text(encoding="utf-8")
        for required_text in (
            "--execute",
            "--opencode-command",
            "--format json",
            "controller-observed",
            "agent-declared",
            "host_observation",
            "does not enforce worker tool permissions",
            "--verification-timeout-seconds",
            "command-timeout",
            "verification-timed-out",
            "Git aliases",
            "python -c",
            "Absolute interpreter paths",
        ):
            self.assertIn(required_text, guide)
        self.assertIn("verification.commands", contracts)
        self.assertIn("ORCHESTRATION.md", opencode)
        self.assertIn("approval token", permissions)
        self.assertIn('"docs/ORCHESTRATION.md"', validator)
        self.assertIn('"scripts/orchestrate_squad.py"', validator)

    def test_orchestrator_resolves_the_default_opencode_command(self) -> None:
        with patch.object(
            orchestrate_squad.shutil,
            "which",
            return_value=r"C:\Users\example\AppData\Roaming\npm\opencode.CMD",
        ):
            command = orchestrate_squad.resolve_opencode_command(None)

        self.assertEqual(command, [r"C:\Users\example\AppData\Roaming\npm\opencode.CMD"])

    def test_public_entry_discloses_unproven_host_routing_before_method_claims(self) -> None:
        readme = (ROOT / "README.md").read_text(encoding="utf-8")
        minimal = (ROOT / "docs" / "MINIMAL.md").read_text(encoding="utf-8")
        design = (ROOT / "DESIGN.md").read_text(encoding="utf-8")
        roadmap = (ROOT / "plans" / "ROADMAP.md").read_text(encoding="utf-8")

        self.assertIn("实证状态：自动宿主路由尚未通过验收", readme[:1200])
        self.assertIn("[最小路径](docs/MINIMAL.md)", readme)
        for concept in ("Skill", "Squad", "Contract", "Evidence"):
            self.assertIn(concept, minimal)
        self.assertIn("This product does not exist today", design[:1200])
        self.assertIn("real-host acceptance is mismatched", roadmap)

    def test_offline_success_output_discloses_host_routing_boundary(self) -> None:
        for script in (VALIDATOR, CONTRACT_VALIDATOR, CONTRACT_EVALUATOR, AUDITOR):
            result = self.run_script(script)
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            self.assertIn("prove host routing", result.stdout)

    def test_contract_validator_rejects_self_handoff(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            contract_root = Path(temp_dir)
            payload = json.loads(
                (ROOT / "contracts" / "examples" / "cross-layer-feature.squad.json").read_text(encoding="utf-8")
            )
            payload["handoffs"][0]["to"] = "architecture"
            (contract_root / "self-handoff.json").write_text(json.dumps(payload), encoding="utf-8")
            result = self.run_script(CONTRACT_VALIDATOR, "--contracts", str(contract_root))
            self.assertEqual(result.returncode, 1)
            self.assertIn("must transfer between distinct members", result.stdout)

    def test_contract_validator_rejects_duplicate_squad_members(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            contract_root = Path(temp_dir)
            payload = json.loads(
                (ROOT / "contracts" / "examples" / "cross-layer-feature.squad.json").read_text(encoding="utf-8")
            )
            payload["members"][1]["skill"] = "architecture"
            (contract_root / "duplicate-member.json").write_text(json.dumps(payload), encoding="utf-8")
            result = self.run_script(CONTRACT_VALIDATOR, "--contracts", str(contract_root))
            self.assertEqual(result.returncode, 1)
            self.assertIn("duplicate squad member", result.stdout)

    def test_contract_validator_rejects_handoff_without_producer_output(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            contract_root = Path(temp_dir)
            payload = json.loads(
                (ROOT / "contracts" / "examples" / "cross-layer-feature.squad.json").read_text(encoding="utf-8")
            )
            payload["handoffs"][0]["artifact_id"] = "missing-artifact"
            (contract_root / "invalid-artifact.json").write_text(json.dumps(payload), encoding="utf-8")
            result = self.run_script(CONTRACT_VALIDATOR, "--contracts", str(contract_root))
            self.assertEqual(result.returncode, 1)
            self.assertIn("not produced", result.stdout)

    def test_contract_layer_assets_are_registered_for_repository_validation(self) -> None:
        validator = (ROOT / "scripts" / "validate_repository.py").read_text(encoding="utf-8")
        contracts = (ROOT / "docs" / "CONTRACTS.md").read_text(encoding="utf-8")
        self.assertTrue((ROOT / "schemas" / "intent-driven-coding-contract-v1.schema.json").is_file())
        self.assertTrue((ROOT / "contracts" / "examples" / "cross-layer-feature.squad.json").is_file())
        self.assertTrue((ROOT / "evals" / "fixtures" / "cross-layer-feature.record.json").is_file())
        self.assertIn('"docs/CONTRACTS.md"', validator)
        self.assertIn('"scripts/validate_contracts.py"', validator)
        self.assertIn('"scripts/evaluate_contracts.py"', validator)
        self.assertIn("validate_contracts", validator)
        self.assertIn("jsonschema", contracts)
        self.assertIn("evaluate_contracts.py", contracts)

    def test_english_quickstart_installs_contract_validation_dependency(self) -> None:
        english = (ROOT / "README.md").read_text(encoding="utf-8").split("## Optional Scaffold Quick Start", 1)[1]
        self.assertIn("python -m pip install -r requirements.txt", english)

    def test_contract_guide_validates_the_idc_parent_directory(self) -> None:
        contracts = (ROOT / "docs" / "CONTRACTS.md").read_text(encoding="utf-8")
        self.assertIn("python scripts/validate_contracts.py --contracts ../my-project/.idc\n", contracts)
        self.assertIn("three document kinds", contracts)
        self.assertIn("scripts/evaluate_contracts.py", contracts)

    def test_quickstart_maps_claude_contract_paths(self) -> None:
        quickstart = (ROOT / "QUICKSTART.md").read_text(encoding="utf-8")
        self.assertIn(".claude/templates/SQUAD.md", quickstart)
        self.assertIn(".claude/evals/squad-routing.json", quickstart)

    def test_ai_entry_prioritizes_adaptation_over_copying(self) -> None:
        entry = (ROOT / "AI_START_HERE.md").read_text(encoding="utf-8")
        self.assertIn("Do not copy this repository unchanged", entry)
        self.assertIn("Understand The Target", entry)
        self.assertIn("Design Before Copying", entry)
        self.assertIn("Optional Scaffolding", entry)

    def test_ai_first_adoption_works_before_full_system_design(self) -> None:
        entry = (ROOT / "AI_START_HERE.md").read_text(encoding="utf-8")
        quickstart = (ROOT / "QUICKSTART.md").read_text(encoding="utf-8")
        readme = (ROOT / "README.md").read_text(encoding="utf-8")
        for phrase in (
            "Learn While Delivering",
            "Do not make full framework adaptation a prerequisite",
            "Progressive Adoption Loop",
        ):
            self.assertIn(phrase, entry)
        self.assertIn("First Useful Task", quickstart)
        self.assertIn("The human does not need to study the whole framework first", quickstart)
        self.assertIn("AI 先学并反哺核心概念", readme)

    def test_adoption_preserves_human_judgment_and_collaborative_learning(self) -> None:
        entry = (ROOT / "AI_START_HERE.md").read_text(encoding="utf-8")
        quickstart = (ROOT / "QUICKSTART.md").read_text(encoding="utf-8")
        readme = (ROOT / "README.md").read_text(encoding="utf-8")
        guide = (ROOT / "docs" / "ADAPTATION_GUIDE.md").read_text(encoding="utf-8")
        router = (ROOT / "skills" / "team" / "SKILL.md").read_text(encoding="utf-8")
        designer = (ROOT / "skills" / "meta-skill-designer" / "SKILL.md").read_text(encoding="utf-8")
        template = (ROOT / "templates" / "AGENT_ENTRY.md").read_text(encoding="utf-8")
        platforms = (ROOT / "docs" / "PLATFORM_ADAPTERS.md").read_text(encoding="utf-8")

        self.assertIn("AI-first is the starting mode", entry)
        self.assertIn("Human judgment sets the quality ceiling", entry)
        self.assertIn("teach back the core concepts", entry)
        self.assertIn("Human And AI Learn Together", quickstart)
        self.assertIn("人机在真实任务中协作学习、共同判断、渐进搭建", readme)
        self.assertIn("Collaborative learning track", guide)
        self.assertIn("Collaborative Learning Mode", router)
        self.assertIn("human experience and judgment", designer)
        self.assertIn("Human judgment is not limited to permission gates", template)
        self.assertIn("teach back relevant concepts", platforms)

    def test_progressive_adoption_collects_evidence_before_creating_skills(self) -> None:
        router = (ROOT / "skills" / "team" / "SKILL.md").read_text(encoding="utf-8")
        designer = (ROOT / "skills" / "meta-skill-designer" / "SKILL.md").read_text(encoding="utf-8")
        guide = (ROOT / "docs" / "ADAPTATION_GUIDE.md").read_text(encoding="utf-8")
        self.assertIn("Adoption Mode", router)
        self.assertIn("deliver the current safe task", router)
        self.assertIn("progressive evidence", designer)
        self.assertIn("Evidence Before Infrastructure", guide)
        self.assertIn("teach through brief decisions", guide.lower())

    def test_author_discloses_las_origin_without_benchmark_claims(self) -> None:
        author = (ROOT / "AUTHOR.md").read_text(encoding="utf-8")
        self.assertIn("https://lasystem.cn/", author)
        self.assertIn("LAS", author)
        self.assertIn("个人实践", author)
        self.assertIn("personal practice", author)
        self.assertIn("not a benchmark", author.lower())

    def test_requirement_translation_remains_router_control_plane(self) -> None:
        router = (ROOT / "skills" / "team" / "SKILL.md").read_text(encoding="utf-8")
        playbook = (ROOT / "docs" / "TEAM_PLAYBOOK.md").read_text(encoding="utf-8")
        self.assertIn("Requirement Translation Gate", router)
        self.assertIn("next smallest safe route", router)
        self.assertIn("not a separate specialist", playbook)

    def test_user_language_preference_controls_final_presentation(self) -> None:
        protocol = (ROOT / "docs" / "PROTOCOL.md").read_text(encoding="utf-8")
        router = (ROOT / "skills" / "team" / "SKILL.md").read_text(encoding="utf-8")
        playbook = (ROOT / "templates" / "AI_ENGINEERING_PLAYBOOK.md").read_text(encoding="utf-8")
        evaluation = (ROOT / "docs" / "EVALUATION.md").read_text(encoding="utf-8")
        las_case = (
            ROOT / "references" / "host-acceptance" / "las-5.2.3-opencode-1.18.5-2026-07-26.md"
        ).read_text(encoding="utf-8")

        self.assertIn("Presentation preference", protocol)
        self.assertIn("explicit language preference", protocol)
        self.assertIn("current user language", protocol)
        self.assertIn("Presentation language", router)
        self.assertIn("Presentation language:", playbook)
        self.assertIn("reviewer or target user's preferred language", evaluation)
        self.assertIn("## 证据卡片", las_case)

    def test_platform_guide_covers_mainstream_tools(self) -> None:
        guide = (ROOT / "docs" / "PLATFORM_ADAPTERS.md").read_text(encoding="utf-8")
        for platform in ("Claude Code", "OpenCode", "Codex", "Cursor", "GitHub Copilot"):
            self.assertIn(platform, guide)
        self.assertIn("does not claim automatic compatibility", guide)

    def test_platforms_receive_self_recognizable_adoption_instructions(self) -> None:
        entry = (ROOT / "AI_START_HERE.md").read_text(encoding="utf-8")
        guide = (ROOT / "docs" / "PLATFORM_ADAPTERS.md").read_text(encoding="utf-8")
        self.assertIn("Identify Your Host First", entry)
        self.assertIn("If You Are Claude Code", guide)
        self.assertIn("If You Are OpenCode", guide)
        self.assertIn("If You Are Codex", guide)
        self.assertIn("If You Are Cursor Or GitHub Copilot", guide)
        self.assertIn("act on that section immediately", guide)

    def test_opencode_adapter_documents_and_validates_native_assets(self) -> None:
        adapter = (ROOT / "docs" / "OPENCODE_ADAPTER.md").read_text(encoding="utf-8")
        validator = (ROOT / "scripts" / "validate_repository.py").read_text(encoding="utf-8")
        self.assertIn("OpenCode Adapter", adapter)
        self.assertIn("--platform opencode", adapter)
        self.assertIn("does not generate `opencode.json`", adapter)
        self.assertIn('"docs/OPENCODE_ADAPTER.md"', validator)
        for name, mode in {
            "team": "primary",
            "architecture": "subagent",
            "debug": "subagent",
            "code-review": "subagent",
            "verify": "subagent",
            "meta-skill-designer": "subagent",
            "skill-creator": "subagent",
        }.items():
            agent = (ROOT / "templates" / "opencode" / "agents" / f"{name}.md").read_text(encoding="utf-8")
            self.assertIn("description:", agent)
            self.assertIn(f"mode: {mode}", agent)

    def test_claude_code_adapter_documents_and_validates_native_assets(self) -> None:
        adapter = (ROOT / "docs" / "CLAUDE_CODE_ADAPTER.md").read_text(encoding="utf-8")
        validator = (ROOT / "scripts" / "validate_repository.py").read_text(encoding="utf-8")
        self.assertIn("Claude Code Adapter", adapter)
        self.assertIn("--platform claude-code", adapter)
        self.assertIn("does not generate `settings.json`", adapter)
        self.assertIn('"docs/CLAUDE_CODE_ADAPTER.md"', validator)
        self.assertIn('"templates/claude/CLAUDE.md"', validator)
        for name in (
            "architecture",
            "debug",
            "code-review",
            "verify",
            "meta-skill-designer",
            "skill-creator",
        ):
            agent = (ROOT / "templates" / "claude" / "agents" / f"{name}.md").read_text(encoding="utf-8")
            self.assertIn(f"name: {name}", agent)
            self.assertIn("description:", agent)
            self.assertRegex(agent, r"(?m)^tools: .*\bSkill\b")

    def test_opencode_execution_agents_disclose_inherited_bash_policy(self) -> None:
        adapter = (ROOT / "docs" / "OPENCODE_ADAPTER.md").read_text(encoding="utf-8")
        self.assertIn("they are not read-only Agents", adapter)
        for name in ("debug", "verify"):
            agent = (ROOT / "templates" / "opencode" / "agents" / f"{name}.md").read_text(encoding="utf-8")
            self.assertNotIn("Read-only", agent)
            self.assertIn("Shell commands remain subject to the target project's OpenCode policy", agent)

    def test_skill_auditor_passes(self) -> None:
        result = self.run_script(AUDITOR)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

    def test_bootstrap_dry_run_writes_nothing(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            target = Path(temp_dir)
            result = self.run_script(
                BOOTSTRAP,
                "--target",
                str(target),
                "--project-name",
                "Example Project",
                "--dry-run",
            )
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            self.assertFalse((target / "AGENTS.md").exists())
            self.assertIn("未写入任何文件", result.stdout)

    def test_bootstrap_applies_and_preserves_existing_files(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            target = Path(temp_dir)
            first = self.run_script(
                BOOTSTRAP,
                "--target",
                str(target),
                "--project-name",
                "Example Project",
                "--apply",
            )
            self.assertEqual(first.returncode, 0, first.stdout + first.stderr)
            self.assertIn("# Example Project Architecture Guide", (target / "AGENTS.md").read_text(encoding="utf-8"))
            skill = target / ".agent" / "skills" / "team" / "SKILL.md"
            self.assertTrue(skill.is_file())
            self.assertTrue((target / "SQUADS.md").is_file())
            self.assertTrue((target / ".agent" / "templates" / "SQUAD.md").is_file())
            self.assertTrue((target / ".agent" / "skills" / "meta-skill-designer" / "SKILL.md").is_file())
            self.assertTrue((target / ".agent" / "skills" / "skill-creator" / "SKILL.md").is_file())
            self.assertTrue((target / ".agent" / "evals" / "squad-routing.json").is_file())
            self.assertTrue((target / ".agent" / "evals" / "skill-design.json").is_file())
            squads = (target / "SQUADS.md").read_text(encoding="utf-8")
            self.assertIn("# Example Project Professional Squads", squads)

            (target / "AGENTS.md").write_text("user-owned\n", encoding="utf-8")
            second = self.run_script(
                BOOTSTRAP,
                "--target",
                str(target),
                "--project-name",
                "Example Project",
                "--apply",
            )
            self.assertEqual(second.returncode, 0, second.stdout + second.stderr)
            self.assertEqual((target / "AGENTS.md").read_text(encoding="utf-8"), "user-owned\n")
            self.assertIn("SKIP existing", second.stdout)

    def test_bootstrap_opencode_applies_native_layout(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            target = Path(temp_dir)
            result = self.run_script(
                BOOTSTRAP,
                "--target",
                str(target),
                "--project-name",
                "Example Project",
                "--platform",
                "opencode",
                "--apply",
            )
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            self.assertTrue((target / ".opencode" / "agents" / "team.md").is_file())
            self.assertTrue((target / ".opencode" / "agents" / "verify.md").is_file())
            self.assertTrue((target / ".opencode" / "skills" / "team" / "SKILL.md").is_file())
            self.assertTrue((target / ".opencode" / "templates" / "SQUAD.md").is_file())
            self.assertTrue((target / ".opencode" / "evals" / "squad-routing.json").is_file())
            self.assertFalse((target / ".agent").exists())

            team_agent = (target / ".opencode" / "agents" / "team.md").read_text(encoding="utf-8")
            self.assertIn("mode: primary", team_agent)
            self.assertNotIn("permission:", team_agent)

            architecture_agent = (target / ".opencode" / "agents" / "architecture.md").read_text(encoding="utf-8")
            self.assertIn("edit: deny", architecture_agent)
            self.assertIn("bash: deny", architecture_agent)

    def test_bootstrap_claude_code_applies_native_layout(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            target = Path(temp_dir)
            result = self.run_script(
                BOOTSTRAP,
                "--target",
                str(target),
                "--project-name",
                "Example Project",
                "--platform",
                "claude-code",
                "--apply",
            )
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            self.assertTrue((target / ".claude" / "CLAUDE.md").is_file())
            self.assertTrue((target / ".claude" / "agents" / "architecture.md").is_file())
            self.assertTrue((target / ".claude" / "skills" / "team" / "SKILL.md").is_file())
            self.assertTrue((target / ".claude" / "templates" / "SQUAD.md").is_file())
            self.assertTrue((target / ".claude" / "evals" / "squad-routing.json").is_file())
            self.assertFalse((target / ".agent").exists())

            entry = (target / ".claude" / "CLAUDE.md").read_text(encoding="utf-8")
            self.assertIn("# Example Project Claude Code Entry", entry)
            architecture_agent = (target / ".claude" / "agents" / "architecture.md").read_text(encoding="utf-8")
            self.assertIn("tools: Read, Grep, Glob", architecture_agent)
            for name in ("debug", "verify", "skill-creator"):
                skill = (target / ".claude" / "skills" / name / "SKILL.md").read_text(encoding="utf-8")
                self.assertNotIn("allowed-tools:", skill)

    def test_project_validator_rejects_missing_team_skill_for_native_adapters(self) -> None:
        for platform, skill_root in (
            ("opencode", Path(".opencode/skills")),
            ("claude-code", Path(".claude/skills")),
        ):
            with self.subTest(platform=platform), tempfile.TemporaryDirectory() as temp_dir:
                target = Path(temp_dir)
                install = self.run_script(
                    BOOTSTRAP,
                    "--target",
                    str(target),
                    "--project-name",
                    "Example Project",
                    "--platform",
                    platform,
                    "--apply",
                )
                self.assertEqual(install.returncode, 0, install.stdout + install.stderr)
                (target / skill_root / "team" / "SKILL.md").unlink()
                result = self.run_script(
                    PROJECT_VALIDATOR,
                    "--target",
                    str(target),
                    "--platform",
                    platform,
                )
                self.assertEqual(result.returncode, 1)
                self.assertIn("missing required Skill: team", result.stdout)

    def test_project_validator_rejects_opencode_agent_missing_read_only_permission(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            target = Path(temp_dir)
            install = self.run_script(
                BOOTSTRAP,
                "--target",
                str(target),
                "--project-name",
                "Example Project",
                "--platform",
                "opencode",
                "--apply",
            )
            self.assertEqual(install.returncode, 0, install.stdout + install.stderr)
            agent = target / ".opencode" / "agents" / "architecture.md"
            agent.write_text(agent.read_text(encoding="utf-8").replace("  edit: deny\n", ""), encoding="utf-8")
            result = self.run_script(
                PROJECT_VALIDATOR,
                "--target",
                str(target),
                "--platform",
                "opencode",
            )
            self.assertEqual(result.returncode, 1)
            self.assertIn("permission edit must be deny", result.stdout)

    def test_project_validator_rejects_opencode_agent_permission_grant(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            target = Path(temp_dir)
            install = self.run_script(
                BOOTSTRAP,
                "--target",
                str(target),
                "--project-name",
                "Example Project",
                "--platform",
                "opencode",
                "--apply",
            )
            self.assertEqual(install.returncode, 0, install.stdout + install.stderr)
            agent = target / ".opencode" / "agents" / "team.md"
            agent.write_text(
                agent.read_text(encoding="utf-8").replace(
                    "mode: primary\n",
                    "mode: primary\npermission:\n  bash: allow\n",
                ),
                encoding="utf-8",
            )
            result = self.run_script(
                PROJECT_VALIDATOR,
                "--target",
                str(target),
                "--platform",
                "opencode",
            )
            self.assertEqual(result.returncode, 1)
            self.assertIn("permission entries must exactly", result.stdout)

    def test_project_validator_rejects_claude_agent_with_unapproved_tools(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            target = Path(temp_dir)
            install = self.run_script(
                BOOTSTRAP,
                "--target",
                str(target),
                "--project-name",
                "Example Project",
                "--platform",
                "claude-code",
                "--apply",
            )
            self.assertEqual(install.returncode, 0, install.stdout + install.stderr)
            agent = target / ".claude" / "agents" / "architecture.md"
            agent.write_text(
                agent.read_text(encoding="utf-8").replace(
                    "tools: Read, Grep, Glob, Skill",
                    "tools: Read, Grep, Glob, Edit, Skill",
                ),
                encoding="utf-8",
            )
            result = self.run_script(
                PROJECT_VALIDATOR,
                "--target",
                str(target),
                "--platform",
                "claude-code",
            )
            self.assertEqual(result.returncode, 1)
            self.assertIn("tools must be exactly", result.stdout)

    def test_project_validator_rejects_claude_agent_permission_override(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            target = Path(temp_dir)
            install = self.run_script(
                BOOTSTRAP,
                "--target",
                str(target),
                "--project-name",
                "Example Project",
                "--platform",
                "claude-code",
                "--apply",
            )
            self.assertEqual(install.returncode, 0, install.stdout + install.stderr)
            agent = target / ".claude" / "agents" / "debug.md"
            agent.write_text(
                agent.read_text(encoding="utf-8").replace(
                    "tools: Read, Grep, Glob, Bash, Skill\n",
                    "tools: Read, Grep, Glob, Bash, Skill\npermissionMode: bypassPermissions\n",
                ),
                encoding="utf-8",
            )
            result = self.run_script(
                PROJECT_VALIDATOR,
                "--target",
                str(target),
                "--platform",
                "claude-code",
            )
            self.assertEqual(result.returncode, 1)
            self.assertIn("unexpected frontmatter field", result.stdout)

    def test_bootstrap_rejects_symlinked_destination_outside_target(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            target = root / "target"
            outside = root / "outside"
            target.mkdir()
            outside.mkdir()
            try:
                os.symlink(outside, target / ".opencode", target_is_directory=True)
            except OSError as exc:
                self.skipTest(f"Directory symlinks are unavailable: {exc}")

            result = self.run_script(
                BOOTSTRAP,
                "--target",
                str(target),
                "--project-name",
                "Example Project",
                "--platform",
                "opencode",
                "--apply",
            )
            self.assertNotEqual(result.returncode, 0, result.stdout + result.stderr)
            self.assertIn("destination escapes target", result.stdout)
            self.assertFalse((outside / "agents" / "team.md").exists())

    def test_bootstrap_rejects_compatible_local_skill_collision(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            target = Path(temp_dir)
            collision = target / ".claude" / "skills" / "team"
            collision.mkdir(parents=True)
            (collision / "SKILL.md").write_text("---\nname: team\ndescription: Existing skill\n---\n", encoding="utf-8")

            result = self.run_script(
                BOOTSTRAP,
                "--target",
                str(target),
                "--project-name",
                "Example Project",
                "--platform",
                "opencode",
                "--apply",
            )
            self.assertEqual(result.returncode, 1, result.stdout + result.stderr)
            self.assertIn("conflicting OpenCode skill", result.stderr)
            self.assertFalse((target / "AGENTS.md").exists())

    def test_bootstrap_rejects_ancestor_compatible_skill_collision(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            (root / ".git").mkdir()
            target = root / "nested" / "project"
            target.mkdir(parents=True)
            collision = root / ".claude" / "skills" / "team"
            collision.mkdir(parents=True)
            (collision / "SKILL.md").write_text("---\nname: team\ndescription: Existing skill\n---\n", encoding="utf-8")

            result = self.run_script(
                BOOTSTRAP,
                "--target",
                str(target),
                "--project-name",
                "Example Project",
                "--platform",
                "opencode",
                "--apply",
            )
            self.assertEqual(result.returncode, 1, result.stdout + result.stderr)
            self.assertIn("conflicting OpenCode skill", result.stderr)
            self.assertFalse((target / "AGENTS.md").exists())

    def test_bootstrap_rejects_ancestor_opencode_skill_collision(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            (root / ".git").mkdir()
            target = root / "nested" / "project"
            target.mkdir(parents=True)
            collision = root / ".opencode" / "skills" / "team"
            collision.mkdir(parents=True)
            (collision / "SKILL.md").write_text("---\nname: team\ndescription: Existing skill\n---\n", encoding="utf-8")

            result = self.run_script(
                BOOTSTRAP,
                "--target",
                str(target),
                "--project-name",
                "Example Project",
                "--platform",
                "opencode",
                "--apply",
            )
            self.assertEqual(result.returncode, 1, result.stdout + result.stderr)
            self.assertIn("conflicting OpenCode skill", result.stderr)
            self.assertFalse((target / "AGENTS.md").exists())

    def test_project_validator_accepts_configured_opencode_framework(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            target = Path(temp_dir)
            install = self.run_script(
                BOOTSTRAP,
                "--target",
                str(target),
                "--project-name",
                "Example Project",
                "--platform",
                "opencode",
                "--apply",
            )
            self.assertEqual(install.returncode, 0, install.stdout + install.stderr)
            for path in (
                target / "AGENTS.md",
                target / "AI_ENGINEERING_PLAYBOOK.md",
                target / "SQUADS.md",
                target / ".opencode" / "templates" / "SQUAD.md",
            ):
                text = path.read_text(encoding="utf-8")
                path.write_text(re.sub(r"\{\{[^{}]+\}\}", "configured-value", text), encoding="utf-8")

            result = self.run_script(
                PROJECT_VALIDATOR,
                "--target",
                str(target),
                "--platform",
                "opencode",
            )
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            self.assertIn("项目验证通过", result.stdout)

    def test_project_validator_accepts_configured_claude_code_framework(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            target = Path(temp_dir)
            install = self.run_script(
                BOOTSTRAP,
                "--target",
                str(target),
                "--project-name",
                "Example Project",
                "--platform",
                "claude-code",
                "--apply",
            )
            self.assertEqual(install.returncode, 0, install.stdout + install.stderr)
            for path in (
                target / "AGENTS.md",
                target / "AI_ENGINEERING_PLAYBOOK.md",
                target / "SQUADS.md",
                target / ".claude" / "templates" / "SQUAD.md",
            ):
                text = path.read_text(encoding="utf-8")
                path.write_text(re.sub(r"\{\{[^{}]+\}\}", "configured-value", text), encoding="utf-8")

            result = self.run_script(
                PROJECT_VALIDATOR,
                "--target",
                str(target),
                "--platform",
                "claude-code",
            )
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            self.assertIn("项目验证通过", result.stdout)

    def test_project_validator_accepts_lean_native_adapter_roster(self) -> None:
        for platform, framework_root, agent_root in (
            ("opencode", Path(".opencode"), Path(".opencode/agents")),
            ("claude-code", Path(".claude"), Path(".claude/agents")),
        ):
            with self.subTest(platform=platform), tempfile.TemporaryDirectory() as temp_dir:
                target = Path(temp_dir)
                install = self.run_script(
                    BOOTSTRAP,
                    "--target",
                    str(target),
                    "--project-name",
                    "Example Project",
                    "--platform",
                    platform,
                    "--apply",
                )
                self.assertEqual(install.returncode, 0, install.stdout + install.stderr)
                for path in (
                    target / "AGENTS.md",
                    target / "AI_ENGINEERING_PLAYBOOK.md",
                    target / "SQUADS.md",
                    target / framework_root / "templates" / "SQUAD.md",
                ):
                    text = path.read_text(encoding="utf-8")
                    path.write_text(re.sub(r"\{\{[^{}]+\}\}", "configured-value", text), encoding="utf-8")
                (target / "SQUADS.md").write_text("# Lean Squads\n", encoding="utf-8")
                for name in (
                    "architecture",
                    "debug",
                    "code-review",
                    "verify",
                    "meta-skill-designer",
                    "skill-creator",
                ):
                    (target / framework_root / "skills" / name / "SKILL.md").unlink()
                    (target / agent_root / f"{name}.md").unlink()
                for path in (target / framework_root / "evals").glob("*.json"):
                    path.unlink()
                result = self.run_script(
                    PROJECT_VALIDATOR,
                    "--target",
                    str(target),
                    "--platform",
                    platform,
                )
                self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

    def test_project_validator_uses_claude_skill_directory_names(self) -> None:
        for replacement in ("", "name: team-display-name\n"):
            with self.subTest(replacement=replacement), tempfile.TemporaryDirectory() as temp_dir:
                target = Path(temp_dir)
                install = self.run_script(
                    BOOTSTRAP,
                    "--target",
                    str(target),
                    "--project-name",
                    "Example Project",
                    "--platform",
                    "claude-code",
                    "--apply",
                )
                self.assertEqual(install.returncode, 0, install.stdout + install.stderr)
                for path in (
                    target / "AGENTS.md",
                    target / "AI_ENGINEERING_PLAYBOOK.md",
                    target / "SQUADS.md",
                    target / ".claude" / "templates" / "SQUAD.md",
                ):
                    text = path.read_text(encoding="utf-8")
                    path.write_text(re.sub(r"\{\{[^{}]+\}\}", "configured-value", text), encoding="utf-8")
                skill = target / ".claude" / "skills" / "team" / "SKILL.md"
                skill.write_text(
                    skill.read_text(encoding="utf-8").replace("name: team\n", replacement),
                    encoding="utf-8",
                )
                result = self.run_script(
                    PROJECT_VALIDATOR,
                    "--target",
                    str(target),
                    "--platform",
                    "claude-code",
                )
                self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

    def test_project_validator_rejects_native_agent_without_matching_skill(self) -> None:
        for platform, framework_root, agent_root in (
            ("opencode", Path(".opencode"), Path(".opencode/agents")),
            ("claude-code", Path(".claude"), Path(".claude/agents")),
        ):
            with self.subTest(platform=platform), tempfile.TemporaryDirectory() as temp_dir:
                target = Path(temp_dir)
                install = self.run_script(
                    BOOTSTRAP,
                    "--target",
                    str(target),
                    "--project-name",
                    "Example Project",
                    "--platform",
                    platform,
                    "--apply",
                )
                self.assertEqual(install.returncode, 0, install.stdout + install.stderr)
                (target / framework_root / "skills" / "debug" / "SKILL.md").unlink()
                result = self.run_script(
                    PROJECT_VALIDATOR,
                    "--target",
                    str(target),
                    "--platform",
                    platform,
                )
                self.assertEqual(result.returncode, 1)
                self.assertIn("Agent requires matching Skill: debug", result.stdout)

    def test_project_validator_rejects_missing_opencode_agent(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            target = Path(temp_dir)
            install = self.run_script(
                BOOTSTRAP,
                "--target",
                str(target),
                "--project-name",
                "Example Project",
                "--platform",
                "opencode",
                "--apply",
            )
            self.assertEqual(install.returncode, 0, install.stdout + install.stderr)
            (target / ".opencode" / "agents" / "verify.md").unlink()

            result = self.run_script(
                PROJECT_VALIDATOR,
                "--target",
                str(target),
                "--platform",
                "opencode",
            )
            self.assertEqual(result.returncode, 1)
            self.assertIn("OpenCode Agent", result.stdout)

    def test_project_validator_rejects_mismatched_opencode_skill_name(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            target = Path(temp_dir)
            install = self.run_script(
                BOOTSTRAP,
                "--target",
                str(target),
                "--project-name",
                "Example Project",
                "--platform",
                "opencode",
                "--apply",
            )
            self.assertEqual(install.returncode, 0, install.stdout + install.stderr)
            for path in (
                target / "AGENTS.md",
                target / "AI_ENGINEERING_PLAYBOOK.md",
                target / "SQUADS.md",
                target / ".opencode" / "templates" / "SQUAD.md",
            ):
                text = path.read_text(encoding="utf-8")
                path.write_text(re.sub(r"\{\{[^{}]+\}\}", "configured-value", text), encoding="utf-8")
            skill_path = target / ".opencode" / "skills" / "team" / "SKILL.md"
            skill_path.write_text(
                skill_path.read_text(encoding="utf-8").replace("name: team", "name: invalid_skill"),
                encoding="utf-8",
            )

            result = self.run_script(
                PROJECT_VALIDATOR,
                "--target",
                str(target),
                "--platform",
                "opencode",
            )
            self.assertEqual(result.returncode, 1)
            self.assertIn("目录名", result.stdout)

    def test_project_validator_rejects_compatible_local_skill_collision(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            target = Path(temp_dir)
            install = self.run_script(
                BOOTSTRAP,
                "--target",
                str(target),
                "--project-name",
                "Example Project",
                "--platform",
                "opencode",
                "--apply",
            )
            self.assertEqual(install.returncode, 0, install.stdout + install.stderr)
            for path in (
                target / "AGENTS.md",
                target / "AI_ENGINEERING_PLAYBOOK.md",
                target / "SQUADS.md",
                target / ".opencode" / "templates" / "SQUAD.md",
            ):
                text = path.read_text(encoding="utf-8")
                path.write_text(re.sub(r"\{\{[^{}]+\}\}", "configured-value", text), encoding="utf-8")
            collision = target / ".agents" / "skills" / "team"
            collision.mkdir(parents=True)
            (collision / "SKILL.md").write_text("---\nname: team\ndescription: Existing skill\n---\n", encoding="utf-8")

            result = self.run_script(
                PROJECT_VALIDATOR,
                "--target",
                str(target),
                "--platform",
                "opencode",
            )
            self.assertEqual(result.returncode, 1)
            self.assertIn("路径冲突", result.stdout)

    def test_project_validator_rejects_ancestor_compatible_skill_collision(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            (root / ".git").mkdir()
            target = root / "nested" / "project"
            target.mkdir(parents=True)
            install = self.run_script(
                BOOTSTRAP,
                "--target",
                str(target),
                "--project-name",
                "Example Project",
                "--platform",
                "opencode",
                "--apply",
            )
            self.assertEqual(install.returncode, 0, install.stdout + install.stderr)
            for path in (
                target / "AGENTS.md",
                target / "AI_ENGINEERING_PLAYBOOK.md",
                target / "SQUADS.md",
                target / ".opencode" / "templates" / "SQUAD.md",
            ):
                text = path.read_text(encoding="utf-8")
                path.write_text(re.sub(r"\{\{[^{}]+\}\}", "configured-value", text), encoding="utf-8")
            collision = root / ".agents" / "skills" / "team"
            collision.mkdir(parents=True)
            (collision / "SKILL.md").write_text("---\nname: team\ndescription: Existing skill\n---\n", encoding="utf-8")

            result = self.run_script(
                PROJECT_VALIDATOR,
                "--target",
                str(target),
                "--platform",
                "opencode",
            )
            self.assertEqual(result.returncode, 1)
            self.assertIn("路径冲突", result.stdout)

    def test_project_validator_rejects_ancestor_opencode_skill_collision(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            (root / ".git").mkdir()
            target = root / "nested" / "project"
            target.mkdir(parents=True)
            install = self.run_script(
                BOOTSTRAP,
                "--target",
                str(target),
                "--project-name",
                "Example Project",
                "--platform",
                "opencode",
                "--apply",
            )
            self.assertEqual(install.returncode, 0, install.stdout + install.stderr)
            for path in (
                target / "AGENTS.md",
                target / "AI_ENGINEERING_PLAYBOOK.md",
                target / "SQUADS.md",
                target / ".opencode" / "templates" / "SQUAD.md",
            ):
                text = path.read_text(encoding="utf-8")
                path.write_text(re.sub(r"\{\{[^{}]+\}\}", "configured-value", text), encoding="utf-8")
            collision = root / ".opencode" / "skills" / "team"
            collision.mkdir(parents=True)
            (collision / "SKILL.md").write_text("---\nname: team\ndescription: Existing skill\n---\n", encoding="utf-8")

            result = self.run_script(
                PROJECT_VALIDATOR,
                "--target",
                str(target),
                "--platform",
                "opencode",
            )
            self.assertEqual(result.returncode, 1)
            self.assertIn("路径冲突", result.stdout)

    def test_project_validator_rejects_overlong_opencode_skill_name(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            target = Path(temp_dir)
            install = self.run_script(
                BOOTSTRAP,
                "--target",
                str(target),
                "--project-name",
                "Example Project",
                "--platform",
                "opencode",
                "--apply",
            )
            self.assertEqual(install.returncode, 0, install.stdout + install.stderr)
            for path in (
                target / "AGENTS.md",
                target / "AI_ENGINEERING_PLAYBOOK.md",
                target / "SQUADS.md",
                target / ".opencode" / "templates" / "SQUAD.md",
            ):
                text = path.read_text(encoding="utf-8")
                path.write_text(re.sub(r"\{\{[^{}]+\}\}", "configured-value", text), encoding="utf-8")
            overlong_name = "a" * 65
            skill_directory = target / ".opencode" / "skills" / "team"
            skill_path = skill_directory / "SKILL.md"
            skill_directory.rename(skill_directory.with_name(overlong_name))
            skill_path = target / ".opencode" / "skills" / overlong_name / "SKILL.md"
            skill_path.write_text(
                skill_path.read_text(encoding="utf-8").replace("name: team", f"name: {overlong_name}"),
                encoding="utf-8",
            )

            result = self.run_script(
                PROJECT_VALIDATOR,
                "--target",
                str(target),
                "--platform",
                "opencode",
            )
            self.assertEqual(result.returncode, 1)
            self.assertIn("长度", result.stdout)

    def test_project_validator_accepts_quoted_opencode_skill_name(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            target = Path(temp_dir)
            install = self.run_script(
                BOOTSTRAP,
                "--target",
                str(target),
                "--project-name",
                "Example Project",
                "--platform",
                "opencode",
                "--apply",
            )
            self.assertEqual(install.returncode, 0, install.stdout + install.stderr)
            for path in (
                target / "AGENTS.md",
                target / "AI_ENGINEERING_PLAYBOOK.md",
                target / "SQUADS.md",
                target / ".opencode" / "templates" / "SQUAD.md",
            ):
                text = path.read_text(encoding="utf-8")
                path.write_text(re.sub(r"\{\{[^{}]+\}\}", "configured-value", text), encoding="utf-8")
            skill_path = target / ".opencode" / "skills" / "team" / "SKILL.md"
            skill_path.write_text(
                skill_path.read_text(encoding="utf-8").replace("name: team", 'name: "team"'),
                encoding="utf-8",
            )

            result = self.run_script(
                PROJECT_VALIDATOR,
                "--target",
                str(target),
                "--platform",
                "opencode",
            )
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

    def test_project_validator_rejects_overlong_opencode_skill_description(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            target = Path(temp_dir)
            install = self.run_script(
                BOOTSTRAP,
                "--target",
                str(target),
                "--project-name",
                "Example Project",
                "--platform",
                "opencode",
                "--apply",
            )
            self.assertEqual(install.returncode, 0, install.stdout + install.stderr)
            for path in (
                target / "AGENTS.md",
                target / "AI_ENGINEERING_PLAYBOOK.md",
                target / "SQUADS.md",
                target / ".opencode" / "templates" / "SQUAD.md",
            ):
                text = path.read_text(encoding="utf-8")
                path.write_text(re.sub(r"\{\{[^{}]+\}\}", "configured-value", text), encoding="utf-8")
            skill_path = target / ".opencode" / "skills" / "team" / "SKILL.md"
            skill_path.write_text(
                re.sub(r"^description:.*$", f"description: {'x' * 1025}", skill_path.read_text(encoding="utf-8"), count=1, flags=re.MULTILINE),
                encoding="utf-8",
            )

            result = self.run_script(
                PROJECT_VALIDATOR,
                "--target",
                str(target),
                "--platform",
                "opencode",
            )
            self.assertEqual(result.returncode, 1)
            self.assertIn("description 长度", result.stdout)

    def test_project_validator_rejects_unconfigured_templates(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            target = Path(temp_dir)
            install = self.run_script(
                BOOTSTRAP,
                "--target",
                str(target),
                "--project-name",
                "Example Project",
                "--apply",
            )
            self.assertEqual(install.returncode, 0, install.stdout + install.stderr)
            result = self.run_script(PROJECT_VALIDATOR, "--target", str(target))
            self.assertEqual(result.returncode, 1)
            self.assertIn("模板占位符", result.stdout)

    def test_project_validator_accepts_configured_framework(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            target = Path(temp_dir)
            install = self.run_script(
                BOOTSTRAP,
                "--target",
                str(target),
                "--project-name",
                "Example Project",
                "--apply",
            )
            self.assertEqual(install.returncode, 0, install.stdout + install.stderr)
            framework_files = [
                target / "AGENTS.md",
                target / "AI_ENGINEERING_PLAYBOOK.md",
                target / "SQUADS.md",
                target / ".agent" / "AGENT_ENTRY.md",
                target / ".agent" / "templates" / "SQUAD.md",
            ]
            for path in framework_files:
                text = path.read_text(encoding="utf-8")
                text = re.sub(r"\{\{[^{}]+\}\}", "configured-value", text)
                path.write_text(text, encoding="utf-8")
            result = self.run_script(PROJECT_VALIDATOR, "--target", str(target))
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            self.assertIn("项目验证通过", result.stdout)

    def test_force_requires_apply(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            result = self.run_script(
                BOOTSTRAP,
                "--target",
                temp_dir,
                "--project-name",
                "Example Project",
                "--force",
            )
            self.assertEqual(result.returncode, 2)
            self.assertIn("--force is valid only with --apply", result.stderr)

    def test_meta_squad_has_distinct_handoff(self) -> None:
        designer = (ROOT / "skills" / "meta-skill-designer" / "SKILL.md").read_text(encoding="utf-8")
        creator = (ROOT / "skills" / "skill-creator" / "SKILL.md").read_text(encoding="utf-8")
        self.assertIn("Hand the design package to `skill-creator`", designer)
        self.assertIn("If the role, overlap, or squad composition is still unclear", creator)
        self.assertIn("near misses that share vocabulary", creator.lower())

    def test_meta_skills_enforce_design_and_quality_gates(self) -> None:
        designer = (ROOT / "skills" / "meta-skill-designer" / "SKILL.md").read_text(encoding="utf-8")
        creator = (ROOT / "skills" / "skill-creator" / "SKILL.md").read_text(encoding="utf-8")
        for phrase in (
            "Capability Tiers",
            "Universal candidates",
            "Conditional specialists",
            "Exceptional specialists",
            "Creation Gate",
            "Removal test",
        ):
            self.assertIn(phrase, designer)
        for phrase in (
            "Readiness Gate",
            "Refuse To Draft",
            "Structural Quality",
            "Routing Quality",
            "Handoff Quality",
            "Safety Quality",
        ):
            self.assertIn(phrase, creator)

    def test_capability_guidance_is_reference_not_install_manifest(self) -> None:
        tiers = (ROOT / "docs" / "CAPABILITY_TIERS.md").read_text(encoding="utf-8")
        archetypes = (ROOT / "docs" / "PROJECT_ARCHETYPES.md").read_text(encoding="utf-8")
        catalog = (ROOT / "docs" / "SQUAD_CATALOG.md").read_text(encoding="utf-8")
        self.assertIn("Default To Evaluation, Not Installation", tiers)
        self.assertIn("Code review and verification are different", tiers)
        self.assertIn("Risk traits outrank project labels", archetypes)
        self.assertIn("Candidate Formations", catalog)
        self.assertIn("Do not register these squads unchanged", catalog)

    def test_meta_skill_evals_cover_overbuilding_and_contract_readiness(self) -> None:
        payload = (ROOT / "evals" / "skill-design.json").read_text(encoding="utf-8")
        for case_id in (
            "avoid-job-title-team",
            "project-archetype-is-not-enough",
            "universal-capability-not-every-task",
            "creator-rejects-unclear-contract",
            "creator-evaluates-handoff",
        ):
            self.assertIn(f'"id": "{case_id}"', payload)

    def test_squad_template_makes_third_member_optional(self) -> None:
        template = (ROOT / "templates" / "SQUAD.md").read_text(encoding="utf-8")
        self.assertIn("3, optional", template)
        self.assertIn("Delete the third row unless", template)

    def test_all_skills_have_execution_checklist(self) -> None:
        for path in sorted((ROOT / "skills").glob("*/SKILL.md")):
            with self.subTest(skill=path.parent.name):
                text = path.read_text(encoding="utf-8")
                self.assertIn("## Execution Checklist", text,
                              f"{path.parent.name} missing Execution Checklist section")
                self.assertIn("<HARD-GATE>", text,
                              f"{path.parent.name} missing <HARD-GATE> block")

    def test_team_skill_has_pipeline_phases(self) -> None:
        text = (ROOT / "skills" / "team" / "SKILL.md").read_text(encoding="utf-8")
        self.assertIn("## Pipeline Phases", text)
        self.assertIn("<PHASE-GATE", text)
        self.assertIn("INTAKE", text)
        self.assertIn("Phase path", text)

    def test_squads_template_has_phase_routes(self) -> None:
        template = (ROOT / "templates" / "SQUADS.md").read_text(encoding="utf-8")
        self.assertIn("Phase route", template)
        self.assertIn("pipeline phase path per task type", template.lower())

    def test_claude_entry_references_pipeline_phases(self) -> None:
        text = (ROOT / "templates" / "claude" / "CLAUDE.md").read_text(encoding="utf-8")
        self.assertIn("pipeline phase", text.lower())

    def test_opencode_team_references_pipeline_phases(self) -> None:
        text = (ROOT / "templates" / "opencode" / "agents" / "team.md").read_text(encoding="utf-8")
        self.assertIn("pipeline phase", text.lower())

    def test_adapter_docs_have_pipeline_phase_references(self) -> None:
        for doc in ("CLAUDE_CODE_ADAPTER.md", "OPENCODE_ADAPTER.md"):
            with self.subTest(doc=doc):
                text = (ROOT / "docs" / doc).read_text(encoding="utf-8")
                self.assertIn("pipeline phase", text.lower(),
                              f"{doc} missing pipeline phase reference")

    def test_claude_plugin_manifest_is_valid_json(self) -> None:
        import json
        manifest = (ROOT / ".claude-plugin" / "plugin.json").read_text(encoding="utf-8")
        payload = json.loads(manifest)
        self.assertEqual(payload["name"], "intent-driven-coding")
        self.assertIn("version", payload)

    def test_marketplace_manifest_is_valid_json(self) -> None:
        import json
        manifest = (ROOT / ".claude-plugin" / "marketplace.json").read_text(encoding="utf-8")
        payload = json.loads(manifest)
        self.assertIn("plugins", payload)
        self.assertGreater(len(payload["plugins"]), 0)
        self.assertEqual(payload["plugins"][0]["name"], "intent-driven-coding")

    def test_hooks_json_has_session_start_event(self) -> None:
        import json
        hooks = (ROOT / "hooks" / "hooks.json").read_text(encoding="utf-8")
        payload = json.loads(hooks)
        self.assertIn("hooks", payload)
        self.assertIn("SessionStart", payload["hooks"])
        session_start = payload["hooks"]["SessionStart"][0]
        self.assertIn("startup|clear|compact", session_start["matcher"])
        self.assertEqual(session_start["hooks"][0]["type"], "command")

    def test_session_start_hook_references_team_skill(self) -> None:
        script = (ROOT / "hooks" / "session-start").read_text(encoding="utf-8")
        self.assertIn("skills/team/SKILL.md", script)
        self.assertIn("INTENT-DRIVEN-CODING-ACTIVE", script)
        self.assertIn("CLAUDE_PLUGIN_ROOT", script)

    def test_run_hook_cmd_is_polyglot(self) -> None:
        script = (ROOT / "hooks" / "run-hook.cmd").read_text(encoding="utf-8")
        # Must work as both .cmd batch and bash
        self.assertIn("BATCH_EOF", script)
        self.assertIn("#!/usr/bin/env bash", script)

    def test_opencode_plugin_registers_skills_dir(self) -> None:
        script = (ROOT / ".opencode" / "plugins" / "intent-driven-coding.js").read_text(encoding="utf-8")
        self.assertIn("config.skills.paths", script)
        self.assertIn("INTENT-DRIVEN-CODING-ACTIVE", script)
        self.assertIn("experimental", script)

    def test_plugin_manifest_and_marketplace_versions_match(self) -> None:
        import json
        manifest = json.loads((ROOT / ".claude-plugin" / "plugin.json").read_text(encoding="utf-8"))
        marketplace = json.loads((ROOT / ".claude-plugin" / "marketplace.json").read_text(encoding="utf-8"))
        self.assertEqual(manifest["version"], marketplace["plugins"][0]["version"])
        hook = (ROOT / "hooks" / "session-start").read_text(encoding="utf-8")
        self.assertIn(manifest["version"], hook)


if __name__ == "__main__":
    unittest.main()
