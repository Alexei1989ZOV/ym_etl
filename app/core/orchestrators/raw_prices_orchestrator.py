from datetime import date
from app.core.orchestrators.base import BaseOrchestrator
from app.core.pipelines.raw_prices_pipeline import PricesETLPipeline
from app.storage.repositories.raw_prices_repository import RawPricesRepository
from app.configs.logger_settings import get_logger

logger = get_logger(__name__)


class RawPricesOrchestrator(BaseOrchestrator):
    """
    Оркестратор отчёта по ценам.
    """

    def __init__(
        self,
        etl_pipeline: PricesETLPipeline,
        repository: RawPricesRepository,
        start_date: date | None = None,
        end_date: date | None = None,
        skip_if_exists: bool = True
    ):
        super().__init__(start_date, end_date)
        self.pipeline = etl_pipeline  # pipeline создаём и передаём извне
        self.repository = repository
        self.skip_if_exists = skip_if_exists

    def run_for_date(self, run_date: date) -> None:
        existing_count = self.repository.count_by_date(run_date)

        if existing_count > 0 and self.skip_if_exists:
            logger.info(f"[RAW PRICES] Данные за {run_date} уже есть, пропускаем")
            return

        if existing_count > 0 and not self.skip_if_exists:
            logger.warning(f"[RAW PRICES] Перезаписываем {existing_count} записей за {run_date}")
            self.repository.delete_by_date(run_date)

        logger.info("[RAW PRICES] Запуск отчёта за %s", run_date)
        self.pipeline.run(run_date)
        logger.info("[RAW PRICES] Успешно завершён за %s", run_date)