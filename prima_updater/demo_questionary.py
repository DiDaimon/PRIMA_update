# -*- coding: utf-8 -*-
"""Демонстрация использования Questionary для интерактивного меню.

Questionary - более современная альтернатива Inquirer с лучшей поддержкой.
"""

try:
    import questionary
except ImportError:
    print("Для работы этого демо необходимо установить questionary:")
    print("pip install questionary")
    exit(1)


def demo_select_menu():
    """Демонстрация меню выбора."""
    print("\n" + "=" * 60)
    print("Демонстрация: Меню выбора (Select)")
    print("=" * 60)
    
    choice = questionary.select(
        "Выберите действие",
        choices=[
            "Для замены измененных файлов",
            "Для копирования отсутствующих файлов",
            "Для внесения всех изменений",
            "Для полного копирования",
            "Для пропуска (без изменений)",
        ],
        use_shortcuts=True,  # Поддержка горячих клавиш
        style=questionary.Style([
            ('question', 'fg:#ff0066 bold'),
            ('answer', 'fg:#44ff00 bold'),
            ('pointer', 'fg:#44ff00 bold'),
            ('highlighted', 'fg:#ff0066 bg:#000000 bold'),
            ('selected', 'fg:#ccff00'),
            ('separator', 'fg:#cc00ff'),
            ('instruction', 'fg:#000000'),
            ('text', 'fg:#f0f0f0'),
            ('disabled', 'fg:#858585 italic')
        ])
    ).ask()
    
    if choice:
        print(f"\nВыбрано: {choice}")


def demo_checkbox_files():
    """Демонстрация множественного выбора файлов."""
    print("\n" + "=" * 60)
    print("Демонстрация: Множественный выбор (Checkbox)")
    print("=" * 60)
    
    files = [
        "PRIMA.exe",
        "config.ini",
        "module.dll",
        "data.json",
        "settings.xml"
    ]
    
    selected = questionary.checkbox(
        "Выберите файлы для обновления",
        choices=files,
        default=files[:2]  # По умолчанию выбраны первые два
    ).ask()
    
    if selected:
        print(f"\nВыбраны файлы: {', '.join(selected)}")


def demo_backup_list():
    """Демонстрация выбора бэкапа."""
    print("\n" + "=" * 60)
    print("Демонстрация: Выбор бэкапа")
    print("=" * 60)
    
    backups = [
        questionary.Choice(
            title="PRIMA[10.11.25].exe (создан: 10.11.2025 14:30)",
            value="backup1"
        ),
        questionary.Choice(
            title="PRIMA[09.11.25].exe (создан: 09.11.2025 10:15)",
            value="backup2"
        ),
        questionary.Choice(
            title="PRIMA[08.11.25].exe (создан: 08.11.2025 16:45)",
            value="backup3"
        ),
        questionary.Separator(),
        questionary.Choice(
            title="Отмена",
            value="cancel"
        )
    ]
    
    choice = questionary.select(
        "Выберите бэкап для восстановления",
        choices=backups
    ).ask()
    
    if choice:
        if choice == "cancel":
            print("\nОперация отменена")
        else:
            print(f"\nВыбран бэкап: {choice}")


def demo_confirm():
    """Демонстрация подтверждения."""
    print("\n" + "=" * 60)
    print("Демонстрация: Подтверждение действия")
    print("=" * 60)
    
    confirmed = questionary.confirm(
        "Вы уверены, что хотите выполнить полное копирование?",
        default=False
    ).ask()
    
    if confirmed:
        print("\nОперация подтверждена")
    else:
        print("\nОперация отменена")


def demo_text_input():
    """Демонстрация текстового ввода."""
    print("\n" + "=" * 60)
    print("Демонстрация: Текстовый ввод")
    print("=" * 60)
    
    def validate_path(text):
        """Валидация пути."""
        if len(text) < 3:
            return "Путь слишком короткий (минимум 3 символа)"
        return True
    
    path = questionary.text(
        "Введите путь к директории",
        validate=validate_path
    ).ask()
    
    if path:
        print(f"\nВведен путь: {path}")


def demo_password():
    """Демонстрация ввода пароля."""
    print("\n" + "=" * 60)
    print("Демонстрация: Ввод пароля (скрытый)")
    print("=" * 60)
    
    password = questionary.password(
        "Введите пароль для доступа к серверу"
    ).ask()
    
    if password:
        print("\nПароль введен (скрыт для безопасности)")


def demo_autocomplete():
    """Демонстрация автодополнения."""
    print("\n" + "=" * 60)
    print("Демонстрация: Автодополнение")
    print("=" * 60)
    
    def autocomplete_path(text, state):
        """Автодополнение путей."""
        options = [
            r"D:\User\PRIMA_Updated",
            r"D:\User\PRIMA_Old",
            r"D:\Programs\PRIMA",
            r"D:\Backup\PRIMA"
        ]
        matches = [opt for opt in options if opt.lower().startswith(text.lower())]
        try:
            return matches[state]
        except IndexError:
            return None
    
    path = questionary.autocomplete(
        "Введите путь (начните вводить для автодополнения)",
        choices=[
            r"D:\User\PRIMA_Updated",
            r"D:\User\PRIMA_Old",
            r"D:\Programs\PRIMA",
            r"D:\Backup\PRIMA"
        ]
    ).ask()
    
    if path:
        print(f"\nВыбран путь: {path}")


def demo_combined():
    """Демонстрация комбинированного использования."""
    print("\n" + "=" * 60)
    print("Демонстрация: Комбинированное использование")
    print("=" * 60)
    
    action = questionary.select(
        "Выберите действие",
        choices=[
            "Обновить измененные файлы",
            "Копировать отсутствующие файлы",
            "Внести все изменения",
            "Полное копирование",
            "Пропустить",
        ]
    ).ask()
    
    if action:
        create_backup = questionary.confirm(
            "Создать бэкап перед обновлением?",
            default=True
        ).ask()
        
        print(f"\nДействие: {action}")
        print(f"Создать бэкап: {'Да' if create_backup else 'Нет'}")


def main():
    """Главная функция демонстрации."""
    print("\n" + "=" * 60)
    print("Демонстрация возможностей Questionary для UI")
    print("=" * 60)
    print("\nИспользуйте стрелки ↑↓ для навигации, Enter для выбора")
    
    try:
        demo_select_menu()
        demo_checkbox_files()
        demo_backup_list()
        demo_confirm()
        demo_text_input()
        demo_password()
        demo_autocomplete()
        demo_combined()
        
        print("\n" + "=" * 60)
        print("Демонстрация завершена!")
        print("=" * 60)
    except KeyboardInterrupt:
        print("\n\nОперация прервана пользователем")


if __name__ == '__main__':
    main()

