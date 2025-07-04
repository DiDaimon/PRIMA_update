
"""
Модуль для настройки и управления логированием.
"""

import logging
import logging.handlers
import sys
from pathlib import Path
from typing import Optional

from colorama import init, Fore, Style
from src.prima_updater.config.settings import LoggingConfig

# Инициализируем colorama
init(autoreset=True)


class ColoredFormatter(logging.Formatter):
    """Цветной форматтер для консольного вывода."""
    
    COLORS = {
        'DEBUG': Fore.CYAN,
        'INFO': Fore.GREEN,
        'WARNING': Fore.YELLOW,
        'ERROR': Fore.RED,
        'CRITICAL': Fore.RED + Style.BRIGHT,
    }
    
    def format(self, record):
        if record.levelname in self.COLORS:
            record.levelname = f"{self.COLORS[record.levelname]}{record.levelname}{Style.RESET_ALL}"
        return super().format(record)


def setup_logging(config: LoggingConfig) -> logging.Logger:
    """
    Настраивает систему логирования согласно конфигурации.
    
    Args:
        config: Конфигурация логирования
        
    Returns:
        Настроенный логгер
    """
    # Создаем директорию для логов
    log_path = Path(config.file_path)
    log_path.parent.mkdir(parents=True, exist_ok=True)
    
    # Настраиваем корневой логгер
    logger = logging.getLogger("prima_updater")
    logger.setLevel(getattr(logging, config.level))
    
    # Очищаем существующие обработчики
    logger.handlers.clear()
    
    # Консольный обработчик
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(logging.INFO)
    console_formatter = ColoredFormatter("%(asctime)s - %(levelname)s - %(message)s")
    console_handler.setFormatter(console_formatter)
    logger.addHandler(console_handler)
    
    # Файловый обработчик
    file_handler = logging.handlers.RotatingFileHandler(
        config.file_path,
        maxBytes=_parse_size(config.max_file_size),
        backupCount=config.log_count,
        encoding='utf-8'
    )
    file_handler.setLevel(getattr(logging, config.level))
    file_formatter = logging.Formatter(config.format)
    file_handler.setFormatter(file_formatter)
    logger.addHandler(file_handler)
    
    return logger


def _parse_size(size_str: str) -> int:
    """Парсит размер файла из строки типа '10MB'."""
    size_str = size_str.upper()
    if size_str.endswith('KB'):
        return int(size_str[:-2]) * 1024
    elif size_str.endswith('MB'):
        return int(size_str[:-2]) * 1024 * 1024
    elif size_str.endswith('GB'):
        return int(size_str[:-2]) * 1024 * 1024 * 1024
    else:
        return int(size_str)


# Функции для быстрого логирования с цветами
def log_success(message: str, logger: Optional[logging.Logger] = None):
    """Логирует сообщение об успехе."""
    if logger is None:
        logger = logging.getLogger("prima_updater")
    print(f"{Fore.GREEN + Style.BRIGHT}[OK]{Style.RESET_ALL} {Fore.GREEN}{message}{Style.RESET_ALL}")
    logger.info(f"SUCCESS: {message}")


def log_error(message: str, logger: Optional[logging.Logger] = None):
    """Логирует сообщение об ошибке."""
    if logger is None:
        logger = logging.getLogger("prima_updater")
    print(f"{Fore.RED + Style.BRIGHT}[FAILED]{Style.RESET_ALL} {Fore.RED}{message}{Style.RESET_ALL}")
    logger.error(f"ERROR: {message}")


def log_warning(message: str, logger: Optional[logging.Logger] = None):
    """Логирует предупреждение."""
    if logger is None:
        logger = logging.getLogger("prima_updater")
    print(f"{Fore.YELLOW + Style.BRIGHT}[WARNING]{Style.RESET_ALL} {Fore.YELLOW}{message}{Style.RESET_ALL}")
    logger.warning(f"WARNING: {message}")


def log_attention(message: str, logger: Optional[logging.Logger] = None):
    """Логирует сообщение, требующее внимания."""
    if logger is None:
        logger = logging.getLogger("prima_updater")
    print(f"{Fore.BLUE + Style.BRIGHT}[ATTENTION]{Style.RESET_ALL} {Fore.BLUE}{message}{Style.RESET_ALL}")
    logger.info(f"ATTENTION: {message}")
