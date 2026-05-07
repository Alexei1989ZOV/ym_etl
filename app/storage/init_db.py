from app.storage.database import engine, Base
from app.storage.models.raw_sales import RawSalesReport
from app.storage.models.raw_stocks import RawStocksReport
from app.storage.models.raw_goods_movement import RawGoodsMovementReport
from app.storage.models.raw_prices import RawPricesReport
from app.storage.models.dim_offers import DimOffersReport, RawDimOffersReport
from app.storage.models.orders_info import OrdersTbl, OrdersStatusesTbl, OrdersCommissionsTbl, OrderItemsTbl, OrderPaymentsTbl, OrdersSubsidiesTbl

print("Using DB:", engine.url)

Base.metadata.create_all(engine)
print("Tables created:", Base.metadata.tables.keys())
