from sqlalchemy.orm import Session
from typing import Iterable
from app.storage.models.dim_offers import DimOffersReport
from datetime import date
from sqlalchemy.dialects.postgresql import insert



class DimOffersRepository:
    def __init__(self, session: Session):
        self.session = session

    def upsert(self, records: Iterable[DimOffersReport]) -> None:
        if not records:
            return

        values_list = []
        for r in records:
            values_list.append({
                'offer_id': r.offer_id,
                'offer_name': r.offer_name,
                'market_category_id': r.market_category_id,
                'length': r.length,
                'width': r.width,
                'height': r.height,
                'weight': r.weight,
                'load_date': r.load_date,
            })


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
                'load_date': stmt.excluded.load_date,
            }
        )
        self.session.execute(stmt)
        self.session.commit()