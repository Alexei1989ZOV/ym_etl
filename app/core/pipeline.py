import time
from app.api.report_client import ReportAPIClient
from app.reports.base import BaseReport
from app.core.rate_limiter import RateLimiter
from app.configs.logger_settings import get_logger

logger = get_logger(__name__)

class ReportPipeline:
    """
    Пайплайн для асинхронных отчетов с учетом лимитов и ожиданием готовности отчетов.
    """
    def __init__(self, api_client: ReportAPIClient, poll_interval: int = 20, timeout: int = 1200):
        self.api_client = api_client
        self.poll_interval = poll_interval
        self.timeout = timeout

        # Создаем лимитеры для разных отчетов
        self.limiters = {
            "sales": RateLimiter(max_requests=1, period_seconds=600),  # 1 запрос в 10 минут
            "stocks": RateLimiter(max_requests=1, period_seconds=120),  # 1 запрос в 2 минуты
            "goods_movement": RateLimiter(max_requests=1, period_seconds=120),  # 1 запрос в 2 минуты
            "prices": RateLimiter(max_requests=1, period_seconds=120),  # # 1 запрос в 2 минуты
            "orders_info" : RateLimiter(max_requests=10000) # 10_000 в час
        }

    def run(self, report: BaseReport) -> str:
        """Запуск генерации асинхронного отчета и ожидание готовности"""
        # Ждем, если нужно (автоматически уснет, если лимит исчерпан)
        if report.report_type in self.limiters:
            self.limiters[report.report_type].wait_if_needed()
        request_data = report.build_request()
        logger.debug(f"Запрос данных для отчета {report.report_type}: {request_data}")
        response = self.api_client.generate_report(report, request_data)
        report_id = self.api_client.get_report_id(response)
        logger.debug(f"Получен ID отчета {report.report_type}: {report_id}")
        download_url = self._wait_report_generation(report_id)
        return download_url

    def _wait_report_generation(self, report_id: str) -> str:
        """
        Ожидает завершения генерации отчета.
        Args:
            report_id: Идентификатор отчета
        Returns:
            str: Ссылка для скачивания
        Raises:
            TimeoutError: Если отчет не сгенерирован за timeout секунд
            ValueError: При ошибке генерации или отсутствии ссылки
        """
        start_time = time.time()
        while True:
            status_response = self.api_client.check_generation_status(report_id)
            result = status_response.get("result", {})
            status = result.get("status")
            logger.debug(f"Статус генерации отчета {report_id}: {status}")
            if status == "DONE":
                file_url = result.get("file")
                if not file_url:
                    raise ValueError("Отчет сгенерирован, но ссылка на файл отсутствует")
                logger.info(f"Отчет {report_id} сгенерирован, ссылка получена")
                return file_url
            elif status == "FAILED":
                raise ValueError("Ошибка генерации отчета")
            if time.time() - start_time > self.timeout:
                raise TimeoutError("Отчет не сгенерирован за отведенное время")
            elapsed = int(time.time() - start_time)
            if elapsed % 300 == 0 and elapsed > 0:
                logger.info(f"Ожидание генерации отчета {report_id}, прошло {elapsed} сек")
            time.sleep(self.poll_interval)