import logging
from datetime import date, timedelta

from app.core.orchestrators.base import BaseOrchestrator
from app.core.pipelines.raw_stocks_pipeline import RawStocksETLPipeline
from app.storage.repositories.raw_stocks_repository import RawStocksRepository

logger = logging.getLogger(__name__)

class RawStocksOrchestrator(BaseOrchestrator):
    """
    Оркестратор отчёта по остаткам.
    """

    def __init__(
        self,
        etl_pipeline: RawStocksETLPipeline,
        repository: RawStocksRepository,
        start_date: date | None = None,
        end_date: date | None = None,
        skip_if_exists: bool = True
    ):
        super().__init__(start_date, end_date)
        self.pipeline = etl_pipeline  # pipeline создаём и передаём извне
        self.repository = repository
        self.skip_if_exists = skip_if_exists

    def run_for_date(self, run_date: date) -> None:
        data_date = run_date - timedelta(days=1)
        existing_count = self.repository.count_by_date(data_date)

        if existing_count > 0 and self.skip_if_exists:
            logger.info(f"[RAW STOCKS] Данные за {data_date} уже есть, пропускаем")
            return

        if existing_count > 0 and not self.skip_if_exists:
            logger.warning(f"[RAW STOCKS] Перезаписываем {existing_count} записей за {data_date}")
            self.repository.delete_by_date(data_date)

        logger.info("[RAW STOCKS] Запуск отчёта за %s (данные за %s)", run_date, data_date)
        self.pipeline.run(run_date)
        logger.info("[RAW STOCKS] Успешно завершён за %s", run_date)