from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import String, Integer, Date, Float, BIGINT, TIMESTAMP, ForeignKey, Boolean, DECIMAL, \
    PrimaryKeyConstraint
from .base_model import Base
from datetime import date
from datetime import datetime
from sqlalchemy import UniqueConstraint, Index


class OrdersTbl(Base):
    __tablename__ = "orders"
    __table_args__ = {"schema": "orders_info"}

    order_id: Mapped[int] = mapped_column(BIGINT, primary_key=True)
    creation_date: Mapped[date] = mapped_column(Date, nullable=False)
    status_upd_date: Mapped[datetime] = mapped_column(TIMESTAMP, nullable=True)
    payment_type: Mapped[str] = mapped_column(String, nullable=True)
    load_date: Mapped[date] = mapped_column(Date, nullable=False, default=date.today())


class OrdersStatusesTbl(Base):
    __tablename__ = "orders_statuses"
    __table_args__ = {"schema": "orders_info"}

    order_id: Mapped[int] = mapped_column(BIGINT, ForeignKey("orders_info.orders.order_id", ondelete="CASCADE"), primary_key=True)
    order_status: Mapped[str] = mapped_column(String, nullable=False)
    status_from: Mapped[datetime] = mapped_column(TIMESTAMP, nullable=True, primary_key=True)
    status_to: Mapped[datetime] = mapped_column(TIMESTAMP, nullable=True)
    is_current:Mapped[bool] = mapped_column(Boolean, nullable=True)
    load_date: Mapped[date] = mapped_column(Date, nullable=False, default=date.today())


class OrdersCommissionsTbl(Base):
    __tablename__ = "orders_commissions"
    __table_args__ = {"schema": "orders_info"}

    order_id: Mapped[int] = mapped_column(BIGINT, ForeignKey("orders_info.orders.order_id", ondelete="CASCADE"), primary_key=True)
    commission_type: Mapped[str] = mapped_column(String, nullable=False, primary_key=True)
    commission_amount: Mapped[float] = mapped_column(DECIMAL(15, 2), nullable=False)
    load_date: Mapped[date] = mapped_column(Date, nullable=False, default=date.today())


class OrderItemsTbl(Base):
    __tablename__ = "orders_items"
    __table_args__ = {"schema": "orders_info"}

    order_id: Mapped[int] = mapped_column(BIGINT, ForeignKey("orders_info.orders.order_id", ondelete="CASCADE"), primary_key=True)
    shop_sku: Mapped[str] = mapped_column(String, primary_key=True)
    ordered_qt: Mapped[int] = mapped_column(Integer, nullable=False)
    delivered_qt: Mapped[int] = mapped_column(Integer, nullable=False)
    returned_qt: Mapped[int] = mapped_column(Integer, nullable=True)
    rejected_qt: Mapped[int] = mapped_column(Integer, nullable=True)
    seller_price_per_unit: Mapped[float] = mapped_column(DECIMAL(15, 2), nullable=False)
    buyer_price_per_unit: Mapped[float] = mapped_column(DECIMAL(15, 2), nullable=False)
    mp_discount_per_unit: Mapped[float] = mapped_column(DECIMAL(15, 2), nullable=True)
    mp_yandex_plus_discount: Mapped[float] = mapped_column(DECIMAL(15, 2), nullable=True)
    bid_fee: Mapped[int] = mapped_column(Integer, nullable=False)
    warehouse_id: Mapped[int] = mapped_column(Integer, nullable=False)
    load_date: Mapped[date] = mapped_column(Date, nullable=False, default=date.today())


class OrderPaymentsTbl(Base):
    __tablename__ = "orders_payments"
    __table_args__ = (
        Index('ix_payments_order_id', 'order_id'),
        {"schema": "orders_info"}
    )

    order_id: Mapped[int] = mapped_column(BIGINT, ForeignKey("orders_info.orders.order_id", ondelete="CASCADE"),
                                          primary_key=True)
    payment_id: Mapped[str] = mapped_column(String, primary_key=True)
    payment_type: Mapped[str] = mapped_column(String, primary_key=True)
    payment_date: Mapped[date] = mapped_column(Date, nullable=False)
    payment_source: Mapped[str] = mapped_column(String, nullable=True)
    payment_amount: Mapped[float] = mapped_column(DECIMAL(15, 2), nullable=False)
    payment_order_id: Mapped[str] = mapped_column(String, nullable=True)
    payment_order_date: Mapped[date] = mapped_column(Date, nullable=True)
    load_date: Mapped[date] = mapped_column(Date, nullable=False, default=date.today())


class OrdersSubsidiesTbl(Base):
    __tablename__ = "orders_subsidies"
    __table_args__ = (
        Index('ix_subsidies_order_id', 'order_id'),
        {"schema": "orders_info"}
    )

    subsidy_id: Mapped[int] = mapped_column(BIGINT, primary_key=True, autoincrement=True)
    order_id: Mapped[int] = mapped_column(BIGINT, ForeignKey("orders_info.orders.order_id", ondelete="CASCADE"))
    operation_type: Mapped[str] = mapped_column(String, nullable=False)
    subsidy_type: Mapped[str] = mapped_column(String, nullable=True)
    subsidy_amount: Mapped[float] = mapped_column(DECIMAL(15, 2), nullable=False)
    load_date: Mapped[date] = mapped_column(Date, nullable=False, default=date.today())