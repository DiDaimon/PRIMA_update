
"""
Фабрика для создания различных GUI интерфейсов.
"""

from enum import Enum
from typing import Optional, Union
import sys

from src.prima_updater.config.settings import UIConfig


class GUIType(Enum):
    """Типы доступных GUI интерфейсов."""
    TKINTER = "tkinter"
    PYSIDE6 = "pyside6"
    DEARPYGUI = "dearpygui"
    CLI = "cli"


class GUIFactory:
    """Фабрика для создания GUI интерфейсов."""
    
    @staticmethod
    def create_gui(gui_type: Union[GUIType, str], config: UIConfig):
        """
        Создает GUI интерфейс указанного типа.
        
        Args:
            gui_type: Тип GUI интерфейса
            config: Конфигурация UI
            
        Returns:
            Экземпляр GUI интерфейса
            
        Raises:
            ValueError: Если тип GUI не поддерживается
            ImportError: Если необходимые библиотеки не установлены
        """
        if isinstance(gui_type, str):
            try:
                gui_type = GUIType(gui_type.lower())
            except ValueError:
                raise ValueError(f"Неподдерживаемый тип GUI: {gui_type}")
        
        if gui_type == GUIType.TKINTER:
            return GUIFactory._create_tkinter_gui(config)
        elif gui_type == GUIType.PYSIDE6:
            return GUIFactory._create_pyside6_gui(config)
        elif gui_type == GUIType.DEARPYGUI:
            return GUIFactory._create_dearpygui_gui(config)
        elif gui_type == GUIType.CLI:
            return GUIFactory._create_cli_gui(config)
        else:
            raise ValueError(f"Неподдерживаемый тип GUI: {gui_type}")
    
    @staticmethod
    def _create_tkinter_gui(config: UIConfig):
        """Создает GUI на tkinter."""
        try:
            from src.prima_updater.ui.tkinter_gui import TkinterGUI
            return TkinterGUI(config)
        except ImportError as e:
            raise ImportError(f"Не удалось загрузить tkinter: {e}")
    
    @staticmethod
    def _create_pyside6_gui(config: UIConfig):
        """Создает GUI на PySide6."""
        try:
            from src.prima_updater.ui.pyside6_gui import PySide6GUI
            return PySide6GUI(config)
        except ImportError as e:
            raise ImportError(f"Не удалось загрузить PySide6: {e}")
    
    @staticmethod
    def _create_dearpygui_gui(config: UIConfig):
        """Создает GUI на DearPyGui."""
        try:
            from src.prima_updater.ui.dearPyGui import MenuApp
            return MenuApp()
        except ImportError as e:
            raise ImportError(f"Не удалось загрузить DearPyGui: {e}")
    
    @staticmethod
    def _create_cli_gui(config: UIConfig):
        """Создает CLI интерфейс."""
        from src.prima_updater.ui.cli import CLIInterface
        return CLIInterface(config)
    
    @staticmethod
    def get_available_guis() -> list:
        """
        Возвращает список доступных GUI интерфейсов.
        
        Returns:
            Список доступных типов GUI
        """
        available = []
        
        # Проверяем tkinter (встроенный в Python)
        try:
            import tkinter
            available.append(GUIType.TKINTER)
        except ImportError:
            pass
        
        # Проверяем PySide6
        try:
            import PySide6
            available.append(GUIType.PYSIDE6)
        except ImportError:
            pass
        
        # Проверяем DearPyGui
        try:
            import dearpygui
            available.append(GUIType.DEARPYGUI)
        except ImportError:
            pass
        
        # CLI всегда доступен
        available.append(GUIType.CLI)
        
        return available
    
    @staticmethod
    def get_recommended_gui() -> GUIType:
        """
        Возвращает рекомендуемый тип GUI в зависимости от системы.
        
        Returns:
            Рекомендуемый тип GUI
        """
        available = GUIFactory.get_available_guis()
        
        # Приоритет: tkinter (встроенный) -> PySide6 -> DearPyGui -> CLI
        if GUIType.TKINTER in available:
            return GUIType.TKINTER
        elif GUIType.PYSIDE6 in available:
            return GUIType.PYSIDE6
        elif GUIType.DEARPYGUI in available:
            return GUIType.DEARPYGUI
        else:
            return GUIType.CLI
    
    @staticmethod
    def print_available_guis():
        """Выводит список доступных GUI интерфейсов."""
        available = GUIFactory.get_available_guis()
        recommended = GUIFactory.get_recommended_gui()
        
        print("Доступные GUI интерфейсы:")
        for gui_type in available:
            marker = " (рекомендуется)" if gui_type == recommended else ""
            print(f"  - {gui_type.value}{marker}")


def main():
    """Демонстрация работы фабрики GUI."""
    print("PRIMA Updater - Фабрика GUI интерфейсов")
    print("=" * 50)
    
    GUIFactory.print_available_guis()
    
    print("\nВыберите тип GUI:")
    print("1. tkinter")
    print("2. pyside6")
    print("3. dearpygui")
    print("4. cli")
    print("5. автоматический выбор")
    
    try:
        choice = input("\nВведите номер (1-5): ").strip()
        
        if choice == "1":
            gui_type = GUIType.TKINTER
        elif choice == "2":
            gui_type = GUIType.PYSIDE6
        elif choice == "3":
            gui_type = GUIType.DEARPYGUI
        elif choice == "4":
            gui_type = GUIType.CLI
        elif choice == "5":
            gui_type = GUIFactory.get_recommended_gui()
        else:
            print("Неверный выбор, используется автоматический выбор")
            gui_type = GUIFactory.get_recommended_gui()
        
        print(f"\nЗапуск GUI: {gui_type.value}")
        
        # Создаем конфигурацию
        from src.prima_updater.config.settings import UIConfig
        config = UIConfig()
        
        # Создаем и запускаем GUI
        gui = GUIFactory.create_gui(gui_type, config)
        
        if gui_type == GUIType.CLI:
            gui.show_header()
            print("CLI интерфейс готов к работе")
        else:
            gui.run()
            
    except KeyboardInterrupt:
        print("\nПрограмма завершена пользователем")
    except Exception as e:
        print(f"\nОшибка: {e}")
        print("Переключение на CLI интерфейс...")
        from src.prima_updater.config.settings import UIConfig
        config = UIConfig()
        cli_gui = GUIFactory.create_gui(GUIType.CLI, config)
        cli_gui.show_header()


if __name__ == "__main__":
    main()
