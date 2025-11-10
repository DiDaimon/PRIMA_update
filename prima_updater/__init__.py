# -*- coding: utf-8 -*-
"""Пакет PRIMA Updater.

Пакет для обновления PRIMA с сервера.
"""

__version__ = "1.0.0"

# Импортируем основные классы для удобства использования
from prima_updater.config import Config
from prima_updater.logger import setup_logging
from prima_updater.server import check_server_availability, validate_paths
from prima_updater.backup import BackupManager
from prima_updater.sync import FileSync
from prima_updater.ui import UserInterface

__all__ = [
    'Config',
    'setup_logging',
    'check_server_availability',
    'validate_paths',
    'BackupManager',
    'FileSync',
    'UserInterface',
]

