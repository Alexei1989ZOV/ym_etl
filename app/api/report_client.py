from app.api.client import BaseAPIClient
from app.reports.base import BaseReport
from datetime import datetime
import time
from app.configs.logger_settings import get_logger

logger = get_logger(__name__)

class ReportAPIClient(BaseAPIClient):
    """
    Клиент API Яндекс.Маркета для работы с отчетами.

    - Асинхронные отчеты: generate_report() -> check_generation_status() -> download_report()
    - Синхронные API: get_offer_mappings() (автоматическая пагинация)
    - Поддерживает лимиты: RateLimiter в ReportPipeline

    Атрибуты:
        api_key, business_id, campaign_id — из settings
        session — сессия requests с API-ключом
    """
    def __init__(self, api_key: str, business_id: int, campaign_id: int):
        super().__init__()  # инициализация BaseAPIClient
        self.api_key = api_key
        self.business_id = business_id
        self.campaign_id = campaign_id

    def get_report_id(self, response: dict) -> str:
        """Извлекает report_id из ответа API"""
        result = response.get("result")
        if not result:
            raise ValueError("В ответе отсутствует result")

        report_id = result.get("reportId")
        if not report_id:
            raise ValueError("reportId отсутствует")

        return report_id

    def check_generation_status(self, report_id: str) -> dict:
        """Проверяет статус генерации отчета"""
        endpoint = f"reports/info/{report_id}"
        logger.debug(f"Проверка статуса отчета {report_id}")
        return self.make_request("GET", endpoint)

    def get_download_url(self, api_response: dict) -> str:
        """Извлекает ссылку на скачивание отчета"""
        result = api_response.get("result")
        if not result:
            raise ValueError("В ответе отсутствует result")

        download_url = result.get("file")
        if not download_url:
            raise ValueError("В ответе отсутствует file")

        return download_url

    def download_report(self, download_url: str) -> bytes:
        """Скачивает отчет и возвращает его как bytes"""
        logger.info(f"Скачивание отчета...")
        with self.session.get(download_url, stream=True) as response:
            response.raise_for_status()
            logger.info(f"Отчет скачан, размер: {len(response.content)} байт")
            return response.content

    def generate_report(self, report: BaseReport, request_data: dict) -> dict:
        logger.info(f"Генерация отчета: {report.report_type}")
        payload = request_data.get("json", {}).copy()

        if report.requires_business_id:
            payload["businessId"] = self.business_id

        if report.requires_campaign_id:
            payload["campaignId"] = self.campaign_id

        logger.info(f"Отчет {report.report_type} отправлен на генерацию")
        return self.make_request(
            "POST",
            report.endpoint,
            params=request_data.get("params"),
            json=payload
        )

    def get_offer_mappings(self, report: BaseReport):
        logger.debug("Загрузка справочника товаров (offer mappings)")
        all_offers = []
        next_page_token = None
        params = {"limit": 100}

        while True:
            if next_page_token:
                params["pageToken"] = next_page_token

            request_data = report.build_request()
            response = self.make_request(
                "POST",
                report.endpoint,
                params=params,
                json=request_data.get("json", {})
            )
            result = response.get("result", {})
            offers_on_page = result.get("offerMappings", [])
            all_offers.extend(offers_on_page)

            paging = result.get("paging", {})
            next_page_token = paging.get("nextPageToken")
            if not next_page_token:
                break
        logger.info(f"Загружено {len(all_offers)} товаров")
        return {"result": {"offerMappings": all_offers}}

    def get_orders_info(self, report: BaseReport):
        """
        Получает все заказы за период с автоматической пагинацией.

        Args:
            report: OrdersInfoReport с updateFrom и updateTo

        Returns:
            dict: {"result": {"orders": [...]}}
        """
        all_orders = []
        next_page_token = None
        params = {"limit": 200}
        page_number = 0
        while True:
            page_number += 1
            if next_page_token:
                params["pageToken"] = next_page_token

            request_data = report.build_request()
            response = self.make_request(
                "POST",
                report.endpoint,
                params=params,
                json=request_data.get("json", {})
            )
            result = response.get("result", {})
            orders_on_page = result.get("orders", [])
            all_orders.extend(orders_on_page)
            logger.info(f"Страница {page_number} загружено {len(all_orders)} заказов")
            paging = result.get("paging", {})
            next_page_token = paging.get("nextPageToken")
            if not next_page_token:
                logger.info(f"Загрузка завершена. Загружено {len(all_orders)} заказов")
                break
            time.sleep(0.5)
        return {"result": {"orders": all_orders}}