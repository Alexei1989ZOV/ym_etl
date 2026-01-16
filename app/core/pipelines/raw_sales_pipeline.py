from datetime import date
from sqlalchemy.orm import Session
from app.reports.sales import SalesReport
from app.core.pipeline import ReportPipeline
from app.processing.file_manager import FileManager
from app.raw_transformers.sales_transformer import SalesCSVTransformer
from app.storage.repositories.raw_sales_repository import RawSalesRepository

class RawSalesETLPipeline:
    def __init__(self, session: Session, file_manager: FileManager, report_pipeline: ReportPipeline):
        self.session = session
        self.file_manager = file_manager
        self.report_pipeline = report_pipeline
        self.repository = RawSalesRepository(session)

    def run(self, report_date: date) -> None:
        # 1. Создаём объект отчёта
        report = SalesReport(date_from=str(report_date), date_to=str(report_date))

        # 2. Генерация и получение ссылки на скачивание
        download_url = self.report_pipeline.run(report)

        # 3. Скачиваем ZIP
        raw_bytes = self.report_pipeline.api_client.download_report(download_url)

        # 4. Сохраняем raw ZIP
        raw_zip_path = self.file_manager.save_raw(report, report_date, raw_bytes)

        # 5. Распаковываем CSV
        csv_files = self.file_manager.extract_archive(report, raw_zip_path)

        for csv_path in csv_files:
            transformer = SalesCSVTransformer(csv_path)
            records = transformer.transform()

            if not records:
                continue

            # Берём период из первой строки
            first = records[0]

            # 6. Удаляем старые данные
            self.repository.delete_by_period(
                year=first.year,
                month=first.month,
                day=first.day
            )

            # 7. Вставляем новые данные
            self.repository.bulk_insert(records)

            # 8. Логируем
            count = self.repository.count_by_period(
                year=first.year,
                month=first.month,
                day=first.day
            )
            print(f"[RAW SALES] Загружено {count} строк за {first.day}.{first.month}.{first.year}")