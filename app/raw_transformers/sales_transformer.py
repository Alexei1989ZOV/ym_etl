from decimal import Decimal
import pandas as pd

from app.raw_transformers.base import BaseCSVTransformer
from app.configs.report_configs import TRANSFORM_CONFIGS
from app.storage.models.raw_sales import RawSalesReport


class SalesCSVTransformer(BaseCSVTransformer):
    def __init__(self, csv_path):
        super().__init__(csv_path)
        self.config = TRANSFORM_CONFIGS["sales"]["columns"]

    def transform(self) -> list[RawSalesReport]:
        df = self.read_csv()

        self._validate_columns(df)

        records: list[RawSalesReport] = []

        for _, row in df.iterrows():
            data = {}

            for csv_col, cfg in self.config.items():
                field = cfg["field_name"]
                value = row.get(csv_col)

                if pd.isna(value):
                    data[field] = None
                    continue

                data[field] = self._cast(value, cfg["type"])

            records.append(RawSalesReport(**data))

        return records

    def _validate_columns(self, df: pd.DataFrame) -> None:
        missing = set(self.config.keys()) - set(df.columns)
        if missing:
            raise ValueError(f"Отсутствуют колонки в CSV: {missing}")

    @staticmethod
    def _cast(value, target_type):
        if target_type is Decimal:
            return Decimal(str(value))
        return target_type(value)