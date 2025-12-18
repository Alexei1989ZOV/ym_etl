from app.reports.base import BaseReport
from typing import Any


class SalesReport(BaseReport):
    endpoint = "reports/shows-sales/generate"
    report_type = "sales"

    requires_business_id = True
    requires_campaign_id = False

    def build_request(self, date_from: str, date_to: str, format_: str = "CSV", grouping: str = "OFFERS") -> dict[str, Any]:
        return {
            "params": {"format": format_},
            "json": {
                "dateFrom": date_from,
                "dateTo": date_to,
                "grouping": grouping
            }
        }
