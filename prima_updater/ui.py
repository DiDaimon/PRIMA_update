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
    ACTION_UPDATE_ALL = 1
    ACTION_ADDITIONAL = 2
    ACTION_RESTORE_BACKUP = 3
    ACTION_SKIP = 4
    # Дополнительные действия (из подменю)
    ACTION_UPDATE_CHANGED = 11
    ACTION_COPY_MISSING = 12
    ACTION_FULL_COPY = 13
    # Подварианты полного копирования
    ACTION_FULL_COPY_IGNORE = 20
    ACTION_FULL_COPY_KEEP_PRIMA = 21
    ACTION_FULL_COPY_KEEP_SERVERS = 22
    ACTION_FULL_COPY_KEEP_BOTH = 23
    ACTION_FULL_COPY_OVERWRITE_ALL = 24
    
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
        self.logger.info('Проверка наличия изменений...')
        
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
    
    def show_menu(self) -> int:
        """Отображает главное меню выбора действий и возвращает выбор пользователя.
        
        Returns:
            int: Выбранное действие
        """
        print('\n' + '=' * 60)
        print(' ' * 20 + 'ВЫБЕРИТЕ ДЕЙСТВИЕ')
        print('=' * 60)
        print()
        
        print('📦 ОБНОВЛЕНИЕ:')
        print('  [1] Обновить все')
        print('  [2] Дополнительно')
        print()
        print('💾 ВОССТАНОВЛЕНИЕ:')
        print('  [3] Восстановить из бэкапа')
        print()
        
        print('❌ ОТМЕНА:')
        print('  [4] Пропустить обновление')
        print()
        print('=' * 60)
        print()
        
        max_choice = 4
        
        while True:
            try:
                answer = input('Выберите действие: ')
                if answer.isdecimal():
                    choice = int(answer)
                    if 1 <= choice <= max_choice:
                        # Преобразуем выбор пользователя в константу действия
                        if choice == 1:
                            action = self.ACTION_UPDATE_ALL
                        elif choice == 2:
                            action = self.ACTION_ADDITIONAL
                        elif choice == 3:
                            action = self.ACTION_RESTORE_BACKUP
                        elif choice == 4:
                            action = self.ACTION_SKIP
                        else:
                            action = choice
                        
                        self.logger.debug(f"Пользователь выбрал действие: {action}")
                        return action
                self.logger.debug(f"Неверный ввод от пользователя: '{answer}'")
                self.logger.warning('Неверный ввод, повторите')
            except (ValueError, KeyboardInterrupt) as e:
                self.logger.debug(f"Ошибка ввода: {type(e).__name__}")
                self.logger.warning('Неверный ввод, повторите')
    
    def show_additional_menu(self) -> int:
        """Отображает подменю дополнительных опций обновления.
        
        Returns:
            int: Выбранное действие из подменю
        """
        print('\n' + '=' * 60)
        print(' ' * 15 + 'ДОПОЛНИТЕЛЬНЫЕ ОПЦИИ')
        print('=' * 60)
        print()
        print('📦 ОБНОВЛЕНИЕ:')
        print('  [1] Обновить только измененные файлы')
        print('  [2] Скопировать только отсутствующие файлы')
        print('  [3] Полное копирование директории')
        print()
        print('  [0] Назад в главное меню')
        print()
        print('=' * 60)
        print()
        
        while True:
            try:
                answer = input('Выберите действие: ')
                if answer.isdecimal():
                    choice = int(answer)
                    if choice == 0:
                        self.logger.debug("Пользователь вернулся в главное меню")
                        return -1  # Специальное значение для возврата в главное меню
                    elif choice == 1:
                        self.logger.debug("Пользователь выбрал: Обновить только измененные файлы")
                        return self.ACTION_UPDATE_CHANGED
                    elif choice == 2:
                        self.logger.debug("Пользователь выбрал: Скопировать только отсутствующие файлы")
                        return self.ACTION_COPY_MISSING
                    elif choice == 3:
                        self.logger.debug("Пользователь выбрал: Полное копирование директории")
                        return self.ACTION_FULL_COPY
                self.logger.debug(f"Неверный ввод от пользователя: '{answer}'")
                self.logger.warning('Неверный ввод, повторите')
            except (ValueError, KeyboardInterrupt) as e:
                self.logger.debug(f"Ошибка ввода: {type(e).__name__}")
                self.logger.warning('Неверный ввод, повторите')
    
    def show_full_copy_options(self, local_dir: str) -> int:
        """Отображает варианты полного копирования в зависимости от наличия ini-файлов.
        
        Args:
            local_dir (str): Путь к целевой директории
        
        Returns:
            int: Константа действия полного копирования или -1 для возврата
        """
        local_path = Path(local_dir)
        has_prima_ini = (local_path / 'PRIMA.ini').exists()
        has_servers_ini = (local_path / 'Servers.ini').exists()
        
        print('\n' + '=' * 60)
        print(' ' * 12 + 'ПАРАМЕТРЫ ПОЛНОГО КОПИРОВАНИЯ')
        print('=' * 60)
        print()
        
        if has_prima_ini or has_servers_ini:
            print('Обнаружены конфигурационные файлы в целевой директории:')
            if has_prima_ini:
                print('  • PRIMA.ini')
            if has_servers_ini:
                print('  • Servers.ini')
            print()
            print('Выберите вариант:')
            print('  [1] Полное копирование (ignore-лист включен)')
            print('  [2] Не игнорировать PRIMA.ini')
            print('  [3] Не игнорировать Servers.ini')
            print('  [4] Не игнорировать PRIMA.ini и Servers.ini')
            print('  [5] Полное копирование (переписать все)')
            print('  [0] Назад')
            print()
            
            while True:
                try:
                    answer = input('Выберите действие: ')
                    if answer.isdecimal():
                        choice = int(answer)
                        if choice == 0:
                            return -1
                        if choice == 1:
                            return self.ACTION_FULL_COPY_IGNORE
                        if choice == 2:
                            return self.ACTION_FULL_COPY_KEEP_PRIMA
                        if choice == 3:
                            return self.ACTION_FULL_COPY_KEEP_SERVERS
                        if choice == 4:
                            return self.ACTION_FULL_COPY_KEEP_BOTH
                        if choice == 5:
                            return self.ACTION_FULL_COPY_OVERWRITE_ALL
                    self.logger.debug(f"Неверный ввод при выборе полного копирования: '{answer}'")
                    self.logger.warning('Неверный ввод, повторите')
                except (ValueError, KeyboardInterrupt) as e:
                    self.logger.debug(f"Ошибка ввода при полном копировании: {type(e).__name__}")
                    self.logger.warning('Неверный ввод, повторите')
        else:
            print('Конфигурационные файлы PRIMA.ini и Servers.ini не найдены.')
            print('Выберите вариант:')
            print('  [1] Полное копирование (переписать все)')
            print('  [0] Назад')
            print()
            
            while True:
                try:
                    answer = input('Выберите действие: ')
                    if answer.isdecimal():
                        choice = int(answer)
                        if choice == 0:
                            return -1
                        if choice == 1:
                            return self.ACTION_FULL_COPY_OVERWRITE_ALL
                    self.logger.debug(f"Неверный ввод при выборе полного копирования: '{answer}'")
                    self.logger.warning('Неверный ввод, повторите')
                except (ValueError, KeyboardInterrupt) as e:
                    self.logger.debug(f"Ошибка ввода при полном копировании: {type(e).__name__}")
                    self.logger.warning('Неверный ввод, повторите')
    
    def confirm_full_copy_overwrite(self) -> bool:
        """Подтверждение для режима полного переписывания всех файлов."""
        while True:
            try:
                answer = input('Переписать всю директорию без исключений? [Y/N]: ').strip().lower()
                if answer in ('y', 'yes', 'д', 'да'):
                    return True
                if answer in ('n', 'no', 'н', 'нет'):
                    return False
                self.logger.debug(f"Неверный ввод при подтверждении: '{answer}'")
                self.logger.warning('Введите Y или N')
            except (ValueError, KeyboardInterrupt):
                return False
    
    def show_restore_filters(self, years: list[int] | None = None):
        """Отображает подменю фильтров для восстановления из бэкапа.
        
        Возвращает одно из:
        - ('current_month', None)
        - ('current_year', None)
        - ('older_year', year:int)
        - None — если выбран 'Назад'
        """
        while True:
            print('\n' + '=' * 60)
            print(' ' * 14 + 'ФИЛЬТРЫ ВОССТАНОВЛЕНИЯ')
            print('=' * 60)
            print()
            print('💾 ВОССТАНОВЛЕНИЕ:')
            print('  [1] Текущий месяц')
            print('  [2] Текущий год')
            print('  [3] Старше')
            print()
            print('  [0] Назад')
            print()
            print('=' * 60)
            print()
            
            try:
                answer = input('Выберите фильтр: ')
                if answer.isdecimal():
                    choice = int(answer)
                    if choice == 0:
                        self.logger.debug("Фильтр восстановления: Назад (в главное меню)")
                        return None
                    if choice == 1:
                        self.logger.debug("Фильтр восстановления: Текущий месяц")
                        return ('current_month', None)
                    if choice == 2:
                        self.logger.debug("Фильтр восстановления: Текущий год")
                        return ('current_year', None)
                    if choice == 3:
                        # Подменю выбора года для "Старше"
                        res = self._show_restore_older_years(years or [])
                        if res is None:
                            # Назад из подменю годов — показать снова это меню
                            continue
                        return res
                self.logger.debug(f"Неверный ввод при выборе фильтра восстановления: '{answer}'")
                self.logger.warning('Неверный ввод, повторите')
            except (ValueError, KeyboardInterrupt) as e:
                self.logger.debug(f"Ошибка ввода при выборе фильтра восстановления: {type(e).__name__}")
                self.logger.warning('Неверный ввод, повторите')
    
    def _show_restore_older_years(self, years: list[int]):
        """Подменю выбора года для фильтра 'Старше'."""
        print('\n' + '=' * 60)
        print(' ' * 10 + 'СТАРШЕ ТЕКУЩЕГО МЕСЯЦА — ВЫБОР ГОДА')
        print('=' * 60)
        print()
        if not years:
            print('Нет бэкапов старше текущего месяца.')
            print()
            print('  [0] Назад')
            print()
            print('=' * 60)
            while True:
                answer = input('Нажмите 0 для возврата: ')
                if answer == '0':
                    return None
                self.logger.warning('Неверный ввод, повторите')
        
        print('Выберите год:')
        for idx, y in enumerate(years, 1):
            print(f'  [{idx}] {y}')
        print()
        print('  [0] Назад')
        print()
        print('=' * 60)
        print()
        
        while True:
            try:
                answer = input('Выберите год: ')
                if answer.isdecimal():
                    choice = int(answer)
                    if choice == 0:
                        return None
                    if 1 <= choice <= len(years):
                        year = years[choice - 1]
                        self.logger.debug(f"Фильтр восстановления: Старше, год={year}")
                        return ('older_year', year)
                self.logger.debug(f"Неверный ввод при выборе года: '{answer}'")
                self.logger.warning('Неверный ввод, повторите')
            except (ValueError, KeyboardInterrupt) as e:
                self.logger.debug(f"Ошибка ввода при выборе года: {type(e).__name__}")
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
            print('\n' + '=' * 60)
            print(' ' * 16 + 'ДОСТУПНЫЕ БЭКАПЫ')
            print('=' * 60)
            print('\nБэкапы не найдены.')
            print('\n  [0] Назад')
            print('\n' + '=' * 60)
            return -1
        
        self.logger.info(f"Отображение списка бэкапов. Найдено бэкапов: {len(backups)}")
        print('\n' + '=' * 60)
        print(' ' * 16 + 'ДОСТУПНЫЕ БЭКАПЫ')
        print('=' * 60)
        print()
        for i, backup in enumerate(backups, 1):
            backup_time = datetime.fromtimestamp(backup.stat().st_mtime)
            backup_date = backup_time.strftime('%d.%m.%Y %H:%M')
            print(f'  [{i}] {backup.name}  —  {backup_date}')
        print()
        print('  [0] Назад')
        print()
        print('=' * 60)
        
        while True:
            try:
                answer = input('Выберите бэкап для восстановления: ')
                if answer.isdecimal():
                    choice = int(answer)
                    if choice == 0:
                        self.logger.debug("Пользователь вернулся назад из списка бэкапов")
                        return -1
                    if 1 <= choice <= len(backups):
                        selected_backup = backups[choice - 1]
                        self.logger.debug(f"Пользователь выбрал бэкап для восстановления: {selected_backup.name}")
                        return choice - 1
                self.logger.debug(f"Неверный ввод при выборе бэкапа: '{answer}'")
                self.logger.warning('Неверный ввод, повторите')
            except (ValueError, KeyboardInterrupt) as e:
                self.logger.debug(f"Ошибка ввода при выборе бэкапа: {type(e).__name__}")
                self.logger.warning('Неверный ввод, повторите')

