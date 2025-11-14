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

def check_dependencies():
    """Проверка наличия необходимых зависимостей.

    Returns:
        bool - True если все зависимости установлены, False иначе.
    """
    try:
        import art
        import rich
        return True
    except ImportError as e:
        print("="*60)
        print("Ошибка: Не установлены необходимые зависимости.")
        print("="*60)
        print("Отсутствует модуль:", e.name)
        print("Попытка установить необходимые модули...")
        from prima_updater import install
        if install.setup():
            print("="*60)
            print("Все необходимые модули успешно установлены.")
            print("="*60)
            return True
        else:
            return False

if not check_dependencies():
    print("="*60)
    print("Не удалось установить необходимые модули.")
    print("="*60)


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
    logger = setup_logging(config.logs_directory)
    logger.info("=" * 60)
    logger.info("Запуск программы обновления PRIMA")
    logger.info("=" * 60)
    
    # Инициализация пользовательского интерфейса
    ui = UserInterface(logger)
    ui.show_header()
    
    # Проверка доступности сервера, валидация путей, сравнение директорий
    with ui.console.status("Проверка доступности сервера") as status:
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
        status.update("Сравнение директорий") 
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
    backup_manager = BackupManager(prima_exe_path, config.backups_directory, logger)
    
    # Проверяем наличие бэкапов для отображения опции восстановления
    backups = backup_manager.get_all_backups()
    has_backups = len(backups) > 0
    if has_backups:
        logger.info(f"Найдено доступных бэкапов: {len(backups)}")
    else:
        logger.debug("Доступных бэкапов не найдено")
    
    # Отображение меню и получение выбора пользователя
    selected_full_copy_option = None
    while True:
        choice = ui.show_menu()
        logger.info(f"Пользователь выбрал действие: {choice}")
        
        # Обработка выбора "Дополнительно" - показываем подменю
        if choice == UserInterface.ACTION_ADDITIONAL:
            additional_choice = ui.show_additional_menu()
            if additional_choice == -1:
                # Пользователь вернулся в главное меню, показываем его снова
                continue
            # Если выбран "Полное копирование", показываем подварианты
            if additional_choice == UserInterface.ACTION_FULL_COPY:
                while True:
                    full_option = ui.show_full_copy_options(config.local_directory)
                    if full_option == -1:
                        # Вернуться к подменю "Дополнительно"
                        additional_choice = ui.show_additional_menu()
                        if additional_choice == -1:
                            # Назад в главное меню
                            additional_choice = None
                            break
                        if additional_choice != UserInterface.ACTION_FULL_COPY:
                            break
                        else:
                            continue
                    selected_full_copy_option = full_option
                    break
                if additional_choice is None:
                    continue
                if selected_full_copy_option is None:
                    # Пользователь выбрал не полное копирование из подменю
                    choice = additional_choice
                    break
                # Пользователь выбрал один из вариантов полного копирования
                choice = UserInterface.ACTION_FULL_COPY
                break
            else:
                # Пользователь выбрал действие из подменю (не полное копирование)
                choice = additional_choice
                logger.info(f"Пользователь выбрал действие из подменю: {choice}")
                break
        else:
            # Выбрано действие из главного меню
            break
    
    # Обработка выбора пользователя
    if choice == UserInterface.ACTION_RESTORE_BACKUP:
        # Восстановление из бэкапа
        # Подготовка списка лет для опции "Старше"
        from datetime import datetime, timedelta
        now = datetime.now()
        first_day_current_month = datetime(now.year, now.month, 1)
        while True:
            older_years = []
            for b in backups:
                bt = datetime.fromtimestamp(b.stat().st_mtime)
                if bt < first_day_current_month:
                    if bt.year not in older_years:
                        older_years.append(bt.year)
            older_years.sort(reverse=True)

            selected_filter = ui.show_restore_filters(older_years)
            if selected_filter is None:
                logger.info("Пользователь отменил выбор фильтра восстановления")
                # Возврат в предыдущее меню (главное) — перезапуск главного меню
                return main()

            filter_key, filter_arg = selected_filter
            filtered_backups = []
            if filter_key == 'current_month':
                filtered_backups = [b for b in backups if datetime.fromtimestamp(b.stat().st_mtime) >= first_day_current_month]
            elif filter_key == 'current_year':
                first_day_current_year = datetime(now.year, 1, 1)
                filtered_backups = [b for b in backups if datetime.fromtimestamp(b.stat().st_mtime) >= first_day_current_year]
            elif filter_key == 'older_year':
                year = int(filter_arg)
                # Для текущего года — только месяцы до текущего месяца; для прошлых лет — весь год
                def is_match(bpath):
                    ts = datetime.fromtimestamp(bpath.stat().st_mtime)
                    if ts.year != year:
                        return False
                    if year == now.year:
                        return ts < first_day_current_month
                    return True
                filtered_backups = [b for b in backups if is_match(b)]
            else:
                filtered_backups = backups[:]

            if not filtered_backups:
                logger.info("По выбранному фильтру бэкапы не найдены")
                # Вернуться к выбору фильтра
                continue

            backup_index = ui.show_backup_list(filtered_backups)
            if backup_index >= 0:
                backup_path = filtered_backups[backup_index]
                logger.info(f"Попытка восстановления из бэкапа: {backup_path.name}")
                if backup_manager.restore_from_backup(backup_path):
                    success_msg = "Восстановление из бэкапа выполнено успешно"
                    logger.info(success_msg)
                    ui.update_shortcut(config.desktop_path, prima_exe_path)
                else:
                    error_msg = "Ошибка при восстановлении из бэкапа"
                    logger.error(error_msg)
                return
            else:
                # Назад из списка бэкапов — снова показать фильтры
                logger.debug("Возврат к выбору фильтра восстановления")
                continue
        return
    
    # Для всех остальных действий создаем бэкап перед изменениями
    if choice != UserInterface.ACTION_SKIP:
        logger.info("Создание бэкапа перед обновлением...")
        backup_result = backup_manager.create_backup
        if backup_result:
            logger.debug(f"Бэкап создан: {backup_result.name}")
        backup_manager.cleanup_old_backups()
    
    # Выполнение выбранного действия
    if choice == UserInterface.ACTION_UPDATE_ALL:
        # Обновление всех изменений (измененные + отсутствующие)
        all_files = diff_files + only_files
        logger.info(f"Обновление всех изменений. Всего файлов: {len(all_files)} (изменено: {len(diff_files)}, отсутствует: {len(only_files)})")
        if file_sync.copy_files(all_files):
            success_msg = "Все изменения успешно применены"
            logger.info(success_msg)
        else:
            error_msg = "Ошибки при применении изменений"
            logger.error(error_msg)
    
    elif choice == UserInterface.ACTION_UPDATE_CHANGED:
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
    
    elif choice == UserInterface.ACTION_FULL_COPY:
        # Полное копирование директории с учетом выбранных опций
        logger.info("Выполнение полного копирования директории")
        if selected_full_copy_option is None:
            # Если сюда попали из главного меню (без подменю) — показываем опции
            selected_full_copy_option = ui.show_full_copy_options(config.local_directory)
            if selected_full_copy_option == -1:
                logger.info("Пользователь отменил полное копирование")
                return
        
        remove_from_ignore = []
        overwrite_all = False
        if selected_full_copy_option == UserInterface.ACTION_FULL_COPY_IGNORE:
            remove_from_ignore = []
        elif selected_full_copy_option == UserInterface.ACTION_FULL_COPY_KEEP_PRIMA:
            remove_from_ignore = ['PRIMA.ini']
        elif selected_full_copy_option == UserInterface.ACTION_FULL_COPY_KEEP_SERVERS:
            remove_from_ignore = ['Servers.ini']
        elif selected_full_copy_option == UserInterface.ACTION_FULL_COPY_KEEP_BOTH:
            remove_from_ignore = ['PRIMA.ini', 'Servers.ini']
        elif selected_full_copy_option == UserInterface.ACTION_FULL_COPY_OVERWRITE_ALL:
            # Подтверждение на переписывание
            if not ui.confirm_full_copy_overwrite():
                logger.info("Пользователь отменил полное переписывание")
                return
            overwrite_all = True
        else:
            logger.warning("Неизвестный вариант полного копирования, операция отменена")
            return

        if file_sync.copy_all(remove_from_ignore=remove_from_ignore, overwrite_all=overwrite_all):
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
