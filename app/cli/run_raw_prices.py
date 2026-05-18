from datetime import date
from app.configs.settings import settings
from app.storage.database import SessionLocal
from app.core.date_manager import DateManager
from app.core.orchestrators.raw_prices_orchestrator import RawPricesOrchestrator
from app.core.pipelines.raw_prices_pipeline import PricesETLPipeline
from app.processing.file_manager import FileManager
from app.core.pipeline import ReportPipeline
from app.api.report_client import ReportAPIClient
from app.storage.repositories.raw_prices_repository import RawPricesRepository
from app.configs.logger_settings import setup_logging, get_logger


def main():
    setup_logging()
    logger = get_logger("raw_prices")
    
    logger.info("[RAW PRICES] Запуск загрузки отчета по ценам")
    session = SessionLocal()

    # Менеджер дат (начало с конкретной даты, по умолчанию до вчера)
    date_manager = DateManager(

    )

    # Файловый менеджер
    file_manager = FileManager(
        raw_dir=settings.temp_dir,
        processed_dir=settings.reports_dir,
    )

    # API клиент
    api_client = ReportAPIClient(
        api_key=settings.api_key,
        business_id=settings.business_id,   # обязательно
        campaign_id=settings.campaign_id,   # можно None
    )

    # Pipeline для отчёта
    report_pipeline = ReportPipeline(
        api_client=api_client,
    )

    # ETL пайплайн
    etl_pipeline = PricesETLPipeline(
        session=session,
        file_manager=file_manager,
        report_pipeline=report_pipeline,
    )

    repository = RawPricesRepository(session)

    # Оркестратор
    orchestrator = RawPricesOrchestrator(
        etl_pipeline=etl_pipeline,
        repository=repository,
        start_date=date_manager.start_date,
        end_date=date_manager.end_date,
        skip_if_exists=True
    )

    # Пробегаем по всем датам и запускаем
    for run_date in date_manager.get_dates():
        try:
            orchestrator.run_for_date(run_date)
            logger.info(f"[RAW PRICES] Отчет за {run_date} загружен")
        except Exception as e:
            logger.error(f"[RAW PRICES] Ошибка при загрузке отчета за {run_date} : {e}")
            continue

if __name__ == "__main__":
    main()
