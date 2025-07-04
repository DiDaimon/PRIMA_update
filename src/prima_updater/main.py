
"""
Основной модуль PRIMA Updater.
Современная версия программы обновления PRIMA.
"""

import sys
from pathlib import Path

# Добавляем корневую директорию в путь для импортов
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from src.prima_updater.config.settings import get_config
from src.prima_updater.core.updater import PrimaUpdater
from src.prima_updater.utils.logger import setup_logging
from src.prima_updater.ui.cli import CLIInterface


def main():
    """Точка входа в приложение."""
    try:
        # Загружаем конфигурацию
        config = get_config()
        
        # Настраиваем логирование
        logger = setup_logging(config.logging)
        logger.info("PRIMA Updater запущен")
        
        # Создаем экземпляры основных компонентов
        updater = PrimaUpdater(config)
        ui = CLIInterface(config.ui)
        
        # Запускаем основной цикл программы
        ui.show_header()
        
        # Проверяем изменения
        changes = updater.check_changes()
        
        if not changes.has_changes():
            ui.show_message("Изменений не обнаружено.", "success")
            return
            
        # Показываем найденные изменения
        ui.show_changes(changes)
        
        # Получаем выбор пользователя
        choice = ui.get_user_choice()
        
        # Выполняем выбранное действие
        if choice != "skip":
            updater.apply_changes(changes, choice)
            
        logger.info("PRIMA Updater завершен")
        
    except Exception as e:
        print(f"Критическая ошибка: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
