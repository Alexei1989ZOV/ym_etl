from app.reports.base import BaseReport
from typing import Any


class GoodsMovementReport(BaseReport):
    endpoint = 'reports/goods-movement/generate'
    report_type = 'goods_movement'
    requires_business_id = False
    requires_campaign_id = True

    def __init__(self, date_from: str, date_to: str):
        self.date_from = date_from
        self.date_to = date_to

    def build_request(self, format_: str = "CSV") -> dict[str, Any]:
        return {
            "params": {"format": format_},
            "json": {
                "dateFrom": self.date_from,
                "dateTo": self.date_to,
            }
        }
