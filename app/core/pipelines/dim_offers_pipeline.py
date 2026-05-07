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
        self.raw_repo = RawOffersRepository(session)  # ← для сырых данных
        self.dim_repo = DimOffersRepository(session)  # ← для чистых

    def run(self, report_date: date) -> None:
        """
        Загружает справочник товаров из API и сохраняет в БД.
        Процесс:
            1. Получает данные из API Яндекс.Маркета
            2. Сохраняет сырой JSON в raw_offers
            3. Трансформирует JSON в модели dim_offers
            4. Сохраняет (обновляет) данные в dim_offers
        Args:
            report_date: Дата запуска (используется для логирования)
        """
        logger.info(f"[OFFERS] Начало загрузки справочника товаров")
        # 1. Получаем данные из API
        report = DimOffersReport()
        data = self.api_client.get_offer_mappings(report)

        # 2. Сохраняем сырой ответ (для истории/отладки)
        self.raw_repo.insert(data)
        logger.info(f"[RAW OFFERS] Сохранен сырой ответ API")

        # 3. Трансформируем и сохраняем в витрину
        transformer = OffersJSONTransformer(data)
        records = transformer.transform()
        logger.debug(f"[RAW OFFERS] Трансформация завершена, получено {len(records)} записей")

        if not records:
            logger.warning("[OFFERS] Нет данных для загрузки")
            return

        self.dim_repo.upsert(records)
        self.session.commit()
        logger.info(f"[DIM OFFERS] Загружено/обновлено {len(records)} товаров")