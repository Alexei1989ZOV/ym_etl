from decimal import Decimal

TRANSFORM_CONFIGS = {
    "sales": {
        "columns": {
            "DAY": {"field_name": "day", "type": str, "nullable": False},
            "MONTH": {"field_name": "month", "type": str, "nullable": False},
            "YEAR": {"field_name": "year", "type": int, "nullable": False},
            "CATEGORY_NAME": {"field_name": "category_name", "type": str, "nullable": True},
            "BRAND_NAME": {"field_name": "brand_name", "type": str, "nullable": True},
            "OFFER_ID": {"field_name": "offer_id", "type": str, "nullable": False},
            "OFFER_NAME": {"field_name": "offer_name", "type": str, "nullable": True},
            "VISIBILITY_INDEX": {"field_name": "visibility_index", "type": str, "nullable": True},
            "SHOWS": {"field_name": "shows", "type": int, "nullable": True},
            "SHOWS_WITH_PROMOTION": {"field_name": "shows_with_promotion", "type": int, "nullable": True},
            "SHOWS_SHARE": {"field_name": "shows_share", "type": Decimal, "nullable": True},
            "CLICKS": {"field_name": "clicks", "type": int, "nullable": True},
            "CLICKS_WITH_PROMOTION": {"field_name": "clicks_with_promotion", "type": int, "nullable": True},
            "TO_CART_CONVERSION": {"field_name": "to_cart_conversion", "type": Decimal, "nullable": True},
            "TO_CART": {"field_name": "to_cart", "type": int, "nullable": True},
            "TO_CART_WITH_PROMOTION": {"field_name": "to_cart_with_promotion", "type": int, "nullable": True},
            "TO_CART_SHARE": {"field_name": "to_cart_share", "type": Decimal, "nullable": True},
            "ORDER_ITEMS": {"field_name": "order_items", "type": int, "nullable": True},
            "ORDER_ITEMS_WITH_PROMOTION": {"field_name": "order_items_with_promotion", "type": int, "nullable": True},
            "ORDER_ITEMS_TOTAL_AMOUNT": {"field_name": "order_items_total_amount", "type": int, "nullable": True},
            "ORDER_ITEMS_TOTAL_AMOUNT_WITH_PROMOTION": {"field_name": "order_items_total_amount_with_promotion", "type": int, "nullable": True},
            "TO_ORDER_CONVERSION": {"field_name": "to_order_conversion", "type": Decimal, "nullable": True},
            "ORDER_ITEMS_SHARE": {"field_name": "order_items_share", "type": Decimal, "nullable": True},
            "ORDER_ITEMS_DELIVERED_COUNT": {"field_name": "order_items_delivered_count", "type": int, "nullable": True},
            "ORDER_ITEMS_DELIVERED_COUNT_WITH_PROMOTION": {"field_name": "order_items_delivered_count_with_promotion", "type": int, "nullable": True},
            "ORDER_ITEMS_DELIVERED_TOTAL_AMOUNT": {"field_name": "order_items_delivered_total_amount", "type": int, "nullable": True},
            "ORDER_ITEMS_DELIVERED_TOTAL_AMOUNT_WITH_PROMOTION": {"field_name": "order_items_delivered_total_amount_with_promotion", "type": int, "nullable": True},
            "ORDER_ITEMS_DELIVERED_FROM_ORDERED_COUNT": {"field_name": "order_items_delivered_from_ordered_count", "type": int, "nullable": True},
            "ORDER_ITEMS_DELIVERED_FROM_ORDERED_TOTAL_AMOUNT": {"field_name": "order_items_delivered_from_ordered_total_amount", "type": int, "nullable": True},
            "ORDER_ITEMS_DELIVERED_FROM_ORDERED_TOTAL_AMOUNT_WITH_PROMOTION": {"field_name": "order_items_delivered_from_ordered_total_amount_with_promotion", "type": int, "nullable": True},
            "ORDER_ITEMS_CANCELED_COUNT": {"field_name": "order_items_canceled_count", "type": int, "nullable": True},
            "ORDER_ITEMS_CANCELED_BY_CREATED_AT_COUNT": {"field_name": "order_items_canceled_by_created_at_count", "type": int, "nullable": True},
            "ORDER_ITEMS_RETURNED_COUNT": {"field_name": "order_items_returned_count", "type": int, "nullable": True},
            "ORDER_ITEMS_RETURNED_BY_CREATED_AT_COUNT": {"field_name": "order_items_returned_by_created_at_count", "type": int, "nullable": True}
        },
    },
    "stocks": {
        "columns": {
            "SHOP_SKU" : {"field_name": "shop_sku", "type": str, "nullable": False},
            "ARTICLE": {"field_name": "article", "type": str, "nullable": True},
            "MARKET_SKU": {"field_name": "market_sku", "type": int, "nullable": True},
            "PRODUCT_NAME": {"field_name": "product_name", "type": str, "nullable": True},
            "VALID": {"field_name": "valid", "type": int, "nullable": False},
            "RESERVED": {"field_name": "reserved", "type": int, "nullable": False},
            "AVAILABLE_FOR_ORDER" : {"field_name": "available_for_order", "type": int, "nullable": False},
            "QUARANTINE": {"field_name": "quarantine", "type": int, "nullable": False},
            "UTILIZATION": {"field_name": "utilization", "type": int, "nullable": False},
            "DEFECT": {"field_name": "defect", "type": int, "nullable": False},
            "EXPIRED": {"field_name": "expired", "type": int, "nullable": False},
            "LENGTH": {"field_name": "length", "type": int, "nullable": False},
            "WIDTH": {"field_name": "width", "type": int, "nullable": False},
            "HEIGHT": {"field_name": "height", "type": int, "nullable": False},
            "WEIGHT": {"field_name": "weight", "type": Decimal, "nullable": False},
            "WAREHOUSE": {"field_name": "warehouse", "type": str, "nullable": True},
            "SELLING_STATUS": {"field_name": "selling_status", "type": str, "nullable": True},
            "RECOMMENDATIONS": {"field_name": "recommendations", "type": str, "nullable": True},
            "TURNOVER": {"field_name": "turnover", "type": str, "nullable": False}
        }
    },
    "goods_movement": {
        "columns": {
            "SHOP_SKU": {"field_name": "shop_sku", "type": str, "nullable": False},
            "SKU_NAME": {"field_name": "sku_name", "type": str, "nullable": True},
            "SHIPMENTS_INCOME": {"field_name": "shipments_income", "type": int, "nullable": True},
            "RETURNS_INCOME": {"field_name": "returns_income", "type": int, "nullable": True},
            "INVENTORY_SURPLUS": {"field_name": "inventory_surplus", "type": int, "nullable": True},
            "ORDERS_OUTCOME": {"field_name": "orders_outcome", "type": int, "nullable": True},
            "WAREHOUSE_WITHDRAWAL": {"field_name": "warehouse_withdrawal", "type": int, "nullable": True},
            "RECYCLING": {"field_name": "recycling", "type": int, "nullable": True},
            "INVENTORY_SHORTAGE": {"field_name": "inventory_shortage", "type": int, "nullable": True},
            "WAREHOUSE_NAME": {"field_name": "warehouse_name", "type": str, "nullable": True}
        }
    },
    "prices": {
        "columns": {
            "ERRORS": {"field_name": "errors", "type": str, "nullable": True},
            "WARNINGS": {"field_name": "warnings", "type": str, "nullable": True},
            "OFFER_ID": {"field_name": "offer_id", "type": str, "nullable": False},
            "OFFER_NAME": {"field_name": "offer_name", "type": str, "nullable": True},
            "BASIC_PRICE": {"field_name": "basic_price", "type": int, "nullable": True},
            "BASIC_DISCOUNT_BASE": {"field_name": "basic_discount_base", "type": int, "nullable": True},
            #"CURRENCY": {"field_name": "currency", "type": str, "nullable": True}, В документации есть, а в csv нет
            "MINIMUM_FOR_BESTSELLER": {"field_name": "minimum_for_bestseller", "type": int, "nullable": True},
            "COST_PRICE": {"field_name": "cost_price", "type": int, "nullable": True},
            "ADDITIONAL_EXPENSES": {"field_name": "additional_expenses", "type": int, "nullable": True},
            "ON_DISPLAY": {"field_name": "on_display", "type": int, "nullable": True},# В документации тут почему-то Str
            "PRICE_GREEN_THRESHOLD": {"field_name": "price_green_threshold", "type": int, "nullable": True},
            "PRICE_RED_THRESHOLD": {"field_name": "price_red_threshold", "type": int, "nullable": True},
            "MINIMUM_PRICE_ON_MARKETPLACES": {"field_name": "minimum_price_on_marketplaces", "type": int, "nullable": True},
            "MARKETPLACE_WITH_BEST_PRICE_WITHOUT_MARKET": {"field_name": "marketplace_with_best_price", "type": str, "nullable": True},
            "PRICE_VALUE_OUTSIDE_MARKET": {"field_name": "price_value_outside_market", "type": int, "nullable": True},
            "SHOP_WITH_BEST_PRICE_ON_MARKET": {"field_name": "shop_with_best_price_on_market", "type": str, "nullable": True},
            "PRICE_VALUE_ON_MARKET": {"field_name": "price_value_on_market", "type": int, "nullable": True}
        }
    }
}