"""Модуль пользовательского интерфейса.

Этот модуль содержит функции для взаимодействия с пользователем:
отображение меню, выбор действий, вывод сообщений в консоли Rich.
"""

import logging
from datetime import datetime
from pathlib import Path
from typing import Union

from art import text2art
from rich.align import Align
from rich.panel import Panel
from rich.prompt import Confirm, Prompt
from rich.table import Table

from .rich_console import get_console


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
        self.console = get_console()
    
    def clear_terminal(self):
        """Очищает экран терминала."""
        self.console.clear()
    
    def show_header(self):
        """Отображает заголовок программы в панели Rich."""
        self.clear_terminal()
        header_text = text2art('PRIMA - UPDATER', font='tarty1')
        panel = Panel(
            Align.center(header_text.rstrip(), vertical="middle"),
            title="[menu.title]PRIMA Updater[/menu.title]",
            border_style="menu.title"
        )
        self.console.print(panel)
    
    def _render_changes_table(self, diff_files: list, only_files: list) -> Table:
        """Формирует таблицу с изменениями."""
        table = Table(
            title="[menu.title]Найденные изменения[/menu.title]",
            show_lines=False,
            header_style="bold magenta",
            expand=True,
        )
        table.add_column("Тип", style="info", width=14)
        table.add_column("Файл", style="menu.item", width=30, no_wrap=True)
        table.add_column("Путь", style="dim", overflow="fold")
        
        for file_path in diff_files:
            path = Path(file_path)
            table.add_row("Изменен", path.name, str(path.parent))
        
        for file_path in only_files:
            path = Path(file_path)
            table.add_row("Отсутствует", path.name, str(path.parent))
        
        return table
    
    def show_changes(self, diff_files: list, only_files: list):
        """Отображает список найденных изменений."""
        
        if not diff_files and not only_files:
            self.logger.info("Изменений не обнаружено")
            self.console.print(
                Panel("[info]Изменений не обнаружено[/info]", border_style="info")
            )
            return
        
        self.logger.info(
            "Найдено изменений: измененных файлов - %s, отсутствующих файлов - %s",
            len(diff_files),
            len(only_files),
        )
        
        table = self._render_changes_table(diff_files, only_files)
        self.console.print(table)
    
    def show_menu(self) -> int:
        """Отображает главное меню выбора действий и возвращает выбор пользователя.
        
        Returns:
            int: Выбранное действие
        """
        menu_items = [
            "[menu.hotkey][1][/menu.hotkey] [menu.item]Обновить все[/menu.item]",
            "[menu.hotkey][2][/menu.hotkey] [menu.item]Дополнительные опции[/menu.item]",
            "[menu.hotkey][3][/menu.hotkey] [menu.item]Восстановить из бэкапа[/menu.item]",
            "[menu.hotkey][4][/menu.hotkey] [menu.item]Пропустить обновление[/menu.item]",
        ]
        panel = Panel("\n".join(menu_items), title="[menu.title]Выберите действие[/menu.title]", border_style="menu.title")
        self.console.print(panel)
        
        choices = ["1", "2", "3", "4"]
        answer = Prompt.ask("Ваш выбор", choices=choices, default="1")
        choice = int(answer)
        
        mapping = {
            1: self.ACTION_UPDATE_ALL,
            2: self.ACTION_ADDITIONAL,
            3: self.ACTION_RESTORE_BACKUP,
            4: self.ACTION_SKIP,
        }
        action = mapping.get(choice, self.ACTION_SKIP)
        self.logger.debug("Пользователь выбрал действие: %s", action)
        return action
    
    def show_additional_menu(self) -> int:
        """Отображает подменю дополнительных опций обновления.
        
        Returns:
            int: Выбранное действие из подменю
        """
        menu_items = [
            "[menu.hotkey][1][/menu.hotkey] [menu.item]Обновить только измененные файлы[/menu.item]",
            "[menu.hotkey][2][/menu.hotkey] [menu.item]Скопировать только отсутствующие файлы[/menu.item]",
            "[menu.hotkey][3][/menu.hotkey] [menu.item]Полное копирование директории[/menu.item]",
            "[menu.hotkey][0][/menu.hotkey] [menu.item]Назад[/menu.item]",
        ]
        panel = Panel("\n".join(menu_items), title="[menu.title]Дополнительные опции[/menu.title]", border_style="menu.title")
        self.console.print(panel)
        
        choices = ["0", "1", "2", "3"]
        answer = Prompt.ask("Ваш выбор", choices=choices, default="0")
        choice = int(answer)
        
        mapping = {
            0: -1,
            1: self.ACTION_UPDATE_CHANGED,
            2: self.ACTION_COPY_MISSING,
            3: self.ACTION_FULL_COPY,
        }
        action = mapping.get(choice, -1)
        self.logger.debug("Пользователь выбрал дополнительное действие: %s", action)
        return action
    
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
        
        if has_prima_ini or has_servers_ini:
            items = [
                "[menu.hotkey][1][/menu.hotkey] Полное копирование (с учётом ignore-листа)",
                "[menu.hotkey][2][/menu.hotkey] Не игнорировать PRIMA.ini",
                "[menu.hotkey][3][/menu.hotkey] Не игнорировать Servers.ini",
                "[menu.hotkey][4][/menu.hotkey] Не игнорировать оба файла",
                "[menu.hotkey][5][/menu.hotkey] Полное копирование (переписать всё)",
                "[menu.hotkey][0][/menu.hotkey] Назад",
            ]
            files_detected = []
            if has_prima_ini:
                files_detected.append("[info]• PRIMA.ini[/info]")
            if has_servers_ini:
                files_detected.append("[info]• Servers.ini[/info]")
            header = "Обнаружены конфигурационные файлы:\n" + "\n".join(files_detected)
            panel = Panel(
                f"{header}\n\n" + "\n".join(items),
                title="[menu.title]Параметры полного копирования[/menu.title]",
                border_style="menu.title",
            )
            self.console.print(panel)
            choices = ["0", "1", "2", "3", "4", "5"]
            answer = Prompt.ask("Ваш выбор", choices=choices, default="0")
            choice = int(answer)
            mapping = {
                0: -1,
                1: self.ACTION_FULL_COPY_IGNORE,
                2: self.ACTION_FULL_COPY_KEEP_PRIMA,
                3: self.ACTION_FULL_COPY_KEEP_SERVERS,
                4: self.ACTION_FULL_COPY_KEEP_BOTH,
                5: self.ACTION_FULL_COPY_OVERWRITE_ALL,
            }
            result = mapping.get(choice, -1)
            self.logger.debug("Вариант полного копирования: %s", result)
            return result
        else:
            panel = Panel(
                "[info]Файлы PRIMA.ini и Servers.ini не найдены в целевой директории.[/info]\n\n"
                "[menu.hotkey][1][/menu.hotkey] Полное копирование (переписать всё)\n"
                "[menu.hotkey][0][/menu.hotkey] Назад",
                title="[menu.title]Параметры полного копирования[/menu.title]",
                border_style="menu.title",
            )
            self.console.print(panel)
            answer = Prompt.ask("Ваш выбор", choices=["0", "1"], default="0")
            choice = int(answer)
            mapping = {
                0: -1,
                1: self.ACTION_FULL_COPY_OVERWRITE_ALL,
            }
            result = mapping.get(choice, -1)
            self.logger.debug("Вариант полного копирования без ini-файлов: %s", result)
            return result
    
    def confirm_full_copy_overwrite(self) -> bool:
        """Подтверждение для режима полного переписывания всех файлов."""
        result = Confirm.ask(
            "Переписать всю директорию без исключений?", default=False, show_default=True
        )
        self.logger.debug("Подтверждение полного переписывания: %s", result)
        return result
    
    def show_restore_filters(self, years: list[int] | None = None):
        """Отображает подменю фильтров для восстановления из бэкапа.
        
        Возвращает одно из:
        - ('current_month', None)
        - ('current_year', None)
        - ('older_year', year:int)
        - None — если выбран 'Назад'
        """
        choices_panel = Panel(
            "[menu.hotkey][1][/menu.hotkey] Текущий месяц\n"
            "[menu.hotkey][2][/menu.hotkey] Текущий год\n"
            "[menu.hotkey][3][/menu.hotkey] Старше\n\n"
            "[menu.hotkey][0][/menu.hotkey] Назад",
            title="[menu.title]Фильтры восстановления[/menu.title]",
            border_style="menu.title",
        )
        self.console.print(choices_panel)
        
        choices = ["0", "1", "2", "3"]
        answer = Prompt.ask("Ваш выбор", choices=choices, default="0")
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
            res = self._show_restore_older_years(years or [])
            return res
        return None
    
    def _show_restore_older_years(self, years: list[int]):
        """Подменю выбора года для фильтра 'Старше'."""
        if not years:
            panel = Panel(
                "[warning]Нет бэкапов старше текущего месяца.[/warning]\n\n"
                "[menu.hotkey][0][/menu.hotkey] Назад",
                title="[menu.title]Старше текущего месяца[/menu.title]",
                border_style="menu.title",
            )
            self.console.print(panel)
            Prompt.ask("Нажмите 0 для возврата", choices=["0"], default="0")
            return None
        
        options = [f"[menu.hotkey][{idx}][/menu.hotkey] {year}" for idx, year in enumerate(years, 1)]
        panel = Panel(
            "\n".join(options) + "\n\n[menu.hotkey][0][/menu.hotkey] Назад",
            title="[menu.title]Выберите год[/menu.title]",
            border_style="menu.title",
        )
        self.console.print(panel)
        
        choices = ["0"] + [str(i) for i in range(1, len(years) + 1)]
        answer = Prompt.ask("Ваш выбор", choices=choices, default="0")
        choice = int(answer)
        
        if choice == 0:
            return None
        year = years[choice - 1]
        self.logger.debug("Фильтр восстановления: Старше, год=%s", year)
        return ('older_year', year)

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
            panel = Panel(
                "[warning]Бэкапы не найдены.[/warning]\n\n[menu.hotkey][0][/menu.hotkey] Назад",
                title="[menu.title]Доступные бэкапы[/menu.title]",
                border_style="menu.title",
            )
            self.console.print(panel)
            Prompt.ask("Нажмите 0 для возврата", choices=["0"], default="0")
            return -1
        
        self.logger.info("Отображение списка бэкапов. Найдено бэкапов: %s", len(backups))
        table = Table(
            title="[menu.title]Доступные бэкапы[/menu.title]",
            header_style="bold magenta",
            expand=True,
        )
        table.add_column("#", justify="center", style="menu.hotkey", width=4)
        table.add_column("Имя файла", style="menu.item", overflow="fold")
        table.add_column("Дата создания", style="info", width=20, justify="center")
        
        for index, backup in enumerate(backups, 1):
            backup_time = datetime.fromtimestamp(backup.stat().st_mtime)
            backup_date = backup_time.strftime('%d.%m.%Y %H:%M')
            table.add_row(str(index), backup.name, backup_date)
        table.add_row("0", "[dim]Отмена[/dim]", "[dim]-[/dim]")
        
        self.console.print(table)
        
        choices = ["0"] + [str(i) for i in range(1, len(backups) + 1)]
        answer = Prompt.ask("Выберите бэкап", choices=choices, default="0")
        choice = int(answer)
        
        if choice == 0:
            self.logger.debug("Пользователь вернулся назад из списка бэкапов")
            return -1
        
        selected_backup = backups[choice - 1]
        self.logger.debug("Пользователь выбрал бэкап для восстановления: %s", selected_backup.name)
        return choice - 1

