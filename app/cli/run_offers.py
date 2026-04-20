from datetime import date
import logging
from app.configs.settings import settings
from app.storage.database import SessionLocal
from app.core.date_manager import DateManager
from app.core.orchestrators.offers_orchestrator import OffersOrchestrator
from app.core.pipelines.dim_offers_pipeline import OffersETLPipeline
from app.core.pipeline import ReportPipeline
from app.api.report_client import ReportAPIClient

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def main():
    logger.info("=" * 60)
    logger.info("Запуск загрузки справочника товаров (dim_offers)")
    logger.info("=" * 60)

    # 1️⃣ Подключение к БД
    session = SessionLocal()

    try:
        # 2️⃣ Менеджер дат (справочник не зависит от даты, запускаем один раз)
        date_manager = DateManager(
            start_date=date.today(),
            end_date=date.today()
        )
        logger.info(f"Дата запуска: {date.today()}")

        # 3️⃣ API клиент
        api_client = ReportAPIClient(
            api_key=settings.api_key,
            business_id=settings.business_id,
            campaign_id=settings.campaign_id,
        )
        logger.info("API клиент создан")

        # 4️⃣ Pipeline для отчёта
        report_pipeline = ReportPipeline(api_client=api_client)
        logger.info("ReportPipeline создан")

        # 5️⃣ ETL пайплайн для справочника
        etl_pipeline = OffersETLPipeline(
            session=session,
            report_pipeline=report_pipeline,
        )
        logger.info("ETL пайплайн создан")

        # 6️⃣ Оркестратор
        orchestrator = OffersOrchestrator(
            etl_pipeline=etl_pipeline,
            start_date=date_manager.start_date,
            end_date=date_manager.end_date,
        )
        logger.info("Оркестратор создан")

        # 7️⃣ Запускаем загрузку
        for run_date in date_manager.get_dates():
            try:
                orchestrator.run_for_date(run_date)
                logger.info(f"✅ Справочник товаров загружен")
            except Exception as e:
                logger.error(f"❌ Ошибка при загрузке справочника: {e}")
                raise

    except Exception as e:
        logger.error(f"Критическая ошибка: {e}")
        raise
    finally:
        session.close()
        logger.info("Сессия БД закрыта")

    logger.info("=" * 60)
    logger.info("Загрузка справочника товаров завершена")
    logger.info("=" * 60)


if __name__ == "__main__":
    main()