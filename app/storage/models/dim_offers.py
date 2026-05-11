from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import String, Integer, Date, Float, JSON, DECIMAL
from .base_model import Base
from datetime import date
from datetime import datetime
from sqlalchemy import UniqueConstraint
from decimal import Decimal


class DimOffersReport(Base):
    __tablename__ = "dim_offers"
    __table_args__ = {"schema": "catalog_mp"}

    offer_id: Mapped[int] = mapped_column(Integer, primary_key=True)
    offer_name: Mapped[str] = mapped_column(String, nullable=False)
    market_category_id: Mapped[int] = mapped_column(Integer, nullable=True)
    length: Mapped[Decimal] = mapped_column(DECIMAL(9, 2), nullable=True)
    width: Mapped[Decimal] = mapped_column(DECIMAL(9, 2), nullable=True)
    height: Mapped[Decimal] = mapped_column(DECIMAL(9, 2), nullable=True)
    weight: Mapped[Decimal] = mapped_column(DECIMAL(9, 2), nullable=True)
    report_date: Mapped[date] = mapped_column(Date, nullable=False, default=date.today())


class RawDimOffersReport(Base):
    __tablename__ = "raw_offers"
    __table_args__ = (
        UniqueConstraint('report_date', name='uq_raw_offers_report_date'),
        {"schema": "raw"}
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    report_date: Mapped[date] = mapped_column(Date, default=date.today())
    data: Mapped[dict] = mapped_column(JSON)