import logging
from datetime import date

from app.core.orchestrators.base import BaseOrchestrator
from app.core.pipelines.raw_stocks_pipeline import RawStocksETLPipeline

logger = logging.getLogger(__name__)

class RawStocksOrchestrator(BaseOrchestrator):
    """
    Оркестратор отчёта по остаткам.
    """

    def __init__(
        self,
        etl_pipeline: RawStocksETLPipeline,
        start_date: date | None = None,
        end_date: date | None = None,
    ):
        super().__init__(start_date, end_date)
        self.pipeline = etl_pipeline  # pipeline создаём и передаём извне

    def run_for_date(self, run_date: date) -> None:
        logger.info("[RAW STOCKS] Запуск отчёта за %s", run_date)
        self.pipeline.run(run_date)
        logger.info("[RAW STOCKS] Успешно завершён за %s", run_date)
