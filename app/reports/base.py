from abc import ABC, abstractmethod
from typing import Any

class BaseReport(ABC):
    endpoint: str
    report_type: str

    requires_business_id: bool = False
    requires_campaign_id: bool = False


    @abstractmethod
    def build_request(self, **kwargs) -> dict[str, Any]:
        """
       Формирует данные для HTTP-запроса генерации отчета:
       {
           "params": {...},
           "json": {...}
       }
        """
        pass