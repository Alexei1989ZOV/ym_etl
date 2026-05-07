from app.reports.base import BaseReport
from typing import Any


class GoodsMovementReport(BaseReport):
    """
    Класс отчета по движению товаров на складах.
    Атрибуты хранят эндпоинт, тип отчета, требуются ли business_id и/или campaign_id
    согласно документации.
    """
    endpoint = 'reports/goods-movement/generate'
    report_type = 'goods_movement'
    requires_business_id = False
    requires_campaign_id = True

    def __init__(self, date_from: str, date_to: str):
        """
        Args:
            date_from(str): Дата начала периода за который хотим получить отчет.
            date_to(str): Дата конца периода за который хотим получить отчет.
        """
        self.date_from = date_from
        self.date_to = date_to

    def build_request(self, format_: str = "CSV") -> dict[str, Any]:
        """
        Формирует данные для HTTP-запроса генерации отчета:
        Args:
            format_: Формат отчета (CSV, JSON, FILE). Default: CSV
        Returns:
            dict: Параметры запроса в формате {"params": {...}, "json": {...}}
        """
        return {
            "params": {"format": format_},
            "json": {
                "dateFrom": self.date_from,
                "dateTo": self.date_to,
            }
        }
