from datetime import date, datetime
from sqlalchemy.orm import Session
from app.api.report_client import ReportAPIClient
from app.reports.orders import OrdersInfoReport
from app.stg_transformers.orders_transformer import OrdersTransformer
from app.storage.repositories.orders_repository import OrdersRepository
from app.storage.repositories.orders_statuses_repository import OrdersStatusesRepository
from app.storage.repositories.orders_commissions_repository import OrdersCommissionsRepository
from app.storage.repositories.orders_payments_repository import OrdersPaymentsRepository
from app.storage.repositories.orders_items_repository import OrdersItemsRepository
from app.storage.repositories.orders_subsidies_repository import OrdersSubsidiesRepository
from app.configs.logger_settings import get_logger

logger = get_logger(__name__)

class OrdersInfoPipeline:
    """
    ETL pipeline для получения детальной информации о заказах.
    """
    def __init__(
            self,
            session: Session,
            api_client: ReportAPIClient,
             ):
        """
        Args:
            session: Сессия SQLAlchemy для работы с базой данных
            api_client: Объект ReportAPIClient для доступа к API
        """
        self.session = session
        self.api_client = api_client
        self.orders_repo = OrdersRepository(session)
        self.statuses_repo = OrdersStatusesRepository(session)
        self.commissions_repo = OrdersCommissionsRepository(session)
        self.payments_repo = OrdersPaymentsRepository(session)
        self.items_repo = OrdersItemsRepository(session)
        self.subsidies_repo = OrdersSubsidiesRepository(session)

    def run(self, update_from: date, update_to: date) -> None:
        """
        Загружает данные о заказах из API и сохраняет в БД.
        Процесс:
            1. Получает данные из API Яндекс.Маркета за период изменений
            2. Трансформирует JSON в модели для 6 таблиц
            3. Сохраняет (обновляет) данные в БД
        Args:
            update_from: Начальная дата периода изменений
            update_to: Конечная дата периода изменений
        """
        #Получаем данные из API
        logger.info("[ORDERS INFO] Начало загрузки информации о заказах")
        report = OrdersInfoReport(
            update_from=update_from.isoformat(),
            update_to=update_to.isoformat(), )
        data = self.api_client.get_orders_info(report)

        #Делаем трансформации
        transformer = OrdersTransformer(data)
        records = transformer.transform()

        if not records["all_orders"]:
            logger.error("[ORDERS INFO] Нет данных для загрузки")
            return

        #Вставляем данные в БД
        try:
            logger.info("[ORDERS INFO] Сохраняем заказы...")
            self.orders_repo.upsert(records["all_orders"])
            logger.info("[ORDERS INFO] Заказы сохранены, сохраняем статусы...")
            self.statuses_repo.upsert(records["all_orders_statuses"])
            logger.info("[ORDERS INFO] Статусы сохранены...")
            self.payments_repo.upsert(records["all_orders_payments"])
            logger.info("[ORDERS INFO] Платежи сохранены...")
            self.commissions_repo.upsert(records["all_orders_commissions"])
            logger.info("[ORDERS INFO] Комиссии сохранены...")
            self.items_repo.replace_by_order(records["all_orders_items"])
            logger.info("[ORDERS INFO] Товары сохранены...")
            self.subsidies_repo.replace_by_order(records["all_orders_subsidies"])
            logger.info("[ORDERS INFO] Субсидии сохранены. ГОТОВО!")
            self.session.commit()
            logger.info(f"[ORDERS INFO] Загружено {len(records['all_orders'])} заказов")
        except Exception as e:
            logger.error(f"[ORDERS INFO] Ошибка при загрузке данных в БД: {e}")
            self.session.rollback()
            raise RuntimeError(f"[ORDERS INFO] Ошибка при загрузке данных в БД: {e}")





