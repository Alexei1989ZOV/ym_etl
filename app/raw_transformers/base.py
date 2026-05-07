from abc import ABC, abstractmethod
from pathlib import Path
import pandas as pd
from app.configs.logger_settings import get_logger

logger = get_logger(__name__)

class BaseCSVTransformer(ABC):
    """
    Базовый класс для трансформации CSV-файлов в модели БД.
    Используется для асинхронных отчетов.
    Наследники должны реализовать метод transform().
    """
    def __init__(self, csv_path: Path):
        """
        Args:
            csv_path: Путь к CSV-файлу
        """
        self.csv_path = csv_path

    def read_csv(self) -> pd.DataFrame:
        """
        Читает CSV-файл в pandas DataFrame.
        Returns:
            pd.DataFrame: Данные из CSV
        Raises:
            ValueError: Если файл пуст
        """
        if self.csv_path.stat().st_size == 0:
            logger.error("CSV файл пуст")
            raise ValueError("CSV файл пуст")
        logger.debug(f"CSV файл {self.csv_path} прочитан в DataFrame")
        return pd.read_csv(self.csv_path)

    @abstractmethod
    def transform(self):
        """
        Трансформирует данные из CSV в список объектов моделей БД.
        Returns:
            list: Список объектов моделей
        Raises:
            NotImplementedError: Должен быть реализован в наследнике
        """
        pass
