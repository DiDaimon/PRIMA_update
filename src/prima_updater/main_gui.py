
"""
Главный файл для запуска GUI версии PRIMA Updater.
"""

import sys
import argparse
from pathlib import Path

# Добавляем корневую директорию в путь для импортов
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from src.prima_updater.config.settings import get_config
from src.prima_updater.ui.gui_factory import GUIFactory, GUIType
from src.prima_updater.utils.logger import setup_logging


def parse_arguments():
    """Парсинг аргументов командной строки."""
    parser = argparse.ArgumentParser(
        description="PRIMA Updater - Графический интерфейс",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Доступные GUI интерфейсы:
  tkinter    - Встроенный GUI (рекомендуется)
  pyside6    - Современный Qt-интерфейс
  dearpygui  - Быстрый игровой интерфейс
  cli        - Консольный интерфейс
  auto       - Автоматический выбор (по умолчанию)

Примеры использования:
  python -m src.prima_updater.main_gui
  python -m src.prima_updater.main_gui --gui tkinter
  python -m src.prima_updater.main_gui --gui pyside6
  python -m src.prima_updater.main_gui --list-guis
        """
    )
    
    parser.add_argument(
        "--gui",
        choices=["tkinter", "pyside6", "dearpygui", "cli", "auto"],
        default="auto",
        help="Тип GUI интерфейса (по умолчанию: auto)"
    )
    
    parser.add_argument(
        "--list-guis",
        action="store_true",
        help="Показать доступные GUI интерфейсы"
    )
    
    parser.add_argument(
        "--config",
        type=str,
        help="Путь к файлу конфигурации"
    )
    
    parser.add_argument(
        "--debug",
        action="store_true",
        help="Включить отладочный режим"
    )
    
    return parser.parse_args()


def main():
    """Главная функция для запуска GUI."""
    args = parse_arguments()
    
    # Показываем список доступных GUI и выходим
    if args.list_guis:
        GUIFactory.print_available_guis()
        return
    
    try:
        # Загружаем конфигурацию
        config_path = Path(args.config) if args.config else None
        config = get_config(config_path)
        
        # Настраиваем логирование
        if args.debug:
            config.logging.level = "DEBUG"
        logger = setup_logging(config.logging)
        
        logger.info("PRIMA Updater GUI запущен")
        logger.debug(f"Выбранный GUI: {args.gui}")
        
        # Определяем тип GUI
        if args.gui == "auto":
            gui_type = GUIFactory.get_recommended_gui()
            logger.info(f"Автоматически выбран GUI: {gui_type.value}")
        else:
            gui_type = GUIType(args.gui)
        
        # Создаем и запускаем GUI
        gui = GUIFactory.create_gui(gui_type, config.ui)
        
        if gui_type == GUIType.CLI:
            # Для CLI запускаем обычный цикл
            from src.prima_updater.core.updater import PrimaUpdater
            updater = PrimaUpdater(config)
            
            gui.show_header()
            changes = updater.check_changes()
            
            if not changes.has_changes():
                gui.show_message("Изменений не обнаружено.", "success")
                return
            
            gui.show_changes(changes)
            choice = gui.get_user_choice()
            
            if choice != "skip":
                updater.apply_changes(changes, choice)
        else:
            # Для GUI запускаем интерфейс
            gui.run()
        
        logger.info("PRIMA Updater GUI завершен")
        
    except KeyboardInterrupt:
        print("\nПрограмма завершена пользователем")
    except ImportError as e:
        print(f"Ошибка импорта: {e}")
        print("Возможно, не установлены необходимые библиотеки.")
        print("Попробуйте запустить с --gui cli для консольного интерфейса")
        sys.exit(1)
    except Exception as e:
        print(f"Критическая ошибка: {e}")
        if args.debug:
            import traceback
            traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
