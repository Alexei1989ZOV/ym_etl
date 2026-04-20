import logging
from datetime import date

from app.core.orchestrators.base import BaseOrchestrator
from app.core.pipelines.dim_offers_pipeline import OffersETLPipeline

logger = logging.getLogger(__name__)


class OffersOrchestrator(BaseOrchestrator):
    """
    Оркестратор для загрузки справочника товаров.
    """

    def __init__(
        self,
        etl_pipeline: OffersETLPipeline,
        start_date: date | None = None,
        end_date: date | None = None,
    ):
        super().__init__(start_date, end_date)
        self.pipeline = etl_pipeline

    def run_for_date(self, run_date: date) -> None:
        """
        Запуск загрузки справочника товаров.
        """
        logger.info("[DIM OFFERS] Запуск загрузки справочника товаров")
        self.pipeline.run(run_date)
        logger.info("[DIM OFFERS] Успешно завершён")