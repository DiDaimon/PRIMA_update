"""Общий модуль для работы с Rich-консолью.

Содержит фабрики для получения настроенной консоли и тем оформления,
чтобы обеспечить единообразный вывод во всех частях приложения.
"""

from functools import lru_cache
from typing import Optional

from rich.console import Console
from rich.theme import Theme


CUSTOM_THEME = Theme(
    {
        "info": "green",
        "warning": "yellow",
        "error": "bold red",
        "critical": "bold red reverse",
        "debug": "cyan",
        "menu.title": "bold blue",
        "menu.item": "cyan",
        "menu.hotkey": "bold yellow",
    }
)


@lru_cache(maxsize=1)
def get_console(*, record: bool = False, log_path: Optional[str] = None) -> Console:
    """Возвращает экземпляр Rich Console с настроенной темой.

    Args:
        record: Включить запись вывода (используется RichHandler).
        log_path: Путь для записи, если включена запись.

    Returns:
        Console: Настроенная консоль Rich.
    """
    return Console(theme=CUSTOM_THEME, highlight=False, record=record, log_path=log_path)


