
"""
Модуль для работы с изменениями файлов и директорий.
"""

from dataclasses import dataclass, field
from typing import List, Set
from pathlib import Path


@dataclass
class ChangeSet:
    """Набор изменений между исходной и целевой директориями."""
    
    modified_files: List[str] = field(default_factory=list)
    missing_files: List[str] = field(default_factory=list)
    new_directories: List[str] = field(default_factory=list)
    deleted_files: List[str] = field(default_factory=list)
    
    def has_changes(self) -> bool:
        """Проверяет, есть ли какие-либо изменения."""
        return bool(
            self.modified_files or 
            self.missing_files or 
            self.new_directories or 
            self.deleted_files
        )
    
    def get_all_files(self) -> List[str]:
        """Возвращает все файлы, которые нужно обновить."""
        return self.modified_files + self.missing_files
    
    def get_total_count(self) -> int:
        """Возвращает общее количество изменений."""
        return len(self.modified_files) + len(self.missing_files) + len(self.new_directories)


@dataclass
class FileChange:
    """Информация об изменении файла."""
    
    source_path: str
    target_path: str
    change_type: str  # 'modified', 'missing', 'new', 'deleted'
    size: int = 0
    timestamp: float = 0.0
    
    def __str__(self) -> str:
        return f"{self.change_type.upper()}: {self.target_path}"


class ChangeDetector:
    """Детектор изменений между директориями."""
    
    def __init__(self, ignore_patterns: List[str] = None):
        self.ignore_patterns = ignore_patterns or []
        self.ignored_files: Set[str] = set()
        self.ignored_dirs: Set[str] = set()
    
    def should_ignore(self, path: Path, is_dir: bool = False) -> bool:
        """
        Проверяет, нужно ли игнорировать файл или директорию.
        
        Args:
            path: Путь к файлу или директории
            is_dir: True, если это директория
            
        Returns:
            True, если нужно игнорировать
        """
        path_str = str(path)
        name = path.name
        
        # Проверяем точные совпадения имен
        if name in self.ignore_patterns:
            return True
        
        # Проверяем паттерны
        for pattern in self.ignore_patterns:
            if pattern.startswith('*.') and name.endswith(pattern[1:]):
                return True
            elif pattern.startswith('*') and pattern[1:] in name:
                return True
            elif pattern in path_str:
                return True
        
        return False
    
    def add_ignored_file(self, file_path: str):
        """Добавляет файл в список игнорируемых."""
        self.ignored_files.add(file_path)
    
    def add_ignored_directory(self, dir_path: str):
        """Добавляет директорию в список игнорируемых."""
        self.ignored_dirs.add(dir_path)
    
    def remove_ignored_file(self, file_path: str):
        """Удаляет файл из списка игнорируемых."""
        self.ignored_files.discard(file_path)
    
    def get_ignored_files(self) -> Set[str]:
        """Возвращает множество игнорируемых файлов."""
        return self.ignored_files.copy()
    
    def clear_ignored(self):
        """Очищает списки игнорируемых файлов и директорий."""
        self.ignored_files.clear()
        self.ignored_dirs.clear()


@dataclass 
class BackupInfo:
    """Информация о бэкапе."""
    
    path: str
    timestamp: float
    version: str
    size: int
    
    def __str__(self) -> str:
        from datetime import datetime
        date_str = datetime.fromtimestamp(self.timestamp).strftime('%d.%m.%Y %H:%M')
        return f"{self.version} ({date_str}, {self.size} bytes)"


class BackupManager:
    """Менеджер для работы с бэкапами."""
    
    def __init__(self, backup_dir: str, max_backups: int = 5):
        self.backup_dir = Path(backup_dir)
        self.max_backups = max_backups
        self.backup_dir.mkdir(parents=True, exist_ok=True)
    
    def create_backup(self, file_path: str, version: str = None) -> str:
        """
        Создает бэкап файла.
        
        Args:
            file_path: Путь к файлу для бэкапа
            version: Версия бэкапа (если не указана, используется дата)
            
        Returns:
            Путь к созданному бэкапу
        """
        source = Path(file_path)
        if not source.exists():
            raise FileNotFoundError(f"Файл не найден: {file_path}")
        
        if version is None:
            from datetime import datetime
            version = datetime.now().strftime('%Y%m%d_%H%M%S')
        
        backup_name = f"{source.stem}[{version}]{source.suffix}"
        backup_path = self.backup_dir / backup_name
        
        import shutil
        shutil.copy2(source, backup_path)
        
        # Очищаем старые бэкапы
        self._cleanup_old_backups(source.name)
        
        return str(backup_path)
    
    def _cleanup_old_backups(self, original_name: str):
        """Удаляет старые бэкапы, оставляя только последние max_backups."""
        stem = Path(original_name).stem
        suffix = Path(original_name).suffix
        
        # Находим все бэкапы этого файла
        backup_pattern = f"{stem}[*]{suffix}"
        backups = list(self.backup_dir.glob(backup_pattern))
        
        if len(backups) > self.max_backups:
            # Сортируем по времени создания
            backups.sort(key=lambda x: x.stat().st_mtime)
            
            # Удаляем самые старые
            for backup in backups[:-self.max_backups]:
                backup.unlink()
    
    def list_backups(self, file_name: str = None) -> List[BackupInfo]:
        """
        Возвращает список доступных бэкапов.
        
        Args:
            file_name: Имя файла для фильтрации (если None, возвращает все)
            
        Returns:
            Список информации о бэкапах
        """
        backups = []
        
        if file_name:
            stem = Path(file_name).stem
            suffix = Path(file_name).suffix
            pattern = f"{stem}[*]{suffix}"
        else:
            pattern = "*[*]*"
        
        for backup_path in self.backup_dir.glob(pattern):
            stat = backup_path.stat()
            
            # Извлекаем версию из имени файла
            name = backup_path.name
            start = name.find('[')
            end = name.find(']')
            version = name[start+1:end] if start != -1 and end != -1 else "unknown"
            
            backups.append(BackupInfo(
                path=str(backup_path),
                timestamp=stat.st_mtime,
                version=version,
                size=stat.st_size
            ))
        
        # Сортируем по времени (новые первыми)
        backups.sort(key=lambda x: x.timestamp, reverse=True)
        return backups
    
    def restore_backup(self, backup_path: str, target_path: str):
        """
        Восстанавливает файл из бэкапа.
        
        Args:
            backup_path: Путь к бэкапу
            target_path: Путь для восстановления
        """
        import shutil
        backup = Path(backup_path)
        target = Path(target_path)
        
        if not backup.exists():
            raise FileNotFoundError(f"Бэкап не найден: {backup_path}")
        
        # Создаем директорию если нужно
        target.parent.mkdir(parents=True, exist_ok=True)
        
        shutil.copy2(backup, target)
