from datetime import date

import logging
from app.configs.settings import settings
from app.storage.database import SessionLocal
from app.core.date_manager import DateManager
from app.core.orchestrators.raw_stocks_orchestrator import RawStocksOrchestrator
from app.core.pipelines.raw_stocks_pipeline import RawStocksETLPipeline
from app.processing.file_manager import FileManager
from app.core.pipeline import ReportPipeline
from app.api.report_client import ReportAPIClient
from app.storage.repositories.raw_stocks_repository import RawStocksRepository

logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
logger = logging.getLogger(__name__)

def main():

    # 1️⃣ Подключение к БД
    session = SessionLocal()

    # 2️⃣ Менеджер дат (начало с конкретной даты, по умолчанию до вчера)
    date_manager = DateManager(
        start_date=date(2026, 5, 25),
        end_date=date(2026, 5, 25),
    )

    # 3️⃣ Файловый менеджер
    file_manager = FileManager(
        raw_dir=settings.temp_dir,
        processed_dir=settings.reports_dir,
    )

    # 4️⃣ API клиент
    api_client = ReportAPIClient(
        api_key=settings.api_key,
        business_id=settings.business_id,   # обязательно
        campaign_id=settings.campaign_id,   # можно None
    )

    # 5️⃣ Pipeline для отчёта
    report_pipeline = ReportPipeline(
        api_client=api_client,
    )

    # 6️⃣ ETL пайплайн
    etl_pipeline = RawStocksETLPipeline(
        session=session,
        file_manager=file_manager,
        report_pipeline=report_pipeline,
    )

    repository = RawStocksRepository(session)

    # 7️⃣ Оркестратор
    orchestrator = RawStocksOrchestrator(
        etl_pipeline=etl_pipeline,
        repository=repository,
        start_date=date_manager.start_date,
        end_date=date_manager.end_date,
        skip_if_exists=False
    )

    # 8️⃣ Пробегаем по всем датам и запускаем
    for run_date in date_manager.get_dates():
        try:
            orchestrator.run_for_date(run_date)
            logger.info(f"Отчет за {run_date} загружен")
        except Exception as e:
            logger.error(f"Ошибка при загрузке отчета за {run_date} : {e}")
            continue

if __name__ == "__main__":
    main()
