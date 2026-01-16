from datetime import date, timedelta
from app.configs.settings import settings
from app.storage.database import SessionLocal
from app.processing.file_manager import FileManager
from app.core.pipelines.raw_sales_pipeline import RawSalesETLPipeline
from app.core.pipeline import ReportPipeline
from app.api.report_client import ReportAPIClient  # твой API клиент

def main(run_date: date):
    # 1. Сессия SQLAlchemy
    session = SessionLocal()

    # 2. Менеджер файлов
    file_manager = FileManager(
        raw_dir=settings.temp_dir,
        processed_dir=settings.reports_dir
    )

    # 3. API клиент
    api_client = ReportAPIClient(
        api_key=settings.api_key,
        business_id=settings.business_id,
        campaign_id=settings.campaign_id
    )

    # 4. Pipeline для отчётов
    report_pipeline = ReportPipeline(api_client=api_client)

    # 5. Raw пайплайн
    raw_sales_pipeline = RawSalesETLPipeline(
        session=session,
        file_manager=file_manager,
        report_pipeline=report_pipeline
    )

    # 6. Запуск для указанной даты
    raw_sales_pipeline.run(run_date)

if __name__ == "__main__":
    day = date.today() - timedelta(days=1)
    main(day)
