from pathlib import Path
import zipfile
from datetime import date, datetime
from app.reports.base import BaseReport


class FileManager:
    def __init__(self, raw_dir: str, processed_dir: str):
        self.raw_dir = Path(raw_dir)
        self.processed_dir = Path(processed_dir)

        self.raw_dir.mkdir(parents=True, exist_ok=True)
        self.processed_dir.mkdir(parents=True, exist_ok=True)

    def save_raw(
        self,
        report: BaseReport,
        report_date: date,
        data: bytes
    ) -> Path:
        filename = f"{report.report_type}_{report_date}.zip"
        report_dir = self.raw_dir / report.report_type
        report_dir.mkdir(parents=True, exist_ok=True)
        archive_path = report_dir / filename

        with open(archive_path, "wb") as f:
            f.write(data)

        return archive_path

    def extract_archive(self, report: BaseReport, archive_path: Path) -> list[Path]:
        """
        Распаковывает архив и возвращает пути к CSV файлам.
        """
        target_dir = self.processed_dir / report.report_type / archive_path.stem
        target_dir.mkdir(parents=True, exist_ok=True)

        csv_files: list[Path] = []

        with zipfile.ZipFile(archive_path) as zf:
            zf.extractall(target_dir)

            for name in zf.namelist():
                if name.lower().endswith(".csv"):
                    # Добавляем timestamp к имени файла, чтобы избежать перезаписи
                    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                    name_timestamp = f"{Path(name).stem}_{timestamp}{Path(name).suffix}"
                    csv_files.append(target_dir / name_timestamp)

                    # Переименовываем файл на диске
                    (target_dir / name).rename(target_dir / name_timestamp)

        if not csv_files:
            raise ValueError("В архиве не найдено CSV файлов")

        return csv_files

