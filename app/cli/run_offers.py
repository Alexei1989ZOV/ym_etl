from datetime import date
import logging
from app.configs.settings import settings
from app.storage.database import SessionLocal
from app.core.date_manager import DateManager
from app.core.orchestrators.offers_orchestrator import OffersOrchestrator
from app.core.pipelines.dim_offers_pipeline import OffersETLPipeline
from app.api.report_client import ReportAPIClient
from app.configs.logger_settings import setup_logging, get_logger


def main():
    """
    Загружает справочник товаров (dim_offers) из API Яндекс.Маркета.
    Порядок действий:
        1. Настраивает логирование
        2. Подключается к БД
        3. Создает API-клиент
        4. Запускает ETL-пайплайн
        5. Сохраняет данные в таблицы raw_offers и dim_offers
    """
    setup_logging()
    logger = get_logger(__name__)

    logger.info("Запуск загрузки справочника товаров (dim_offers)")


    # Подключение к БД
    session = SessionLocal()

    try:

        date_manager = DateManager(
            start_date=date.today(),
            end_date=date.today()
        )
        logger.info(f"Дата запуска: {date.today()}")


        api_client = ReportAPIClient(
            api_key=settings.api_key,
            business_id=settings.business_id,
            campaign_id=settings.campaign_id,
        )
        logger.info("API клиент создан")



        etl_pipeline = OffersETLPipeline(
            session=session,
            api_client=api_client,
        )
        logger.info("ETL пайплайн создан")


        orchestrator = OffersOrchestrator(
            etl_pipeline=etl_pipeline,
            start_date=date_manager.start_date,
            end_date=date_manager.end_date,
        )
        logger.info("Оркестратор создан")


        for run_date in date_manager.get_dates():
            try:
                orchestrator.run_for_date(run_date)
                logger.info(f"Справочник товаров загружен")
            except Exception as e:
                logger.error(f"Ошибка при загрузке справочника: {e}")
                raise

    except Exception as e:
        logger.error(f"Критическая ошибка: {e}")
        raise
    finally:
        session.close()
        logger.info("Сессия БД закрыта")

    logger.info("Загрузка справочника товаров завершена")

if __name__ == "__main__":
    main()