from app.reports.base import BaseReport
from typing import Any


class PricesReport(BaseReport):
    """
    Класс для отчета по ценам.
    Атрибуты хранят эндпоинт, тип отчета, требуются ли business_id и/или campaign_id
    согласно документации.
    """
    endpoint = 'reports/goods-prices/generate'
    report_type = 'prices'
    requires_business_id = True
    requires_campaign_id = False

    def build_request(self, format_: str = "CSV") -> dict[str, Any]:
        """
        Формирует данные для HTTP-запроса генерации отчета:
        Returns:
            dict: Параметры запроса в формате {"params": {...}, "json": {...}}
        """
        return {
            "params": {"format": format_},
            "json": {}
        }
