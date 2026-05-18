from sqlalchemy.orm import Session
from app.storage.models.raw_prices import RawPricesReport
from datetime import date
from app.configs.logger_settings import get_logger

logger = get_logger(__name__)


class RawPricesRepository:
    """
    Репозиторий для работы с таблицей raw_prices.
    Отвечает за работу с БД.
    Отчет по ценам.
    """

    def __init__(self, session: Session):
        """
        Args:
            session: Сессия SQLAlchemy
        """
        self.session = session

    def bulk_insert(self, records: list[RawPricesReport]) -> None:
        """
        Массовая вставка raw записей.
        Args:
            records: Список объектов RawPricesReport.
        Raises:
            IOError: при ошибке сохранения данных.
        """
        if not records:
            logger.warning("Нет данных для сохранения в таблицу raw_prices.")
            return
        try:
            logger.debug("Сохранение данных в таблицу raw_prices.")
            self.session.bulk_save_objects(records)
            logger.debug(
                f"Данные успешно сохранены в таблицу raw_prices. Количество записей: {len(records)}")
        except Exception as e:
            logger.error(f"Ошибка при сохранении данных в таблицу raw_prices")
            self.session.rollback()
            raise IOError(f"Ошибка при сохранении данных в таблицу raw_prices: {e}")

    def delete_by_date(self, target_date: date) -> None:
        """
        Удаляет из таблицы raw_prices данные за конкретную дату.
        Используется для идемпотентной перезагрузки.
        Args:
            target_date: Дата, за которую нужно удалить данные.
        Raises:
            IOError: при удалении данных за дату.
        """
        logger.debug(f"Удаляем данные за {target_date} из таблицы raw_prices.")
        try:
            self.session.query(RawPricesReport).filter(
                RawPricesReport.report_date == target_date
            ).delete(synchronize_session=False)
            logger.debug(
            f"Данные за {target_date} удалены из таблицы raw_prices. Количество записей: {self.count_by_date(target_date)}")
        except Exception as e:
            logger.error(f"Ошибка при удалении данных из таблицы raw_prices за {target_date}")
            self.session.rollback()
            raise IOError(f"Ошибка при удалении данных из таблицы raw_prices за {target_date}: {e}")

    def count_by_date(self, target_date: date) -> int:  
        """
        Возвращает количество записей за дату.
        Полезно для логов и sanity-check.
        Args:
            target_date: Дата, за которую нужно получить количество записей.
        Returns:
            Количество записей в таблице raw_prices за дату.
        """
        try:
            return self.session.query(RawPricesReport).filter(
                RawPricesReport.report_date == target_date
            ).count()
        except Exception as e:
            raise IOError(f"Ошибка при получении количества записей в таблице raw_prices за {target_date}: {e}")