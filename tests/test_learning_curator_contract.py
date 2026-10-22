from __future__ import annotations

import unittest
from pathlib import Path


SKILL = Path(__file__).resolve().parents[1] / "skills" / "learning-curator" / "SKILL.md"


class LearningCuratorContractTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.text = SKILL.read_text(encoding="utf-8")

    def candidate_example(self) -> str:
        self.assertIn("## Candidate Example", self.text)
        return self.text.split("## Candidate Example", 1)[1].split("\n## ", 1)[0]

    def test_candidate_example_separates_rule_mechanism_from_open_question(self) -> None:
        example = self.candidate_example()
        self.assertRegex(
            example,
            r"Rule: (?:Before|When|Keep|Update|Check|Verify)\b[^\n]+\bbecause\b[^\n]+",
        )
        self.assertRegex(example, r"Open question: [^\n]+\?[^\n]*")
        self.assertRegex(example, r"(?i)unresolved[^\n]*not (?:a )?validated practice")
        self.assertNotRegex(example, r"(?i)rule:.*(?:yesterday|last week|in task|we tried)")

    def test_merge_and_retirement_require_traceable_provenance(self) -> None:
        self.assertIn("absorbed-into", self.text)
        self.assertRegex(
            self.text,
            r"(?is)(?:retir\w+|remov\w+)[^\n]*"
            r"(?:absorbed-into[^\n]*falsif\w+|falsif\w+[^\n]*absorbed-into)",
        )
        example = self.candidate_example()
        self.assertRegex(example, r"(?m)^Merge provenance: absorbed-into:? \S+;")

    def test_guidance_order_and_human_gate_remain_explicit(self) -> None:
        self.assertRegex(
            self.text,
            r"(?s)strengthen (?:the )?(?:current|existing) rule.*?merge (?:into )?(?:an? )?umbrella"
            r".*?add (?:a )?support reference.*?propose (?:a )?class-level new Skill",
        )
        self.assertRegex(self.text, r"(?i)human disposition[^\n]*before (?:any )?change")
        self.assertIn("Candidate | Evidence | Destination | Duplicate/Supersedes | Keep test | Human disposition", self.text)
        self.assertIn("removal test", self.text)
        self.assertRegex(self.text, r"(?i)(?:omit|without) incident narration")


if __name__ == "__main__":
    unittest.main()
