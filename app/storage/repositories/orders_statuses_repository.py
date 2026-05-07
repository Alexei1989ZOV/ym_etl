from sqlalchemy.orm import Session
from sqlalchemy.dialects.postgresql import insert
from datetime import date
from app.storage.models.orders_info import OrdersTbl
from app.storage.models.orders_info import OrdersStatusesTbl
from app.configs.logger_settings import get_logger

logger = get_logger(__name__)


class OrdersStatusesRepository:
    """
    Репозиторий для работы с таблицей orders_statuses.
    Реализует SCD Type 2 (Slowly Changing Dimension) для отслеживания истории статусов заказов.

    Логика:
        - Если у заказа нет активного статуса → создаем новую запись (is_current = True)
        - Если статус изменился (текст статуса другой) → закрываем старый (is_current = False,
          заполняем status_to) и вставляем новую запись с новым статусом (is_current = True)
        - Если статус не изменился → ничего не делаем
        - При любом изменении статуса обновляем поле status_upd_date в таблице orders
    """

    def __init__(self, session: Session):
        """
        Args:
            session: Сессия SQLAlchemy
        """
        self.session = session

    def upsert(self, records: list[OrdersStatusesTbl]) -> None:
        """
        Сохраняет/обновляет статусы заказов по SCD Type 2.

        Args:
            records: Список новых статусов из API

        Raises:
            IOError: При ошибке сохранения данных
        """
        if not records:
            logger.warning("Нет данных для сохранения в таблицу orders_statuses.")
            return

        logger.info(f"Обработка статусов для {len(records)} заказов")

        try:
            # Находим текущие активные статусы в БД
            order_ids = [r.order_id for r in records]
            current_statuses = {
                row.order_id: row
                for row in self.session.query(OrdersStatusesTbl).filter(
                    OrdersStatusesTbl.order_id.in_(order_ids),
                    OrdersStatusesTbl.is_current == True
                ).all()
            }
            logger.debug(f"Найдено {len(current_statuses)} активных статусов в БД")

            to_update = []      # (старый статус, новый статус)
            to_insert = []      # новые статусы для вставки

            # Анализируем изменения
            for new_status in records:
                current = current_statuses.get(new_status.order_id)

                if not current:
                    # Новый заказ — нет активного статуса
                    to_insert.append(new_status)
                    logger.debug(f"Заказ {new_status.order_id}: новый заказ, создаем статус")
                elif current.order_status != new_status.order_status:
                    # Статус изменился
                    to_update.append((current, new_status))
                    to_insert.append(new_status)
                    logger.debug(f"Заказ {new_status.order_id}: статус изменился '{current.order_status}' → '{new_status.order_status}'")
                # else: статус не изменился — ничего не делаем

            logger.info(f"Статусы: изменений {len(to_update)}, новых заказов {len(to_insert) - len(to_update)}")

            # 1. Закрываем старые статусы и обновляем orders
            for current, new in to_update:
                current.status_to = new.status_from
                current.is_current = False
                current.load_date = date.today()
                self.session.add(current)

                # Обновляем дату статуса в основной таблице заказов
                self.session.query(OrdersTbl).filter(
                    OrdersTbl.order_id == current.order_id
                ).update({"status_upd_date": new.status_from})
                logger.debug(f"Заказ {current.order_id}: закрыт старый статус")

            # 2. Вставляем новые статусы (bulk + защита от дубликатов)
            if to_insert:
                data = [{
                    'order_id': r.order_id,
                    'order_status': r.order_status,
                    'status_from': r.status_from,
                    'status_to': None,
                    'is_current': True,
                    'load_date': date.today(),
                } for r in to_insert]

                stmt = insert(OrdersStatusesTbl).values(data)
                stmt = stmt.on_conflict_do_nothing(
                    index_elements=['order_id', 'status_from']
                )
                self.session.execute(stmt)
                logger.debug(f"Вставлено {len(data)} новых статусов")

            logger.info(f"Статусы успешно сохранены. Обновлено: {len(to_update)}, вставлено: {len(to_insert)}")

        except Exception as e:
            logger.error(f"Ошибка при сохранении статусов: {e}")
            self.session.rollback()
            raise IOError(f"Ошибка при сохранении данных в таблицу orders_statuses: {e}")