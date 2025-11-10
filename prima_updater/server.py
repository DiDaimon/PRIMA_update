# -*- coding: utf-8 -*-
"""Модуль для проверки доступности сервера.

Этот модуль содержит функции для проверки доступности сетевого сервера
и валидации путей перед началом синхронизации.
"""

import logging
from pathlib import Path
from typing import Union


def check_server_availability(server_path: Union[str, Path], logger: logging.Logger = None) -> bool:
    """Проверяет доступность сервера по указанному пути.
    
    Проверяет, доступен ли сетевой путь и можно ли к нему подключиться.
    
    Args:
        server_path (str): Путь к серверной директории
        logger (logging.Logger, optional): Логгер для записи сообщений
    
    Returns:
        bool: True если сервер доступен, False в противном случае
    """
    if logger is None:
        logger = logging.getLogger('PRIMA_Updater')
    
    try:
        server_path_obj = Path(server_path)
        
        # Проверяем существование пути
        if not server_path_obj.exists():
            logger.error(f"Серверный путь недоступен: {server_path}")
            return False
        
        # Проверяем, что это директория
        if not server_path_obj.is_dir():
            logger.error(f"Указанный путь не является директорией: {server_path}")
            return False
        
        # Пытаемся прочитать содержимое директории
        try:
            list(server_path_obj.iterdir())
            logger.info(f"Сервер доступен: {server_path}")
            return True
        except PermissionError:
            logger.error(f"Нет прав доступа к серверной директории: {server_path}")
            return False
        except OSError as e:
            logger.error(f"Ошибка доступа к серверу: {e}")
            return False
            
    except Exception as e:
        logger.error(f"Неожиданная ошибка при проверке сервера: {e}")
        return False


def validate_paths(server_path: Union[str, Path], local_path: Union[str, Path], logger: logging.Logger = None) -> bool:
    """Валидирует пути сервера и локальной директории.
    
    Проверяет корректность путей и возможность работы с ними.
    
    Args:
        server_path (Union[str, Path]): Путь к серверной директории
        local_path (Union[str, Path]): Путь к локальной директории
        logger (logging.Logger, optional): Логгер для записи сообщений
    
    Returns:
        bool: True если пути валидны, False в противном случае
    """
    if logger is None:
        logger = logging.getLogger('PRIMA_Updater')
    
    # Проверяем серверный путь
    if not check_server_availability(server_path, logger):
        return False
    
    # Проверяем локальный путь
    try:
        local_path_obj = Path(local_path) if not isinstance(local_path, Path) else local_path
        
        # Создаем локальную директорию, если её нет
        if not local_path_obj.exists():
            local_path_obj.mkdir(parents=True, exist_ok=True)
            logger.info(f"Создана локальная директория: {local_path_obj}")
        
        # Проверяем права на запись
        test_file = local_path_obj / '.write_test'
        try:
            test_file.write_text('test')
            test_file.unlink()
            logger.info(f"Локальная директория доступна для записи: {local_path_obj}")
            return True
        except PermissionError:
            logger.error(f"Нет прав на запись в локальную директорию: {local_path_obj}")
            return False
            
    except Exception as e:
        logger.error(f"Ошибка при валидации локального пути: {e}")
        return False

