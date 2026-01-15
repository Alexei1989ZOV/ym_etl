from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import String, Integer, DECIMAL, Date
from .base_model import Base
from datetime import date
from decimal import Decimal


class RawSalesReport(Base):
    __tablename__ = "raw_sales_reports"
    __table_args__ = {"schema": "raw"}


    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)

    day: Mapped[str] = mapped_column(String, nullable=False)
    month: Mapped[str] = mapped_column(String, nullable=False)
    year: Mapped[int] = mapped_column(Integer, nullable=False)

    category_name: Mapped[str | None] = mapped_column(String)
    brand_name: Mapped[str | None] = mapped_column(String)

    offer_id: Mapped[str | None] = mapped_column(String)
    offer_name: Mapped[str | None] = mapped_column(String)

    visibility_index: Mapped[str | None] = mapped_column(String)

    shows: Mapped[int | None] = mapped_column(Integer)
    shows_with_promotion: Mapped[int | None] = mapped_column(Integer)
    shows_share: Mapped[Decimal | None] = mapped_column(DECIMAL(10, 4))

    clicks: Mapped[int | None] = mapped_column(Integer)
    clicks_with_promotion: Mapped[int | None] = mapped_column(Integer)

    to_cart_conversion: Mapped[Decimal | None] = mapped_column(DECIMAL(10, 4))
    to_cart: Mapped[int | None] = mapped_column(Integer)
    to_cart_with_promotion: Mapped[int | None] = mapped_column(Integer)
    to_cart_share: Mapped[Decimal | None] = mapped_column(DECIMAL(10, 4))

    order_items: Mapped[int | None] = mapped_column(Integer)
    order_items_with_promotion: Mapped[int | None] = mapped_column(Integer)

    order_items_total_amount: Mapped[int | None] = mapped_column(Integer)
    order_items_total_amount_with_promotion: Mapped[int | None] = mapped_column(Integer)

    to_order_conversion: Mapped[Decimal | None] = mapped_column(DECIMAL(10, 4))
    order_items_share: Mapped[Decimal | None] = mapped_column(DECIMAL(10, 4))

    order_items_delivered_count: Mapped[int | None] = mapped_column(Integer)
    order_items_delivered_count_with_promotion: Mapped[int | None] = mapped_column(Integer)
    order_items_delivered_total_amount: Mapped[int | None] = mapped_column(Integer)
    order_items_delivered_total_amount_with_promotion: Mapped[int | None] = mapped_column(Integer)
    order_items_delivered_from_ordered_count: Mapped[int | None] = mapped_column(Integer)
    order_items_delivered_from_ordered_total_amount: Mapped[int | None] = mapped_column(Integer)
    order_items_delivered_from_ordered_total_amount_with_promotion: Mapped[int | None] = mapped_column(Integer)


    order_items_canceled_count: Mapped[int | None] = mapped_column(Integer)
    order_items_canceled_by_created_at_count: Mapped[int | None] = mapped_column(Integer)

    order_items_returned_count: Mapped[int | None] = mapped_column(Integer)
    order_items_returned_by_created_at_count: Mapped[int | None] = mapped_column(Integer)