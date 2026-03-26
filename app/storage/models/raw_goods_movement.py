from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import String, Integer, Date
from .base_model import Base
from datetime import date



class RawGoodsMovementReport(Base):
    __tablename__ = "raw_goods_movement"


    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    day: Mapped[date] = mapped_column(Date)
    shop_sku: Mapped[str] = mapped_column(String)
    sku_name: Mapped[str | None] = mapped_column(String)
    shipments_income: Mapped[int | None] = mapped_column(Integer)
    returns_income: Mapped[int | None] = mapped_column(Integer)
    inventory_surplus: Mapped[int | None] = mapped_column(Integer)
    orders_outcome: Mapped[int | None] = mapped_column(Integer)
    warehouse_withdrawal: Mapped[int | None] = mapped_column(Integer)
    recycling: Mapped[int | None] = mapped_column(Integer)
    inventory_shortage: Mapped[int | None] = mapped_column(Integer)
    warehouse_name: Mapped[str] = mapped_column(String)
