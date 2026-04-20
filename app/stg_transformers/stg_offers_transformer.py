from decimal import Decimal
from pathlib import Path
from datetime import datetime, timedelta, date
from app.storage.models.dim_offers import DimOffersReport
from app.stg_transformers.stg_base import BaseJSONtransformer



class OffersJSONTransformer(BaseJSONtransformer):
    def __init__(self, json_data: dict):
        super().__init__(json_data)


    def transform(self) -> list[DimOffersReport]:
        records_to_insert = []

        if not self.json_data:
            raise IOError("Ответ API пустой")

        #Извлекаем список с офферами
        offers = self.json_data["result"].get("offerMappings", [])
        if not offers:
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
        return records_to_insert




