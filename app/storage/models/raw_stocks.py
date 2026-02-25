from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import String, Integer, DECIMAL, Date
from .base_model import Base
from datetime import date
from decimal import Decimal


class RawStocksReport(Base):
    __tablename__ = "raw_stocks"



id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
day: Mapped[date] = mapped_column(Date)
shop_sku: Mapped[str | None] = mapped_column(String)
article: Mapped[str | None] = mapped_column(String)
market_sku: Mapped[int | None] = mapped_column(Integer)
product_name: Mapped[str | None] = mapped_column(String)
valid: Mapped[int | None] = mapped_column(Integer)
reserved: Mapped[int | None] = mapped_column(Integer)
available_for_order: Mapped[int | None] = mapped_column(Integer)
quarantine: Mapped[int | None] = mapped_column(Integer)
utilization: Mapped[int | None] = mapped_column(Integer)
defect: Mapped[int | None] = mapped_column(Integer)
expired: Mapped[int | None] = mapped_column(Integer)
length: Mapped[int | None] = mapped_column(Integer)
width: Mapped[int | None] = mapped_column(Integer)
height: Mapped[int | None] = mapped_column(Integer)
weight: Mapped[Decimal | None] = mapped_column(DECIMAL(10, 4))
warehouse: Mapped[str | None] = mapped_column(String)
selling_status: Mapped[str | None] = mapped_column(String)
recommendations: Mapped[str | None] = mapped_column(String)
turnover: Mapped[str | None] = mapped_column(String)
