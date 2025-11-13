# -*- coding: utf-8 -*-
"""Модуль для логирования работы приложения.

Этот модуль настраивает систему логирования с записью в файл и выводом в консоль.
"""

import logging
from datetime import datetime
from pathlib import Path
from typing import Union
from logging.handlers import RotatingFileHandler

from rich.logging import RichHandler

from .rich_console import get_console


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
    log_filename = log_path / f"prima_update_{datetime.now().strftime('%Y_%m_%d')}.log"
    
    # Создаем логгер
    logger = logging.getLogger('PRIMA_Updater')
    logger.setLevel(logging.DEBUG)
    
    # Очищаем существующие обработчики
    logger.handlers.clear()
    
    # Формат логов для файла (без цветов)
    file_formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%d.%m.%Y %H:%M:%S'
    )
    
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
    console = get_console(record=True, log_path=str(log_filename))
    console_handler = RichHandler(
        console=console,
        rich_tracebacks=True,
        show_path=False,
        markup=True,
        omit_repeated_times=False,
        log_time_format='%d.%m.%Y %H:%M:%S',
    )
    console_handler.setLevel(logging.INFO)
    console_handler.setFormatter(logging.Formatter("%(message)s"))
    
    # Добавляем обработчики к логгеру
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)
    
    return logger

