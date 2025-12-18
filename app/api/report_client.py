from app.api.client import BaseAPIClient
from app.reports.base import BaseReport


class ReportAPIClient(BaseAPIClient):
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
        with self.session.get(download_url, stream=True) as response:
            response.raise_for_status()
            return response.content

    def generate_report(self, report: BaseReport, request_data: dict) -> dict:
        payload = request_data.get("json", {}).copy()

        if report.requires_business_id:
            payload["businessId"] = self.business_id

        if report.requires_campaign_id:
            payload["campaignId"] = self.campaign_id

        return self.make_request(
            "POST",
            report.endpoint,
            params=request_data.get("params"),
            json=payload
        )