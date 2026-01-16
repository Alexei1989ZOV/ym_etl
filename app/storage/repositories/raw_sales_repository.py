from sqlalchemy.orm import Session
from typing import Iterable
from app.storage.models.raw_sales import RawSalesReport


class RawSalesRepository:
    """
    Репозиторий для raw слоя отчёта продаж.
    Отвечает ТОЛЬКО за работу с БД.
    """

    def __init__(self, session: Session):
        self.session = session

    def bulk_insert(self, records: Iterable[RawSalesReport]) -> None:
        """
        Массовая вставка raw записей.
        Используется для загрузки CSV (10k+ строк).
        """
        if not records:
            return

        self.session.bulk_save_objects(records)
        self.session.commit()

    def delete_by_period(
        self,
        year: int,
        month: str,
        day: str | None = None
    ) -> None:
        """
        Удаляет raw данные за период.
        Используется для идемпотентной перезагрузки.
        """
        query = self.session.query(RawSalesReport).filter(
            RawSalesReport.year == year,
            RawSalesReport.month == month
        )

        if day:
            query = query.filter(RawSalesReport.day == day)

        query.delete(synchronize_session=False)
        self.session.commit()

    def count_by_period(
        self,
        year: int,
        month: str,
        day: str | None = None
    ) -> int:
        """
        Полезно для логов и sanity-check.
        """
        query = self.session.query(RawSalesReport).filter(
            RawSalesReport.year == year,
            RawSalesReport.month == month
        )

        if day:
            query = query.filter(RawSalesReport.day == day)

        return query.count()
