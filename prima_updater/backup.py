# -*- coding: utf-8 -*-
"""Модуль для управления бэкапами PRIMA.exe.

Этот модуль содержит класс BackupManager для создания, управления и восстановления
бэкапов файла PRIMA.exe с автоматической очисткой старых бэкапов.
"""

import shutil
import logging
from datetime import datetime, timedelta
from pathlib import Path
from typing import Optional, List, Union


class BackupManager:
    """Класс для управления бэкапами файла PRIMA.exe.
    
    Обеспечивает создание бэкапов, автоматическую очистку старых бэкапов
    согласно правилам хранения и восстановление из бэкапа.
    """
    
    def __init__(self, prima_exe_path: Union[str, Path], backup_directory: Union[str, Path] = None, logger: logging.Logger = None):
        """Инициализация менеджера бэкапов.
        
        Args:
            prima_exe_path (Union[str, Path]): Полный путь к файлу PRIMA.exe
            backup_directory (Union[str, Path], optional): Директория для хранения бэкапов. Если ее нет создается.
            logger (logging.Logger, optional): Логгер для записи сообщений
        """
        self.prima_exe_path = Path(prima_exe_path)

        self.backup_directory = Path(backup_directory)
        self.backup_directory.mkdir(parents=True, exist_ok=True)

        self.logger = logger or logging.getLogger('PRIMA_Updater')
        self.prima_exe_name = self.prima_exe_path.name
    
    @property
    def create_backup(self) -> Optional[Path]:
        """Создает бэкап файла PRIMA.exe.
        
        Создает копию файла с именем PRIMA[DD.MM.YY].exe, где DD.MM.YY - дата изменения файла.
        Если бэкап с такой датой уже существует и актуален, новый не создается.
        
        Returns:
            Optional[Path]: Путь к созданному бэкапу или None в случае ошибки
        """
        if not self.prima_exe_path.exists():
            self.logger.error(f"Файл PRIMA.exe не найден: {self.prima_exe_path}")
            return None
        
        try:
            # Получаем дату изменения файла
            date_change = self.prima_exe_path.stat().st_mtime
            date_str = datetime.fromtimestamp(date_change).strftime('%d.%m.%y')
            
            # Формируем имя бэкапа
            backup_name = f'PRIMA[{date_str}].exe'
            backup_path = self.backup_directory / backup_name
            
            # Проверяем, существует ли уже бэкап с такой датой
            if backup_path.exists():
                backup_mtime = backup_path.stat().st_mtime
                if backup_mtime >= date_change:
                    self.logger.info(f"Бэкап уже существует и актуален: {backup_name}")
                    return backup_path
                else:
                    # Удаляем устаревший бэкап
                    backup_path.unlink()
                    self.logger.info(f"Удален устаревший бэкап: {backup_name}")
            
            # Создаем новый бэкап
            shutil.copy2(str(self.prima_exe_path), str(backup_path))
            self.logger.info(f"Бэкап создан: {backup_name}")
            return backup_path
            
        except Exception as e:
            self.logger.error(f"Не удалось создать бэкап: {e}")
            return None
    
    def get_all_backups(self) -> List[Path]:
        """Получает список всех бэкапов в директории.
        
        Returns:
            List[Path]: Список путей к файлам бэкапов
        """
        backups = []
        pattern = "PRIMA*.exe"
        
        for file_path in self.backup_directory.glob(pattern):
            if file_path.is_file():
                backups.append(file_path)
        
        # Сортируем по дате изменения (новые первыми)
        backups.sort(key=lambda x: x.stat().st_mtime, reverse=True)
        return backups
    
    def cleanup_old_backups(self):
        """Очищает старые бэкапы согласно правилам хранения.
        
        Правила:
        - Не более 1 бэкапа за неделю
        - Не более 1 бэкапа в месяц для бэкапов старше 1 года
        """
        backups = self.get_all_backups()
        if not backups:
            return
        
        now = datetime.now()
        one_year_ago = now - timedelta(days=365)
        
        # Группируем бэкапы по неделям (для бэкапов младше года)
        weekly_backups = {}  # ключ: (год, неделя), значение: список бэкапов
        monthly_backups = {}  # ключ: (год, месяц), значение: список бэкапов
        
        for backup in backups:
            backup_time = datetime.fromtimestamp(backup.stat().st_mtime)
            backup_year = backup_time.year
            backup_week = backup_time.isocalendar()[1]  # номер недели в году
            backup_month = backup_time.month
            
            if backup_time >= one_year_ago:
                # Бэкап младше года - группируем по неделям
                week_key = (backup_year, backup_week)
                if week_key not in weekly_backups:
                    weekly_backups[week_key] = []
                weekly_backups[week_key].append(backup)
            else:
                # Бэкап старше года - группируем по месяцам
                month_key = (backup_year, backup_month)
                if month_key not in monthly_backups:
                    monthly_backups[month_key] = []
                monthly_backups[month_key].append(backup)
        
        # Удаляем лишние бэкапы в каждой неделе (оставляем только самый новый)
        deleted_count = 0
        for week_key, week_backups in weekly_backups.items():
            if len(week_backups) > 1:
                # Оставляем самый новый, остальные удаляем
                week_backups.sort(key=lambda x: x.stat().st_mtime, reverse=True)
                for backup in week_backups[1:]:
                    try:
                        backup.unlink()
                        deleted_count += 1
                        self.logger.info(f"Удален старый бэкап (правило недели): {backup.name}")
                    except Exception as e:
                        self.logger.error(f"Не удалось удалить бэкап {backup.name}: {e}")
        
        # Удаляем лишние бэкапы в каждом месяце (оставляем только самый новый)
        for month_key, month_backups in monthly_backups.items():
            if len(month_backups) > 1:
                # Оставляем самый новый, остальные удаляем
                month_backups.sort(key=lambda x: x.stat().st_mtime, reverse=True)
                for backup in month_backups[1:]:
                    try:
                        backup.unlink()
                        deleted_count += 1
                        self.logger.info(f"Удален старый бэкап (правило месяца): {backup.name}")
                    except Exception as e:
                        self.logger.error(f"Не удалось удалить бэкап {backup.name}: {e}")
        
        if deleted_count > 0:
            self.logger.info(f"Очистка бэкапов завершена. Удалено: {deleted_count}")
    
    def restore_from_backup(self, backup_path: Union[str, Path]) -> bool:
        """Восстанавливает PRIMA.exe из указанного бэкапа.
        
        Args:
            backup_path (Union[str, Path]): Путь к файлу бэкапа
        
        Returns:
            bool: True если восстановление успешно, False в противном случае
        """
        backup_path_obj = Path(backup_path)
        if not backup_path_obj.exists():
            self.logger.error(f"Файл бэкапа не найден: {backup_path}")
            return False
        
        try:
            # Создаем временный бэкап текущего файла на случай ошибки
            temp_backup = self.prima_exe_path.with_suffix('.exe.temp_restore')
            if self.prima_exe_path.exists():
                shutil.copy2(str(self.prima_exe_path), str(temp_backup))
            
            # Копируем бэкап на место PRIMA.exe
            shutil.copy2(str(backup_path_obj), str(self.prima_exe_path))
            self.logger.info(f"Восстановление из бэкапа успешно: {backup_path_obj.name}")
            
            # Удаляем временный бэкап
            if temp_backup.exists():
                temp_backup.unlink()
            
            return True
            
        except Exception as e:
            self.logger.error(f"Ошибка при восстановлении из бэкапа: {e}")
            # Пытаемся восстановить из временного бэкапа
            if temp_backup.exists():
                try:
                    shutil.copy2(str(temp_backup), str(self.prima_exe_path))
                    self.logger.info("Восстановлен исходный файл из временного бэкапа")
                    temp_backup.unlink()
                except:
                    pass
            return False

