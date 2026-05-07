import time
from datetime import datetime, timedelta
from collections import deque
from threading import Lock
from app.configs.logger_settings import get_logger

logger = get_logger(__name__)

class RateLimiter:
    def __init__(self, max_requests: int, period_seconds: int = 3600):
        """
        Args:
            max_requests (int): максимально разрешенное количество запросов за временной период
            period_seconds (int): временной период в секундах
        """
        self.max_requests = max_requests
        self.period = period_seconds
        self.requests = deque()
        self.lock = Lock()

    def wait_if_needed(self):
        """Ждет, если лимит исчерпан"""
        wait_seconds = 0

        with self.lock:
            now = datetime.now()
            cutoff = now - timedelta(seconds=self.period)

            # Удаляем старые запросы
            while self.requests and self.requests[0] < cutoff:
                self.requests.popleft()

            # Если лимит исчерпан, считаем сколько ждать
            if len(self.requests) >= self.max_requests:
                oldest = self.requests[0]
                wait_seconds = (oldest + timedelta(seconds=self.period) - now).total_seconds()

                if wait_seconds > 0:
                    logger.info(f"[RATE LIMIT] Достигнут лимит {self.max_requests} запросов в час. "
                                f"Ожидание {wait_seconds:.0f} секунд")
                    # Не добавляем запрос сейчас, выйдем из with и будем ждать
                else:
                    # wait_seconds <= 0 — можно делать запрос
                    self.requests.append(now)
                    logger.debug(f"[RATE LIMIT] Запрос разрешен. Всего за час: {len(self.requests)}")
                    return
            else:
                # Лимит не достигнут — можно делать запрос
                self.requests.append(now)
                logger.debug(f"[RATE LIMIT] Запрос разрешен. Всего за час: {len(self.requests)}")
                return

        # Если нужно ждать — делаем это вне блокировки
        if wait_seconds > 0:
            time.sleep(wait_seconds)
            # После ожидания рекурсивно проверяем снова
            self.wait_if_needed()