import logging
import sys
from pathlib import Path
from logging.handlers import RotatingFileHandler
from app.configs.settings import settings


def setup_logging():
    """Настройка логгера для всего приложения"""
    # Защита от повторной настройки
    root_logger = logging.getLogger()
    if root_logger.handlers:
        return

    # Создаем папку для логов
    log_dir = Path("logs")
    log_dir.mkdir(exist_ok=True)

    # Уровень логирования из настроек
    log_level = getattr(logging, settings.log_level.upper(), logging.INFO)

    # Форматтер
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )

    # Хендлер для основного лога (с ротацией)
    file_handler = RotatingFileHandler(
        log_dir / "yandex_market_api.log",
        maxBytes=10_485_760,  # 10 MB
        backupCount=5,
        encoding='utf-8'
    )
    file_handler.setFormatter(formatter)
    file_handler.setLevel(log_level)

    # Хендлер для ошибок
    error_handler = RotatingFileHandler(
        log_dir / "errors.log",
        maxBytes=10_485_760,
        backupCount=5,
        encoding='utf-8'
    )
    error_handler.setLevel(logging.ERROR)
    error_handler.setFormatter(formatter)

    # Хендлер для консоли
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(formatter)
    console_handler.setLevel(log_level)

    # Корневой логгер
    root_logger.setLevel(log_level)
    root_logger.addHandler(file_handler)
    root_logger.addHandler(error_handler)
    root_logger.addHandler(console_handler)


def get_logger(name: str) -> logging.Logger:
    """Получить именованный логгер"""
    return logging.getLogger(name)