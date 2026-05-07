from app.reports.base import BaseReport
from app.configs.settings import settings
from typing import Any


class DimOffersReport(BaseReport):
    """
    Класс для отчета по товарам.
    Атрибуты хранят эндпоинт, тип отчета, требуются ли business_id и/или campaign_id
    согласно документации.
    """
    endpoint = f'businesses/{settings.business_id}/offer-mappings'
    report_type = 'dim_offers'
    requires_business_id = False
    requires_campaign_id = False

    def __init__(self, offers_on_page: int = None):
        """
        Args:
            offers_on_page: Количество товаров на странице. Лимит указан в документации.
        """
        self.offers_on_page = offers_on_page


    def build_request(self) -> dict[str, Any]:
        """
        Формирует данные для HTTP-запроса генерации отчета:
        Returns:
            dict: Параметры запроса в формате {"params": {...}, "json": {...}}
        """
        if not self.offers_on_page:
            return {
                "params": {},
                "json":{}
            }
        return {
            "params": {"limit": self.offers_on_page},
            "json": {}
        }
