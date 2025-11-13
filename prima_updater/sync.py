# -*- coding: utf-8 -*-
"""Модуль для синхронизации файлов между сервером и локальной директорией.

Этот модуль содержит класс FileSync для сравнения директорий и копирования файлов.
"""

import logging
import shutil
from filecmp import dircmp
from pathlib import Path
from typing import List, Union

from rich.progress import (
    BarColumn,
    Progress,
    SpinnerColumn,
    TextColumn,
    TimeElapsedColumn,
)

from .rich_console import get_console


class FileSync:
    """Класс для синхронизации файлов между сервером и локальной директорией.
    
    Обеспечивает сравнение директорий, определение измененных и отсутствующих файлов,
    а также их копирование.
    """
    
    def __init__(self, source_dir: Union[str, Path], destination_dir: Union[str, Path], ignore_list: List[str], logger: logging.Logger = None):
        """Инициализация синхронизатора файлов.
        
        Args:
            source_dir (Union[str, Path]): Путь к исходной директории (сервер)
            destination_dir (Union[str, Path]): Путь к целевой директории (локально)
            ignore_list (List[str]): Список файлов и папок для игнорирования
            logger (logging.Logger, optional): Логгер для записи сообщений
        """
        self.source_dir = str(source_dir) if isinstance(source_dir, Path) else source_dir
        self.destination_dir = str(destination_dir) if isinstance(destination_dir, Path) else destination_dir
        self.ignore_list = ignore_list
        self.logger = logger or logging.getLogger('PRIMA_Updater')
        self.console = get_console()
    
    def compare_directories(self) -> tuple[List[str], List[str]]:
        """Сравнивает две директории и находит различия.
        
        Находит файлы, которые были изменены или отсутствуют в целевой директории.
        
        Returns:
            tuple[List[str], List[str]]: Кортеж из двух списков:
                - список измененных файлов
                - список отсутствующих файлов
        """
        diff_list = []
        only_list = []
        
        # Создаем объект сравнения директорий
        dcmp = dircmp(self.source_dir, self.destination_dir, self.ignore_list)
        
        # Рекурсивно находим все различия
        self._find_differences(dcmp, diff_list, only_list)
        
        return diff_list, only_list
    
    def _find_differences(self, dcmp: dircmp, diff_list: List[str], only_list: List[str]):
        """Рекурсивно находит различия между директориями.
        
        Args:
            dcmp (dircmp): Объект сравнения директорий
            diff_list (List[str]): Список для хранения измененных файлов
            only_list (List[str]): Список для хранения отсутствующих файлов
        """
        # Обрабатываем измененные файлы
        if dcmp.diff_files:
            for file in dcmp.diff_files:
                file_path = str(Path(dcmp.left) / file)
                self.logger.debug(f"Файл изменен: {file_path}")
                diff_list.append(file_path)
        
        # Обрабатываем отсутствующие файлы
        if dcmp.left_only:
            for file in dcmp.left_only:
                file_path = str(Path(dcmp.left) / file)
                self.logger.debug(f"Файл отсутствует: {file_path}")
                only_list.append(file_path)
        
        # Рекурсивно обрабатываем поддиректории
        for sub_dcmp in dcmp.subdirs.values():
            self._find_differences(sub_dcmp, diff_list, only_list)
    
    def copy_files(self, file_paths: List[str]) -> bool:
        """Копирует указанные файлы из исходной директории в целевую.
        
        Args:
            file_paths (List[str]): Список путей к файлам для копирования
        
        Returns:
            bool: True если все файлы скопированы успешно, False в противном случае
        """
        success = True
        source_path = Path(self.source_dir)
        dest_path = Path(self.destination_dir)

        if not file_paths:
            return True

        progress_columns = (
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            BarColumn(),
            TextColumn("[progress.percentage]{task.percentage:>3.0f}%"),
            TimeElapsedColumn(),
        )

        with Progress(*progress_columns, console=self.console, transient=True) as progress:
            task = progress.add_task("[info]Подготовка...", total=len(file_paths))

            for file_path_str in file_paths:
                try:
                    file_path = Path(file_path_str)

                    # Формируем путь назначения
                    relative_path = file_path.relative_to(source_path)
                    destination = dest_path / relative_path

                    # Создаем директорию назначения, если её нет
                    destination.parent.mkdir(parents=True, exist_ok=True)

                    description = f"[info]Копирование: {relative_path.as_posix()}"
                    progress.update(task, description=description)

                    # Копируем файл или директорию
                    if file_path.is_dir():
                        if destination.exists():
                            shutil.rmtree(str(destination))
                        shutil.copytree(str(file_path), str(destination))
                        self.logger.info("Каталог скопирован: %s", destination)
                    else:
                        shutil.copy2(str(file_path), str(destination))
                        self.logger.info("Файл скопирован: %s", destination)

                except PermissionError as e:
                    self.logger.error("Нет прав доступа для копирования %s: %s", file_path_str, e)
                    success = False
                except OSError as e:
                    self.logger.error("Ошибка при копировании %s: %s", file_path_str, e)
                    success = False
                except Exception as e:
                    self.logger.error("Неожиданная ошибка при копировании %s: %s", file_path_str, e)
                    success = False
                finally:
                    progress.advance(task)

        return success
    
    def copy_all(self, remove_from_ignore: list | None = None, overwrite_all: bool = False) -> bool:
        """Копирует всю директорию из исходной в целевую.
        
        Выполняет полное копирование всех файлов и поддиректорий.
        
        Returns:
            bool: True если копирование успешно, False в противном случае
        """
        dest_path = Path(self.destination_dir)

        status_message = "[info]Подготовка полного копирования..."
        with self.console.status(status_message, spinner="dots") as status:
            try:
                # Полное переписывание всего без игнор-листа
                if overwrite_all:
                    status.update("[info]Удаление существующей директории...[/info]")
                    if dest_path.exists():
                        shutil.rmtree(str(dest_path))
                    status.update("[info]Копирование всех файлов...[/info]")
                    shutil.copytree(self.source_dir, str(dest_path))
                    self.logger.info("Полное копирование (переписать все) завершено: %s", self.destination_dir)
                    return True

                effective_ignore = list(self.ignore_list)
                if remove_from_ignore:
                    effective_ignore = [x for x in effective_ignore if x not in remove_from_ignore]

                status.update("[info]Очистка целевой директории...[/info]")
                if dest_path.exists():
                    shutil.rmtree(str(dest_path))

                status.update("[info]Копирование с учётом ignore-листа...[/info]")
                shutil.copytree(
                    self.source_dir,
                    str(dest_path),
                    ignore=shutil.ignore_patterns(*effective_ignore) if effective_ignore else None,
                )
                self.logger.info("Полное копирование завершено: %s", self.destination_dir)
                return True

            except Exception as e:
                self.logger.error("Ошибка при полном копировании: %s", e)
                return False

