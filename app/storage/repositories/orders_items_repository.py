from sqlalchemy.orm import Session
from app.storage.models.orders_info import OrderItemsTbl
from app.configs.logger_settings import get_logger

logger = get_logger(__name__)


class OrdersItemsRepository:
    """
    Репозиторий для работы с таблицей orders_items.
    Отвечает за полное обновление товаров в заказах.
    """
    def __init__(self, session: Session):
        """
        Args:
            session: Сессия SQLAlchemy
        """
        self.session = session

    def replace_by_order(self, records: list[OrderItemsTbl])-> None:
        """
        Полностью заменяет позиции заказа (удаляет старые, вставляет новые).
        Используется для идемпотентной загрузки.
        Args:
            records: Список объектов OrderItemsTbl.
        Raises:
            IOError при ошибке сохранения данных.
        """
        if not records:
            logger.warning("Нет данных для сохранения в таблицу orders_items.")
            return
        try:
            # Получаем order_id всех заказов
            order_ids = {r.order_id for r in records}

            # Удаляем старые записи по всем заказам
            logger.debug("Удаляем старые позиции в заказах в таблице orders_items")
            self.session.query(OrderItemsTbl).filter(
                OrderItemsTbl.order_id.in_(order_ids)
            ).delete(synchronize_session=False)
            logger.debug("Вставляем новые позиции заказов в таблице orders_items")
            self.session.bulk_save_objects(records)
            logger.debug(f"Данные успешно сохранены в таблицу orders_items. Количество записей: {len(records)}")
        except Exception as e:
            logger.error(f"Ошибка при сохранении данных в таблицу orders_items")
            self.session.rollback()
            raise IOError(f"Ошибка при сохранении данных в таблицу orders_items: {e}")


