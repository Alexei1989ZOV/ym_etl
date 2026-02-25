from abc import ABC, abstractmethod
from datetime import date
from typing import Iterable
import logging

from app.core.date_manager import DateManager


logger = logging.getLogger(__name__)


class BaseOrchestrator(ABC):
    """
    Базовый оркестратор для всех отчётов.
    Управляет датами и последовательным запуском пайплайнов.
    """

    def __init__(
        self,
        start_date: date | None = None,
        end_date: date | None = None,
    ):
        self.date_manager = DateManager(
            start_date=start_date,
            end_date=end_date,
        )

    def run(self) -> None:
        """
        Основная точка входа.
        """
        dates = self.date_manager.get_dates()

        logger.info(
            "[ORCHESTRATOR] Запуск %s дат: %s → %s",
            self.__class__.__name__,
            dates[0],
            dates[-1],
        )

        for run_date in dates:
            try:
                self.run_for_date(run_date)
            except Exception:
                logger.exception(
                    "[ORCHESTRATOR] Ошибка при обработке даты %s",
                    run_date,
                )
                raise  # важно: пусть падение видно в CI / Airflow

    @abstractmethod
    def run_for_date(self, run_date: date) -> None:
        """
        Запуск пайплайна для одной даты.
        """
        raise NotImplementedError
