from abc import ABC, abstractmethod
from pathlib import Path
import pandas as pd


class BaseCSVTransformer(ABC):
    def __init__(self, csv_path: Path):
        self.csv_path = csv_path

    def read_csv(self) -> pd.DataFrame:
        if self.csv_path.stat().st_size == 0:
            raise ValueError("CSV файл пуст")

        return pd.read_csv(self.csv_path)

    @abstractmethod
    def transform(self):
        pass
