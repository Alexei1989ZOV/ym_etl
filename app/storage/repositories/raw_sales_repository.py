from sqlalchemy.orm import Session
from app.storage.models.raw_sales import RawSalesReport
from app.configs.logger_settings import get_logger

logger = get_logger(__name__)


class RawSalesRepository:
    """
    Репозиторий для работы с таблицей raw_sales_reports.
    Отвечает за работу с БД.
    Отчет Аналитика продаж.
    """

    def __init__(self, session: Session):
        """
        Args:
            session: Сессия SQLAlchemy
        """
        self.session = session

    def bulk_insert(self, records: list[RawSalesReport]) -> None:
        """
        Массовая вставка raw записей.
        Args:
            records: Список объектов RawSalesReport.
        Raises:
            IOError: при ошибке сохранения данных.
        """
        if not records:
            logger.warning("Нет данных для сохранения в таблицу raw_sales_reports.")
            return
        try:
            logger.debug("Сохранение данных в таблицу raw_sales_reports.")
            self.session.bulk_save_objects(records)
            logger.debug(
                f"Данные успешно сохранены в таблицу raw_sales_reports. Количество записей: {len(records)}")
        except Exception as e:
            logger.error(f"Ошибка при сохранении данных в таблицу raw_sales_reports")
            self.session.rollback()
            raise IOError(f"Ошибка при сохранении данных в таблицу raw_sales_reports: {e}")

    def delete_by_period(self, day: str) -> None:
        """
        Удаляет из таблицы raw_sales_reports данные за конкретную дату.
        Используется для идемпотентной перезагрузки.
        Args:
            day : Дата, за которую нужно удалить данные 'ГГГГ-ММ-ДД'.
        Raises:
            IOError: при удалении данных за дату.
        """
        logger.debug(f"Удаляем данные за {day} из таблицы raw_sales_reports.")
        try:
            self.session.query(RawSalesReport).filter(
                RawSalesReport.day == day
            ).delete(synchronize_session=False)
        except Exception as e:
            logger.error(f"Ошибка при удалении данных из таблицы raw_sales_reports за {day}")
            self.session.rollback()
            raise IOError(f"Ошибка при удалении данных из таблицы raw_sales_reports за {day}: {e}")


    def count_by_period(self, day: str) -> int:
        """
        Возвращает количество записей за дату.
        Полезно для логов и sanity-check.
        Args:
            day: Дата, за которую нужно получить количество записей.
        Returns:
            Количество записей в таблице raw_sales_reports за дату.
        """
        try:
            return self.session.query(RawSalesReport).filter(
                RawSalesReport.day == day
            ).count()
        except Exception as e:
            raise IOError(f"Ошибка при получении количества записей в таблице raw_sales_reports за {day}: {e}")