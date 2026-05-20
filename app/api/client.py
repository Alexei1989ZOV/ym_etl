from app.configs.settings import settings
import requests
from app.configs.logger_settings import get_logger

logger = get_logger(__name__)

class BaseAPIClient:
    """
    Базовый клиент для работы с API Яндекс.Маркета.

    Обеспечивает:
    - единую точку настройки Session (заголовки, API-ключ)
    - отправку HTTP-запросов
    - обработку сетевых ошибок
    - проверку ошибок API (когда внутри JSON есть поле "errors")
    """

    def __init__(self):
        """
        Инициализирует сессию и загружает настройки из Settings.
        """
        self.api_key = settings.api_key.get_secret_value()
        self.business_id = settings.business_id
        self.campaign_id = settings.campaign_id
        self.base_url = "https://api.partner.market.yandex.ru/v2"

        self.session = requests.Session()
        self.session.headers.update({
            "Api-key": self.api_key,
            "Content-Type": "application/json",
            "Accept": "application/json",
        })

    def _build_url(self, endpoint: str) -> str:
        """
        Строит полный URL для API-метода.

        Args:
            endpoint: путь после базового URL

        Returns:
            str: полный адрес запроса
        """
        return f"{self.base_url}/{endpoint}"

    def _send(self, method: str, url: str, **kwargs) -> requests.Response:
        """
        Отправляет HTTP-запрос и обрабатывает сетевые ошибки.

        Args:
            method: HTTP-метод ("GET", "POST")
            url: полный URL
            **kwargs: параметры requests.request()

        Returns:
            requests.Response: объект ответа

        Raises:
            RuntimeError: при ошибке сети или недоступности ресурса
        """
        try:
            logger.debug(f"Sending {method} to {url}")
            response = self.session.request(method, url, **kwargs)
            response.raise_for_status()
            logger.debug(f"Response {response.status_code} from {url}")
            return response
        except requests.exceptions.RequestException as e:
            logger.error(f"Network error: {method} {url} - {e}")
            raise RuntimeError(f"Ошибка сети: {e}") from e

    @staticmethod
    def _parse_json(response: requests.Response) -> dict:
        """
        Пытается распарсить тело ответа как JSON.

        Args:
            response: HTTP-ответ

        Returns:
            dict: распарсенный JSON или пустой dict при ошибке
        """
        try:
            return response.json()
        except ValueError:
            return {}

    @staticmethod
    def _check_api_errors(data: dict) -> None:
        """
        Проверяет поле 'errors' в JSON-ответе.

        Args:
            data: данные ответа API

        Raises:
            RuntimeError: если API вернул список ошибок
        """
        errors = data.get("errors", [])
        if errors:
            msg = ", ".join(f"{e.get('code')}: {e.get('message')}" for e in errors)
            raise RuntimeError(f"API error: {msg}")

    def make_request(self, method: str, endpoint: str, **kwargs) -> dict:
        """
        Выполняет запрос к API, обрабатывает ошибки и возвращает данные.

        Args:
            method: HTTP-метод (GET/POST/...)
            endpoint: путь внутри API
            **kwargs: параметры запроса

        Returns:
            dict: итоговый JSON от сервера

        Raises:
            RuntimeError: при сетевой ошибке или ошибке API
        """
        url = self._build_url(endpoint)
        try:
            logger.debug(f"API request: {method} {endpoint}")
            response = self._send(method, url, **kwargs)
            data = self._parse_json(response)
            self._check_api_errors(data)
            logger.debug(f"API response: {method} {endpoint} - status {response.status_code}")
            return data
        except Exception as e:
            logger.error(f"API request failed: {method} {endpoint} - {e}", exc_info=True)
            raise
