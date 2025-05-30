# config/settings.py
"""
Модуль для работы с конфигурацией приложения.
Поддерживает TOML формат с возможностью переопределения через переменные окружения.
"""

import os
import tomllib
from pathlib import Path
from dataclasses import dataclass, field
from typing import List, Optional


@dataclass
class ServerConfig:
    """Конфигурация сервера."""
    directory: str
    timeout: int = 30
    retry_attempts: int = 3

    def __post_init__(self):
        """Валидация конфигурации сервера."""
        if not self.directory:
            raise ValueError("Server directory cannot be empty")
        if self.timeout <= 0:
            raise ValueError("Timeout must be positive")


@dataclass
class LocalConfig:
    """Локальная конфигурация."""
    directory: str
    backup_directory: Optional[str] = None
    max_backups: int = 5
    max_long_backups: int = 1

    def __post_init__(self):
        """Валидация локальной конфигурации."""
        if not self.directory:
            raise ValueError("Local directory cannot be empty")
        if self.backup_directory is None:
            self.backup_directory = str(Path(self.directory) / "backups")


@dataclass
class IgnoreConfig:
    """Конфигурация игнорируемых файлов."""
    files: List[str] = field(default_factory=list)
    patterns: List[str] = field(default_factory=list)
    directories: List[str] = field(default_factory=list)


@dataclass
class UIConfig:
    """Конфигурация пользовательского интерфейса."""
    clear_terminal: bool = True
    show_progress: bool = True
    auto_mode: bool = False


@dataclass
class LoggingConfig:
    """Конфигурация логирования."""
    level: str = "INFO"
    file_path: str = "logs/prima_updater.log"
    max_file_size: str = "10MB"
    log_count: int = 5
    format: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"

    def __post_init__(self):
        """Валидация конфигурации логирования."""
        valid_levels = ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]
        if self.level.upper() not in valid_levels:
            raise ValueError(f"Invalid log level: {self.level}")
        self.level = self.level.upper()


@dataclass
class AppConfig:
    """Основная конфигурация приложения."""
    server: ServerConfig
    local: LocalConfig
    ignore: IgnoreConfig = field(default_factory=IgnoreConfig)
    ui: UIConfig = field(default_factory=UIConfig)
    logging: LoggingConfig = field(default_factory=LoggingConfig)


class ConfigManager:
    """Менеджер конфигурации с поддержкой TOML и переменных окружения."""

    DEFAULT_CONFIG_PATHS = [
        Path("config/settings.toml"),
        Path("settings.toml"),
        Path.home() / ".prima_updater" / "settings.toml"
    ]

    def __init__(self, config_path: Optional[Path] = None):
        self.config_path = config_path
        self._config = None

    def load_config(self) -> AppConfig:
        """Загружает конфигурацию из файла."""
        if self._config is not None:
            return self._config

        config_file = self._find_config_file()
        if config_file is None:
            raise FileNotFoundError("Configuration file not found")

        with open(config_file, "rb") as f:
            raw_config = tomllib.load(f)

        # Применяем переменные окружения
        self._apply_env_overrides(raw_config)

        # Создаем объекты конфигурации
        self._config = self._build_config(raw_config)
        return self._config

    def _find_config_file(self) -> Optional[Path]:
        """Находит файл конфигурации."""
        if self.config_path and self.config_path.exists():
            return self.config_path

        for path in self.DEFAULT_CONFIG_PATHS:
            if path.exists():
                return path
        return None

    def _apply_env_overrides(self, config: dict) -> None:
        """Применяет переопределения из переменных окружения."""
        env_mappings = {
            "PRIMA_SERVER_DIR": ("server", "directory"),
            "PRIMA_LOCAL_DIR": ("local", "directory"),
            "PRIMA_BACKUP_DIR": ("local", "backup_directory"),
            "PRIMA_LOG_LEVEL": ("logging", "level"),
            "PRIMA_LOG_FILE": ("logging", "file_path"),
            "PRIMA_AUTO_MODE": ("ui", "auto_mode"),
        }

        for env_var, (section, key) in env_mappings.items():
            value = os.getenv(env_var)
            if value is not None:
                if section not in config:
                    config[section] = {}
                # Конвертируем булевы значения
                if key in ["auto_mode", "clear_screen", "colored_output", "show_progress"]:
                    config[section][key] = value.lower() in ("true", "1", "yes", "on")
                else:
                    config[section][key] = value

    def _build_config(self, raw_config: dict) -> AppConfig:
        """Строит объект конфигурации из raw данных."""
        server_config = ServerConfig(**raw_config.get("server", {}))
        local_config = LocalConfig(**raw_config.get("local", {}))
        ignore_config = IgnoreConfig(**raw_config.get("ignore", {}))
        ui_config = UIConfig(**raw_config.get("ui", {}))
        logging_config = LoggingConfig(**raw_config.get("logging", {}))

        return AppConfig(
            server=server_config,
            local=local_config,
            ignore=ignore_config,
            ui=ui_config,
            logging=logging_config
        )

    def save_config(self, config: AppConfig, path: Optional[Path] = None) -> None:
        """Сохраняет конфигурацию в файл (требует tomli-w для записи)."""
        try:
            import tomli_w
        except ImportError:
            raise ImportError("tomli-w required for saving TOML files. Install with: pip install tomli-w")

        save_path = path or self.config_path or self.DEFAULT_CONFIG_PATHS[0]
        save_path.parent.mkdir(parents=True, exist_ok=True)

        # Конвертируем dataclass в dict
        config_dict = {
            "server": {
                "directory": config.server.directory,
                "timeout": config.server.timeout,
                "retry_attempts": config.server.retry_attempts,
            },
            "local": {
                "directory": config.local.directory,
                "backup_directory": config.local.backup_directory,
                "max_backups": config.local.max_backups,
            },
            "ignore": {
                "files": config.ignore.files,
                "patterns": config.ignore.patterns,
                "directories": config.ignore.directories,
            },
            "ui": {
                "clear_screen": config.ui.clear_terminal,
                "show_progress": config.ui.show_progress,
                "auto_mode": config.ui.auto_mode,
            },
            "logging": {
                "level": config.logging.level,
                "file_path": config.logging.file_path,
                "max_file_size": config.logging.max_file_size,
                "log_count": config.logging.log_count,
                "format": config.logging.format,
            }
        }

        with open(save_path, "wb") as f:
            tomli_w.dump(config_dict, f)


# Утилита-функция для быстрого доступа к конфигурации
_config_manager = None

def get_config() -> AppConfig:
    """Получает текущую конфигурацию приложения."""
    global _config_manager
    if _config_manager is None:
        _config_manager = ConfigManager()
    return _config_manager.load_config()


def init_config(config_path: Optional[Path] = None) -> ConfigManager:
    """Инициализирует менеджер конфигурации."""
    global _config_manager
    _config_manager = ConfigManager(config_path)
    return _config_manager


if __name__ == "__main__":
    # Пример использования
    try:
        config = get_config()
        print(f"Server directory: {config.server.directory}")
        print(f"Local directory: {config.local.directory}")
        print(f"Log level: {config.logging.level}")
    except FileNotFoundError:
        print("Config file not found. Creating example...")
        # Здесь можно создать пример конфигурации
        