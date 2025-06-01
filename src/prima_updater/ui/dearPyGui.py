# Демонстрация меню с помощью DearPyGui
# Установка: pip install dearpygui

import dearpygui.dearpygui as dpg
import os
import sys

# Альтернативный способ - создать файл шрифта
def create_cyrillic_font_file():
    """Создать минимальный TTF файл с кириллицей (если нет системного шрифта)"""
    # Это простой способ создать базовый шрифт
    # В реальном проекте лучше использовать готовый TTF файл
    font_data = b'\x00\x01\x00\x00\x00\x0f\x00\x80\x00\x03\x00 \x4f\x53/2V\x1b\xe8\x14\x00\x00\x01\x88\x00\x00\x00V'
    
    try:
        with open('temp_font.ttf', 'wb') as f:
            f.write(font_data)
        return 'temp_font.ttf'
    except:
        return None

# Конфигурационные файлы для демонстрации
CONFIG_FILES = [
    "Prima.ini",
    "Server.ini", 
    "Database.ini",
    "Logger.ini",
    "Network.ini",
    "Security.ini"
]

class MenuApp:
    def __init__(self):
        self.current_window = None
        self.selected_files = set()
        self.backup_exists = False
        
    def show_message(self, title, message, callback=None):
        """Показать сообщение пользователю"""
        with dpg.window(label=title, modal=True, show=True, no_resize=True, 
                       width=400, height=150, pos=[200, 200]) as modal:
            dpg.add_text(message, wrap=350)
            dpg.add_separator()
            with dpg.group(horizontal=True):
                dpg.add_spacer(width=250)
                if callback:
                    dpg.add_button(label="OK", callback=lambda: [callback(), dpg.delete_item(modal)])
                else:
                    dpg.add_button(label="OK", callback=lambda: dpg.delete_item(modal))
    
    def execute_all_changes(self):
        """Выполнить все изменения"""
        self.show_message("Выполнено", 
                         "✓ Все изменения успешно внесены!\n\n"
                         "- Заменены измененные файлы\n"
                         "- Скопированы отсутствующие файлы\n" 
                         "- Обновлены конфигурации", 
                         self.close_app)
    
    def replace_changed_files(self):
        """Замена измененных файлов"""
        self.show_message("Выполнено", 
                         "✓ Измененные файлы успешно заменены!\n\n"
                         "Обработано файлов: 12\n"
                         "Обновлено: 8\n"
                         "Пропущено: 4")
    
    def copy_missing_files(self):
        """Копирование отсутствующих файлов"""
        self.show_message("Выполнено",
                         "✓ Отсутствующие файлы успешно скопированы!\n\n"
                         "Скопировано файлов: 5\n"
                         "Созданы папки: 2")
    
    def toggle_file_selection(self, sender, app_data, user_data):
        """Переключить выбор файла"""
        filename = user_data
        if app_data:
            self.selected_files.add(filename)
        else:
            self.selected_files.discard(filename)
    
    def apply_ignore_changes(self):
        """Применить изменения с отключением игнорирования"""
        if not self.selected_files:
            self.show_message("Ошибка", "Не выбрано ни одного файла!")
            return
        
        files_list = "\n".join([f"• {f}" for f in self.selected_files])
        self.show_message("Выполнено",
                         f"✓ Замена с отключением игнорирования выполнена!\n\n"
                         f"Обработанные файлы:\n{files_list}")
    
    def create_backup(self):
        """Создать backup"""
        self.backup_exists = True
        self.show_message("Выполнено",
                         "✓ Backup успешно создан!\n\n"
                         f"Расположение: {os.getcwd()}/backup/\n"
                         "Файлов архивировано: 45\n"
                         f"Размер: 12.5 МБ")
    
    def restore_backup(self):
        """Восстановить из backup'а"""
        if not self.backup_exists:
            self.show_message("Ошибка", "Backup не найден!\nСначала создайте backup.")
            return
            
        self.show_message("Выполнено",
                         "✓ Восстановление из backup'а завершено!\n\n"
                         "Восстановлено файлов: 45\n"
                         "Время операции: 3.2 сек")
    
    def delete_backup(self):
        """Удалить backup"""
        if not self.backup_exists:
            self.show_message("Ошибка", "Backup не найден!")
            return
            
        self.backup_exists = False
        self.show_message("Выполнено",
                         "✓ Backup успешно удален!\n\n"
                         "Освобождено места: 12.5 МБ")
    
    def skip_changes(self):
        """Пропустить без изменений"""
        self.show_message("Пропущено",
                         "✓ Операция завершена без изменений.\n\n"
                         "Все файлы остались без изменений.",
                         self.close_app)
    
    def close_app(self):
        """Закрыть приложение"""
        dpg.stop_dearpygui()
    
    def show_main_window(self):
        """Показать главное окно"""
        if self.current_window:
            dpg.delete_item(self.current_window)
        
        with dpg.window(label="Главное меню", width=500, height=400, 
                       no_resize=True, no_move=True, no_close=True) as main_window:
            self.current_window = main_window
            
            # Заголовок
            dpg.add_text("СИСТЕМА УПРАВЛЕНИЯ ИЗМЕНЕНИЯМИ", color=[100, 149, 237])
            dpg.add_separator()
            dpg.add_spacer(height=10)
            
            # Основные опции
            with dpg.group():
                dpg.add_button(label="[1] Для внесения ВСЕХ изменений", 
                              callback=self.execute_all_changes,
                              width=400, height=35)
                dpg.add_spacer(height=5)
                
                dpg.add_button(label="[2] Выбор вносимых изменений", 
                              callback=self.show_changes_window,
                              width=400, height=35)
                dpg.add_spacer(height=5)
                
                dpg.add_button(label="[3] Работа с backup'ом", 
                              callback=self.show_backup_window,
                              width=400, height=35)
                dpg.add_spacer(height=5)
                
                dpg.add_button(label="[5] Для пропуска (без изменений)", 
                              callback=self.skip_changes,
                              width=400, height=35)
            
            dpg.add_spacer(height=20)
            dpg.add_separator()
            
            # Информационная панель
            with dpg.child_window(height=100, border=True):
                dpg.add_text("Информация:", color=[255, 215, 0])
                dpg.add_text("• Выберите необходимое действие")
                dpg.add_text("• Все операции безопасны")
                dpg.add_text("• Рекомендуется создать backup перед изменениями")
            
            dpg.add_spacer(height=10)
            
            # Кнопка выхода
            with dpg.group(horizontal=True):
                dpg.add_spacer(width=320)
                dpg.add_button(label="Выход", callback=self.close_app, width=80)
    
    def show_changes_window(self):
        """Показать окно выбора изменений"""
        if self.current_window:
            dpg.delete_item(self.current_window)
        
        with dpg.window(label="Выбор вносимых изменений", width=500, height=400,
                       no_resize=True, no_move=True, no_close=True) as changes_window:
            self.current_window = changes_window
            
            dpg.add_text("ВЫБОР ВНОСИМЫХ ИЗМЕНЕНИЙ", color=[34, 139, 34])
            dpg.add_separator()
            dpg.add_spacer(height=10)
            
            with dpg.group():
                dpg.add_button(label="[1] Замена измененных файлов",
                              callback=self.replace_changed_files,
                              width=400, height=35)
                dpg.add_spacer(height=5)
                
                dpg.add_button(label="[2] Копирование отсутствующих файлов",
                              callback=self.copy_missing_files, 
                              width=400, height=35)
                dpg.add_spacer(height=5)
                
                dpg.add_button(label="[3] Замена с отключением игнорирования",
                              callback=self.show_ignore_window,
                              width=400, height=35)
            
            dpg.add_spacer(height=20)
            dpg.add_separator()
            
            # Информационная панель
            with dpg.child_window(height=120, border=True):
                dpg.add_text("Описание опций:", color=[255, 215, 0])
                dpg.add_text("• Замена измененных - обновляет только модифицированные файлы")
                dpg.add_text("• Копирование отсутствующих - добавляет новые файлы")  
                dpg.add_text("• Замена с отключением игнорирования - принудительная замена")
                dpg.add_text("  выбранных конфигурационных файлов")
            
            dpg.add_spacer(height=10)
            
            # Кнопка назад
            with dpg.group(horizontal=True):
                dpg.add_button(label="← Назад", callback=self.show_main_window, width=80)
                dpg.add_spacer(width=240)
                dpg.add_button(label="Выход", callback=self.close_app, width=80)
    
    def show_ignore_window(self):
        """Показать окно выбора файлов для замены с отключением игнорирования"""
        if self.current_window:
            dpg.delete_item(self.current_window)
        
        with dpg.window(label="Замена с отключением игнорирования", width=500, height=500,
                       no_resize=True, no_move=True, no_close=True) as ignore_window:
            self.current_window = ignore_window
            
            dpg.add_text("ЗАМЕНА С ОТКЛЮЧЕНИЕМ ИГНОРИРОВАНИЯ", color=[255, 140, 0])
            dpg.add_separator()
            dpg.add_spacer(height=10)
            
            dpg.add_text("Выберите файлы для принудительной замены:")
            dpg.add_spacer(height=5)
            
            # Список файлов с чекбоксами
            with dpg.child_window(height=200, border=True):
                for filename in CONFIG_FILES:
                    is_selected = filename in self.selected_files
                    dpg.add_checkbox(label=f"  {filename}", 
                                   default_value=is_selected,
                                   callback=self.toggle_file_selection,
                                   user_data=filename)
            
            dpg.add_spacer(height=10)
            
            # Кнопки управления выбором
            with dpg.group(horizontal=True):
                dpg.add_button(label="Выбрать все", 
                              callback=lambda: self.select_all_files(True), 
                              width=100)
                dpg.add_button(label="Снять все", 
                              callback=lambda: self.select_all_files(False), 
                              width=100)
            
            dpg.add_spacer(height=10)
            dpg.add_separator()
            
            # Информация
            with dpg.child_window(height=80, border=True):
                dpg.add_text("Внимание:", color=[255, 69, 0])
                dpg.add_text("Выбранные файлы будут заменены принудительно,")
                dpg.add_text("игнорируя настройки защиты!")
            
            dpg.add_spacer(height=10)
            
            # Кнопки действий
            with dpg.group(horizontal=True):
                dpg.add_button(label="← Назад", 
                              callback=self.show_changes_window, 
                              width=80)
                dpg.add_spacer(width=150)
                dpg.add_button(label="Применить", 
                              callback=self.apply_ignore_changes, 
                              width=100)
                dpg.add_button(label="Выход", 
                              callback=self.close_app, 
                              width=80)
    
    def select_all_files(self, select_all):
        """Выбрать/снять все файлы"""
        if select_all:
            self.selected_files = set(CONFIG_FILES)
        else:
            self.selected_files.clear()
        
        # Обновить интерфейс
        self.show_ignore_window()
    
    def show_backup_window(self):
        """Показать окно работы с backup'ом"""
        if self.current_window:
            dpg.delete_item(self.current_window)
        
        with dpg.window(label="Работа с backup'ом", width=500, height=400,
                       no_resize=True, no_move=True, no_close=True) as backup_window:
            self.current_window = backup_window
            
            dpg.add_text("РАБОТА С BACKUP'ОМ", color=[186, 85, 211])
            dpg.add_separator()
            dpg.add_spacer(height=10)
            
            # Статус backup'а
            status_color = [34, 139, 34] if self.backup_exists else [220, 20, 60]
            status_text = "✓ Backup существует" if self.backup_exists else "✗ Backup не найден"
            dpg.add_text(f"Статус: {status_text}", color=status_color)
            dpg.add_spacer(height=15)
            
            with dpg.group():
                dpg.add_button(label="[1] Создать backup",
                              callback=self.create_backup,
                              width=400, height=35)
                dpg.add_spacer(height=5)
                
                dpg.add_button(label="[2] Восстановить из backup'а",
                              callback=self.restore_backup,
                              width=400, height=35)
                dpg.add_spacer(height=5)
                
                dpg.add_button(label="[3] Удалить backup",
                              callback=self.delete_backup,
                              width=400, height=35)
            
            dpg.add_spacer(height=20)
            dpg.add_separator()
            
            # Информационная панель
            with dpg.child_window(height=100, border=True):
                dpg.add_text("Информация о backup:", color=[255, 215, 0])
                if self.backup_exists:
                    dpg.add_text(f"• Расположение: {os.getcwd()}/backup/")
                    dpg.add_text("• Размер: 12.5 МБ")
                    dpg.add_text("• Файлов: 45")
                else:
                    dpg.add_text("• Backup не создан")
                    dpg.add_text("• Рекомендуется создать backup перед изменениями")
            
            dpg.add_spacer(height=10)
            
            # Кнопки навигации
            with dpg.group(horizontal=True):
                dpg.add_button(label="← Назад", callback=self.show_main_window, width=80)
                dpg.add_spacer(width=240)
                dpg.add_button(label="Выход", callback=self.close_app, width=80)
    
    def setup_font(self):
        """Настроить шрифт с поддержкой кириллицы"""
        try:
            # Попробуем найти системный шрифт с кириллицей
            import platform
            
            font_path = None
            system = platform.system()
            
            if system == "Windows":
                # Windows шрифты
                possible_fonts = [
                    "C:/Windows/Fonts/arial.ttf",
                    "C:/Windows/Fonts/calibri.ttf", 
                    "C:/Windows/Fonts/tahoma.ttf",
                    "C:/Windows/Fonts/verdana.ttf"
                ]
            elif system == "Darwin":  # macOS
                possible_fonts = [
                    "/System/Library/Fonts/Arial.ttf",
                    "/System/Library/Fonts/Helvetica.ttc",
                    "/Library/Fonts/Arial.ttf"
                ]
            else:  # Linux
                possible_fonts = [
                    "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
                    "/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf",
                    "/usr/share/fonts/TTF/DejaVuSans.ttf",
                    "/usr/share/fonts/truetype/ubuntu/Ubuntu-R.ttf"
                ]
            
            # Найти первый доступный шрифт
            for font in possible_fonts:
                if os.path.exists(font):
                    font_path = font
                    break
            
            if font_path:
                # Настроить диапазоны символов для кириллицы
                with dpg.font_registry():
                    with dpg.font(font_path, 16) as font:
                        # Добавить базовые латинские символы
                        dpg.add_font_range_hint(dpg.mvFontRangeHint_Default)
                        # Добавить кириллические символы
                        dpg.add_font_range(0x0400, 0x04FF)  # Кириллица
                        dpg.add_font_range(0x0500, 0x052F)  # Кириллица дополнение
                        # Добавить специальные символы
                        dpg.add_font_chars("←→✓✗•")
                    
                    dpg.bind_font(font)
                    print(f"Шрифт загружен: {font_path}")
            else:
                print("Системный шрифт не найден, используется встроенный (без кириллицы)")
                
        except Exception as e:
            print(f"Ошибка загрузки шрифта: {e}")
            print("Используется встроенный шрифт (без кириллицы)")

    def run(self):
        """Запустить приложение"""
        # Создать контекст DearPyGui
        dpg.create_context()
        
        # Настроить шрифт с кириллицей
        self.setup_font()
        
        # Создать viewport
        dpg.create_viewport(title="Sistema upravleniya izmeneniyami", 
                           width=520, height=450, resizable=False)
        
        # Установить тему
        with dpg.theme() as global_theme:
            with dpg.theme_component(dpg.mvAll):
                dpg.add_theme_color(dpg.mvThemeCol_WindowBg, (45, 45, 48))
                dpg.add_theme_color(dpg.mvThemeCol_Button, (70, 70, 70))
                dpg.add_theme_color(dpg.mvThemeCol_ButtonHovered, (90, 90, 90))
                dpg.add_theme_color(dpg.mvThemeCol_ButtonActive, (110, 110, 110))
                dpg.add_theme_color(dpg.mvThemeCol_CheckMark, (100, 149, 237))
        
        dpg.bind_theme(global_theme)
        
        # Показать главное окно
        self.show_main_window()
        
        # Настроить и запустить приложение
        dpg.setup_dearpygui()
        dpg.show_viewport()
        
        # Центрировать окно на экране
        dpg.set_primary_window(self.current_window, True)
        
        # Основной цикл
        dpg.start_dearpygui()
        dpg.destroy_context()


def main():
    """Главная функция"""
    try:
        app = MenuApp()
        app.run()
    except ImportError:
        print("DearPyGui не установлен!")
        print("Установите: pip install dearpygui")
        sys.exit(1)
    except Exception as e:
        print(f"Ошибка: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()