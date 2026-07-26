import unittest

from fixture_app import render_report, save_report


class ReportTests(unittest.TestCase):
    def test_saved_report_renders_its_body(self) -> None:
        save_report("quarterly", "Revenue increased by 12 percent.")
        self.assertEqual(render_report("quarterly"), "Revenue increased by 12 percent.")
