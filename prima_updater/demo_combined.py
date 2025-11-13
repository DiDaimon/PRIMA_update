# -*- coding: utf-8 -*-
"""Демонстрация комбинированного использования Rich + Questionary.

Этот вариант объединяет лучшее из обеих библиотек:
- Rich для красивого отображения (таблицы, прогресс-бары, панели)
- Questionary для интерактивного меню

Демонстрирует полную структуру меню проекта PRIMA Updater без реализации функционала.
"""

try:
    from rich.console import Console
    from rich.table import Table
    from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn
    from rich.panel import Panel
    from rich.text import Text
    import questionary
except ImportError:
    print("Для работы этого демо необходимо установить:")
    print("pip install rich questionary")
    exit(1)

from datetime import datetime

console = Console()


def show_header():
    """Отображение заголовка программы."""
    console.print("\n[bold cyan]" + "=" * 60)
    console.print("[bold cyan]PRIMA - UPDATER[/bold cyan]")
    console.print("[bold cyan]" + "=" * 60 + "\n")


def show_status_panels():
    """Отображение панелей со статусом."""
    server_panel = Panel(
        "[green]✓[/green] Сервер доступен\n[blue]Путь:[/blue] \\\\tserver1\\RSU\\PRIMA",
        title="[bold]Статус сервера[/bold]",
        border_style="green"
    )
    
    stats_panel = Panel(
        "[cyan]Измененных:[/cyan] [bold]2[/bold] | [cyan]Отсутствующих:[/cyan] [bold]2[/bold]",
        title="[bold]Статистика[/bold]",
        border_style="cyan"
    )
    
    console.print(server_panel)
    console.print(stats_panel)
    console.print()


def show_changes_table(diff_files, only_files):
    """Отображение изменений в виде таблицы."""
    if not diff_files and not only_files:
        console.print("[yellow]Изменений не обнаружено[/yellow]\n")
        return
    
    table = Table(title="[bold green]Найденные изменения[/bold green]", show_header=True)
    table.add_column("Тип", style="cyan", width=15)
    table.add_column("Файл", style="magenta", width=40)
    table.add_column("Размер", justify="right", style="green", width=10)
    
    for file_path, size in diff_files:
        table.add_row("[yellow]Изменен[/yellow]", file_path, size)
    
    for file_path, size in only_files:
        table.add_row("[red]Отсутствует[/red]", file_path, size)
    
    console.print(table)
    console.print()


def show_main_menu():
    """Главное меню выбора действий."""
    console.print("[bold]" + "=" * 60)
    console.print("[bold]" + " " * 20 + "ВЫБЕРИТЕ ДЕЙСТВИЕ")
    console.print("[bold]" + "=" * 60 + "\n")
    
    choice = questionary.select(
        "Выберите действие:",
        choices=[
            questionary.Separator("📦 ОБНОВЛЕНИЕ:"),
            "1. Обновить все",
            "2. Дополнительно",
            questionary.Separator("💾 ВОССТАНОВЛЕНИЕ:"),
            "3. Восстановить из бэкапа",
            questionary.Separator("❌ ОТМЕНА:"),
            "4. Пропустить обновление",
        ],
        style=questionary.Style([
            ('question', 'fg:#00ff00 bold'),
            ('selected', 'fg:#ffff00 bold'),
            ('separator', 'fg:#888888'),
        ])
    ).ask()
    
    if choice:
        if "1. Обновить все" in choice:
            return 1
        elif "2. Дополнительно" in choice:
            return 2
        elif "3. Восстановить из бэкапа" in choice:
            return 3
        elif "4. Пропустить обновление" in choice:
            return 4
    return None


def show_additional_menu():
    """Подменю дополнительных опций обновления."""
    console.print("\n[bold]" + "=" * 60)
    console.print("[bold]" + " " * 15 + "ДОПОЛНИТЕЛЬНЫЕ ОПЦИИ")
    console.print("[bold]" + "=" * 60 + "\n")
    
    choice = questionary.select(
        "Выберите действие:",
        choices=[
            questionary.Separator("📦 ОБНОВЛЕНИЕ:"),
            "1. Обновить только измененные файлы",
            "2. Скопировать только отсутствующие файлы",
            "3. Полное копирование директории",
            questionary.Separator(""),
            "0. Назад в главное меню",
        ],
        style=questionary.Style([
            ('question', 'fg:#00ff00 bold'),
            ('selected', 'fg:#ffff00 bold'),
        ])
    ).ask()
    
    if choice:
        if "1. Обновить только измененные файлы" in choice:
            return 11
        elif "2. Скопировать только отсутствующие файлы" in choice:
            return 12
        elif "3. Полное копирование директории" in choice:
            return 13
        elif "0. Назад" in choice:
            return -1
    return None


def show_full_copy_options(has_prima_ini=True, has_servers_ini=True):
    """Отображение вариантов полного копирования."""
    console.print("\n[bold]" + "=" * 60)
    console.print("[bold]" + " " * 12 + "ПАРАМЕТРЫ ПОЛНОГО КОПИРОВАНИЯ")
    console.print("[bold]" + "=" * 60 + "\n")
    
    if has_prima_ini or has_servers_ini:
        console.print("[yellow]Обнаружены конфигурационные файлы в целевой директории:[/yellow]")
        if has_prima_ini:
            console.print("  • [cyan]PRIMA.ini[/cyan]")
        if has_servers_ini:
            console.print("  • [cyan]Servers.ini[/cyan]")
        console.print()
        
        choice = questionary.select(
            "Выберите вариант:",
            choices=[
                "1. Полное копирование (ignore-лист включен)",
                "2. Не игнорировать PRIMA.ini",
                "3. Не игнорировать Servers.ini",
                "4. Не игнорировать PRIMA.ini и Servers.ini",
                "5. Полное копирование (переписать все)",
                questionary.Separator(""),
                "0. Назад",
            ],
            style=questionary.Style([
                ('question', 'fg:#00ff00 bold'),
                ('selected', 'fg:#ffff00 bold'),
            ])
        ).ask()
        
        if choice:
            if "1. Полное копирование (ignore-лист включен)" in choice:
                return 20
            elif "2. Не игнорировать PRIMA.ini" in choice:
                return 21
            elif "3. Не игнорировать Servers.ini" in choice:
                return 22
            elif "4. Не игнорировать PRIMA.ini и Servers.ini" in choice:
                return 23
            elif "5. Полное копирование (переписать все)" in choice:
                return 24
            elif "0. Назад" in choice:
                return -1
    else:
        console.print("[yellow]Конфигурационные файлы PRIMA.ini и Servers.ini не найдены.[/yellow]\n")
        
        choice = questionary.select(
            "Выберите вариант:",
            choices=[
                "1. Полное копирование (переписать все)",
                questionary.Separator(""),
                "0. Назад",
            ],
            style=questionary.Style([
                ('question', 'fg:#00ff00 bold'),
                ('selected', 'fg:#ffff00 bold'),
            ])
        ).ask()
        
        if choice:
            if "1. Полное копирование (переписать все)" in choice:
                return 24
            elif "0. Назад" in choice:
                return -1
    
    return None


def confirm_full_copy_overwrite():
    """Подтверждение для режима полного переписывания всех файлов."""
    return questionary.confirm(
        "Переписать всю директорию без исключений?",
        default=False
    ).ask()


def show_restore_filters(years=None):
    """Отображение подменю фильтров для восстановления из бэкапа."""
    console.print("\n[bold]" + "=" * 60)
    console.print("[bold]" + " " * 14 + "ФИЛЬТРЫ ВОССТАНОВЛЕНИЯ")
    console.print("[bold]" + "=" * 60 + "\n")
    
    choice = questionary.select(
        "Выберите фильтр:",
        choices=[
            questionary.Separator("💾 ВОССТАНОВЛЕНИЕ:"),
            "1. Текущий месяц",
            "2. Текущий год",
            "3. Старше",
            questionary.Separator(""),
            "0. Назад",
        ],
        style=questionary.Style([
            ('question', 'fg:#00ff00 bold'),
            ('selected', 'fg:#ffff00 bold'),
        ])
    ).ask()
    
    if choice:
        if "1. Текущий месяц" in choice:
            return ('current_month', None)
        elif "2. Текущий год" in choice:
            return ('current_year', None)
        elif "3. Старше" in choice:
            return show_restore_older_years(years or [])
        elif "0. Назад" in choice:
            return None
    
    return None


def show_restore_older_years(years):
    """Подменю выбора года для фильтра 'Старше'."""
    console.print("\n[bold]" + "=" * 60)
    console.print("[bold]" + " " * 10 + "СТАРШЕ ТЕКУЩЕГО МЕСЯЦА — ВЫБОР ГОДА")
    console.print("[bold]" + "=" * 60 + "\n")
    
    if not years:
        console.print("[yellow]Нет бэкапов старше текущего месяца.[/yellow]\n")
        choice = questionary.select(
            "",
            choices=["0. Назад"],
            style=questionary.Style([
                ('question', 'fg:#00ff00 bold'),
            ])
        ).ask()
        return None
    
    choices = [f"{i}. {year}" for i, year in enumerate(years, 1)]
    choices.append(questionary.Separator(""))
    choices.append("0. Назад")
    
    choice = questionary.select(
        "Выберите год:",
        choices=choices,
        style=questionary.Style([
            ('question', 'fg:#00ff00 bold'),
            ('selected', 'fg:#ffff00 bold'),
        ])
    ).ask()
    
    if choice:
        if "0. Назад" in choice:
            return None
        for i, year in enumerate(years, 1):
            if f"{i}. {year}" in choice:
                return ('older_year', year)
    
    return None


def show_backup_list(backups):
    """Отображение списка бэкапов для выбора."""
    if not backups:
        console.print("\n[bold]" + "=" * 60)
        console.print("[bold]" + " " * 16 + "ДОСТУПНЫЕ БЭКАПЫ")
        console.print("[bold]" + "=" * 60 + "\n")
        console.print("[yellow]Бэкапы не найдены.[/yellow]\n")
        
        questionary.select(
            "",
            choices=["0. Назад"],
            style=questionary.Style([
                ('question', 'fg:#00ff00 bold'),
            ])
        ).ask()
        return -1
    
    table = Table(title="[bold yellow]Доступные бэкапы[/bold yellow]", show_header=True)
    table.add_column("#", style="cyan", width=3, justify="center")
    table.add_column("Имя файла", style="magenta", width=30)
    table.add_column("Дата создания", style="green", width=20)
    
    for i, (name, date) in enumerate(backups, 1):
        table.add_row(str(i), name, date)
    
    table.add_row("0", "[dim]Назад[/dim]", "[dim]-[/dim]")
    
    console.print(table)
    console.print()
    
    choices = [f"{i}. {name} ({date})" for i, (name, date) in enumerate(backups, 1)]
    choices.append(questionary.Separator(""))
    choices.append("0. Назад")
    
    choice = questionary.select(
        "Выберите бэкап для восстановления:",
        choices=choices,
        style=questionary.Style([
            ('question', 'fg:#00ff00 bold'),
            ('selected', 'fg:#ffff00 bold'),
        ])
    ).ask()
    
    if choice:
        if "0. Назад" in choice:
            return -1
        for i in range(len(backups)):
            if f"{i+1}." in choice:
                return i
    
    return -1


def show_progress_bar(files, action_name="Копирование"):
    """Отображение прогресс-бара при копировании."""
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        BarColumn(),
        TextColumn("[progress.percentage]{task.percentage:>3.0f}%"),
        console=console
    ) as progress:
        task = progress.add_task(f"[green]{action_name} файлов...", total=len(files))
        
        import time
        for file in files:
            time.sleep(0.2)
            progress.update(task, advance=1, description=f"[green]{action_name}: {file}")


def show_action_result(action_name, success=True):
    """Отображение результата выполнения действия."""
    if success:
        console.print(f"\n[bold green]✓ {action_name} выполнено успешно![/bold green]\n")
    else:
        console.print(f"\n[bold red]✗ Ошибка при выполнении: {action_name}[/bold red]\n")


def main():
    """Главная функция демонстрации."""
    show_header()
    
    # Пример данных
    diff_files = [
        ("PRIMA.exe", "2.5 MB"),
        ("config.ini", "1.2 KB")
    ]
    only_files = [
        ("new_module.dll", "150 KB"),
        ("data.json", "5.3 KB")
    ]
    
    backups = [
        ("PRIMA[10.11.25].exe", "10.11.2025 14:30"),
        ("PRIMA[09.11.25].exe", "09.11.2025 10:15"),
        ("PRIMA[08.11.25].exe", "08.11.2025 16:45"),
    ]
    
    older_years = [2024, 2023]
    
    # Показываем статус
    show_status_panels()
    
    # Показываем изменения
    show_changes_table(diff_files, only_files)
    
    # Главный цикл меню
    while True:
        choice = show_main_menu()
        
        if choice == 1:
            # Обновить все
            console.print("\n[cyan]Выбрано: Обновить все[/cyan]\n")
            
            if questionary.confirm("Создать бэкап перед обновлением?", default=True).ask():
                console.print("[green]Бэкап будет создан...[/green]\n")
                import time
                time.sleep(0.5)
            
            files_to_copy = [f[0] for f in diff_files + only_files]
            show_progress_bar(files_to_copy, "Обновление")
            show_action_result("Обновление всех изменений")
            break
            
        elif choice == 2:
            # Дополнительно
            while True:
                additional_choice = show_additional_menu()
                
                if additional_choice == -1:
                    # Назад в главное меню
                    break
                elif additional_choice == 11:
                    # Обновить только измененные файлы
                    console.print("\n[cyan]Выбрано: Обновить только измененные файлы[/cyan]\n")
                    
                    if questionary.confirm("Создать бэкап перед обновлением?", default=True).ask():
                        console.print("[green]Бэкап будет создан...[/green]\n")
                        import time
                        time.sleep(0.5)
                    
                    files_to_copy = [f[0] for f in diff_files]
                    show_progress_bar(files_to_copy, "Обновление")
                    show_action_result("Обновление измененных файлов")
                    break
                    
                elif additional_choice == 12:
                    # Скопировать только отсутствующие файлы
                    console.print("\n[cyan]Выбрано: Скопировать только отсутствующие файлы[/cyan]\n")
                    
                    if questionary.confirm("Создать бэкап перед обновлением?", default=True).ask():
                        console.print("[green]Бэкап будет создан...[/green]\n")
                        import time
                        time.sleep(0.5)
                    
                    files_to_copy = [f[0] for f in only_files]
                    show_progress_bar(files_to_copy, "Копирование")
                    show_action_result("Копирование отсутствующих файлов")
                    break
                    
                elif additional_choice == 13:
                    # Полное копирование
                    while True:
                        full_option = show_full_copy_options(has_prima_ini=True, has_servers_ini=True)
                        
                        if full_option == -1:
                            # Назад к подменю "Дополнительно"
                            break
                        elif full_option == 24:
                            # Полное переписывание - требуется подтверждение
                            if not confirm_full_copy_overwrite():
                                console.print("[yellow]Операция отменена[/yellow]\n")
                                break
                        
                        console.print(f"\n[cyan]Выбрано: Полное копирование (вариант {full_option})[/cyan]\n")
                        
                        if questionary.confirm("Создать бэкап перед обновлением?", default=True).ask():
                            console.print("[green]Бэкап будет создан...[/green]\n")
                            import time
                            time.sleep(0.5)
                        
                        all_files = [f[0] for f in diff_files + only_files] + ["другие файлы..."]
                        show_progress_bar(all_files, "Полное копирование")
                        show_action_result("Полное копирование директории")
                        break
                    
                    if full_option != -1:
                        break
            else:
                continue
            break
            
        elif choice == 3:
            # Восстановить из бэкапа
            while True:
                filter_result = show_restore_filters(older_years)
                
                if filter_result is None:
                    # Назад в главное меню
                    break
                
                filter_key, filter_arg = filter_result
                console.print(f"\n[cyan]Выбран фильтр: {filter_key}[/cyan]\n")
                
                # Симуляция фильтрации бэкапов
                if filter_key == 'current_month':
                    filtered_backups = backups[:1]
                elif filter_key == 'current_year':
                    filtered_backups = backups[:2]
                elif filter_key == 'older_year':
                    filtered_backups = backups[2:]
                else:
                    filtered_backups = backups
                
                if not filtered_backups:
                    console.print("[yellow]По выбранному фильтру бэкапы не найдены[/yellow]\n")
                    continue
                
                backup_index = show_backup_list(filtered_backups)
                
                if backup_index >= 0:
                    selected_backup = filtered_backups[backup_index]
                    console.print(f"\n[cyan]Выбран бэкап: {selected_backup[0]}[/cyan]\n")
                    
                    show_progress_bar([selected_backup[0]], "Восстановление")
                    show_action_result("Восстановление из бэкапа")
                    break
                else:
                    # Назад к фильтрам
                    continue
            break
            
        elif choice == 4:
            # Пропустить обновление
            console.print("\n[yellow]Изменения внесены не будут.[/yellow]\n")
            break
        
        if choice is None:
            break
    
    console.print("[bold green]Демонстрация завершена![/bold green]\n")


if __name__ == '__main__':
    main()
