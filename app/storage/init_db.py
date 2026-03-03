# app/storage/init_db.py
from app.storage.database import engine, Base
from app.storage.models.raw_sales import RawSalesReport  # <- обязательно импортировать модели
from app.storage.models.raw_stocks import RawStocksReport

print("Using DB:", engine.url)

Base.metadata.create_all(engine)
print("Tables created:", Base.metadata.tables.keys())
