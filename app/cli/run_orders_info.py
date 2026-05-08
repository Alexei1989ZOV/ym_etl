import logging
from datetime import date, timedelta
from app.configs.settings import settings
from app.storage.database import SessionLocal
from app.core.pipeline import ReportPipeline
from app.api.report_client import ReportAPIClient
from app.core.pipelines.orders_info_pipeline import OrdersInfoPipeline
from app.core.date_manager import DateManager #новый
from app.core.orchestrators.orders_info_orchestrator import OrdersInfoOrchestrator #новый

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def main():
   # date_manager = DateManager(
    #    start_date=date.today() - timedelta(days=1),
    #    end_date=date.today())

   # logger.info(f"Загрузка изменений заказов за период {date_manager.start_date} - {date_manager.end_date}")

    session = None
    try:
        # 1. Подключение к БД
        session = SessionLocal()

        # 2. API клиент
        api_client = ReportAPIClient(
            api_key=settings.api_key,
            business_id=settings.business_id,
            campaign_id=settings.campaign_id,
        )



        # 4. ETL пайплайн
        etl_pipeline = OrdersInfoPipeline(
            session=session,
            api_client=api_client,
        )

        # 5. Запуск
        #etl_pipeline.run(update_from, update_to)
        orchestrator = OrdersInfoOrchestrator(
            pipeline = etl_pipeline,

        )
        orchestrator.run_for_date(date.today())
        logger.info("Загрузка заказов успешно завершена")

    except Exception as e:
        logger.error(f"Ошибка при загрузке заказов: {e}", exc_info=True)
        raise
    finally:
        if session:
            session.close()


if __name__ == "__main__":
    main()