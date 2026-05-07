from datetime import date, timedelta
from typing import Optional, List


class DateManager:
    """Управляет диапазонами дат для загрузки отчетов."""

    def __init__(
        self,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None,
    ):
        """
        Args:
            start_date: Начальная дата загрузки (включительно)
            end_date: Конечная дата загрузки (включительно), по умолчанию вчера
        """
        self.start_date = start_date
        self.end_date = end_date or (date.today() - timedelta(days=1))

    def get_dates(self) -> List[date]:
        if not self.start_date:
            return [self.end_date]

        if self.start_date > self.end_date:
            raise ValueError("start_date не может быть больше end_date")

        dates = []
        current = self.start_date

        while current <= self.end_date:
            dates.append(current)
            current += timedelta(days=1)

        return dates
