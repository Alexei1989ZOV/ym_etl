from decimal import Decimal
import pandas as pd
from pathlib import Path
from datetime import datetime, timedelta

from app.raw_transformers.base import BaseCSVTransformer
from app.configs.report_configs import TRANSFORM_CONFIGS
from app.storage.models.raw_stocks import RawStocksReport



class StocksCSVTransformer(BaseCSVTransformer):
    def __init__(self, csv_path):
        super().__init__(csv_path)
        self.config = TRANSFORM_CONFIGS["stocks"]["columns"]

    def transform(self) -> list[RawStocksReport]:
        df = self.read_csv()
        self._validate_columns(df)
        records: list[RawStocksReport] = []

        for _, row in df.iterrows():
            data = {
                "day": self._stocks_date()
            }

            for csv_col, cfg in self.config.items():
                field = cfg["field_name"]
                value = row.get(csv_col)

                if pd.isna(value):
                    data[field] = None
                    continue

                data[field] = self._cast(value, cfg["type"])

            records.append(RawStocksReport(**data))

        return records

    def _validate_columns(self, df: pd.DataFrame) -> None:
        missing = set(self.config.keys()) - set(df.columns)
        if missing:
            raise ValueError(f"Отсутствуют колонки в CSV: {missing}")

    def _stocks_date(self):
        name = self.csv_path.stem
        try:
            # Ищем дату в имени CSV (формат: ..._ГГГГ-ММ-ДД_ЧЧММСС.csv)
            # Берем предпоследний элемент после split('_') — это дата
            date = datetime.strptime(name.split('_')[-1], '%Y-%m-%d') - timedelta(days=1)
            return date
        except:
            raise ValueError(f"В имени файла не содержится дата: {name}")

    # app/raw_transformers/stocks_transformer.py

    @staticmethod
    def _cast(value, target_type):
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
