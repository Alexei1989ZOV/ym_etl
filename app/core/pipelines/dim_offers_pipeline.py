from datetime import date
from sqlalchemy.orm import Session
from app.reports.offers import DimOffersReport
from app.api.report_client import ReportAPIClient
from app.stg_transformers.stg_offers_transformer import OffersJSONTransformer
from app.storage.repositories.dim_offers_repository import DimOffersRepository
from app.storage.repositories.raw_offers_repository import RawOffersRepository  # новый
from app.configs.logger_settings import get_logger

logger = get_logger(__name__)

class OffersETLPipeline:
    """
    ETL pipeline для получения каталога товаров с информацией о товарах.
    """
    def __init__(self, session: Session, api_client: ReportAPIClient):
        """
        Args:
            session: Сессия SQLAlchemy для работы с базой данных
            api_client: Объект ReportAPIClient для доступа к API
        """
        self.session = session
        self.api_client = api_client
        self.raw_repo = RawOffersRepository(session)
        self.dim_repo = DimOffersRepository(session)

    def run(self, report_date: date) -> None:
        """
        Загружает справочник товаров из API Яндекс.Маркета и сохраняет в БД.
        Процесс:
            1. Получает данные из API (offer mappings)
            2. Сохраняет сырой JSON в таблицу raw_offers (для истории/отладки)
            3. Трансформирует JSON в модели DimOffersReport
            4. Сохраняет (обновляет) данные в таблицу dim_offers (справочник товаров)
        Args:
            report_date: Дата запуска (используется для логирования)
        Note:
            Справочник обновляется полностью (upsert по offer_id).
            Данные загружаются синхронно через API (пагинация).
        """
        logger.info("[OFFERS] Начало загрузки справочника товаров")

        try:
            report = DimOffersReport()
            data = self.api_client.get_offer_mappings(report)

            self.raw_repo.insert(data)
            logger.info("[RAW OFFERS] Сохранен сырой ответ API")

            transformer = OffersJSONTransformer(data)
            records = transformer.transform()
            logger.debug("[RAW OFFERS] Трансформация завершена, получено {len(records)} записей")

            if not records:
                logger.warning("[OFFERS] Нет данных для загрузки")
                return

            self.dim_repo.upsert(records)
            self.session.commit()
            logger.info(f"[DIM OFFERS] Загружено/обновлено {len(records)} товаров")

        except Exception as e:
            self.session.rollback()
            logger.error(f"[OFFERS] Ошибка при загрузке: {e}")
            raise