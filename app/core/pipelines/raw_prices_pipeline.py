from datetime import date
from sqlalchemy.orm import Session
from app.reports.prices import PricesReport
from app.core.pipeline import ReportPipeline
from app.processing.file_manager import FileManager
from app.raw_transformers.prices_transformer import PricesCSVTransformer
from app.storage.repositories.raw_prices_repository import RawPricesRepository


class PricesETLPipeline:
    def __init__(self, session: Session, file_manager: FileManager, report_pipeline: ReportPipeline, cleanup: bool = True):
        self.session = session
        self.file_manager = file_manager
        self.report_pipeline = report_pipeline
        self.repository = RawPricesRepository(session)
        self.cleanup = cleanup

    def run(self, report_date: date) -> None:
        # 1. Создаём объект отчёта
        report = PricesReport()

        # 2. Генерация и получение ссылки на скачивание
        download_url = self.report_pipeline.run(report)

        # 3. Скачиваем ZIP
        raw_bytes = self.report_pipeline.api_client.download_report(download_url)

        # 4. Сохраняем raw ZIP
        raw_zip_path = self.file_manager.save_raw(report, report_date, raw_bytes)

        # 5. Распаковываем CSV
        csv_files = self.file_manager.extract_archive(report, raw_zip_path)
        all_records = []

        for csv_path in csv_files:
            transformer = PricesCSVTransformer(csv_path)
            records = transformer.transform()
            all_records.extend(records)

        if not all_records:
            print(f"[RAW PRICES] Нет данных за {report_date}")  # для лога
            return

        # 6. Удаляем старые данные
        actual_data_date = all_records[0].day  # <-- берем из первой записи
        self.repository.delete_by_date(actual_data_date)

        # 7. Вставляем новые данные
        self.repository.bulk_insert(all_records)

        # 8. Логируем
        print(f"[RAW PRICES] Загружено {len(all_records)} строк за {actual_data_date}")

        # 9. Очистка
        if self.cleanup:
            self.file_manager.cleanup_extracted_dir(report, raw_zip_path)