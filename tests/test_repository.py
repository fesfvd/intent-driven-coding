from __future__ import annotations

import os
import json
import subprocess
import sys
import tempfile
import unittest
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
BOOTSTRAP = ROOT / "scripts" / "bootstrap.py"
VALIDATOR = ROOT / "scripts" / "validate_repository.py"
AUDITOR = ROOT / "scripts" / "audit_skills.py"
PROJECT_VALIDATOR = ROOT / "scripts" / "validate_project.py"
CONTRACT_VALIDATOR = ROOT / "scripts" / "validate_contracts.py"
CONTRACT_EVALUATOR = ROOT / "scripts" / "evaluate_contracts.py"


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


if __name__ == "__main__":
    unittest.main()
