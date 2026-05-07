from datetime import date, timedelta
from app.core.orchestrators.base import BaseOrchestrator
from app.core.pipelines.orders_info_pipeline import OrdersInfoPipeline
from app.configs.logger_settings import get_logger

logger = get_logger(__name__)



class OrdersInfoOrchestrator(BaseOrchestrator):
    """
    Оркестратор для загрузки данных по заказам.
    Загружает изменения за последние 3 дня относительно даты запуска.
    """
    def __init__(
            self,
            pipeline: OrdersInfoPipeline,
            start_date: date | None = None,
            end_date: date | None = None,
    ):
        """
        Args:
            pipeline: ETL паплайн для заказов
            start_date: Начальная дата (опционально)
            end_date: Конечная дата (опционально)
        """
        super().__init__(start_date, end_date)
        self.pipeline = pipeline

    def run_for_date(self, run_date: date) -> None:
        # Для заказов загружаем изменения за последние 3 дня
        # или за период между запусками
        update_from = run_date - timedelta(days=3)
        update_to = run_date

        logger.info(f"[ORDERS INFO] Загрузка изменений с {update_from} по {update_to}")
        self.pipeline.run(update_from, update_to)
        logger.info(f"[ORDERS INFO] Успешно завершён за {run_date}")