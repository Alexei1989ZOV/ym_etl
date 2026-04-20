from datetime import date
from sqlalchemy.orm import Session
from app.reports.offers import DimOffersReport
from app.core.pipeline import ReportPipeline
from app.stg_transformers.stg_offers_transformer import OffersJSONTransformer
from app.storage.repositories.dim_offers_repository import DimOffersRepository
from app.storage.repositories.raw_offers_repository import RawOffersRepository  # новый


class OffersETLPipeline:
    def __init__(self, session: Session, report_pipeline: ReportPipeline):
        self.session = session
        self.report_pipeline = report_pipeline
        self.raw_repo = RawOffersRepository(session)  # ← для сырых данных
        self.dim_repo = DimOffersRepository(session)  # ← для чистых

    def run(self, report_date: date) -> None:
        # 1. Получаем данные из API
        report = DimOffersReport()
        data = self.report_pipeline.api_client.get_offer_mappings(report)

        # 2. Сохраняем сырой ответ (для истории/отладки)
        self.raw_repo.insert(data)
        print(f"[RAW] Сохранен сырой ответ API")

        # 3. Трансформируем и сохраняем в витрину
        transformer = OffersJSONTransformer(data)
        records = transformer.transform()

        if not records:
            print("[OFFERS] Нет данных для загрузки")
            return

        self.dim_repo.upsert(records)
        print(f"[DIM] Загружено/обновлено {len(records)} товаров")