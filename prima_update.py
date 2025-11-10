# -*- coding: utf-8 -*-
"""Главный модуль программы обновления PRIMA с сервера.

Этот модуль является точкой входа приложения и координирует работу всех модулей:
- Проверка доступности сервера
- Сравнение директорий
- Управление бэкапами
- Синхронизация файлов
- Обновление ярлыка на рабочем столе
"""

from pathlib import Path
from prima_updater import (
    Config,
    setup_logging,
    validate_paths,
    BackupManager,
    FileSync,
    UserInterface
)


def main():
    """Главная функция программы.
    
    Выполняет последовательность действий:
    1. Инициализация конфигурации и логирования
    2. Проверка доступности сервера и валидация путей
    3. Сравнение директорий и поиск изменений
    4. Отображение меню и обработка выбора пользователя
    5. Выполнение выбранного действия
    """
    # Инициализация конфигурации
    config = Config()
    
    # Настройка логирования
    logger = setup_logging()
    logger.info("=" * 60)
    logger.info("Запуск программы обновления PRIMA")
    logger.info("=" * 60)
    
    # Инициализация пользовательского интерфейса
    ui = UserInterface(logger)
    ui.show_header()
    
    # Проверка доступности сервера и валидация путей
    logger.info("Проверка доступности сервера и валидация путей...")
    if not validate_paths(config.server_directory, config.local_directory, logger):
        error_msg = "Сервер недоступен или пути невалидны. Проверьте настройки."
        logger.error(error_msg)
        return
    
    # Инициализация синхронизатора файлов
    file_sync = FileSync(
        config.server_directory,
        config.local_directory,
        config.ignore_list,
        logger
    )
    
    # Сравнение директорий
    logger.info("Начало сравнения директорий...")
    diff_files, only_files = file_sync.compare_directories()
    
    # Отображение найденных изменений
    ui.show_changes(diff_files, only_files)
    
    # Если изменений нет, просто обновляем ярлык и выходим
    if not diff_files and not only_files:
        logger.info("Изменений не обнаружено. Обновление ярлыка и завершение работы.")
        prima_exe_path = config.get_prima_exe_path()
        if prima_exe_path.exists():
            ui.update_shortcut(config.desktop_path, prima_exe_path)
        return
    
    # Инициализация менеджера бэкапов
    prima_exe_path = config.get_prima_exe_path()
    logger.debug(f"Путь к PRIMA.exe: {prima_exe_path}")
    backup_manager = BackupManager(prima_exe_path, None, logger)
    
    # Проверяем наличие бэкапов для отображения опции восстановления
    backups = backup_manager.get_all_backups()
    has_backups = len(backups) > 0
    if has_backups:
        logger.info(f"Найдено доступных бэкапов: {len(backups)}")
    else:
        logger.debug("Доступных бэкапов не найдено")
    
    # Отображение меню и получение выбора пользователя
    choice = ui.show_menu(has_backups=has_backups)
    logger.info(f"Пользователь выбрал действие: {choice}")
    
    # Обработка выбора пользователя
    if choice == UserInterface.ACTION_RESTORE_BACKUP:
        # Восстановление из бэкапа
        backup_index = ui.show_backup_list(backups)
        if backup_index >= 0:
            backup_path = backups[backup_index]
            logger.info(f"Попытка восстановления из бэкапа: {backup_path.name}")
            if backup_manager.restore_from_backup(backup_path):
                success_msg = "Восстановление из бэкапа выполнено успешно"
                logger.info(success_msg)
                ui.update_shortcut(config.desktop_path, prima_exe_path)
            else:
                error_msg = "Ошибка при восстановлении из бэкапа"
                logger.error(error_msg)
        else:
            logger.info("Пользователь отменил восстановление из бэкапа")
        return
    
    # Для всех остальных действий создаем бэкап перед изменениями
    if choice != UserInterface.ACTION_SKIP:
        logger.info("Создание бэкапа перед обновлением...")
        backup_result = backup_manager.create_backup()
        if backup_result:
            logger.debug(f"Бэкап создан: {backup_result.name}")
        backup_manager.cleanup_old_backups()
    
    # Выполнение выбранного действия
    if choice == UserInterface.ACTION_UPDATE_CHANGED:
        # Обновление только измененных файлов
        logger.info(f"Обновление измененных файлов. Количество файлов: {len(diff_files)}")
        if file_sync.copy_files(diff_files):
            success_msg = "Измененные файлы успешно обновлены"
            logger.info(success_msg)
        else:
            error_msg = "Ошибки при обновлении файлов"
            logger.error(error_msg)
    
    elif choice == UserInterface.ACTION_COPY_MISSING:
        # Копирование только отсутствующих файлов
        logger.info(f"Копирование отсутствующих файлов. Количество файлов: {len(only_files)}")
        if file_sync.copy_files(only_files):
            success_msg = "Отсутствующие файлы успешно скопированы"
            logger.info(success_msg)
        else:
            error_msg = "Ошибки при копировании файлов"
            logger.error(error_msg)
    
    elif choice == UserInterface.ACTION_UPDATE_ALL:
        # Обновление всех изменений (измененные + отсутствующие)
        all_files = diff_files + only_files
        logger.info(f"Обновление всех изменений. Всего файлов: {len(all_files)} (изменено: {len(diff_files)}, отсутствует: {len(only_files)})")
        if file_sync.copy_files(all_files):
            success_msg = "Все изменения успешно применены"
            logger.info(success_msg)
        else:
            error_msg = "Ошибки при применении изменений"
            logger.error(error_msg)
    
    elif choice == UserInterface.ACTION_FULL_COPY:
        # Полное копирование директории
        logger.info("Выполнение полного копирования директории")
        if file_sync.copy_all():
            success_msg = "Полное копирование завершено успешно"
            logger.info(success_msg)
        else:
            error_msg = "Ошибка при полном копировании"
            logger.error(error_msg)
    
    elif choice == UserInterface.ACTION_SKIP:
        # Пропуск изменений
        skip_msg = "Изменения внесены не будут."
        logger.info(f"Пользователь пропустил обновление. {skip_msg}")
    
    # Обновление ярлыка на рабочем столе
    if prima_exe_path.exists():
        logger.debug("Обновление ярлыка на рабочем столе...")
        ui.update_shortcut(config.desktop_path, prima_exe_path)
    else:
        logger.warning(f"Файл PRIMA.exe не найден по пути: {prima_exe_path}. Ярлык не обновлен.")
    
    logger.info("Работа программы завершена успешно")


if __name__ == '__main__':
    main()
