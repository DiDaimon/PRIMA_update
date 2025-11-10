# -*- coding: utf-8 -*-
"""Демонстрация использования Rich для улучшения UI.

Rich предоставляет:
- Таблицы для отображения данных
- Прогресс-бары для операций
- Панели и красивое форматирование
- Спиннеры для длительных операций
"""

from rich.console import Console
from rich.table import Table
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn, TimeElapsedColumn
from rich.panel import Panel
from rich.prompt import Prompt, Confirm
from rich.layout import Layout
from rich.live import Live
from rich.text import Text
import time
from pathlib import Path

console = Console()


def demo_table():
    """Демонстрация таблицы для отображения файлов."""
    console.print("\n[bold cyan]Демонстрация: Таблица файлов[/bold cyan]")
    
    # Создаем таблицу для измененных файлов
    table = Table(title="[bold green]Найденные изменения[/bold green]", show_header=True, header_style="bold magenta")
    table.add_column("Тип", style="cyan", width=15)
    table.add_column("Файл", style="magenta", width=40)
    table.add_column("Размер", justify="right", style="green", width=10)
    table.add_column("Дата", style="yellow", width=12)
    
    # Добавляем примеры данных
    table.add_row("Изменен", "PRIMA.exe", "2.5 MB", "10.11.2025")
    table.add_row("Изменен", "config.ini", "1.2 KB", "10.11.2025")
    table.add_row("Отсутствует", "new_module.dll", "150 KB", "-")
    table.add_row("Отсутствует", "data.json", "5.3 KB", "-")
    
    console.print(table)


def demo_progress_bar():
    """Демонстрация прогресс-бара при копировании файлов."""
    console.print("\n[bold cyan]Демонстрация: Прогресс-бар копирования[/bold cyan]")
    
    files = [
        "PRIMA.exe",
        "config.ini",
        "module.dll",
        "data.json",
        "settings.xml"
    ]
    
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        BarColumn(),
        TextColumn("[progress.percentage]{task.percentage:>3.0f}%"),
        TimeElapsedColumn(),
        console=console
    ) as progress:
        task = progress.add_task("[green]Копирование файлов...", total=len(files))
        
        for i, file in enumerate(files, 1):
            time.sleep(0.5)  # Имитация копирования
            progress.update(task, advance=1, description=f"[green]Копирование: {file}")


def demo_panels():
    """Демонстрация панелей с информацией."""
    console.print("\n[bold cyan]Демонстрация: Информационные панели[/bold cyan]")
    
    # Панель статуса сервера
    server_panel = Panel(
        "[green]✓[/green] Сервер доступен\n"
        "[blue]Путь:[/blue] \\\\tserver1\\RSU\\PRIMA\n"
        "[blue]Статус:[/blue] [green]Подключено[/green]",
        title="[bold]Статус сервера[/bold]",
        border_style="green"
    )
    
    # Панель статистики
    stats_panel = Panel(
        "[cyan]Измененных файлов:[/cyan] [bold]2[/bold]\n"
        "[cyan]Отсутствующих файлов:[/cyan] [bold]2[/bold]\n"
        "[cyan]Всего изменений:[/cyan] [bold yellow]4[/bold yellow]",
        title="[bold]Статистика[/bold]",
        border_style="cyan"
    )
    
    # Панель бэкапа
    backup_panel = Panel(
        "[green]✓[/green] Бэкап создан\n"
        "[blue]Имя:[/blue] PRIMA[10.11.25].exe\n"
        "[blue]Размер:[/blue] 2.5 MB",
        title="[bold]Бэкап[/bold]",
        border_style="yellow"
    )
    
    console.print(server_panel)
    console.print(stats_panel)
    console.print(backup_panel)


def demo_menu():
    """Демонстрация интерактивного меню с Rich."""
    console.print("\n[bold cyan]Демонстрация: Интерактивное меню[/bold cyan]")
    
    menu_items = [
        "[1] [cyan]Для замены измененных файлов[/cyan]",
        "[2] [cyan]Для копирования отсутствующих файлов[/cyan]",
        "[3] [cyan]Для внесения всех изменений[/cyan]",
        "[4] [cyan]Для полного копирования[/cyan]",
        "[5] [cyan]Для пропуска (без изменений)[/cyan]",
        "[6] [yellow]Для восстановления из бэкапа[/yellow]"
    ]
    
    menu_text = "\n".join(menu_items)
    menu_panel = Panel(
        menu_text,
        title="[bold]Выберите действие[/bold]",
        border_style="blue"
    )
    console.print(menu_panel)
    
    choice = Prompt.ask("\n[bold]Выберите действие[/bold]", choices=["1", "2", "3", "4", "5", "6"], default="5")
    console.print(f"[green]Выбрано: {choice}[/green]")


def demo_spinner():
    """Демонстрация спиннера для длительных операций."""
    console.print("\n[bold cyan]Демонстрация: Спиннер для операций[/bold cyan]")
    
    with console.status("[bold green]Проверка доступности сервера...") as status:
        time.sleep(2)
        status.update("[bold green]Сравнение директорий...")
        time.sleep(2)
        status.update("[bold green]Анализ изменений...")
        time.sleep(1)
    
    console.print("[green]✓ Операция завершена[/green]")


def demo_layout():
    """Демонстрация layout с несколькими панелями."""
    console.print("\n[bold cyan]Демонстрация: Layout с панелями[/bold cyan]")
    
    layout = Layout()
    layout.split_column(
        Layout(name="header", size=3),
        Layout(name="body"),
        Layout(name="footer", size=3)
    )
    
    layout["header"].update(Panel("[bold blue]PRIMA - UPDATER[/bold blue]", style="blue"))
    layout["body"].split_row(
        Layout(Panel("[cyan]Измененные файлы:\n• PRIMA.exe\n• config.ini[/cyan]", title="Изменения")),
        Layout(Panel("[yellow]Отсутствующие:\n• new_module.dll\n• data.json[/yellow]", title="Отсутствуют"))
    )
    layout["footer"].update(Panel("[green]Готово к обновлению[/green]", style="green"))
    
    console.print(layout)


def demo_backup_list():
    """Демонстрация списка бэкапов в виде таблицы."""
    console.print("\n[bold cyan]Демонстрация: Таблица бэкапов[/bold cyan]")
    
    table = Table(title="[bold yellow]Доступные бэкапы[/bold yellow]", show_header=True)
    table.add_column("#", style="cyan", width=3, justify="center")
    table.add_column("Имя файла", style="magenta", width=25)
    table.add_column("Дата создания", style="green", width=20)
    table.add_column("Размер", justify="right", style="yellow", width=10)
    
    backups = [
        ("PRIMA[10.11.25].exe", "10.11.2025 14:30", "2.5 MB"),
        ("PRIMA[09.11.25].exe", "09.11.2025 10:15", "2.4 MB"),
        ("PRIMA[08.11.25].exe", "08.11.2025 16:45", "2.3 MB"),
    ]
    
    for i, (name, date, size) in enumerate(backups, 1):
        table.add_row(str(i), name, date, size)
    
    table.add_row("0", "[dim]Отмена[/dim]", "[dim]-[/dim]", "[dim]-[/dim]")
    
    console.print(table)


def main():
    """Главная функция демонстрации."""
    console.print("[bold blue]=" * 60)
    console.print("[bold blue]Демонстрация возможностей Rich для UI[/bold blue]")
    console.print("[bold blue]=" * 60)
    
    demo_table()
    demo_progress_bar()
    demo_panels()
    demo_menu()
    demo_spinner()
    demo_layout()
    demo_backup_list()
    
    console.print("\n[bold green]Демонстрация завершена![/bold green]")


if __name__ == '__main__':
    main()

