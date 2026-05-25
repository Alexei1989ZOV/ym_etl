from pathlib import Path
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field, SecretStr

BASE_DIR = Path(__file__).resolve().parents[2]  # C:\ym_etl

class Settings(BaseSettings):
    # Данные для авторизации
    api_key: SecretStr = Field(..., alias="YM_API_KEY")
    business_id: int = Field(..., alias="YM_BUSINESS_ID")
    campaign_id: int = Field(..., alias="YM_CAMPAIGN_ID")
    
    # Работа с файлами проекта    
    temp_dir: str = Field(str(BASE_DIR / "data" / "raw"), alias="TEMP_DIR")
    reports_dir: str = Field(str(BASE_DIR / "data" / "processed"), alias="REPORTS_DIR")

    # Логирование
    log_level: str = Field("INFO", alias="LOG_LEVEL")
    
    # Работа с БД
    db_name: str = Field(..., alias="DB_NAME")
    db_host: str = Field(..., alias="DB_HOST")
    db_port: int = Field(5432, alias="DB_PORT")
    db_user: str = Field(..., alias="DB_USER")
    db_password: SecretStr = Field(..., alias="DB_PASSWORD")    
    
    model_config = SettingsConfigDict(
        env_file=BASE_DIR / ".env",
        env_file_encoding="utf-8",
        extra="ignore"
    )
    
    @property
    def db_url(self) -> str:
        """Формирует URL для подключения к PostgreSQL через psycopg2."""
        password = self.db_password.get_secret_value() 
        return (
            f"postgresql+psycopg2://"
            f"{self.db_user}:{password}@"
            f"{self.db_host}:{self.db_port}/"
            f"{self.db_name}"
        )
        

settings = Settings()
