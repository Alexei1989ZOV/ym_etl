import time
from datetime import datetime, timedelta
from collections import deque
from threading import Lock

class RateLimiter:
    def __init__(self, max_requests: int, period_seconds: int = 3600):
        self.max_requests = max_requests
        self.period = period_seconds
        self.requests = deque()
        self.lock = Lock()

    def wait_if_needed(self):
        """Ждет, если лимит исчерпан"""
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
                    print(f"[RATE LIMIT] Достигнут лимит {self.max_requests} запросов в час. "
                          f"Ожидание {wait_seconds:.0f} секунд...")
                    time.sleep(wait_seconds)

                    # НЕ очищаем requests!
                    # Просто после ожидания рекурсивно вызываем себя для повторной проверки
                    self.wait_if_needed()
                    return

            # Добавляем текущий запрос
            self.requests.append(now)