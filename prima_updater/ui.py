# -*- coding: utf-8 -*-
"""Модуль пользовательского интерфейса.

Этот модуль содержит функции для взаимодействия с пользователем:
отображение меню, выбор действий, вывод сообщений с цветовой индикацией.
"""

import os
import logging
from datetime import datetime
from pathlib import Path
from typing import Union
from art import tprint
from colorama import init


class UserInterface:
    """Класс для управления пользовательским интерфейсом.
    
    Обеспечивает отображение меню, обработку пользовательского ввода
    и вывод сообщений с цветовой индикацией.
    """
    
    # Константы для выбора действий
    ACTION_UPDATE_CHANGED = 1
    ACTION_COPY_MISSING = 2
    ACTION_UPDATE_ALL = 3
    ACTION_FULL_COPY = 4
    ACTION_SKIP = 5
    ACTION_RESTORE_BACKUP = 6
    
    def __init__(self, logger: logging.Logger = None):
        """Инициализация пользовательского интерфейса.
        
        Args:
            logger (logging.Logger, optional): Логгер для записи сообщений
        """
        self.logger = logger or logging.getLogger('PRIMA_Updater')
        # Инициализируем colorama для поддержки цветов в Windows
        init(autoreset=True)
        
        # Цветовые константы больше не нужны, так как используется цветное логирование
    
    def clear_terminal(self):
        """Очищает экран терминала.
        
        Выполняет команду очистки экрана в зависимости от операционной системы.
        """
        os.system('cls' if os.name == 'nt' else 'clear')
    
    def show_header(self):
        """Отображает заголовок программы.
        
        Очищает экран и выводит название программы в ASCII-арте.
        """
        self.clear_terminal()
        tprint('PRIMA - UPDATER', font='tarty1')
    
    def show_changes(self, diff_files: list, only_files: list):
        """Отображает список найденных изменений.
        
        Args:
            diff_files (list): Список измененных файлов
            only_files (list): Список отсутствующих файлов
        """
        self.logger.info('\nПроверка наличия изменений:')
        
        if not diff_files and not only_files:
            self.logger.info("Изменений не обнаружено")
            return
        
        # Логируем общую информацию о найденных изменениях
        self.logger.info(f"Найдено изменений: измененных файлов - {len(diff_files)}, отсутствующих файлов - {len(only_files)}")
        
        # Выводим измененные файлы
        for file_path in diff_files:
            file_name = Path(file_path).name
            self.logger.warning(f"[*] Файл изменен: {file_name}")
        
        # Выводим отсутствующие файлы
        for file_path in only_files:
            file_name = Path(file_path).name
            self.logger.warning(f"[-] Файл отсутствует: {file_name}")
    
    def show_menu(self, has_backups: bool = False) -> int:
        """Отображает меню выбора действий и возвращает выбор пользователя.
        
        Args:
            has_backups (bool): Показывать ли опцию восстановления из бэкапа
        
        Returns:
            int: Выбранное действие (1-6)
        """
        menu_items = [
            '[1] Для замены измененных файлов.',
            '[2] Для копирования отсутствующих файлов.',
            '[3] Для внесения всех изменений.',
            '[4] Для полного копирования.',
            '[5] Для пропуска (без изменений).'
        ]
        
        if has_backups:
            menu_items.append('[6] Для восстановления из бэкапа.')
        
        print('\nВыберите действие и нажмите Enter:')
        for item in menu_items:
            print(f' {item}')
        print()
        
        max_choice = 6 if has_backups else 5
        
        while True:
            try:
                answer = input('Выберите действие: ')
                if answer.isdecimal():
                    choice = int(answer)
                    if self.ACTION_UPDATE_CHANGED <= choice <= max_choice:
                        self.logger.debug(f"Пользователь выбрал действие: {choice}")
                        return choice
                self.logger.debug(f"Неверный ввод от пользователя: '{answer}'")
                self.logger.warning('Неверный ввод, повторите')
            except (ValueError, KeyboardInterrupt) as e:
                self.logger.debug(f"Ошибка ввода: {type(e).__name__}")
                self.logger.warning('Неверный ввод, повторите')
    
    def update_shortcut(self, desktop_path: str, prima_exe_path: Union[str, Path]) -> bool:
        """Обновляет ярлык на рабочем столе с новой датой версии.
        
        Args:
            desktop_path (str): Путь к рабочему столу
            prima_exe_path (Union[str, Path]): Путь к файлу PRIMA.exe
        
        Returns:
            bool: True если ярлык обновлен, False в противном случае
        """
        prima_path = Path(prima_exe_path)
        desktop_path_obj = Path(desktop_path)
        
        if not prima_path.exists():
            self.logger.error(f"Файл PRIMA.exe не найден: {prima_exe_path}")
            return False
        
        try:
            # Получаем дату изменения файла
            date_change = prima_path.stat().st_mtime
            new_date = datetime.fromtimestamp(date_change).strftime('%d.%m.%y')
            
            # Ищем существующий ярлык
            for file_path in desktop_path_obj.iterdir():
                if '[PRIMA]' in file_path.name and file_path.suffix == '.lnk':
                    old_name = file_path.name
                    new_name = f'[PRIMA] {new_date}.lnk'
                    new_path = desktop_path_obj / new_name
                    
                    # Проверяем, нужно ли обновлять
                    if new_date in old_name:
                        self.logger.debug("Ярлык уже актуален")
                        return True
                    
                    # Переименовываем ярлык
                    file_path.rename(new_path)
                    self.logger.info(f"Ярлык на Рабочем столе изменен на {new_name}")
                    return True
            
            self.logger.warning("Ярлык на рабочем столе не найден")
            return False
            
        except Exception as e:
            self.logger.error(f"Ошибка при обновлении ярлыка: {e}")
            return False
    
    def show_backup_list(self, backups: list) -> int:
        """Отображает список бэкапов для выбора.
        
        Args:
            backups (list): Список путей к бэкапам
        
        Returns:
            int: Индекс выбранного бэкапа или -1 если отменено
        """
        if not backups:
            self.logger.warning("Бэкапы не найдены для восстановления")
            return -1
        
        self.logger.info(f"Отображение списка бэкапов. Найдено бэкапов: {len(backups)}")
        self.logger.info('\nДоступные бэкапы:')
        for i, backup in enumerate(backups, 1):
            backup_time = datetime.fromtimestamp(backup.stat().st_mtime)
            backup_date = backup_time.strftime('%d.%m.%Y %H:%M')
            self.logger.info(f' [{i}] {backup.name} (создан: {backup_date})')
        
        self.logger.info(' [0] Отмена')
        
        while True:
            try:
                answer = input('\nВыберите бэкап для восстановления: ')
                if answer.isdecimal():
                    choice = int(answer)
                    if choice == 0:
                        self.logger.info("Пользователь отменил выбор бэкапа")
                        return -1
                    if 1 <= choice <= len(backups):
                        selected_backup = backups[choice - 1]
                        self.logger.info(f"Пользователь выбрал бэкап для восстановления: {selected_backup.name}")
                        return choice - 1
                self.logger.debug(f"Неверный ввод при выборе бэкапа: '{answer}'")
                self.logger.warning('Неверный ввод, повторите')
            except (ValueError, KeyboardInterrupt) as e:
                self.logger.debug(f"Ошибка ввода при выборе бэкапа: {type(e).__name__}")
                self.logger.warning('Неверный ввод, повторите')

