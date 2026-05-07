from sqlalchemy.orm import Session
from sqlalchemy.dialects.postgresql import insert
from app.storage.models.orders_info import OrdersCommissionsTbl
from app.configs.logger_settings import get_logger

logger = get_logger(__name__)


class OrdersCommissionsRepository:
    """
    Репозиторий для работы с таблицей orders_commissions.
    Отвечает за сохранение/обновление данных.
    """
    def __init__(self, session: Session):
        """
        Args:
            session: Сессия SQLAlchemy
        """
        self.session = session

    def upsert(self, records: list[OrdersCommissionsTbl])-> None:
        """
        Сохраняет/обновляет данные в таблицу orders_commissions
        по первичному ключу ('order_id', 'commission_type').
        Если запись существует — обновляем сумму комиссии и дату загрузки.
        Args:
            records: Список объектов OrdersCommissionsTbl.
        Raises:
            IOError при ошибке сохранения данных.
        """
        if not records:
            logger.warning("Нет данных для сохранения в таблицу orders_commissions.")
            return
        values_list = []
        try:
            logger.debug("Сохранение данных в таблицу orders_commissions.")
            for r in records:
                values_list.append({
                    'order_id': r.order_id,
                    'commission_type': r.commission_type,
                    'commission_amount': r.commission_amount,
                    'load_date': r.load_date
                })
            stmt = insert(OrdersCommissionsTbl).values(values_list)
            stmt = stmt.on_conflict_do_update(
                index_elements=['order_id', 'commission_type'],
                set_={
                    'commission_amount': stmt.excluded.commission_amount,
                    'load_date': stmt.excluded.load_date
                }
            )
            self.session.execute(stmt)
            logger.debug(f"Данные успешно сохранены в таблицу orders_commissions. Количество записей: {len(values_list)}")
        except Exception as e:
            logger.error(f"Ошибка при сохранении данных в таблицу orders_commissions")
            self.session.rollback()
            raise IOError(f"Ошибка при сохранении данных в таблицу orders_commissions: {e}")
