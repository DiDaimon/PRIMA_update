
"""
Модуль командного интерфейса пользователя.
"""

import os
from typing import List, Dict, Any
from art import tprint

from src.prima_updater.config.settings import UIConfig
from src.prima_updater.core.changes import ChangeSet


class CLIInterface:
    """Командный интерфейс пользователя."""
    
    def __init__(self, config: UIConfig):
        self.config = config
    
    def clear_terminal(self):
        """Очищает экран терминала."""
        if self.config.clear_terminal:
            os.system('cls' if os.name == 'nt' else 'clear')
    
    def show_header(self):
        """Показывает заголовок программы."""
        self.clear_terminal()
        tprint('PRIMA - UPDATER', font='tarty1')
        print()
    
    def show_message(self, message: str, message_type: str = "info"):
        """
        Показывает сообщение пользователю.
        
        Args:
            message: Текст сообщения
            message_type: Тип сообщения (info, success, error, warning)
        """
        print(f"\n{message}")
    
    def show_changes(self, changes: 'ChangeSet'):
        """
        Показывает найденные изменения.
        
        Args:
            changes: Набор изменений
        """
        print("\nПроверка наличия изменений:")
        
        if changes.modified_files:
            print("\nИзмененные файлы:")
            for file_path in changes.modified_files:
                print(f"  [*] {file_path}")
        
        if changes.missing_files:
            print("\nОтсутствующие файлы:")
            for file_path in changes.missing_files:
                print(f"  [-] {file_path}")
        
        if changes.new_directories:
            print("\nНовые директории:")
            for dir_path in changes.new_directories:
                print(f"  [+] {dir_path}")
    
    def get_user_choice(self) -> str:
        """
        Получает выбор пользователя.
        
        Returns:
            Строка с выбором пользователя
        """
        print('''
Выберите действие и нажмите Enter:
 [1] Для замены измененных файлов.
 [2] Для копирования отсутствующих файлов.
 [3] Для внесения всех изменений.
 [4] Для полного копирования.
 [5] Для пропуска (без изменений).
        ''')
        
        choice_map = {
            "1": "modified_only",
            "2": "missing_only", 
            "3": "all_changes",
            "4": "full_copy",
            "5": "skip"
        }
        
        while True:
            answer = input('Выберите действие: ').strip()
            if answer in choice_map:
                return choice_map[answer]
            else:
                print('Неверный ввод, повторите')
    
    def show_progress(self, current: int, total: int, operation: str):
        """
        Показывает прогресс операции.
        
        Args:
            current: Текущий элемент
            total: Общее количество элементов
            operation: Описание операции
        """
        if self.config.show_progress and total > 0:
            percent = (current / total) * 100
            print(f"\r{operation}: {current}/{total} ({percent:.1f}%)", end='', flush=True)
            if current == total:
                print()  # Новая строка в конце


class MenuOption:
    """Опция меню."""
    
    def __init__(self, key: str, title: str, action: str, description: str = ""):
        self.key = key
        self.title = title
        self.action = action
        self.description = description


class InteractiveMenu:
    """Интерактивное меню с возможностью навигации."""
    
    def __init__(self, title: str):
        self.title = title
        self.options: List[MenuOption] = []
        self.parent_menu = None
    
    def add_option(self, option: MenuOption):
        """Добавляет опцию в меню."""
        self.options.append(option)
    
    def show(self) -> str:
        """
        Показывает меню и возвращает выбранное действие.
        
        Returns:
            Действие выбранной опции
        """
        while True:
            print(f"\n{self.title}")
            print("=" * len(self.title))
            
            for option in self.options:
                print(f" [{option.key}] {option.title}")
                if option.description:
                    print(f"     {option.description}")
            
            if self.parent_menu:
                print(" [0] Назад")
            
            choice = input("\nВыберите действие: ").strip()
            
            if choice == "0" and self.parent_menu:
                return "back"
            
            for option in self.options:
                if option.key == choice:
                    return option.action
            
            print("Неверный выбор, попробуйте снова.")
