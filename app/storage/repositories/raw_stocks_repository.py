from sqlalchemy.orm import Session
from typing import Iterable
from app.storage.models.raw_stocks import RawStocksReport
from datetime import date


class RawStocksRepository:
    """
    Репозиторий для raw слоя отчёта по остаткам.
    Отвечает ТОЛЬКО за работу с БД.
    """

    def __init__(self, session: Session):
        self.session = session

    def bulk_insert(self, records: Iterable[RawStocksReport]) -> None:
        """
        Массовая вставка raw записей.
        Используется для загрузки CSV (10k+ строк).
        """
        if not records:
            return

        self.session.bulk_save_objects(records)
        self.session.commit()

    def delete_by_date(self, target_date: date) -> None:
        """
        Удаляет raw данные за конкретную дату.
        Используется для идемпотентной перезагрузки.
        """
        self.session.query(RawStocksReport).filter(
            RawStocksReport.day == target_date
        ).delete(synchronize_session=False)
        self.session.commit()

    def count_by_date(self, target_date: date) -> int:  # <-- тоже date
        """
        Возвращает количество записей за дату.
        Полезно для логов и sanity-check.
        """
        return self.session.query(RawStocksReport).filter(
            RawStocksReport.day == target_date
        ).count()
