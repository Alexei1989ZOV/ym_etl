from app.reports.base import BaseReport
from typing import Any

class SalesReport(BaseReport):
    endpoint = "reports/shows-sales/generate"
    report_type = "sales"
    requires_business_id = True
    requires_campaign_id = False

    def __init__(self, date_from: str, date_to: str):
        self.date_from = date_from
        self.date_to = date_to

    def build_request(self, format_: str = "CSV", grouping: str = "OFFERS") -> dict[str, Any]:
        return {
            "params": {"format": format_},
            "json": {
                "dateFrom": self.date_from,
                "dateTo": self.date_to,
                "grouping": grouping
            }
        }