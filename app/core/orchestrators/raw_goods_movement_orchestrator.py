import logging
from datetime import date

from app.core.orchestrators.base import BaseOrchestrator
from app.core.pipelines.raw_goods_movement_pipeline import GoodsMovementETLPipeline
from app.storage.repositories.raw_goods_movement_repository import  RawGoodsMovementRepository

logger = logging.getLogger(__name__)

class RawGoodsMovementOrchestrator(BaseOrchestrator):
    """
    Оркестратор отчёта по движению товаров.
    """

    def __init__(
        self,
        etl_pipeline: GoodsMovementETLPipeline,
        repository: RawGoodsMovementRepository,
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
            logger.info(f"[RAW GOODS MOVEMENT] Данные за {run_date} уже есть, пропускаем")
            return

        if existing_count > 0 and not self.skip_if_exists:
            logger.warning(f"[RAW GOODS MOVEMENT] Перезаписываем {existing_count} записей за {run_date}")
            self.repository.delete_by_date(run_date)

        logger.info("[RAW GOODS MOVEMENT] Запуск отчёта за %s", run_date)
        self.pipeline.run(run_date)
        logger.info("[RAW GOODS MOVEMENT] Успешно завершён за %s", run_date)