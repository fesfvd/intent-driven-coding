import subprocess
import sys
import tomllib
import json
import re
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


class ProgressiveDistributionTests(unittest.TestCase):
    def test_public_guidance_uses_event_first_progressive_contract(self) -> None:
        surfaces = (
            "README.md",
            "AI_START_HERE.md",
            "QUICKSTART.md",
            "docs/CLI.md",
            "docs/INSTALLATION.md",
            "docs/MINIMAL.md",
            "docs/TEAM_PLAYBOOK.md",
            "docs/CLAUDE_CODE_ADAPTER.md",
            "docs/OPENCODE_ADAPTER.md",
            "templates/IDC.md",
            "templates/AI_ENGINEERING_PLAYBOOK.md",
            "templates/AGENT_ENTRY.md",
            "templates/SQUADS.md",
            "templates/claude/CLAUDE.md",
            "templates/opencode/agents/team.md",
        )

        combined = "\n".join((ROOT / relative).read_text(encoding="utf-8") for relative in surfaces)
        self.assertNotIn("IDC-<PROJECT>-<SCENARIO>", combined)
        self.assertNotIn("IDC-项目-场景", combined)
        for phrase in ("events.jsonl", "dynamic obligations", "captured", "IDC-<PROJECT>-<YYYYMMDD>-<NNN>"):
            self.assertIn(phrase, combined)

    def test_progressive_guide_lists_state_changing_commands(self) -> None:
        guide = (ROOT / "docs" / "PROGRESSIVE_TASKS.md").read_text(encoding="utf-8")

        for command in ("idc classify", "idc condition", "idc resolve-decision"):
            self.assertIn(command, guide)

    def test_progressive_guidance_documents_temporary_capture_and_confirmation(self) -> None:
        guide = (ROOT / "docs" / "PROGRESSIVE_TASKS.md").read_text(encoding="utf-8")
        self.assertIn("temporary", guide.lower())
        self.assertIn("confirmation_ref", guide)

    def test_codex_scaffold_uses_agents_skills_and_leaves_runtime_init_to_cli(self) -> None:
        bootstrap = ROOT / "scripts" / "bootstrap.py"
        validator = ROOT / "scripts" / "validate_project.py"
        with tempfile.TemporaryDirectory() as temp_dir:
            target = Path(temp_dir)
            install = subprocess.run(
                [
                    sys.executable,
                    str(bootstrap),
                    "--target",
                    str(target),
                    "--project-name",
                    "Codex Pilot",
                    "--platform",
                    "codex",
                    "--apply",
                ],
                cwd=ROOT,
                capture_output=True,
                text=True,
                check=False,
            )

            self.assertEqual(install.returncode, 0, install.stdout + install.stderr)
            self.assertTrue((target / ".agents" / "skills" / "team" / "SKILL.md").is_file())
            self.assertFalse((target / ".idc" / "config.json").exists())

            for path in (
                target / "AGENTS.md",
                target / "AI_ENGINEERING_PLAYBOOK.md",
                target / "SQUADS.md",
                target / ".agents" / "templates" / "SQUAD.md",
            ):
                path.write_text(
                    re.sub(r"\{\{[^{}]+\}\}", "configured-value", path.read_text(encoding="utf-8")),
                    encoding="utf-8",
                )
            validation = subprocess.run(
                [sys.executable, str(validator), "--target", str(target), "--platform", "codex"],
                cwd=ROOT,
                capture_output=True,
                text=True,
                check=False,
            )
            self.assertEqual(validation.returncode, 0, validation.stdout + validation.stderr)
    def test_pyproject_exposes_the_host_neutral_idc_command(self) -> None:
        metadata = tomllib.loads((ROOT / "pyproject.toml").read_text(encoding="utf-8"))

        self.assertEqual(metadata["project"]["name"], "intent-driven-coding")
        self.assertEqual(metadata["project"]["scripts"]["idc"], "scripts.idc:main")
        self.assertIn("jsonschema", metadata["project"]["dependencies"][0])

    def test_module_entrypoint_exposes_existing_and_progressive_commands(self) -> None:
        result = subprocess.run(
            [sys.executable, "-m", "idc_core", "--help"],
            cwd=ROOT,
            capture_output=True,
            text=True,
            check=False,
        )

        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("status", result.stdout)
        self.assertIn("start", result.stdout)
        self.assertIn("doctor", result.stdout)

    def test_packaged_and_public_event_schemas_are_identical(self) -> None:
        public = (ROOT / "schemas" / "idc-task-event-v1.schema.json").read_bytes()
        packaged = (ROOT / "idc_core" / "resources" / "idc-task-event-v1.schema.json").read_bytes()

        self.assertEqual(packaged, public)

    def test_primary_guidance_uses_progressive_records_and_mutable_labels(self) -> None:
        progressive = (ROOT / "docs" / "PROGRESSIVE_TASKS.md").read_text(encoding="utf-8")
        scenarios = (ROOT / "docs" / "TASK_SCENARIOS.md").read_text(encoding="utf-8")
        team = (ROOT / "skills" / "team" / "SKILL.md").read_text(encoding="utf-8")
        template = (ROOT / "templates" / "IDC_TASK.md").read_text(encoding="utf-8")

        for text in (progressive, scenarios, team):
            self.assertIn("captured", text)
            self.assertIn("dynamic obligations", text.lower())
        self.assertIn("mutable label", scenarios.lower())
        self.assertIn("AUTO-GENERATED", template)
        self.assertIn("events.jsonl", template)

    def test_all_distribution_surfaces_use_the_package_version(self) -> None:
        metadata = tomllib.loads((ROOT / "pyproject.toml").read_text(encoding="utf-8"))
        version = metadata["project"]["version"]
        plugin = json.loads((ROOT / ".claude-plugin" / "plugin.json").read_text(encoding="utf-8"))
        marketplace = json.loads(
            (ROOT / ".claude-plugin" / "marketplace.json").read_text(encoding="utf-8")
        )
        hook = (ROOT / "hooks" / "session-start").read_text(encoding="utf-8")
        opencode = (ROOT / ".opencode" / "plugins" / "intent-driven-coding.js").read_text(
            encoding="utf-8"
        )

        self.assertEqual(plugin["version"], version)
        self.assertEqual(marketplace["plugins"][0]["version"], version)
        self.assertRegex(hook, rf'VERSION="{re.escape(version)}"')
        self.assertRegex(opencode, rf'VERSION = "{re.escape(version)}"')

    def test_repository_validator_registers_progressive_runtime_assets(self) -> None:
        validator = (ROOT / "scripts" / "validate_repository.py").read_text(encoding="utf-8")
        for relative in (
            "pyproject.toml",
            "docs/PROGRESSIVE_TASKS.md",
            "schemas/idc-task-event-v1.schema.json",
            "idc_core/events.py",
            "idc_core/workflow.py",
            "idc_core/resources/idc-task-event-v1.schema.json",
        ):
            self.assertIn(f'"{relative}"', validator)


if __name__ == "__main__":
    unittest.main()
