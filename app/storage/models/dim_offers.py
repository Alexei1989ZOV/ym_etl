from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import String, Integer, Date, Float, JSON
from .base_model import Base
from datetime import date
from datetime import datetime
from sqlalchemy import UniqueConstraint


class DimOffersReport(Base):
    __tablename__ = "dim_offers"
    __table_args__ = {"schema": "orders_info"}

    offer_id: Mapped[str] = mapped_column(String, primary_key=True)
    offer_name: Mapped[str] = mapped_column(String, nullable=False)
    market_category_id: Mapped[int] = mapped_column(Integer, nullable=True)
    length: Mapped[float] = mapped_column(Float, nullable=True)
    width: Mapped[float] = mapped_column(Float, nullable=True)
    height: Mapped[float] = mapped_column(Float, nullable=True)
    weight: Mapped[float] = mapped_column(Float, nullable=True)
    load_date: Mapped[date] = mapped_column(Date, nullable=False, default=date.today())


class RawDimOffersReport(Base):
    __tablename__ = "raw_offers"
    __table_args__ = (
        UniqueConstraint('loaded_at', name='uq_raw_offers_loaded_at'),
        {"schema": "raw"}
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    loaded_at: Mapped[date] = mapped_column(Date, default=date.today())
    data: Mapped[dict] = mapped_column(JSON)