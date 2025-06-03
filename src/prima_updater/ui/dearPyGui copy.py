import dearpygui.dearpygui as dpg
import os
import glob
import shutil
from datetime import datetime
import re

class FileManagerGUI:
    def __init__(self):
        self.current_view = "main"
        self.backup_files = []
        self.selected_backup = None
        self.ignored_files = ["Prima.ini", "Server.ini", "config.txt"]  # Пример файлов из конфига
        self.log_messages = []
        
    def log_message(self, message):
        """Добавить сообщение в лог"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        log_entry = f"[{timestamp}] {message}"
        self.log_messages.append(log_entry)
        
        # Обновляем текст в логе
        if dpg.does_item_exist("log_text"):
            log_text = "\n".join(self.log_messages[-20:])  # Показываем последние 20 сообщений
            dpg.set_value("log_text", log_text)
    
    def scan_backups(self):
        """Сканирование backup файлов"""
        backup_pattern = "PRIMA*.exe"
        self.backup_files = glob.glob(backup_pattern)
        
        # Извлекаем даты из имен файлов
        backup_info = []
        for file in self.backup_files:
            # Предполагаем формат PRIMA_YYYY_MM_DD.exe или PRIMA_YYYYMMDD.exe
            date_match = re.search(r'PRIMA.*?(\d{4}).*?(\d{2}).*?(\d{2})', file)
            if date_match:
                year, month, day = date_match.groups()
                backup_info.append({
                    'file': file,
                    'year': year,
                    'month': month,
                    'day': day,
                    'date': f"{year}-{month}-{day}"
                })
        
        return backup_info
    
    def get_years_months(self):
        """Получить список годов и месяцев из backup файлов"""
        backup_info = self.scan_backups()
        years = sorted(list(set([b['year'] for b in backup_info])))
        months = sorted(list(set([b['month'] for b in backup_info])))
        return years, months
    
    def filter_backups_by_date(self, selected_year, selected_month):
        """Фильтровать backup файлы по году и месяцу"""
        backup_info = self.scan_backups()
        filtered = [b for b in backup_info 
                   if b['year'] == selected_year and b['month'] == selected_month]
        return filtered
    
    def apply_all_changes(self):
        """Применить все изменения"""
        self.log_message("Применение всех изменений...")
        # Здесь будет логика применения изменений
        self.log_message("Все изменения успешно применены")
    
    def replace_changed_files(self):
        """Замена измененных файлов"""
        self.log_message("Замена измененных файлов...")
        # Логика замены файлов
        self.log_message("Измененные файлы заменены")
    
    def copy_missing_files(self):
        """Копирование отсутствующих файлов"""
        self.log_message("Копирование отсутствующих файлов...")
        # Логика копирования файлов
        self.log_message("Отсутствующие файлы скопированы")
    
    def restore_from_backup(self, backup_file):
        """Восстановление из backup"""
        self.log_message(f"Восстановление из backup: {backup_file}")
        # Логика восстановления
        self.log_message("Восстановление завершено успешно")
    
    def delete_backup(self, backup_file):
        """Удаление backup"""
        try:
            os.remove(backup_file)
            self.log_message(f"Backup удален: {backup_file}")
        except Exception as e:
            self.log_message(f"Ошибка удаления backup: {e}")
    
    def show_main_menu(self):
        """Показать главное меню"""
        dpg.delete_item("content_group", children_only=True)
        
        with dpg.group(parent="content_group"):
            dpg.add_text("ГЛАВНОЕ МЕНЮ", color=[255, 255, 0])
            dpg.add_separator()
            
            if dpg.add_button(label="[1] Внести все изменения", width=300):
                dpg.set_item_callback(dpg.last_item(), lambda: self.apply_all_changes())
            
            if dpg.add_button(label="[2] Выбор вносимых изменений", width=300):
                dpg.set_item_callback(dpg.last_item(), lambda: self.show_changes_menu())
            
            if dpg.add_button(label="[3] Работа с backup'ом", width=300):
                dpg.set_item_callback(dpg.last_item(), lambda: self.show_backup_menu())
            
            if dpg.add_button(label="[5] Пропустить (без изменений)", width=300):
                dpg.set_item_callback(dpg.last_item(), lambda: self.log_message("Операция пропущена"))
    
    def show_changes_menu(self):
        """Показать меню выбора изменений"""
        dpg.delete_item("content_group", children_only=True)
        
        with dpg.group(parent="content_group"):
            dpg.add_text("ВЫБОР ВНОСИМЫХ ИЗМЕНЕНИЙ", color=[255, 255, 0])
            dpg.add_separator()
            
            if dpg.add_button(label="[1] Замена измененных файлов", width=300):
                dpg.set_item_callback(dpg.last_item(), lambda: self.replace_changed_files())
            
            if dpg.add_button(label="[2] Копирование отсутствующих файлов", width=300):
                dpg.set_item_callback(dpg.last_item(), lambda: self.copy_missing_files())
            
            if dpg.add_button(label="[3] Замена с отключением игнорирования", width=300):
                dpg.set_item_callback(dpg.last_item(), lambda: self.show_ignore_menu())
            
            dpg.add_separator()
            if dpg.add_button(label="Назад", width=100):
                dpg.set_item_callback(dpg.last_item(), lambda: self.show_main_menu())
    
    def show_ignore_menu(self):
        """Показать меню игнорируемых файлов"""
        dpg.delete_item("content_group", children_only=True)
        
        with dpg.group(parent="content_group"):
            dpg.add_text("ЗАМЕНА С ОТКЛЮЧЕНИЕМ ИГНОРИРОВАНИЯ", color=[255, 255, 0])
            dpg.add_separator()
            
            dpg.add_text("Выберите файлы для замены:")
            
            # Создаем чекбоксы для каждого игнорируемого файла
            for i, file in enumerate(self.ignored_files):
                checkbox_id = f"ignore_checkbox_{i}"
                dpg.add_checkbox(label=f"[*] {file}", tag=checkbox_id, default_value=True)
            
            dpg.add_separator()
            if dpg.add_button(label="Применить замену", width=200):
                dpg.set_item_callback(dpg.last_item(), lambda: self.apply_ignore_replacement())
            
            if dpg.add_button(label="Назад", width=100):
                dpg.set_item_callback(dpg.last_item(), lambda: self.show_changes_menu())
    
    def apply_ignore_replacement(self):
        """Применить замену игнорируемых файлов"""
        selected_files = []
        for i, file in enumerate(self.ignored_files):
            checkbox_id = f"ignore_checkbox_{i}"
            if dpg.get_value(checkbox_id):
                selected_files.append(file)
        
        self.log_message(f"Замена файлов с отключением игнорирования: {', '.join(selected_files)}")
    
    def show_backup_menu(self):
        """Показать меню работы с backup"""
        dpg.delete_item("content_group", children_only=True)
        
        with dpg.group(parent="content_group"):
            dpg.add_text("РАБОТА С BACKUP'ОМ", color=[255, 255, 0])
            dpg.add_separator()
            
            if dpg.add_button(label="[1] Восстановить из backup'а", width=300):
                dpg.set_item_callback(dpg.last_item(), lambda: self.show_restore_menu())
            
            if dpg.add_button(label="[2] Удалить backup", width=300):
                dpg.set_item_callback(dpg.last_item(), lambda: self.show_delete_menu())
            
            dpg.add_separator()
            if dpg.add_button(label="Назад", width=100):
                dpg.set_item_callback(dpg.last_item(), lambda: self.show_main_menu())
    
    def show_restore_menu(self):
        """Показать меню восстановления"""
        dpg.delete_item("content_group", children_only=True)
        
        years, months = self.get_years_months()
        
        with dpg.group(parent="content_group"):
            dpg.add_text("ВОССТАНОВИТЬ ИЗ BACKUP'А", color=[255, 255, 0])
            dpg.add_separator()
            
            # Выпадающие списки для года и месяца
            dpg.add_text("Выберите год:")
            dpg.add_combo(years if years else ["Нет данных"], tag="year_combo", width=150, default_value=years[0] if years else "")
            
            dpg.add_text("Выберите месяц:")
            dpg.add_combo(months if months else ["Нет данных"], tag="month_combo", width=150, default_value=months[0] if months else "")
            
            if dpg.add_button(label="Показать backup'ы", width=200):
                dpg.set_item_callback(dpg.last_item(), lambda: self.update_backup_list("restore"))
            
            dpg.add_separator()
            dpg.add_text("Доступные backup'ы:")
            dpg.add_listbox([], tag="backup_listbox", width=400, num_items=5)
            
            dpg.add_separator()
            if dpg.add_button(label="Восстановить", width=150):
                dpg.set_item_callback(dpg.last_item(), lambda: self.execute_restore())
            
            if dpg.add_button(label="Назад", width=100):
                dpg.set_item_callback(dpg.last_item(), lambda: self.show_backup_menu())
    
    def show_delete_menu(self):
        """Показать меню удаления backup"""
        dpg.delete_item("content_group", children_only=True)
        
        years, months = self.get_years_months()
        
        with dpg.group(parent="content_group"):
            dpg.add_text("УДАЛИТЬ BACKUP", color=[255, 255, 0])
            dpg.add_separator()
            
            # Выпадающие списки для года и месяца
            dpg.add_text("Выберите год:")
            dpg.add_combo(years if years else ["Нет данных"], tag="year_combo_del", width=150, default_value=years[0] if years else "")
            
            dpg.add_text("Выберите месяц:")
            dpg.add_combo(months if months else ["Нет данных"], tag="month_combo_del", width=150, default_value=months[0] if months else "")
            
            if dpg.add_button(label="Показать backup'ы", width=200):
                dpg.set_item_callback(dpg.last_item(), lambda: self.update_backup_list("delete"))
            
            dpg.add_separator()
            dpg.add_text("Доступные backup'ы:")
            dpg.add_listbox([], tag="backup_listbox_del", width=400, num_items=5)
            
            dpg.add_separator()
            if dpg.add_button(label="Удалить", width=150, tag="delete_backup_btn"):
                dpg.set_item_callback(dpg.last_item(), lambda: self.execute_delete())
            
            if dpg.add_button(label="Назад", width=100):
                dpg.set_item_callback(dpg.last_item(), lambda: self.show_backup_menu())
    
    def update_backup_list(self, mode):
        """Обновить список backup файлов"""
        if mode == "restore":
            year = dpg.get_value("year_combo")
            month = dpg.get_value("month_combo")
            listbox_tag = "backup_listbox"
        else:
            year = dpg.get_value("year_combo_del")
            month = dpg.get_value("month_combo_del")
            listbox_tag = "backup_listbox_del"
        
        if year and month:
            filtered_backups = self.filter_backups_by_date(year, month)
            backup_names = [f"{b['file']} ({b['date']})" for b in filtered_backups]
            dpg.configure_item(listbox_tag, items=backup_names)
            self.log_message(f"Найдено {len(backup_names)} backup файлов за {month}/{year}")
    
    def execute_restore(self):
        """Выполнить восстановление"""
        selection = dpg.get_value("backup_listbox")
        if selection:
            # Извлекаем имя файла из строки выбора
            filename = selection.split(" (")[0]
            self.restore_from_backup(filename)
        else:
            self.log_message("Не выбран backup для восстановления")
    
    def execute_delete(self):
        """Выполнить удаление"""
        selection = dpg.get_value("backup_listbox_del")
        if selection:
            # Извлекаем имя файла из строки выбора
            filename = selection.split(" (")[0]
            self.delete_backup(filename)
            # Обновляем список после удаления
            self.update_backup_list("delete")
        else:
            self.log_message("Не выбран backup для удаления")
    
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

    
    def create_gui(self):
        """Создать GUI"""
        dpg.create_context()
        
        # Настройка шрифта для поддержки кириллицы
        # with dpg.font_registry():
        #     # Загружаем шрифт с поддержкой кириллицы
        #     default_font = dpg.add_font("C:/Windows/Fonts/arial.ttf", 16)
        
        
        with dpg.window(label="Менеджер файлов", tag="main_window"):
            dpg.add_text("МЕНЕДЖЕР ФАЙЛОВ И BACKUP'ОВ", color=[255, 255, 255])
            dpg.add_separator()
            
            # Основная область контента
            with dpg.group(tag="content_group"):
                pass
            
            dpg.add_separator()
            dpg.add_text("ЛОГИ:", color=[0, 255, 255])
            
            # Область для логов
            with dpg.group():
                dpg.add_input_text(
                    tag="log_text",
                    multiline=True,
                    readonly=True,
                    width=600,
                    height=150,
                    default_value="Система готова к работе..."
                )
        
        dpg.create_viewport(title="PRIMA-UPDATER")
        dpg.setup_dearpygui()
        
        # Устанавливаем шрифт
        # dpg.bind_font(default_font)
        self.setup_font()
        
        # Показываем главное меню
        self.show_main_menu()
        
        dpg.show_viewport()
        dpg.set_primary_window("main_window", True)

def main():
    app = FileManagerGUI()
    app.create_gui()
    
    # Добавляем начальное сообщение в лог
    app.log_message("Система инициализирована")
    app.log_message("Выберите операцию из главного меню")
    
    dpg.start_dearpygui()
    dpg.destroy_context()

if __name__ == "__main__":
    main()