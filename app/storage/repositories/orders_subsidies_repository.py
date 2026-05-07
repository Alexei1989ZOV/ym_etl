from sqlalchemy.orm import Session
from app.storage.models.orders_info import OrdersSubsidiesTbl
from app.configs.logger_settings import get_logger

logger = get_logger(__name__)


class OrdersSubsidiesRepository:
    """
    Репозиторий для работы с таблицей orders_subsidies.
    Отвечает за полное обновление данных.
    """
    def __init__(self, session: Session):
        """
        Args:
            session: Сессия SQLAlchemy
        """
        self.session = session

    def replace_by_order(self, records: list[OrdersSubsidiesTbl]) -> None:
        """
        Полностью заменяет информацию о соинвесте в заказах.
        Args:
            records: Список объектов OrdersSubsidiesTbl.
        Raises:
            IOError: при ошибке сохранения данных.
        """
        if not records:
            logger.warning("Нет данных для сохранения в таблицу orders_subsidies.")
            return

        try:
            logger.debug("Сохранение данных в таблицу orders_subsidies.")
            order_ids = {r.order_id for r in records}

            # ОДИН DELETE для всех заказов
            self.session.query(OrdersSubsidiesTbl).filter(
                OrdersSubsidiesTbl.order_id.in_(order_ids)
            ).delete(synchronize_session=False)

            # ОДИН BULK INSERT
            self.session.bulk_save_objects(records)
            logger.debug(
                f"Данные успешно сохранены в таблицу orders_subsidies. Количество записей: {len(records)}")
        except Exception as e:
            logger.error(f"Ошибка при сохранении данных в таблицу orders_subsidies")
            self.session.rollback()
            raise IOError(f"Ошибка при сохранении данных в таблицу orders_subsidies: {e}")

