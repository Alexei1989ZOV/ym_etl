from sqlalchemy.orm import Session
from app.storage.models.dim_offers import RawDimOffersReport
from sqlalchemy.dialects.postgresql import insert
from datetime import date
from app.configs.logger_settings import get_logger

logger = get_logger(__name__)

class RawOffersRepository:
    """
    Репозиторий для работы с таблицей raw_offers.
    Отвечает за работу с БД.
    Отчет по движению товаров.
    """
    def __init__(self, session: Session):
        """
        Args:
            session: Сессия SQLAlchemy
        """
        self.session = session

    def insert(self, data: dict) -> None:
        """
        Сохраняет/обновляет данные в таблицу raw_offers
        по первичному ключу 'loaded_at'.
        Если запись существует — полностью обновляет данные за дату.
        Args:
            data: JSON ответ API.
        Raises:
            IOError: при ошибке сохранения данных.
        """
        if not data:
            logger.warning("Нет данных для сохранения в таблицу raw_offers.")
            return
        try:
            logger.debug("Сохраняем данные в таблицу raw_offers")
            stmt = insert(RawDimOffersReport).values(
                loaded_at=date.today(),
                data=data
            )
            # Если запись за сегодня уже есть — обновляем data
            stmt = stmt.on_conflict_do_update(
                constraint='uq_raw_offers_loaded_at',  # имя уникального ограничения
                set_={'data': data}
            )
            self.session.execute(stmt)
            logger.debug("Данные успешно сохранены в таблицу raw_offers.")
        except Exception as e:
            logger.error(f"Ошибка при сохранении/обновлении данных в таблице raw_offers за {date.today()}.")
            self.session.rollback()
            raise IOError(f"Ошибка при сохранении/обновлении данных в таблице raw_offers за {date.today()}: {e}")