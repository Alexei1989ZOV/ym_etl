from sqlalchemy.orm import Session
from typing import Iterable
from app.storage.models.dim_offers import DimOffersReport
from datetime import date
from sqlalchemy.dialects.postgresql import insert
from app.configs.logger_settings import get_logger

logger = get_logger(__name__)

class DimOffersRepository:
    """
    Репозиторий для работы с таблицей dim_offers.
    Отвечает за сохранение/обновление данных.
    """
    def __init__(self, session: Session):
        """
        Args:
            session: Сессия SQLAlchemy
        """
        self.session = session

    def upsert(self, records: Iterable[DimOffersReport]) -> None:
        """
        Сохраняет/обновляет данные в таблицу dim_offers.
        Args:
            records: Список объектов DimOffersReport.
        Raises:
            IOError при ошибке сохранения данных.
        """
        if not records:
            logger.warning("Нет данных для сохранения в таблицу dim_offers.")
            return

        values_list = []
        logger.debug("Сохранение данных в таблицу dim_offers.")
        for r in records:
            values_list.append({
                'offer_id': r.offer_id,
                'offer_name': r.offer_name,
                'market_category_id': r.market_category_id,
                'length': r.length,
                'width': r.width,
                'height': r.height,
                'weight': r.weight,
                'report_date': r.report_date,
            })

        try:
            stmt = insert(DimOffersReport).values(values_list)
            stmt = stmt.on_conflict_do_update(
                index_elements=['offer_id'],
                set_={
                    'offer_name': stmt.excluded.offer_name,
                    'market_category_id': stmt.excluded.market_category_id,
                    'length': stmt.excluded.length,
                    'width': stmt.excluded.width,
                    'height': stmt.excluded.height,
                    'weight': stmt.excluded.weight,
                    'report_date': stmt.excluded.report_date,
                }
            )
            self.session.execute(stmt)
            logger.debug(f"Данные успешно сохранены в таблицу dim_offers. Количество записей: {len(values_list)}")
        except Exception as e:
            logger.error(f"Ошибка при сохранении данных в таблицу dim_offers")
            self.session.rollback()
            raise IOError(f"Ошибка при сохранении данных в таблицу dim_offers: {e}")