from app.reports.base import BaseReport
from typing import Any


class StocksReport(BaseReport):
    """
    Класс для отчета по остаткам.
    Атрибуты хранят эндпоинт, тип отчета, требуются ли business_id и/или campaign_id
    согласно документации.
    """
    endpoint = 'reports/stocks-on-warehouses/generate'
    report_type = 'stocks'
    requires_business_id = False
    requires_campaign_id = True

    def __init__(self, report_date: str):
        """
        Args:
            report_date(str): Дата начала периода на которую хотим получить отчет
        """
        self.report_date = report_date

    def build_request(self, format_: str = "CSV") -> dict:
        """
        Формирует данные для HTTP-запроса генерации отчета:
        Args:
            format_: Формат отчета (CSV, JSON, FILE). Default: CSV
        Returns:
            dict: Параметры запроса в формате {"params": {...}, "json": {...}}
        """
        return {
            "params": {"format": format_},
            "json": {"reportDate": self.report_date}
        }