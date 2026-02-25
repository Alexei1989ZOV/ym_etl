import logging
from datetime import date

from app.core.orchestrators.base import BaseOrchestrator
from app.core.pipelines.raw_sales_pipeline import RawSalesETLPipeline

logger = logging.getLogger(__name__)

class RawSalesOrchestrator(BaseOrchestrator):
    """
    Оркестратор отчёта по продажам (raw sales).
    """

    def __init__(
        self,
        etl_pipeline: RawSalesETLPipeline,
        start_date: date | None = None,
        end_date: date | None = None,
    ):
        super().__init__(start_date, end_date)
        self.pipeline = etl_pipeline  # pipeline создаём и передаём извне

    def run_for_date(self, run_date: date) -> None:
        logger.info("[RAW SALES] Запуск отчёта за %s", run_date)
        self.pipeline.run(run_date)
        logger.info("[RAW SALES] Успешно завершён за %s", run_date)
