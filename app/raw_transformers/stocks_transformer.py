from decimal import Decimal
import pandas as pd
from pathlib import Path
from datetime import datetime, timedelta
from app.raw_transformers.base import BaseCSVTransformer
from app.configs.report_configs import TRANSFORM_CONFIGS
from app.storage.models.raw_stocks import RawStocksReport
from app.configs.logger_settings import get_logger

logger = get_logger(__name__)



class StocksCSVTransformer(BaseCSVTransformer):
    """
    Трансформер для отчета по остаткам.
    Приводит данные из CSV в необходимые типы для загрузки в БД.
    """
    def __init__(self, csv_path):
       """
       Args:
           csv_path: Путь к CSV-файлу с отчетом по остаткам.
       """
       super().__init__(csv_path)
       self.config = TRANSFORM_CONFIGS["stocks"]["columns"]

    def transform(self) -> list[RawStocksReport]:
        """
        Преобразование CSV в объекты модели.
        Returns:
            список объектов модели RawStocksReport
        """
        logger.info(f"Начало трансформации stocks_report из {self.csv_path.name}")
        df = self.read_csv()
        self._validate_columns(df)
        records: list[RawStocksReport] = []

        for _, row in df.iterrows():
            data = {
                "day": self._extract_date()
            }

            for csv_col, cfg in self.config.items():
                field = cfg["field_name"]
                value = row.get(csv_col)

                if pd.isna(value):
                    data[field] = None
                    continue

                data[field] = self._cast(value, cfg["type"])

            records.append(RawStocksReport(**data))
        logger.info(f"Трансформация stocks_report выполнена. Подготовлено {len(records)} записей")
        return records

    def _validate_columns(self, df: pd.DataFrame) -> None:
        """
        Проверка наличия всех необходимых колонок в CSV
        Args:
            df (pd.DataFrame): DataFrame с данными из CSV
        Raises:
            ValueError: если отсутствуют необходимые колонки
        """
        missing = set(self.config.keys()) - set(df.columns)
        if missing:
            raise ValueError(f"Отсутствуют колонки в CSV: {missing}")

    def _extract_date(self):
        """
        Извлечение даты из имени файла CSV.
        Верная дата в файле CSV гарантируется классом FileManager.
        Returns:
            date: дата из имени файла
        Raises:
            ValueError: Если по каким-либо причинам дата не содержится в имени файла.
        """
        logger.debug(f"Извлечение даты из имени файла: {self.csv_path.name}")
        name = self.csv_path.stem
        try:
            # Ищем дату в имени CSV (формат: ..._ГГГГ-ММ-ДД.csv)
            # Берем предпоследний элемент после split('_') — это дата
            date = datetime.strptime(name.split('_')[-1], '%Y-%m-%d') - timedelta(days=1)
            return date
        except:
            logger.error(f"[stocks] Не удалось извлечь дату из имени файла: {name}")
            raise ValueError(f"В имени файла не содержится дата: {name}")

    @staticmethod
    def _cast(value, target_type):
        """
        Приводит значение к указанному типу с очисткой float.
        Особенности:
            - Преобразует float 110448.0 → int 110448
            - Для Decimal чистит запятые и пробелы
            - Для str приводит без изменений
        Args:
            value: Значение для приведения
            target_type: Целевой тип (Decimal, str, int, float)
        Returns:
            Значение в нужном типе
        """
        # Очищаем float от .0
        if isinstance(value, float):
            if value.is_integer():
                value = int(value)
            else:
                value = str(value).rstrip('0').rstrip('.')

        if target_type is Decimal:
            cleaned = str(value).strip().replace(',', '.')
            return Decimal(cleaned)

        if target_type is str:
            return str(value)

        return target_type(value)
