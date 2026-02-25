from datetime import date

import logging
from app.configs.settings import settings
from app.storage.database import SessionLocal
from app.core.date_manager import DateManager
from app.core.orchestrators.raw_sales_orchestrator import RawSalesOrchestrator
from app.core.pipelines.raw_sales_pipeline import RawSalesETLPipeline
from app.processing.file_manager import FileManager
from app.core.pipeline import ReportPipeline
from app.api.report_client import ReportAPIClient

logger = logging.getLogger(__name__)

def main():
    # 1️⃣ Подключение к БД
    session = SessionLocal()

    # 2️⃣ Менеджер дат (начало с конкретной даты, по умолчанию до вчера)
    date_manager = DateManager(
        start_date=date(2026, 1, 17),
        end_date=date(2026, 1, 19),
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
    etl_pipeline = RawSalesETLPipeline(
        session=session,
        file_manager=file_manager,
        report_pipeline=report_pipeline,
    )

    # 7️⃣ Оркестратор
    orchestrator = RawSalesOrchestrator(
        etl_pipeline=etl_pipeline,
        start_date=date_manager.start_date,
        end_date=date_manager.end_date
    )

    # 8️⃣ Пробегаем по всем датам и запускаем
    for run_date in date_manager.get_dates():
        orchestrator.run_for_date(run_date)

if __name__ == "__main__":
    main()
