from sqlalchemy.orm import Session
from sqlalchemy.dialects.postgresql import insert
from app.storage.models.orders_info import OrderPaymentsTbl
from app.configs.logger_settings import get_logger

logger = get_logger(__name__)

class OrdersPaymentsRepository:
    """
    Репозиторий для работы с таблицей orders_payments.
    Отвечает за сохранение/обновление данных.
    """
    def __init__(self, session: Session):
        """
        Args:
            session: Сессия SQLAlchemy
        """
        self.session = session

    def upsert(self, records: list[OrderPaymentsTbl]) -> None:
        """
        Сохраняет/обновляет данные в таблицу orders_payments
        по первичному ключу ('order_id', 'payment_id', 'payment_type').
        Если запись существует — обновляем статусы и дату загрузки.
        Args:
            records: Список объектов OrderPaymentsTbl.
        Raises:
            IOError при ошибке сохранения данных.
        """
        if not records:
            logger.warning("Нет данных для сохранения в таблицу orders_payments.")
            return
        values_list = []
        try:
            logger.debug("Сохранение данных в таблицу orders_payments.")
            for r in records:
                values_list.append({
                    'order_id': r.order_id,
                    'payment_id': r.payment_id,
                    'payment_type': r.payment_type,
                    'payment_date' : r.payment_date,
                    'payment_source': r.payment_source,
                    'payment_amount': r.payment_amount,
                    'payment_order_id': r.payment_order_id,
                    'payment_order_date': r.payment_order_date,
                    'load_date': r.load_date
                })

            stmt = insert(OrderPaymentsTbl).values(values_list)
            stmt = stmt.on_conflict_do_update(
                index_elements=['order_id', 'payment_id', 'payment_type'],
                set_={
                    'payment_source': stmt.excluded.payment_source,
                    'payment_amount': stmt.excluded.payment_amount,
                    'payment_date': stmt.excluded.payment_date,
                    'payment_order_id': stmt.excluded.payment_order_id,
                    'payment_order_date': stmt.excluded.payment_order_date,
                    'load_date': stmt.excluded.load_date
                }
            )
            self.session.execute(stmt)
            logger.debug(f"Данные успешно сохранены в таблицу orders_payments. Количество записей: {len(values_list)}")
        except Exception as e:
            logger.error(f"Ошибка при сохранении данных в таблицу orders_payments")
            self.session.rollback()
            raise IOError(f"Ошибка при сохранении данных в таблицу orders_payments: {e}")
