from sqlalchemy.orm import Session
from sqlalchemy.dialects.postgresql import insert
from app.storage.models.orders_info import OrdersTbl
from app.configs.logger_settings import get_logger

logger = get_logger(__name__)

class OrdersRepository:
    """
    Репозиторий для работы с таблицей orders.
    Отвечает за сохранение/обновление данных о заказах.
    """
    def __init__(self, session: Session):
        """
        Args:
            session: Сессия SQLAlchemy
        """
        self.session = session

    def upsert(self, records: list[OrdersTbl]) -> None:
        """
        Вставка или обновление заказов по первичному ключу order_id.
        Если запись существует — обновляем статусы и дату загрузки.
        Args:
            records: Список объектов OrdersTbl
        Raises:
            IOError: При ошибке сохранения данных
        """
        if not records:
            logger.warning("Нет данных для сохранения в таблицу orders.")
            return
        # 1. Извлекаем данные из объектов SQLAlchemy
        values_list = []
        try:
            for r in records:
                values_list.append({
                    'order_id': r.order_id,
                    'creation_date': r.creation_date,
                    'status_upd_date': r.status_upd_date,
                    'payment_type': r.payment_type,
                    'load_date': r.load_date
                })

            # 2. Формируем запрос
            stmt = insert(OrdersTbl).values(values_list)

            stmt = stmt.on_conflict_do_update(
                index_elements=['order_id'],
                set_={
                    'status_upd_date': stmt.excluded.status_upd_date,
                    'payment_type': stmt.excluded.payment_type,
                    'load_date': stmt.excluded.load_date,
                }
            )
            self.session.execute(stmt)
            logger.debug(f"Данные успешно сохранены в таблицу orders. Количество записей: {len(values_list)}")
        except Exception as e:
            logger.error(f"Ошибка при сохранении данных в таблицу orders: {e}")
            self.session.rollback()
            raise IOError(f"Ошибка при сохранении данных в таблицу orders: {e}")


