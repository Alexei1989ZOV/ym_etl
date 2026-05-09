from sqlalchemy.orm import Session
from app.storage.models.raw_goods_movement import RawGoodsMovementReport
from datetime import date
from app.configs.logger_settings import get_logger

logger = get_logger(__name__)


class RawGoodsMovementRepository:
    """
    Репозиторий для работы с таблицей raw_goods_movement.
    Отвечает за работу с БД.
    Отчет по движению товаров.
    """

    def __init__(self, session: Session):
        """
        Args:
            session: Сессия SQLAlchemy
        """
        self.session = session

    def bulk_insert(self, records: list[RawGoodsMovementReport]) -> None:
        """
        Массовая вставка raw записей.
        Args:
            records: Список объектов RawGoodsMovementReport.
        Raises:
            IOError: при ошибке сохранения данных.
        """
        if not records:
            logger.warning("Нет данных для сохранения в таблицу raw_goods_movement.")
            return
        try:
            logger.debug("Сохранение данных в таблицу raw_goods_movement.")
            self.session.bulk_save_objects(records)
            logger.debug(
                f"Данные успешно сохранены в таблицу raw_goods_movement. Количество записей: {len(records)}")
        except Exception as e:
            logger.error(f"Ошибка при сохранении данных в таблицу raw_goods_movement")
            self.session.rollback()
            raise IOError(f"Ошибка при сохранении данных в таблицу raw_goods_movement: {e}")

    def delete_by_date(self, target_date: date) -> None:
        """
        Удаляет из таблицы raw_goods_movement данные за конкретную дату.
        Используется для идемпотентной перезагрузки.
        Args:
            target_date: Дата, за которую нужно удалить данные.
        Raises:
            IOError: при удалении данных за дату.
        """
        try:
            logger.debug(f"Удаляем данные за {target_date} из таблицы raw_goods_movement.")
            self.session.query(RawGoodsMovementReport).filter(
                RawGoodsMovementReport.report_date == target_date
            ).delete(synchronize_session=False)
            logger.debug(
            f"Данные за {target_date} удалены из таблицы raw_goods_movement. Количество записей: {self.count_by_date(target_date)}")
        except Exception as e:
            logger.error(f"Ошибка при удалении данных из таблицы raw_goods_movement за {target_date}")
            self.session.rollback()
            raise IOError(f"Ошибка при удалении данных из таблицы raw_goods_movement за {target_date}: {e}")

    def count_by_date(self, target_date: date) -> int:
        """
        Возвращает количество записей за дату.
        Полезно для логов и sanity-check.
        Args:
            target_date: Дата, за которую нужно получить количество записей.
        Returns:
            Количество записей в таблице raw_goods_movement за дату.
        """
        try:
            return self.session.query(RawGoodsMovementReport).filter(
                RawGoodsMovementReport.report_date == target_date
            ).count()
        except Exception as e:
            raise IOError(f"Ошибка при получении количества записей в таблице raw_goods_movement за {target_date}: {e}")