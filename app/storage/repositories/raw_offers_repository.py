from sqlalchemy.orm import Session
from app.storage.models.dim_offers import RawDimOffersReport
from sqlalchemy.dialects.postgresql import insert
from datetime import date


class RawOffersRepository:
    def __init__(self, session: Session):
        self.session = session

    def insert(self, data: dict) -> None:
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
        self.session.commit()