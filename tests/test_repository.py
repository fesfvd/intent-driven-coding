from __future__ import annotations

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

    def test_ai_entry_prioritizes_adaptation_over_copying(self) -> None:
        entry = (ROOT / "AI_START_HERE.md").read_text(encoding="utf-8")
        self.assertIn("Do not copy this repository unchanged", entry)
        self.assertIn("Understand The Target", entry)
        self.assertIn("Design Before Copying", entry)
        self.assertIn("Optional Scaffolding", entry)

    def test_platform_guide_covers_mainstream_tools(self) -> None:
        guide = (ROOT / "docs" / "PLATFORM_ADAPTERS.md").read_text(encoding="utf-8")
        for platform in ("Claude Code", "OpenCode", "Codex", "Cursor", "GitHub Copilot"):
            self.assertIn(platform, guide)
        self.assertIn("does not claim automatic compatibility", guide)

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

    def test_squad_template_makes_third_member_optional(self) -> None:
        template = (ROOT / "templates" / "SQUAD.md").read_text(encoding="utf-8")
        self.assertIn("3, optional", template)
        self.assertIn("Delete the third row unless", template)


if __name__ == "__main__":
    unittest.main()
