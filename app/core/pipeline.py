from app.api.report_client import ReportAPIClient
from app.reports.base import BaseReport
import time


class ReportPipeline:
    def __init__(
        self,
        api_client: ReportAPIClient,
        report: BaseReport,
        poll_interval: int = 10,
        timeout: int = 600
    ):
        self.api_client = api_client
        self.report = report
        self.poll_interval = poll_interval
        self.timeout = timeout

    def run(self, **report_params) -> bytes:
        """
        Запуск полного цикла генерации и загрузки отчета.
        """
        request_data = self.report.build_request(**report_params)

        response = self.api_client.generate_report(
            report = self.report,
            request_data = request_data
        )

        report_id = self.api_client.get_report_id(response)

        download_url = self._wait_report_generation(report_id)

        return self.api_client.download_report(download_url)

    def _wait_report_generation(self, report_id: str) -> str:
        start_time = time.time()
        while True:
            status_response = self.api_client.check_generation_status(report_id)
            result = status_response.get("result", {})
            status = result.get("status")
            if status == "DONE":
                if result.get("file"):
                    return result.get("file")
                else:
                    raise IOError("Отчет сгенерирован, но ссылка на файл отсутствует")
            elif status == "FAILED":
                raise IOError("Ошибка генерации отчета")
            if time.time() - start_time > self.timeout:
                raise TimeoutError(f"Отчет не сгенерирован за {self.timeout} секунд")
            time.sleep(self.poll_interval)



