from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import String, Integer, Date
from .base_model import Base
from datetime import date



class RawPricesReport(Base):
    __tablename__ = "raw_prices"
    __table_args__ = {"schema": "raw"}

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    day: Mapped[date] = mapped_column(Date)
    errors: Mapped[str] = mapped_column(String, nullable=True)
    warnings: Mapped[str] = mapped_column(String, nullable=True)
    offer_id: Mapped[str] = mapped_column(String, nullable=False)
    offer_name: Mapped[str] = mapped_column(String, nullable=True)
    basic_price: Mapped[int] = mapped_column(Integer, nullable=True)
    basic_discount_base: Mapped[int] = mapped_column(Integer, nullable=True)
    currency: Mapped[str] = mapped_column(String, nullable=True)
    minimum_for_bestseller: Mapped[int] = mapped_column(Integer, nullable=True)
    cost_price: Mapped[int] = mapped_column(Integer, nullable=True)
    additional_expenses: Mapped[int] = mapped_column(Integer, nullable=True)
    on_display: Mapped[int] = mapped_column(Integer, nullable=True)
    price_green_threshold: Mapped[int] = mapped_column(Integer, nullable=True)
    price_red_threshold: Mapped[int] = mapped_column(Integer, nullable=True)
    minimum_price_on_marketplaces: Mapped[int] = mapped_column(Integer, nullable=True)
    marketplace_with_best_price: Mapped[str] = mapped_column(String, nullable=True)
    price_value_outside_market: Mapped[int] = mapped_column(Integer, nullable=True)
    shop_with_best_price_on_market: Mapped[str] = mapped_column(String, nullable=True)
    price_value_on_market: Mapped[int] = mapped_column(Integer, nullable=True)