import unittest

from fixture_app import dashboard_invoices


class ApprovalTests(unittest.TestCase):
    def test_dashboard_exposes_pending_approval_state(self) -> None:
        invoice = dashboard_invoices()[0]
        self.assertEqual(invoice["approval_state"], "pending")
