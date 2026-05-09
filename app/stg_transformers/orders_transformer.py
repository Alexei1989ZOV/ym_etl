from datetime import date, datetime
from decimal import Decimal
from .stg_base import BaseJSONtransformer
from app.storage.models.orders_info import OrdersTbl, OrdersStatusesTbl, OrdersCommissionsTbl, OrderItemsTbl, OrderPaymentsTbl, OrdersSubsidiesTbl
from app.configs.logger_settings import get_logger

logger = get_logger(__name__)

class OrdersTransformer(BaseJSONtransformer):
    """
    Трансформер для отчета Детальная информация о заказах.
    Приводит данные из CSV в необходимые типы для загрузки в БД.
    """

    def __init__(self, json_data: dict):
        """
        Args:
            json_data: dict - ответ API в формате JSON
        """
        super().__init__(json_data)

    def transform(self) -> dict:
        """
        Преобразует ответ API в словарь таблиц для загрузки в БД
        Returns:
            dict: словарь таблиц для загрузки в БД
        Raises:
            IOError: если ответ API пустой
                или отсутствует обязательное поле в заказе
            ValueError: при ошибках преобразования
        """
        logger.info("Начало трансформации ответа API детальной информации о заказах")
        all_orders = []
        all_orders_statuses = []
        all_orders_commissions = []
        all_orders_items = []
        all_orders_payments = []
        all_orders_subsidies = []

        if not self.json_data:
            logger.error("Ответ API пустой")
            raise IOError("Ответ API пустой")

        orders = self.json_data.get("result", {}).get("orders", [])
        logger.debug(f"Загружено {len(orders)} заказов из API")
        for order in orders:
            order_id = int(order.get("id"))
            all_orders.append(self._tbl_orders(order, order_id))
            all_orders_statuses.append(self._tbl_orders_statuses(order, order_id))
            all_orders_commissions.extend(self._tbl_orders_commissions(order, order_id))
            all_orders_items.extend(self._tbl_orders_items(order, order_id))
            all_orders_payments.extend(self._tbl_orders_payments(order, order_id))
            all_orders_subsidies.extend(self._tbl_orders_subsidies(order, order_id))
        logger.info(f"Трансформация ответа API детальной информации о заказах завершена. Заказов: {len(all_orders)}")
        return {
            "all_orders": all_orders,
            "all_orders_statuses": all_orders_statuses,
            "all_orders_commissions": all_orders_commissions,
            "all_orders_items": all_orders_items,
            "all_orders_payments": all_orders_payments,
            "all_orders_subsidies": all_orders_subsidies
        }


    @staticmethod
    def _tbl_orders(order: dict, order_id: int) -> OrdersTbl:
        """Преобразует один заказ из ответа в объект OrdersTbl для таблицы orders"""
        try:
            record = OrdersTbl(
                order_id = order_id,
                creation_date = datetime.fromisoformat(order["creationDate"]).date() if order.get("creationDate") else None,
                status_upd_date = datetime.fromisoformat(order["statusUpdateDate"]) if order.get("statusUpdateDate") else None,
                payment_type = str(order["paymentType"]) if order.get("paymentType") else None,
                report_date = date.today()
            )
            return record
        except KeyError as e:
            raise IOError(f"Отсутствует обязательное поле в заказе: {e}")
        except ValueError as e:
            raise IOError(f"Ошибка преобразования данных в заказе {order_id}: {e}")
        except Exception as e:
            raise IOError(f"Ошибка преобразования в заказе {order_id}: {e}")

    @staticmethod
    def _tbl_orders_statuses(order: dict, order_id: int) -> OrdersStatusesTbl:
        """
        Преобразует один заказ из ответа в объект OrdersStatusesTbl.
        ВНИМАНИЕ: API возвращает только ТЕКУЩИЙ статус.
        История статусов будет построена в репозитории (SCD2).
        """
        try:
            record = OrdersStatusesTbl(
                order_id = order_id,
                order_status = str(order["status"]) if order.get("status") else None,
                date_from = datetime.fromisoformat(order["statusUpdateDate"]) if order.get("statusUpdateDate") else None,
                date_to = None,
                is_current = True,
                report_date = date.today()
                )
            return record
        except KeyError as e:
            raise IOError(f"Отсутствует обязательное поле в заказе: {e}")
        except ValueError as e:
            raise IOError(f"Ошибка преобразования данных в заказе {order_id}: {e}")
        except Exception as e:
            raise IOError(f"Ошибка преобразования в заказе {order_id}: {e}")

    @staticmethod
    def _tbl_orders_commissions(order: dict, order_id: int) -> list[OrdersCommissionsTbl]:
        """
        Преобразует один заказ из ответа в объект OrdersCommissionsTbl.
        """
        commission_list = order["commissions"]
        records = []
        for commission in commission_list:
            try:
                record = OrdersCommissionsTbl(
                    order_id = order_id,
                    commission_type = str(commission["type"]) if commission.get("type") else None,
                    commission_amount = Decimal(str(commission.get("actual", 0))),
                    report_date = date.today()
                    )
                records.append(record)
            except KeyError as e:
                raise IOError(f"Отсутствует обязательное поле в заказе: {e}")
            except ValueError as e:
                raise IOError(f"Ошибка преобразования данных в заказе {order_id}: {e}")
            except Exception as e:
                raise IOError(f"Ошибка преобразования в заказе {order_id}: {e}")
        return records

    @staticmethod
    def _tbl_orders_items(order: dict, order_id: int) -> list[OrderItemsTbl]:
        """
        Преобразует один заказ из ответа в объект OrderItemsTbl.
        """
        records = []
        items = order.get("items", [])
        for item in items:
            try:
                shop_sku = int(item["shopSku"]) if item.get("shopSku") else None
                ordered_qt = int(item.get("count", 0))
                returned_qt = 0
                rejected_qt = 0
                for detail in item.get("details", []):
                    if detail.get("itemStatus") == "REJECTED":
                        rejected_qt += detail.get("itemCount", 0)
                    elif detail.get("itemStatus") == "RETURNED":
                        returned_qt += detail.get("itemCount", 0)
                if order["status"] in {"DELIVERED", "PARTIALLY_DELIVERED", "PARTIALLY_RETURNED"}:
                    delivery_qt = max(ordered_qt - rejected_qt - returned_qt, 0)
                else:
                    delivery_qt = 0
                prices = item.get("prices", [])
                seller_price_per_unit = Decimal(0)
                mp_discount_per_unit = Decimal(0)
                mp_yandex_plus_discount = Decimal(0)
                buyer_price_per_unit = Decimal(0)
                for price in prices:
                    if price["type"] == "MARKETPLACE":
                        mp_discount_per_unit = Decimal(str(price.get("costPerItem", 0)))
                    elif price["type"] == "CASHBACK":
                        mp_yandex_plus_discount = Decimal(str(price.get("costPerItem", 0)))
                    elif price["type"] == "BUYER":
                        buyer_price_per_unit = Decimal(str(price.get("costPerItem", 0)))
                seller_price_per_unit = buyer_price_per_unit
                if mp_discount_per_unit:
                    seller_price_per_unit += mp_discount_per_unit
                if mp_yandex_plus_discount:
                    seller_price_per_unit += mp_yandex_plus_discount
                bid_fee = item.get("bidFee", 0)
                warehouse = item.get("warehouse")
                warehouse_id = warehouse.get("id") if warehouse else None
                record = OrderItemsTbl(
                    order_id = order_id,
                    shop_sku = shop_sku,
                    ordered_qt = ordered_qt,
                    delivered_qt = delivery_qt,
                    returned_qt = returned_qt,
                    rejected_qt = rejected_qt,
                    seller_price_per_unit = seller_price_per_unit,
                    buyer_price_per_unit = buyer_price_per_unit,
                    mp_discount_per_unit = mp_discount_per_unit,
                    mp_yandex_plus_discount = mp_yandex_plus_discount,
                    bid_fee = bid_fee,
                    warehouse_id = warehouse_id,
                    report_date = date.today()
                )
                records.append(record)
            except KeyError as e:
                raise IOError(f"Отсутствует обязательное поле в заказе: {e}")
            except ValueError as e:
                raise IOError(f"Ошибка преобразования данных в заказе {order_id}: {e}")
            except Exception as e:
                raise IOError(f"Ошибка преобразования в заказе {order_id}: {e}")
        return records

    @staticmethod
    def _tbl_orders_payments(order: dict, order_id: int) -> list[OrderPaymentsTbl]:
        """
        Преобразует один заказ из ответа в объект OrderPaymentsTbl.
        """
        records = []
        payments = order.get("payments", [])
        for payment in payments:
            try:
                payment_order_id = None
                payment_order_date = None
                payment_order = payment.get("paymentOrder", {})
                if payment_order:
                    payment_order_id = int(payment_order["id"]) if payment_order.get("id") else None
                    payment_order_date = datetime.fromisoformat(payment_order["date"]).date() if payment_order.get("date") else None
                payment_id = payment.get("id")
                payment_type = payment.get("type")
                payment_source = payment.get("source")
                payment_amount = Decimal(str(payment["total"])) if "total" in payment else None
                payment_date = payment.get("date")

                if not payment_id:
                    raise ValueError(f"payment_id is required for order {order_id}")
                if not payment_type:
                    raise ValueError(f"payment_type is required for order {order_id}")
                if payment_date and isinstance(payment_date, str):
                    payment_date = datetime.fromisoformat(payment_date).date()
                record = OrderPaymentsTbl(
                    order_id = order_id,
                    payment_id = payment_id,
                    payment_type = payment_type,
                    payment_date = payment_date,
                    payment_source = payment_source,
                    payment_amount = payment_amount,
                    payment_order_id = payment_order_id,
                    payment_order_date = payment_order_date,
                    report_date = date.today()
                )
                records.append(record)
            except KeyError as e:
                raise IOError(f"Отсутствует обязательное поле в заказе: {e}")
            except ValueError as e:
                raise IOError(f"Ошибка преобразования данных в заказе {order_id}: {e}")
            except Exception as e:
                raise IOError(f"Ошибка преобразования в заказе {order_id}: {e}")
        return records

    @staticmethod
    def _tbl_orders_subsidies(order: dict, order_id: int) -> list[OrdersSubsidiesTbl]:
        """
            Преобразует один заказ из ответа в объект OrdersSubsidiesTbl.
        """
        records = []
        subsidies = order.get("subsidies", [])
        for subsidy in subsidies:
            try:
                operation_type = subsidy.get("operationType")
                subsidy_type = subsidy.get("type")
                subsidy_amount = Decimal(str(subsidy.get("amount"))) if "amount" in subsidy else None
                record = OrdersSubsidiesTbl(
                    order_id = order_id,
                    operation_type = operation_type,
                    subsidy_type = subsidy_type,
                    subsidy_amount = subsidy_amount,
                    report_date=date.today()
                )
                records.append(record)
            except KeyError as e:
                raise IOError(f"Отсутствует обязательное поле в заказе: {e}")
            except ValueError as e:
                raise IOError(f"Ошибка преобразования данных в заказе {order_id}: {e}")
            except Exception as e:
                raise IOError(f"Ошибка преобразования в заказе {order_id}: {e}")
        return records



