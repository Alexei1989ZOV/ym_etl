import time
from app.api.report_client import ReportAPIClient
from app.reports.base import BaseReport

class ReportPipeline:
    def __init__(self, api_client: ReportAPIClient, poll_interval: int = 10, timeout: int = 600):
        self.api_client = api_client
        self.poll_interval = poll_interval
        self.timeout = timeout

    def run(self, report: BaseReport) -> str:
        """Запуск генерации отчета и ожидание готовности"""
        request_data = report.build_request()
        response = self.api_client.generate_report(report, request_data)
        report_id = self.api_client.get_report_id(response)
        download_url = self._wait_report_generation(report_id)
        return download_url

    def _wait_report_generation(self, report_id: str) -> str:
        import time
        start_time = time.time()
        while True:
            status_response = self.api_client.check_generation_status(report_id)
            result = status_response.get("result", {})
            status = result.get("status")
            if status == "DONE":
                file_url = result.get("file")
                if not file_url:
                    raise ValueError("Отчет сгенерирован, но ссылка на файл отсутствует")
                return file_url
            elif status == "FAILED":
                raise ValueError("Ошибка генерации отчета")
            if time.time() - start_time > self.timeout:
                raise TimeoutError("Отчет не сгенерирован за отведенное время")
            time.sleep(self.poll_interval)