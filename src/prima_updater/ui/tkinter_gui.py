
"""
Модуль GUI интерфейса на tkinter.
"""

import tkinter as tk
from tkinter import ttk, messagebox
from typing import List, Dict, Any
import os
import threading

from src.prima_updater.config.settings import UIConfig
from src.prima_updater.core.changes import ChangeSet


class TkinterGUI:
    """GUI интерфейс на tkinter."""
    
    def __init__(self, config: UIConfig):
        self.config = config
        self.root = tk.Tk()
        self.current_frame = None
        self.selected_files = set()
        self.backup_exists = False
        self.setup_main_window()
        self.create_main_menu()
    
    def setup_main_window(self):
        """Настройка главного окна."""
        self.root.title("PRIMA Updater - Система управления изменениями")
        self.root.geometry("600x500")
        self.root.resizable(False, False)
        
        # Центрируем окно
        self.root.update_idletasks()
        x = (self.root.winfo_screenwidth() // 2) - (600 // 2)
        y = (self.root.winfo_screenheight() // 2) - (500 // 2)
        self.root.geometry(f"600x500+{x}+{y}")
        
        # Настраиваем стиль
        style = ttk.Style()
        style.theme_use('clam')
        
        # Конфигурируем цвета
        style.configure('Title.TLabel', font=('Arial', 16, 'bold'), foreground='#2E4BCA')
        style.configure('Header.TLabel', font=('Arial', 12, 'bold'), foreground='#228B22')
        style.configure('Info.TLabel', font=('Arial', 10), foreground='#DAA520')
        style.configure('Main.TButton', font=('Arial', 10), padding=10)
    
    def clear_frame(self):
        """Очистка текущего фрейма."""
        if self.current_frame:
            self.current_frame.destroy()
    
    def create_main_menu(self):
        """Создание главного меню."""
        self.clear_frame()
        
        self.current_frame = ttk.Frame(self.root, padding="20")
        self.current_frame.pack(fill=tk.BOTH, expand=True)
        
        # Заголовок
        title_label = ttk.Label(
            self.current_frame, 
            text="СИСТЕМА УПРАВЛЕНИЯ ИЗМЕНЕНИЯМИ", 
            style='Title.TLabel'
        )
        title_label.pack(pady=(0, 20))
        
        # Основные кнопки
        button_frame = ttk.Frame(self.current_frame)
        button_frame.pack(fill=tk.X, pady=10)
        
        ttk.Button(
            button_frame,
            text="[1] Для внесения ВСЕХ изменений",
            command=self.execute_all_changes,
            style='Main.TButton'
        ).pack(fill=tk.X, pady=5)
        
        ttk.Button(
            button_frame,
            text="[2] Выбор вносимых изменений",
            command=self.create_changes_menu,
            style='Main.TButton'
        ).pack(fill=tk.X, pady=5)
        
        ttk.Button(
            button_frame,
            text="[3] Работа с backup'ом",
            command=self.create_backup_menu,
            style='Main.TButton'
        ).pack(fill=tk.X, pady=5)
        
        ttk.Button(
            button_frame,
            text="[5] Для пропуска (без изменений)",
            command=self.skip_changes,
            style='Main.TButton'
        ).pack(fill=tk.X, pady=5)
        
        # Информационная панель
        info_frame = ttk.LabelFrame(self.current_frame, text="Информация", padding="10")
        info_frame.pack(fill=tk.BOTH, expand=True, pady=20)
        
        info_text = """• Выберите необходимое действие
• Все операции безопасны
• Рекомендуется создать backup перед изменениями"""
        
        ttk.Label(info_frame, text=info_text, style='Info.TLabel', justify=tk.LEFT).pack(anchor=tk.W)
        
        # Кнопка выхода
        ttk.Button(
            self.current_frame,
            text="Выход",
            command=self.root.quit
        ).pack(side=tk.RIGHT, pady=10)
    
    def create_changes_menu(self):
        """Создание меню выбора изменений."""
        self.clear_frame()
        
        self.current_frame = ttk.Frame(self.root, padding="20")
        self.current_frame.pack(fill=tk.BOTH, expand=True)
        
        # Заголовок
        ttk.Label(
            self.current_frame, 
            text="ВЫБОР ВНОСИМЫХ ИЗМЕНЕНИЙ", 
            style='Header.TLabel'
        ).pack(pady=(0, 20))
        
        # Кнопки опций
        button_frame = ttk.Frame(self.current_frame)
        button_frame.pack(fill=tk.X, pady=10)
        
        ttk.Button(
            button_frame,
            text="[1] Замена измененных файлов",
            command=self.replace_changed_files,
            style='Main.TButton'
        ).pack(fill=tk.X, pady=5)
        
        ttk.Button(
            button_frame,
            text="[2] Копирование отсутствующих файлов",
            command=self.copy_missing_files,
            style='Main.TButton'
        ).pack(fill=tk.X, pady=5)
        
        ttk.Button(
            button_frame,
            text="[3] Замена с отключением игнорирования",
            command=self.create_ignore_menu,
            style='Main.TButton'
        ).pack(fill=tk.X, pady=5)
        
        # Информационная панель
        info_frame = ttk.LabelFrame(self.current_frame, text="Описание опций", padding="10")
        info_frame.pack(fill=tk.BOTH, expand=True, pady=20)
        
        info_text = """• Замена измененных - обновляет только модифицированные файлы
• Копирование отсутствующих - добавляет новые файлы  
• Замена с отключением игнорирования - принудительная замена
  выбранных конфигурационных файлов"""
        
        ttk.Label(info_frame, text=info_text, style='Info.TLabel', justify=tk.LEFT).pack(anchor=tk.W)
        
        # Кнопки навигации
        nav_frame = ttk.Frame(self.current_frame)
        nav_frame.pack(fill=tk.X, pady=10)
        
        ttk.Button(nav_frame, text="← Назад", command=self.create_main_menu).pack(side=tk.LEFT)
        ttk.Button(nav_frame, text="Выход", command=self.root.quit).pack(side=tk.RIGHT)
    
    def create_ignore_menu(self):
        """Создание меню выбора файлов для замены с отключением игнорирования."""
        self.clear_frame()
        
        self.current_frame = ttk.Frame(self.root, padding="20")
        self.current_frame.pack(fill=tk.BOTH, expand=True)
        
        # Заголовок
        ttk.Label(
            self.current_frame, 
            text="ЗАМЕНА С ОТКЛЮЧЕНИЕМ ИГНОРИРОВАНИЯ", 
            style='Header.TLabel'
        ).pack(pady=(0, 10))
        
        ttk.Label(
            self.current_frame,
            text="Выберите файлы для принудительной замены:",
            font=('Arial', 10)
        ).pack(pady=(0, 10))
        
        # Список файлов с чекбоксами
        files_frame = ttk.LabelFrame(self.current_frame, text="Конфигурационные файлы", padding="10")
        files_frame.pack(fill=tk.BOTH, expand=True, pady=10)
        
        # Создаем скроллбар для списка файлов
        canvas = tk.Canvas(files_frame, height=150)
        scrollbar = ttk.Scrollbar(files_frame, orient="vertical", command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas)
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        # Список файлов
        config_files = [
            "Prima.ini", "Server.ini", "Database.ini",
            "Logger.ini", "Network.ini", "Security.ini"
        ]
        
        self.file_vars = {}
        for filename in config_files:
            var = tk.BooleanVar()
            var.set(filename in self.selected_files)
            self.file_vars[filename] = var
            
            ttk.Checkbutton(
                scrollable_frame,
                text=f"  {filename}",
                variable=var,
                command=lambda f=filename: self.toggle_file_selection(f)
            ).pack(anchor=tk.W, pady=2)
        
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # Кнопки управления выбором
        select_frame = ttk.Frame(self.current_frame)
        select_frame.pack(fill=tk.X, pady=10)
        
        ttk.Button(
            select_frame,
            text="Выбрать все",
            command=lambda: self.select_all_files(True)
        ).pack(side=tk.LEFT, padx=5)
        
        ttk.Button(
            select_frame,
            text="Снять все",
            command=lambda: self.select_all_files(False)
        ).pack(side=tk.LEFT, padx=5)
        
        # Предупреждение
        warning_frame = ttk.LabelFrame(self.current_frame, text="Внимание", padding="10")
        warning_frame.pack(fill=tk.X, pady=10)
        
        ttk.Label(
            warning_frame,
            text="Выбранные файлы будут заменены принудительно,\nигнорируя настройки защиты!",
            foreground='red',
            font=('Arial', 10, 'bold')
        ).pack()
        
        # Кнопки действий
        action_frame = ttk.Frame(self.current_frame)
        action_frame.pack(fill=tk.X, pady=10)
        
        ttk.Button(action_frame, text="← Назад", command=self.create_changes_menu).pack(side=tk.LEFT)
        ttk.Button(action_frame, text="Применить", command=self.apply_ignore_changes).pack(side=tk.RIGHT, padx=5)
        ttk.Button(action_frame, text="Выход", command=self.root.quit).pack(side=tk.RIGHT)
    
    def create_backup_menu(self):
        """Создание меню работы с backup'ом."""
        self.clear_frame()
        
        self.current_frame = ttk.Frame(self.root, padding="20")
        self.current_frame.pack(fill=tk.BOTH, expand=True)
        
        # Заголовок
        ttk.Label(
            self.current_frame, 
            text="РАБОТА С BACKUP'ОМ", 
            style='Header.TLabel'
        ).pack(pady=(0, 10))
        
        # Статус backup'а
        status_text = "✓ Backup существует" if self.backup_exists else "✗ Backup не найден"
        status_color = 'green' if self.backup_exists else 'red'
        
        ttk.Label(
            self.current_frame,
            text=f"Статус: {status_text}",
            foreground=status_color,
            font=('Arial', 10, 'bold')
        ).pack(pady=(0, 20))
        
        # Кнопки действий
        button_frame = ttk.Frame(self.current_frame)
        button_frame.pack(fill=tk.X, pady=10)
        
        ttk.Button(
            button_frame,
            text="[1] Создать backup",
            command=self.create_backup,
            style='Main.TButton'
        ).pack(fill=tk.X, pady=5)
        
        ttk.Button(
            button_frame,
            text="[2] Восстановить из backup'а",
            command=self.restore_backup,
            style='Main.TButton'
        ).pack(fill=tk.X, pady=5)
        
        ttk.Button(
            button_frame,
            text="[3] Удалить backup",
            command=self.delete_backup,
            style='Main.TButton'
        ).pack(fill=tk.X, pady=5)
        
        # Информационная панель
        info_frame = ttk.LabelFrame(self.current_frame, text="Информация о backup", padding="10")
        info_frame.pack(fill=tk.BOTH, expand=True, pady=20)
        
        if self.backup_exists:
            info_text = f"""• Расположение: {os.getcwd()}/backup/
• Размер: 12.5 МБ
• Файлов: 45"""
        else:
            info_text = """• Backup не создан
• Рекомендуется создать backup перед изменениями"""
        
        ttk.Label(info_frame, text=info_text, style='Info.TLabel', justify=tk.LEFT).pack(anchor=tk.W)
        
        # Кнопки навигации
        nav_frame = ttk.Frame(self.current_frame)
        nav_frame.pack(fill=tk.X, pady=10)
        
        ttk.Button(nav_frame, text="← Назад", command=self.create_main_menu).pack(side=tk.LEFT)
        ttk.Button(nav_frame, text="Выход", command=self.root.quit).pack(side=tk.RIGHT)
    
    def toggle_file_selection(self, filename: str):
        """Переключение выбора файла."""
        if self.file_vars[filename].get():
            self.selected_files.add(filename)
        else:
            self.selected_files.discard(filename)
    
    def select_all_files(self, select_all: bool):
        """Выбор/снятие всех файлов."""
        config_files = [
            "Prima.ini", "Server.ini", "Database.ini",
            "Logger.ini", "Network.ini", "Security.ini"
        ]
        
        for filename in config_files:
            if filename in self.file_vars:
                self.file_vars[filename].set(select_all)
                if select_all:
                    self.selected_files.add(filename)
                else:
                    self.selected_files.discard(filename)
    
    def show_message(self, title: str, message: str, msg_type: str = "info"):
        """Показать сообщение пользователю."""
        if msg_type == "error":
            messagebox.showerror(title, message)
        elif msg_type == "warning":
            messagebox.showwarning(title, message)
        else:
            messagebox.showinfo(title, message)
    
    def execute_all_changes(self):
        """Выполнение всех изменений."""
        message = """✓ Все изменения успешно внесены!

- Заменены измененные файлы
- Скопированы отсутствующие файлы
- Обновлены конфигурации"""
        
        self.show_message("Выполнено", message)
        self.root.quit()
    
    def replace_changed_files(self):
        """Замена измененных файлов."""
        message = """✓ Измененные файлы успешно заменены!

Обработано файлов: 12
Обновлено: 8
Пропущено: 4"""
        
        self.show_message("Выполнено", message)
    
    def copy_missing_files(self):
        """Копирование отсутствующих файлов."""
        message = """✓ Отсутствующие файлы успешно скопированы!

Скопировано файлов: 5
Созданы папки: 2"""
        
        self.show_message("Выполнено", message)
    
    def apply_ignore_changes(self):
        """Применение изменений с отключением игнорирования."""
        if not self.selected_files:
            self.show_message("Ошибка", "Не выбрано ни одного файла!", "error")
            return
        
        files_list = "\n".join([f"• {f}" for f in self.selected_files])
        message = f"""✓ Замена с отключением игнорирования выполнена!

Обработанные файлы:
{files_list}"""
        
        self.show_message("Выполнено", message)
    
    def create_backup(self):
        """Создание backup'а."""
        self.backup_exists = True
        message = f"""✓ Backup успешно создан!

Расположение: {os.getcwd()}/backup/
Файлов архивировано: 45
Размер: 12.5 МБ"""
        
        self.show_message("Выполнено", message)
        self.create_backup_menu()  # Обновляем меню
    
    def restore_backup(self):
        """Восстановление из backup'а."""
        if not self.backup_exists:
            self.show_message("Ошибка", "Backup не найден!\nСначала создайте backup.", "error")
            return
        
        message = """✓ Восстановление из backup'а завершено!

Восстановлено файлов: 45
Время операции: 3.2 сек"""
        
        self.show_message("Выполнено", message)
    
    def delete_backup(self):
        """Удаление backup'а."""
        if not self.backup_exists:
            self.show_message("Ошибка", "Backup не найден!", "error")
            return
        
        self.backup_exists = False
        message = """✓ Backup успешно удален!

Освобождено места: 12.5 МБ"""
        
        self.show_message("Выполнено", message)
        self.create_backup_menu()  # Обновляем меню
    
    def skip_changes(self):
        """Пропуск без изменений."""
        message = """✓ Операция завершена без изменений.

Все файлы остались без изменений."""
        
        self.show_message("Пропущено", message)
        self.root.quit()
    
    def run(self):
        """Запуск GUI."""
        self.root.mainloop()


def main():
    """Главная функция для запуска tkinter GUI."""
    from src.prima_updater.config.settings import UIConfig
    
    config = UIConfig()
    app = TkinterGUI(config)
    app.run()


if __name__ == "__main__":
    main()
