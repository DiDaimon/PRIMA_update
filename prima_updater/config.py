# -*- coding: utf-8 -*-
"""Модуль для работы с конфигурацией приложения.

Этот модуль содержит класс Config, который управляет всеми настройками приложения.
Настройки хранятся в коде, а не в отдельном файле settings.ini.
"""

from pathlib import Path


class Config:
    """Класс для хранения и управления конфигурацией приложения.
    
    Содержит все необходимые пути, списки игнорируемых файлов и другие настройки.
    Все настройки централизованы в этом классе.
    """
    
    # Путь к директории на сервере
    SERVER_DIRECTORY = r"\\tserver1\RSU\PRIMA"
    
    # Путь к локальной директории
    LOCAL_DIRECTORY = r"D:\User\PRIMA_Updated"
    
    # Список файлов и папок для игнорирования при синхронизации
    IGNORE_LIST = [
        'tract',
        'PRIMA.ini',
        'Servers.ini',
        'DTConfig.stc',
        'DebugTranslate.log',
        'PRIMA.ethl.log',
        'PRIMA.mport.log'
    ]
    
    # Имя исполняемого файла PRIMA
    PRIMA_EXE = "PRIMA.exe"
    
    # Путь к рабочему столу пользователя
    DESKTOP_PATH = None
    
    # Директория для логов и бэкапов (по умолчанию - папки проекта)
    LOGS_DIRECTORY = str((Path(__file__).resolve().parent.parent / 'logs'))
    BACKUPS_DIRECTORY = str((Path(__file__).resolve().parent.parent / 'backups'))
    
    def __init__(self):
        """Инициализация конфигурации.
        
        Устанавливает путь к рабочему столу пользователя.
        """
        self.DESKTOP_PATH = str(Path.home() / 'Desktop')
    
    @property
    def server_directory(self) -> str:
        """Возвращает путь к директории на сервере.
        
        Returns:
            str: Путь к серверной директории
        """
        return self.SERVER_DIRECTORY
    
    @property
    def local_directory(self) -> str:
        """Возвращает путь к локальной директории.
        
        Returns:
            str: Путь к локальной директории
        """
        return self.LOCAL_DIRECTORY
    
    @property
    def ignore_list(self) -> list:
        """Возвращает список файлов и папок для игнорирования.
        
        Returns:
            list: Список имен файлов и папок для игнорирования
        """
        return self.IGNORE_LIST
    
    @property
    def prima_exe(self) -> str:
        """Возвращает имя исполняемого файла PRIMA.
        
        Returns:
            str: Имя файла PRIMA.exe
        """
        return self.PRIMA_EXE
    
    @property
    def desktop_path(self) -> str:
        """Возвращает путь к рабочему столу пользователя.
        
        Returns:
            str: Путь к рабочему столу
        """
        return self.DESKTOP_PATH
    
    def get_prima_exe_path(self) -> Path:
        """Возвращает полный путь к файлу PRIMA.exe в локальной директории.
        
        Returns:
            Path: Полный путь к PRIMA.exe
        """
        return Path(self.local_directory) / self.prima_exe
    
    @property
    def logs_directory(self) -> str:
        """Возвращает путь к директории для логов.
        
        Returns:
            str: Путь к директории логов
        """
        return self.LOGS_DIRECTORY
    
    @property
    def backups_directory(self) -> str:
        """Возвращает путь к директории для бэкапов.
        
        Returns:
            str: Путь к директории бэкапов
        """
        return self.BACKUPS_DIRECTORY

