from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field


class Settings(BaseSettings):
    api_key: str = Field(..., alias="YANDEX_API_KEY", min_length=50, description="API ключ Яндекс Маркета")
    business_id: int = Field(..., alias="YANDEX_BUSINESS_ID")
    campaign_id: int = Field(..., alias="YANDEX_CAMPAIGN_ID")

    db_url: str = Field(..., alias="DB_DSN")

    temp_dir: str = Field("./data/raw", alias="TEMP_DIR")
    reports_dir: str = Field("./data/processed", alias="REPORTS_DIR")

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore"
    )


settings = Settings()
