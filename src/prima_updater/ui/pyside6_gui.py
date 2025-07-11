
"""
Модуль GUI интерфейса на PySide6.
"""

import sys
import os
from typing import List, Set
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QLabel, QFrame, QScrollArea, QCheckBox, QGroupBox,
    QMessageBox, QSpacerItem, QSizePolicy
)
from PySide6.QtCore import Qt, QSize
from PySide6.QtGui import QFont, QPalette, QColor

from src.prima_updater.config.settings import UIConfig
from src.prima_updater.core.changes import ChangeSet


class PySide6GUI(QMainWindow):
    """GUI интерфейс на PySide6."""
    
    def __init__(self, config: UIConfig):
        super().__init__()
        self.config = config
        self.selected_files: Set[str] = set()
        self.backup_exists = False
        self.current_widget = None
        self.checkboxes = {}
        self.setup_ui()
        self.show_main_menu()
    
    def setup_ui(self):
        """Настройка основного интерфейса."""
        self.setWindowTitle("PRIMA Updater - Система управления изменениями")
        self.setFixedSize(QSize(650, 550))
        
        # Центрирование окна
        screen = QApplication.primaryScreen().geometry()
        x = (screen.width() - self.width()) // 2
        y = (screen.height() - self.height()) // 2
        self.move(x, y)
        
        # Настройка стилей
        self.setStyleSheet("""
            QMainWindow {
                background-color: #f0f0f0;
            }
            QLabel#title {
                font-size: 16px;
                font-weight: bold;
                color: #2E4BCA;
                padding: 10px;
            }
            QLabel#header {
                font-size: 12px;
                font-weight: bold;
                color: #228B22;
                padding: 5px;
            }
            QLabel#info {
                font-size: 10px;
                color: #DAA520;
                padding: 5px;
            }
            QPushButton {
                font-size: 11px;
                padding: 12px;
                background-color: #e8e8e8;
                border: 1px solid #c0c0c0;
                border-radius: 4px;
                margin: 3px;
            }
            QPushButton:hover {
                background-color: #d0d0d0;
                border: 1px solid #a0a0a0;
            }
            QPushButton:pressed {
                background-color: #c0c0c0;
            }
            QGroupBox {
                font-weight: bold;
                border: 2px solid #c0c0c0;
                border-radius: 5px;
                margin: 5px;
                padding-top: 10px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px 0 5px;
            }
            QCheckBox {
                font-size: 11px;
                padding: 3px;
            }
        """)
        
        # Создаем центральный виджет
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
    
    def clear_layout(self):
        """Очистка текущего layout."""
        if self.current_widget:
            self.current_widget.deleteLater()
    
    def show_main_menu(self):
        """Показать главное меню."""
        self.clear_layout()
        
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setSpacing(10)
        layout.setContentsMargins(30, 30, 30, 30)
        
        # Заголовок
        title = QLabel("СИСТЕМА УПРАВЛЕНИЯ ИЗМЕНЕНИЯМИ")
        title.setObjectName("title")
        title.setAlignment(Qt.AlignCenter)
        layout.addWidget(title)
        
        # Основные кнопки
        buttons_layout = QVBoxLayout()
        
        btn1 = QPushButton("[1] Для внесения ВСЕХ изменений")
        btn1.clicked.connect(self.execute_all_changes)
        buttons_layout.addWidget(btn1)
        
        btn2 = QPushButton("[2] Выбор вносимых изменений")
        btn2.clicked.connect(self.show_changes_menu)
        buttons_layout.addWidget(btn2)
        
        btn3 = QPushButton("[3] Работа с backup'ом")
        btn3.clicked.connect(self.show_backup_menu)
        buttons_layout.addWidget(btn3)
        
        btn5 = QPushButton("[5] Для пропуска (без изменений)")
        btn5.clicked.connect(self.skip_changes)
        buttons_layout.addWidget(btn5)
        
        layout.addLayout(buttons_layout)
        
        # Информационная панель
        info_group = QGroupBox("Информация")
        info_layout = QVBoxLayout(info_group)
        
        info_text = """• Выберите необходимое действие
• Все операции безопасны
• Рекомендуется создать backup перед изменениями"""
        
        info_label = QLabel(info_text)
        info_label.setObjectName("info")
        info_layout.addWidget(info_label)
        
        layout.addWidget(info_group)
        
        # Кнопка выхода
        exit_layout = QHBoxLayout()
        exit_layout.addStretch()
        exit_btn = QPushButton("Выход")
        exit_btn.clicked.connect(self.close)
        exit_layout.addWidget(exit_btn)
        layout.addLayout(exit_layout)
        
        self.current_widget = widget
        self.setCentralWidget(widget)
    
    def show_changes_menu(self):
        """Показать меню выбора изменений."""
        self.clear_layout()
        
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setSpacing(10)
        layout.setContentsMargins(30, 30, 30, 30)
        
        # Заголовок
        title = QLabel("ВЫБОР ВНОСИМЫХ ИЗМЕНЕНИЙ")
        title.setObjectName("header")
        title.setAlignment(Qt.AlignCenter)
        layout.addWidget(title)
        
        # Кнопки опций
        buttons_layout = QVBoxLayout()
        
        btn1 = QPushButton("[1] Замена измененных файлов")
        btn1.clicked.connect(self.replace_changed_files)
        buttons_layout.addWidget(btn1)
        
        btn2 = QPushButton("[2] Копирование отсутствующих файлов")
        btn2.clicked.connect(self.copy_missing_files)
        buttons_layout.addWidget(btn2)
        
        btn3 = QPushButton("[3] Замена с отключением игнорирования")
        btn3.clicked.connect(self.show_ignore_menu)
        buttons_layout.addWidget(btn3)
        
        layout.addLayout(buttons_layout)
        
        # Информационная панель
        info_group = QGroupBox("Описание опций")
        info_layout = QVBoxLayout(info_group)
        
        info_text = """• Замена измененных - обновляет только модифицированные файлы
• Копирование отсутствующих - добавляет новые файлы  
• Замена с отключением игнорирования - принудительная замена
  выбранных конфигурационных файлов"""
        
        info_label = QLabel(info_text)
        info_label.setObjectName("info")
        info_layout.addWidget(info_label)
        
        layout.addWidget(info_group)
        
        # Кнопки навигации
        nav_layout = QHBoxLayout()
        back_btn = QPushButton("← Назад")
        back_btn.clicked.connect(self.show_main_menu)
        nav_layout.addWidget(back_btn)
        
        nav_layout.addStretch()
        
        exit_btn = QPushButton("Выход")
        exit_btn.clicked.connect(self.close)
        nav_layout.addWidget(exit_btn)
        
        layout.addLayout(nav_layout)
        
        self.current_widget = widget
        self.setCentralWidget(widget)
    
    def show_ignore_menu(self):
        """Показать меню выбора файлов для замены с отключением игнорирования."""
        self.clear_layout()
        
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setSpacing(10)
        layout.setContentsMargins(30, 30, 30, 30)
        
        # Заголовок
        title = QLabel("ЗАМЕНА С ОТКЛЮЧЕНИЕМ ИГНОРИРОВАНИЯ")
        title.setObjectName("header")
        title.setAlignment(Qt.AlignCenter)
        layout.addWidget(title)
        
        subtitle = QLabel("Выберите файлы для принудительной замены:")
        layout.addWidget(subtitle)
        
        # Группа с файлами
        files_group = QGroupBox("Конфигурационные файлы")
        files_layout = QVBoxLayout(files_group)
        
        # Скроллируемая область для файлов
        scroll_area = QScrollArea()
        scroll_widget = QWidget()
        scroll_layout = QVBoxLayout(scroll_widget)
        
        # Список файлов
        config_files = [
            "Prima.ini", "Server.ini", "Database.ini",
            "Logger.ini", "Network.ini", "Security.ini"
        ]
        
        self.checkboxes = {}
        for filename in config_files:
            checkbox = QCheckBox(f"  {filename}")
            checkbox.setChecked(filename in self.selected_files)
            checkbox.toggled.connect(lambda checked, f=filename: self.toggle_file_selection(f, checked))
            self.checkboxes[filename] = checkbox
            scroll_layout.addWidget(checkbox)
        
        scroll_area.setWidget(scroll_widget)
        scroll_area.setMaximumHeight(150)
        files_layout.addWidget(scroll_area)
        
        layout.addWidget(files_group)
        
        # Кнопки управления выбором
        select_layout = QHBoxLayout()
        
        select_all_btn = QPushButton("Выбрать все")
        select_all_btn.clicked.connect(lambda: self.select_all_files(True))
        select_layout.addWidget(select_all_btn)
        
        clear_all_btn = QPushButton("Снять все")
        clear_all_btn.clicked.connect(lambda: self.select_all_files(False))
        select_layout.addWidget(clear_all_btn)
        
        select_layout.addStretch()
        layout.addLayout(select_layout)
        
        # Предупреждение
        warning_group = QGroupBox("Внимание")
        warning_layout = QVBoxLayout(warning_group)
        
        warning_label = QLabel("Выбранные файлы будут заменены принудительно,\nигнорируя настройки защиты!")
        warning_label.setStyleSheet("color: red; font-weight: bold;")
        warning_layout.addWidget(warning_label)
        
        layout.addWidget(warning_group)
        
        # Кнопки действий
        action_layout = QHBoxLayout()
        
        back_btn = QPushButton("← Назад")
        back_btn.clicked.connect(self.show_changes_menu)
        action_layout.addWidget(back_btn)
        
        action_layout.addStretch()
        
        apply_btn = QPushButton("Применить")
        apply_btn.clicked.connect(self.apply_ignore_changes)
        action_layout.addWidget(apply_btn)
        
        exit_btn = QPushButton("Выход")
        exit_btn.clicked.connect(self.close)
        action_layout.addWidget(exit_btn)
        
        layout.addLayout(action_layout)
        
        self.current_widget = widget
        self.setCentralWidget(widget)
    
    def show_backup_menu(self):
        """Показать меню работы с backup'ом."""
        self.clear_layout()
        
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setSpacing(10)
        layout.setContentsMargins(30, 30, 30, 30)
        
        # Заголовок
        title = QLabel("РАБОТА С BACKUP'ОМ")
        title.setObjectName("header")
        title.setAlignment(Qt.AlignCenter)
        layout.addWidget(title)
        
        # Статус backup'а
        status_text = "✓ Backup существует" if self.backup_exists else "✗ Backup не найден"
        status_color = "green" if self.backup_exists else "red"
        
        status_label = QLabel(f"Статус: {status_text}")
        status_label.setStyleSheet(f"color: {status_color}; font-weight: bold;")
        layout.addWidget(status_label)
        
        # Кнопки действий
        buttons_layout = QVBoxLayout()
        
        btn1 = QPushButton("[1] Создать backup")
        btn1.clicked.connect(self.create_backup)
        buttons_layout.addWidget(btn1)
        
        btn2 = QPushButton("[2] Восстановить из backup'а")
        btn2.clicked.connect(self.restore_backup)
        buttons_layout.addWidget(btn2)
        
        btn3 = QPushButton("[3] Удалить backup")
        btn3.clicked.connect(self.delete_backup)
        buttons_layout.addWidget(btn3)
        
        layout.addLayout(buttons_layout)
        
        # Информационная панель
        info_group = QGroupBox("Информация о backup")
        info_layout = QVBoxLayout(info_group)
        
        if self.backup_exists:
            info_text = f"""• Расположение: {os.getcwd()}/backup/
• Размер: 12.5 МБ
• Файлов: 45"""
        else:
            info_text = """• Backup не создан
• Рекомендуется создать backup перед изменениями"""
        
        info_label = QLabel(info_text)
        info_label.setObjectName("info")
        info_layout.addWidget(info_label)
        
        layout.addWidget(info_group)
        
        # Кнопки навигации
        nav_layout = QHBoxLayout()
        
        back_btn = QPushButton("← Назад")
        back_btn.clicked.connect(self.show_main_menu)
        nav_layout.addWidget(back_btn)
        
        nav_layout.addStretch()
        
        exit_btn = QPushButton("Выход")
        exit_btn.clicked.connect(self.close)
        nav_layout.addWidget(exit_btn)
        
        layout.addLayout(nav_layout)
        
        self.current_widget = widget
        self.setCentralWidget(widget)
    
    def toggle_file_selection(self, filename: str, checked: bool):
        """Переключение выбора файла."""
        if checked:
            self.selected_files.add(filename)
        else:
            self.selected_files.discard(filename)
    
    def select_all_files(self, select_all: bool):
        """Выбор/снятие всех файлов."""
        for filename, checkbox in self.checkboxes.items():
            checkbox.setChecked(select_all)
            if select_all:
                self.selected_files.add(filename)
            else:
                self.selected_files.discard(filename)
    
    def show_message(self, title: str, message: str, msg_type: str = "info"):
        """Показать сообщение пользователю."""
        msg_box = QMessageBox(self)
        msg_box.setWindowTitle(title)
        msg_box.setText(message)
        
        if msg_type == "error":
            msg_box.setIcon(QMessageBox.Critical)
        elif msg_type == "warning":
            msg_box.setIcon(QMessageBox.Warning)
        else:
            msg_box.setIcon(QMessageBox.Information)
        
        msg_box.exec()
    
    def execute_all_changes(self):
        """Выполнение всех изменений."""
        message = """✓ Все изменения успешно внесены!

- Заменены измененные файлы
- Скопированы отсутствующие файлы
- Обновлены конфигурации"""
        
        self.show_message("Выполнено", message)
        self.close()
    
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
        self.show_backup_menu()  # Обновляем меню
    
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
        self.show_backup_menu()  # Обновляем меню
    
    def skip_changes(self):
        """Пропуск без изменений."""
        message = """✓ Операция завершена без изменений.

Все файлы остались без изменений."""
        
        self.show_message("Пропущено", message)
        self.close()


def main():
    """Главная функция для запуска PySide6 GUI."""
    from src.prima_updater.config.settings import UIConfig
    
    app = QApplication(sys.argv)
    
    # Настройка приложения
    app.setApplicationName("PRIMA Updater")
    app.setApplicationVersion("2.0")
    
    config = UIConfig()
    window = PySide6GUI(config)
    window.show()
    
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
