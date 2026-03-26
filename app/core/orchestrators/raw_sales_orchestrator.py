import logging
from datetime import date

from app.core.orchestrators.base import BaseOrchestrator
from app.core.pipelines.raw_sales_pipeline import RawSalesETLPipeline
from app.storage.repositories.raw_sales_repository import RawSalesRepository

logger = logging.getLogger(__name__)

class RawSalesOrchestrator(BaseOrchestrator):
    """
    Оркестратор отчёта по продажам (raw sales).
    """

    def __init__(
        self,
        etl_pipeline: RawSalesETLPipeline,
        repository: RawSalesRepository,
        start_date: date | None = None,
        end_date: date | None = None,
        skip_if_exists: bool = True
    ):
        super().__init__(start_date, end_date)
        self.pipeline = etl_pipeline  # pipeline создаём и передаём извне
        self.repository = repository
        self.skip_if_exists = skip_if_exists

    def run_for_date(self, run_date: date) -> None:
        # Разбираем дату на компоненты
        year = run_date.year  # 2026
        month = f"{run_date.month:02d}"  # "01"
        day = f"{run_date.day:02d}"  # "16"

        existing_count = self.repository.count_by_period(
            year=year,
            month=month,
            day=day
        )

        if existing_count > 0 and self.skip_if_exists:
            logger.info(f"[RAW SALES] Данные за {run_date} уже есть, пропускаем")
            return

        if existing_count > 0 and not self.skip_if_exists:
            logger.warning(f"[RAW SALES] Перезаписываем {existing_count} записей за {run_date}")
            self.repository.delete_by_period(
                year=year,
                month=month,
                day=day
            )

        logger.info("[RAW SALES] Запуск отчёта за %s (данные за %s)", run_date, run_date)
        self.pipeline.run(run_date)
        logger.info("[RAW SALES] Успешно завершён за %s", run_date)
