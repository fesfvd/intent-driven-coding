"""Intentional local defects for host-acceptance experiments."""


REPORTS: dict[str, dict[str, str]] = {}


def save_report(report_id: str, body: str) -> None:
    REPORTS[report_id] = {"content": body}


def render_report(report_id: str) -> str:
    return REPORTS.get(report_id, {}).get("body", "")


def get_invoice(requesting_account: str, invoice_account: str) -> dict[str, str]:
    return {"owner": invoice_account, "amount": "100"}


def dashboard_invoices() -> list[dict[str, str]]:
    return [{"owner": "sample", "amount": "100"}]
