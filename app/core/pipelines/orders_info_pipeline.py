from datetime import date, datetime
from sqlalchemy.orm import Session
from app.core.pipeline import ReportPipeline
from app.reports.orders import OrdersInfoReport
from app.stg_transformers.orders_transformer import OrdersTransformer
from app.storage.repositories.orders_repository import OrdersRepository
from app.storage.repositories.orders_statuses_repository import OrdersStatusesRepository
from app.storage.repositories.orders_commissions_repository import OrdersCommissionsRepository
from app.storage.repositories.orders_payments_repository import OrdersPaymentsRepository
from app.storage.repositories.orders_items_repository import OrdersItemsRepository
from app.storage.repositories.orders_subsidies_repository import OrdersSubsidiesRepository


class OrdersInfoPipeline:
    def __init__(
            self,
            session: Session,
            report_pipeline: ReportPipeline,
             ):
        self.session = session
        self.report_pipeline = report_pipeline
        self.orders_repo = OrdersRepository(session)
        self.statuses_repo = OrdersStatusesRepository(session)
        self.commissions_repo = OrdersCommissionsRepository(session)
        self.payments_repo = OrdersPaymentsRepository(session)
        self.items_repo = OrdersItemsRepository(session)
        self.subsidies_repo = OrdersSubsidiesRepository(session)

    def run(self, update_from: date, update_to: date) -> None:
        #Получаем данные из API
        print(f"{datetime.now()} [ORDER INFO PIPELINE]: 1. Получаем данные из API...")
        report = OrdersInfoReport(
            update_from=update_from.isoformat(),
            update_to=update_to.isoformat(), )
        data = self.report_pipeline.api_client.get_orders_info(report)

        print(f"{datetime.now()} [ORDER INFO PIPELINE] 2. Данные получены, начинаем трансформацию...")
        #Делаем трансформации
        transformer = OrdersTransformer(data)
        records = transformer.transform()
        print(f"{datetime.now()} [ORDER INFO PIPELINE] 3. Трансформация завершена. Заказов: {len(records['all_orders'])}")
        if not records["all_orders"]:
            print(f"{datetime.now()} [ORDERS INFO] Нет данных для загрузки")
            return

        #Вставляем данные в БД
        try:
            print(f"{datetime.now()} [ORDER INFO PIPELINE] 4. Сохраняем заказы...")
            self.orders_repo.upsert(records["all_orders"])
            print(f"{datetime.now()} [PIPELINE] 5. Заказы сохранены, сохраняем статусы...")
            self.statuses_repo.upsert(records["all_orders_statuses"])
            print(f"{datetime.now()} [PIPELINE] 6. Статусы сохранены...")
            self.payments_repo.upsert(records["all_orders_payments"])
            print(f"{datetime.now()} [PIPELINE] 7. Платежи сохранены...")
            self.commissions_repo.upsert(records["all_orders_commissions"])
            print(f"{datetime.now()} [PIPELINE] 8. Комиссии сохранены...")
            self.items_repo.replace_by_order(records["all_orders_items"])
            print(f"{datetime.now()} [PIPELINE] 9. Товары сохранены...")
            self.subsidies_repo.replace_by_order(records["all_orders_subsidies"])
            print(f"{datetime.now()} [PIPELINE] 10. Субсидии сохранены. ГОТОВО!")
            self.session.commit()
            print(f"{datetime.now()} [ORDERS INFO] Загружено {len(records['all_orders'])} заказов")
        except Exception as e:
            self.session.rollback()
            raise RuntimeError(f"Ошибка при загрузке данных в в БД: {e}")





