import unittest

from fixture_app import get_invoice


class InvoiceTests(unittest.TestCase):
    def test_cross_account_invoice_access_is_rejected(self) -> None:
        with self.assertRaises(PermissionError):
            get_invoice("account-a", "account-b")
