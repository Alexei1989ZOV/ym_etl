from pathlib import Path
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field

BASE_DIR = Path(__file__).resolve().parents[2]  # C:\ym_etl
DB_FILE = BASE_DIR / "test_yandex_market.db"  # один файл для всех

print("Using DB:", DB_FILE)

class Settings(BaseSettings):
    api_key: str = Field(..., alias="YANDEX_API_KEY")
    business_id: int = Field(..., alias="YANDEX_BUSINESS_ID")
    campaign_id: int = Field(..., alias="YANDEX_CAMPAIGN_ID")

    database_url: str = Field(f"sqlite:///{DB_FILE}", alias="DB_DSN")

    temp_dir: str = Field(str(BASE_DIR / "data" / "raw"), alias="TEMP_DIR")
    reports_dir: str = Field(str(BASE_DIR / "data" / "processed"), alias="REPORTS_DIR")

    model_config = SettingsConfigDict(
        env_file=BASE_DIR / ".env",
        env_file_encoding="utf-8",
        extra="ignore"
    )

settings = Settings()
