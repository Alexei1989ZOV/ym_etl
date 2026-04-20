from abc import ABC, abstractmethod


class BaseJSONtransformer(ABC):

    def __init__(self, json_data: dict):
        self.json_data = json_data

    @abstractmethod
    def transform(self):
        pass