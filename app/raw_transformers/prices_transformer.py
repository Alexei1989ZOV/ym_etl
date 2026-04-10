from decimal import Decimal
import pandas as pd
from pathlib import Path
from datetime import datetime, timedelta

from app.raw_transformers.base import BaseCSVTransformer
from app.configs.report_configs import TRANSFORM_CONFIGS
from app.storage.models.raw_prices import RawPricesReport



class PricesCSVTransformer(BaseCSVTransformer):
    def __init__(self, csv_path):
        super().__init__(csv_path)
        self.config = TRANSFORM_CONFIGS["prices"]["columns"]

    def transform(self) -> list[RawPricesReport]:
        df = self.read_csv()
        self._validate_columns(df)
        records: list[RawPricesReport] = []

        for _, row in df.iterrows():
            data = {
                "day": self._get_date()
            }

            for csv_col, cfg in self.config.items():
                field = cfg["field_name"]
                value = row.get(csv_col)

                if pd.isna(value):
                    data[field] = None
                    continue

                data[field] = self._cast(value, cfg["type"])

            records.append(RawPricesReport(**data))

        return records

    def _validate_columns(self, df: pd.DataFrame) -> None:
        missing = set(self.config.keys()) - set(df.columns)
        if missing:
            raise ValueError(f"Отсутствуют колонки в CSV: {missing}")

    def _get_date(self):
        name = self.csv_path.stem
        try:
            # Ищем дату в имени CSV (формат: ..._ГГГГ-ММ-ДД_ЧЧММСС.csv)
            # Берем предпоследний элемент после split('_') — это дата
            date = datetime.strptime(name.split('_')[-1], '%Y-%m-%d')
            return date
        except:
            raise ValueError(f"В имени файла не содержится дата: {name}")


    @staticmethod
    def _cast(value, target_type):
        if target_type is Decimal:
            return Decimal(str(value))
        return target_type(value)
