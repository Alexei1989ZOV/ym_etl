from decimal import Decimal
from pathlib import Path
from datetime import datetime, timedelta, date
from app.storage.models.dim_offers import DimOffersReport
from app.stg_transformers.stg_base import BaseJSONtransformer
from app.configs.logger_settings import get_logger

logger = get_logger(__name__)


class OffersJSONTransformer(BaseJSONtransformer):
    """
    Трансформер для ответа API с информацией о товарах (offer mappings).
    Преобразует JSON-ответ от Яндекс Маркета в список моделей DimOffersReport
    для загрузки в справочник товаров.
    """
    def __init__(self, json_data: dict):
        """
        Args:
            json_data: dict - ответ API в формате JSON
        """
        super().__init__(json_data)


    def transform(self) -> list[DimOffersReport]:
        """
        Преобразует ответ API в список моделей для загрузки в БД
        Returns:
            list: список моделей для загрузки в БД.
        Raises:
            IOError: если ответ API пустой
                или отсутствует обязательное поле в заказе
            ValueError: при ошибках извлечения по ключам
        """
        logger.info("Начало трансформации ответа API информации о товарах")
        records_to_insert = []

        if not self.json_data:
            logger.error("Ответ API пустой")
            raise IOError("Ответ API пустой")

        #Извлекаем список с офферами
        offers = self.json_data["result"].get("offerMappings", [])
        logger.debug(f"Загружено {len(offers)} товаров")
        if not offers:
            logger.error("В ответе API нет ключа 'offerMappings'")
            raise ValueError("В ответе API нет ключа 'offerMappings")
        date_today = date.today()
        for record in offers:
            offer = record["offer"]
            weight_dimensions = offer.get('weightDimensions', {})
            mapping = record.get('mapping', {})

            to_result = DimOffersReport(
                offer_id = offer.get("offerId"),
                offer_name = offer.get("name"),
                market_category_id = mapping.get("marketCategoryId"),
                length = weight_dimensions.get("length"),
                width = weight_dimensions.get("width"),
                height = weight_dimensions.get("height"),
                weight = weight_dimensions.get("weight"),
                load_date = date_today
            )
            records_to_insert.append(to_result)
        logger.info(f"Трансформация ответа API информации о товарах завершена. Товаров: {len(records_to_insert)}")
        return records_to_insert




