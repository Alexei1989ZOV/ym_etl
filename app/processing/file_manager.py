from pathlib import Path
import zipfile
from datetime import date, datetime
from app.reports.base import BaseReport
import shutil
from app.configs.logger_settings import get_logger

logger = get_logger(__name__)


class FileManager:
    def __init__(self, raw_dir: str, processed_dir: str):
        """
        Args:
            raw_dir(str): Путь к директории для хранения полученных по API архивов
            processed_dir(str): Путь к директории для хранения распакованных архивов
        """
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
        """
        Сохраняет сырые байты, полученные по ссылке в zip архив.
        Args:
            report(BaseReport): Объект отчета
            report_date(date): Дата, за которую сформирован отчет
            data(bytes): Сырые байты
        Returns:
            Path: Путь к сохраненному архиву
        """
        filename = f"{report.report_type}_{report_date}.zip"
        report_dir = self.raw_dir / report.report_type
        report_dir.mkdir(parents=True, exist_ok=True)
        archive_path = report_dir / filename

        with open(archive_path, "wb") as f:
            f.write(data)
        logger.debug(f"Архив сохранен: {archive_path}")
        return archive_path

    def extract_archive(self, report: BaseReport, archive_path: Path) -> list[Path]:
        """
        Распаковывает архив и возвращает пути к CSV файлам.
        Args:
            report(BaseReport): Объект отчета
            archive_path(Path): Путь к архиву, который нужно распаковать
        Returns:
            list[Path]: Список путей к извлеченным CSV файлам
        Raises:
            ValueError: Если в архиве не найдено CSV файлов
        """
        target_dir = self.processed_dir / report.report_type / archive_path.stem
        target_dir.mkdir(parents=True, exist_ok=True)
        # Извлекаем дату из имени файла
        date_str = archive_path.stem.split("_")[-1]
        date_obj = datetime.strptime(date_str, "%Y-%m-%d").date()
        csv_files: list[Path] = []
        logger.debug(f"Распаковка архива {archive_path} в {target_dir}")
        with zipfile.ZipFile(archive_path) as zf:
            zf.extractall(target_dir)

            for name in zf.namelist():
                if name.lower().endswith(".csv"):
                    timestamp = date_obj.strftime("%Y-%m-%d")
                    name_timestamp = f"{Path(name).stem}_{timestamp}{Path(name).suffix}"
                    csv_files.append(target_dir / name_timestamp)

                    # Переименовываем файл на диске
                    (target_dir / name).rename(target_dir / name_timestamp)

        if not csv_files:
            logger.error(f"В архиве {archive_path} не найдено CSV файлов")
            raise ValueError("В архиве не найдено CSV файлов")
        logger.debug(f"Распаковано {len(csv_files)} CSV файлов в {target_dir}")
        return csv_files

    def cleanup_extracted_dir(self, report: BaseReport, archive_path: Path) -> None:
        """
        Удаляет распакованную директорию и исходный ZIP-архив.
        Args:
            report: Объект отчета (для определения типа)
            archive_path: Путь к архиву (по нему определяется имя директории)
        """
        processed_dir = self.processed_dir / report.report_type / archive_path.stem
        raw_zip_file = self.raw_dir / report.report_type / archive_path.name  # ← файл, не папка!
        
        try:
            if processed_dir.exists():
                shutil.rmtree(processed_dir)
                logger.debug(f"[CLEANUP] Удалена директория: {processed_dir}")
                
            if raw_zip_file.exists():
                raw_zip_file.unlink()  # ← удаление файла
                logger.debug(f"[CLEANUP] Удалён архив: {raw_zip_file}")
                
        except Exception as e:
            logger.error(f"[CLEANUP] Ошибка при удалении: {e}")
    
        
