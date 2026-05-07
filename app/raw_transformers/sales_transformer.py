from decimal import Decimal
import pandas as pd
from app.raw_transformers.base import BaseCSVTransformer
from app.configs.report_configs import TRANSFORM_CONFIGS
from app.storage.models.raw_sales import RawSalesReport
from app.configs.logger_settings import get_logger

logger = get_logger(__name__)


class SalesCSVTransformer(BaseCSVTransformer):
    """
    Трансформер для отчета аналитика продаж.
    Приводит данные из CSV в необходимые типы для загрузки в БД.
    """
    def __init__(self, csv_path):
        """
        Args:
            csv_path: Путь к CSV-файлу с отчетом аналитика продаж.
        """
        super().__init__(csv_path)
        self.config = TRANSFORM_CONFIGS["sales"]["columns"]

    def transform(self) -> list[RawSalesReport]:
        """
        Преобразование CSV в объекты модели.
        Returns:
            список объектов модели RawSalesReport
        """
        logger.info(f"Начало трансформации sales_report из {self.csv_path.name}")
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
        logger.info(f"Трансформация sales_report выполнена. Подготовлено {len(records)} записей")
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
            logger.error(f"[sales_report] Отсутствуют необходимые колонки в CSV: {missing}")
            raise ValueError(f"Отсутствуют колонки в CSV: {missing}")

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
