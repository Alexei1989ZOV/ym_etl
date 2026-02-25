from app.reports.base import BaseReport
from typing import Any


class StocksReport(BaseReport):
    endpoint = 'reports/stocks-on-warehouses/generate'
    report_type = 'stocks'
    requires_business_id = False
    requires_campaign_id = True

    def __init__(self, report_date: str):
        self.report_date = report_date

    def build_request(self, format_: str = "CSV") -> dict:
        return {
            "params": {"format": format_},
            "json": {"reportDate": self.report_date}
        }