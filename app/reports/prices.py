from app.reports.base import BaseReport
from typing import Any


class PricesReport(BaseReport):
    endpoint = 'reports/goods-prices/generate'
    report_type = 'prices'
    requires_business_id = True
    requires_campaign_id = False

    def build_request(self, format_: str = "CSV") -> dict[str, Any]:
        return {
            "params": {"format": format_},
            "json": {}
        }
