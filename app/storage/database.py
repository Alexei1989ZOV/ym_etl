# app/storage/database.py
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.configs.settings import settings
from app.storage.models.base_model import Base

engine = create_engine(
    settings.database_url,
    echo=False,  # можно True для дебага
    pool_pre_ping=True,
)

SessionLocal = sessionmaker(
    bind=engine,
    autoflush=False,
    autocommit=False,
)
