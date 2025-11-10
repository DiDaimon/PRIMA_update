# -*- coding: utf-8 -*-
"""Демонстрация комбинированного использования Rich + Questionary.

Этот вариант объединяет лучшее из обоих библиотек:
- Rich для красивого отображения (таблицы, прогресс-бары, панели)
- Questionary для интерактивного меню
"""

try:
    from rich.console import Console
    from rich.table import Table
    from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn
    from rich.panel import Panel
    import questionary
except ImportError:
    print("Для работы этого демо необходимо установить:")
    print("pip install rich questionary")
    exit(1)

from colorama import init
init(autoreset=True)

console = Console()


def show_changes_table(diff_files, only_files):
    """Отображение изменений в виде таблицы."""
    table = Table(title="[bold green]Найденные изменения[/bold green]", show_header=True)
    table.add_column("Тип", style="cyan", width=15)
    table.add_column("Файл", style="magenta", width=40)
    table.add_column("Размер", justify="right", style="green", width=10)
    
    for file_path, size in diff_files:
        table.add_row("Изменен", file_path, size)
    
    for file_path, size in only_files:
        table.add_row("Отсутствует", file_path, size)
    
    console.print(table)


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


def show_interactive_menu():
    """Интерактивное меню с Questionary."""
    choice = questionary.select(
        "Выберите действие",
        choices=[
            "Для замены измененных файлов",
            "Для копирования отсутствующих файлов",
            "Для внесения всех изменений",
            "Для полного копирования",
            "Для пропуска (без изменений)",
        ],
        style=questionary.Style([
            ('question', 'fg:#ff0066 bold'),
            ('answer', 'fg:#44ff00 bold'),
        ])
    ).ask()
    
    return choice


def show_progress_bar(files):
    """Отображение прогресс-бара при копировании."""
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        BarColumn(),
        TextColumn("[progress.percentage]{task.percentage:>3.0f}%"),
        console=console
    ) as progress:
        task = progress.add_task("[green]Копирование файлов...", total=len(files))
        
        import time
        for file in files:
            time.sleep(0.3)
            progress.update(task, advance=1, description=f"[green]Копирование: {file}")


def show_backup_table(backups):
    """Отображение списка бэкапов в виде таблицы."""
    table = Table(title="[bold yellow]Доступные бэкапы[/bold yellow]", show_header=True)
    table.add_column("#", style="cyan", width=3, justify="center")
    table.add_column("Имя файла", style="magenta", width=25)
    table.add_column("Дата создания", style="green", width=20)
    
    for i, (name, date) in enumerate(backups, 1):
        table.add_row(str(i), name, date)
    
    table.add_row("0", "[dim]Отмена[/dim]", "[dim]-[/dim]")
    
    console.print(table)
    
    # Выбор через Questionary
    choices = [f"{i}. {name} ({date})" for i, (name, date) in enumerate(backups, 1)]
    choices.append("0. Отмена")
    
    choice = questionary.select(
        "Выберите бэкап для восстановления",
        choices=choices
    ).ask()
    
    return choice


def main():
    """Главная функция демонстрации."""
    console.print("[bold blue]=" * 60)
    console.print("[bold blue]Демонстрация: Rich + Questionary (Комбинированный вариант)[/bold blue]")
    console.print("[bold blue]=" * 60)
    
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
    ]
    
    # Показываем статус
    show_status_panels()
    
    # Показываем изменения
    show_changes_table(diff_files, only_files)
    
    # Интерактивное меню
    choice = show_interactive_menu()
    console.print(f"[green]Выбрано: {choice}[/green]")
    
    # Подтверждение
    if questionary.confirm("Создать бэкап перед обновлением?", default=True).ask():
        console.print("[green]Бэкап будет создан[/green]")
    
    # Прогресс-бар
    files_to_copy = [f[0] for f in diff_files + only_files]
    show_progress_bar(files_to_copy)
    
    # Выбор бэкапа
    backup_choice = show_backup_table(backups)
    console.print(f"[green]Выбран бэкап: {backup_choice}[/green]")
    
    console.print("\n[bold green]Демонстрация завершена![/bold green]")


if __name__ == '__main__':
    main()

