# -*- coding: utf-8 -*-
"""Модуль для логирования работы приложения.

Этот модуль настраивает систему логирования с записью в файл и выводом в консоль.
"""

import logging
from datetime import datetime
from pathlib import Path
from typing import Union
from logging.handlers import RotatingFileHandler
from colorama import init, Fore, Style


class ColoredFormatter(logging.Formatter):
    """Форматтер для цветного вывода логов в консоль.
    
    Использует colorama для добавления цветов к уровням логирования.
    """
    
    # Цвета для разных уровней логирования
    COLORS = {
        'DEBUG': Fore.CYAN,
        'INFO': Fore.GREEN,
        'WARNING': Fore.YELLOW + Style.BRIGHT,
        'ERROR': Fore.RED + Style.BRIGHT,
        'CRITICAL': Fore.RED + Style.BRIGHT + Style.BRIGHT,
    }
    
    # Префиксы для уровней (соответствуют оригинальным сообщениям)
    PREFIXES = {
        'INFO': '[OK] ',
        'WARNING': '[WARNING] ',
        'ERROR': '[FAILED] ',
        'CRITICAL': '[CRITICAL] ',
        'DEBUG': '[DEBUG] ',
    }
    
    def __init__(self, use_colors=True):
        """Инициализация цветного форматтера.
        
        Args:
            use_colors (bool): Использовать ли цвета в выводе
        """
        super().__init__()
        self.use_colors = use_colors
        # Инициализируем colorama
        if use_colors:
            init(autoreset=True)
    
    def format(self, record):
        """Форматирует запись лога с цветами.
        
        Args:
            record: Запись лога для форматирования
        
        Returns:
            str: Отформатированное сообщение
        """
        # Получаем цвет для уровня
        levelname = record.levelname
        color = self.COLORS.get(levelname, '')
        prefix = self.PREFIXES.get(levelname, '')
        
        # Формируем сообщение
        message = record.getMessage()
        
        if self.use_colors and color:
            # Добавляем цвет и префикс
            colored_prefix = f"{color}{prefix}{Style.RESET_ALL}"
            colored_message = f"{color}{message}{Style.RESET_ALL}"
            return f"{colored_prefix}{colored_message}"
        else:
            # Без цветов
            return f"{prefix}{message}"


def setup_logging(log_dir: Union[str, Path] = ".logs") -> logging.Logger:
    """Настройка системы логирования.
    
    Создает директорию для логов (если её нет), настраивает формат логов
    и создает обработчики для записи в файл и выводом в консоль.
    
    Args:
        log_dir (Union[str, Path]): Директория для хранения логов. По умолчанию ".logs"
    
    Returns:
        logging.Logger: Настроенный логгер
    """
    # Создаем директорию для логов, если её нет
    log_path = Path(log_dir)
    log_path.mkdir(parents=True, exist_ok=True)
    
    # Формируем имя файла лога с текущей датой
    log_filename = log_path / f"prima_update_{datetime.now().strftime('%Y%m%d')}.log"
    
    # Создаем логгер
    logger = logging.getLogger('PRIMA_Updater')
    logger.setLevel(logging.DEBUG)
    
    # Очищаем существующие обработчики
    logger.handlers.clear()
    
    # Формат логов для файла (без цветов)
    file_formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    # Форматтер для консоли (с цветами)
    console_formatter = ColoredFormatter(use_colors=True)
    
    # Обработчик для записи в файл с ротацией
    file_handler = RotatingFileHandler(
        str(log_filename),
        maxBytes=10 * 1024 * 1024,  # 10 МБ
        backupCount=5,
        encoding='utf-8'
    )
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(file_formatter)
    
    # Обработчик для вывода в консоль с цветами
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    console_handler.setFormatter(console_formatter)
    
    # Добавляем обработчики к логгеру
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)
    
    return logger

