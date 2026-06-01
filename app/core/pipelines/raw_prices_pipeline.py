from datetime import date
from sqlalchemy.orm import Session
from app.reports.prices import PricesReport
from app.core.pipeline import ReportPipeline
from app.processing.file_manager import FileManager
from app.raw_transformers.prices_transformer import PricesCSVTransformer
from app.storage.repositories.raw_prices_repository import RawPricesRepository
from app.configs.logger_settings import get_logger

logger = get_logger(__name__)


class PricesETLPipeline:
    """
    ETL pipeline для получения отчета по ценам.
    """
    def __init__(self, session: Session, file_manager: FileManager, report_pipeline: ReportPipeline, cleanup: bool = True):
        """
        Args:
            session: Сессия SQLAlchemy для работы с базой данных
            file_manager: класс для работы с файлами
            report_pipeline: класс, отвечающий за последовательность действий для получения асинхронных отчетов
            cleanup: флаг для указания необходимости очистки извлеченных из архива файлов после загрузки
        """
        self.session = session
        self.file_manager = file_manager
        self.report_pipeline = report_pipeline
        self.repository = RawPricesRepository(session)
        self.cleanup = cleanup

    def run(self, report_date: date) -> None:
        """
        Запуск ETL процесса для получения отчета по ценам за дату.
        Args:
            report_date: Дата на которую нужно получить отчет.
        Raises:
            ValueError: Если дата больше текущей даты.
        """
        if report_date > date.today():
            logger.warning(f"[RAW PRICES] Дата отчета не может быть больше текущей. Дата: {report_date}")
            raise ValueError("Дата отчета не может быть больше текущей")
        try:
            logger.info(f"[RAW PRICES] Начало загрузки отчета по ценам за {report_date}")
            # 1. Создаём объект отчёта
            report = PricesReport()

            logger.info(f"[RAW PRICES] Ожидаем генерацию отчета по ценам за {report_date}")
            # 2. Генерация и получение ссылки на скачивание
            download_url = self.report_pipeline.run(report)

            logger.info(f"[RAW PRICES] Скачиваем архив с отчетом по ценам.")
            # 3. Скачиваем ZIP
            raw_bytes = self.report_pipeline.api_client.download_report(download_url)

            # 4. Сохраняем raw ZIP
            raw_zip_path = self.file_manager.save_raw(report, report_date, raw_bytes)

            logger.info(f"[RAW PRICES] Извлекаем CSV из архива.")
            # 5. Распаковываем CSV
            csv_files = self.file_manager.extract_archive(report, raw_zip_path)
            all_records = []

            logger.info(f"[RAW PRICES] Выполняем трансформации.")
            for csv_path in csv_files:
                transformer = PricesCSVTransformer(csv_path)
                records = transformer.transform()
                all_records.extend(records)

            if not all_records:
                logger.error(f"[RAW PRICES] Нет данных за {report_date}")
                return

            logger.info(f"[RAW PRICES] удаляем данные за {report_date} из БД если они есть.")
            actual_data_date = all_records[0].report_date
            self.repository.delete_by_date(actual_data_date)

            logger.info(f"[RAW PRICES] Сохраняем данные за {report_date} в БД.")
            self.repository.bulk_insert(all_records)

            self.session.commit()

            logger.info(f"[RAW PRICES] Загружено {len(all_records)} строк за {actual_data_date}")

            if self.cleanup:
                logger.info(f"[RAW PRICES] удаляем CSV файлы.")
                self.file_manager.cleanup_extracted_dir(report, raw_zip_path)
        except Exception as e:
            logger.error(f"[RAW PRICES] Ошибка в ETL процессе: {e}")
            raise