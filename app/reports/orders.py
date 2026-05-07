from app.reports.base import BaseReport
from app.configs.settings import settings
from typing import Any


class OrdersInfoReport(BaseReport):
    """
    Класс для отчета Детальная информация по заказам.
    Атрибуты хранят эндпоинт, тип отчета, требуются ли business_id и/или campaign_id
    согласно документации.
    """
    endpoint = f'campaigns/{settings.campaign_id}/stats/orders'
    report_type = 'orders_info'
    requires_business_id = False
    requires_campaign_id = False

    def __init__(self, update_from: str, update_to: str):
        """
        Args:
            update_from: Начальная дата периода изменений (ГГГГ-ММ-ДД)
            update_to: Конечная дата периода изменений (ГГГГ-ММ-ДД)
        """
        self.updateFrom = update_from
        self.updateTo = update_to


    def build_request(self) -> dict[str, Any]:
        """
        Формирует данные для HTTP-запроса генерации отчета:
        Returns:
            dict: Параметры запроса в формате {"params": {...}, "json": {...}}
        """
        return {
                "params": {"limit": 200},
                "json":{
                    "updateFrom": self.updateFrom,
                    "updateTo": self.updateTo
                }
            }

