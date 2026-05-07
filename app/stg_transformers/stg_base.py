from abc import ABC, abstractmethod


class BaseJSONtransformer(ABC):
    """
    Базовый класс для трансформации JSON ответов в модели БД.
    Используется для синхронных отчетов.
    Наследники должны реализовать метод transform().
    """

    def __init__(self, json_data: dict):
        """
        Args:
            json_data: Ответ API в формате JSON (dict)
        """
        self.json_data = json_data

    @abstractmethod
    def transform(self):
        """
        Трансформирует данные из JSON в словарь таблиц для загрузки в БД.
        Returns:
            dict: Словарь объектов моделей (обычно по таблицам)
        Raises:
            NotImplementedError: Должен быть реализован в наследнике
        """
        pass