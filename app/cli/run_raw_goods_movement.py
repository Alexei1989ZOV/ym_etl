from datetime import date, datetime
import argparse
import logging
from app.configs.settings import settings
from app.storage.database import SessionLocal
from app.core.date_manager import DateManager
from app.core.orchestrators.raw_goods_movement_orchestrator import RawGoodsMovementOrchestrator
from app.core.pipelines.raw_goods_movement_pipeline import GoodsMovementETLPipeline
from app.processing.file_manager import FileManager
from app.core.pipeline import ReportPipeline
from app.api.report_client import ReportAPIClient
from app.storage.repositories.raw_goods_movement_repository import RawGoodsMovementRepository
from app.configs.logger_settings import setup_logging, get_logger


def main():
    setup_logging()
        
    parser = argparse.ArgumentParser(description="Запуск отчета по движению товаров")
    
    # Парсим дату запуска
    parser.add_argument(
        "run_date", 
        type=str, 
        help="""Дата запуска отчета в формате ГГГГ-ММ-ДД. 
        """
        )
    # Парсим опцию уровня логгирования
    parser.add_argument(
        "--log-level",
        type=str,
        default="INFO",
        choices=["DEBUG", "INFO", "WARNING", "ERROR"],
        help="Выбор уровня логгирования"
    )
    
    # Парсим опцую пропуска загрузки если данные за дату есть в БД
    parser.add_argument(
        "--skip_if_exists",
        action="store_true",
        help="Пропустить загрузку, если данные за эту дату уже есть"
    )
    args = parser.parse_args()
    run_date = datetime.strptime(args.run_date, "%Y-%m-%d").date()
    
    # Устанавливаем уровень логирования
    log_level = getattr(logging, args.log_level.upper(), logging.INFO)

    # Меняем уровень у корневого логгера и всех обработчиков
    root_logger = logging.getLogger()
    root_logger.setLevel(log_level)
    for handler in root_logger.handlers:
        handler.setLevel(log_level)

    logger = get_logger("raw_goods_movement")
    logger.debug(f"Установлен уровень логирования: {args.log_level}")
    
    # 1️⃣ Подключение к БД
    session = SessionLocal()

    
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
    etl_pipeline = GoodsMovementETLPipeline(
        session=session,
        file_manager=file_manager,
        report_pipeline=report_pipeline,
    )

    repository = RawGoodsMovementRepository(session)

    # 7️⃣ Оркестратор
    orchestrator = RawGoodsMovementOrchestrator(
        etl_pipeline=etl_pipeline,
        repository=repository,
        start_date=run_date,
        end_date=run_date,
        skip_if_exists=args.skip_if_exists
    )

    # 8️⃣ Пробегаем по всем датам и запускаем
    try:
        orchestrator.run_for_date(run_date)
        logger.info(f"Отчет за {run_date} загружен")
    except Exception as e:
        logger.error(f"Ошибка при загрузке отчета за {run_date} : {e}", exc_info=True)
    finally:
        session.close()
            

if __name__ == "__main__":
    main()
