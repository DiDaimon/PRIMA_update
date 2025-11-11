# -*- coding: utf-8 -*-
"""Модуль установки зависимостей PRIMA Updater.

Обеспечивает:
- Проверку доступности Python и pip
- Установку зависимостей из requirements.txt
- Поддержку работы через прокси-сервер
- Создание ярлыка на рабочем столе
"""

import subprocess
import sys
import shutil
from pathlib import Path
from typing import Optional, Tuple


def get_proxy_credentials() -> Tuple[Optional[str], Optional[str], Optional[str]]:
    """Запрос данных прокси-сервера у пользователя."""
    print("\n" + "=" * 60)
    print("Настройка прокси-сервера")
    print("=" * 60)
    print("Для установки через прокси введите данные:")
    print("(Оставьте пустым, если прокси не требуется)\n")

    proxy_host = input("Адрес прокси (например, proxy.company.com:8080): ").strip()
    if not proxy_host:
        return None, None, None

    proxy_user = input("Логин (оставьте пустым, если не требуется): ").strip()
    proxy_pass = ""

    if proxy_user:
        proxy_pass = input("Пароль: ").strip()

    return proxy_host, proxy_user, proxy_pass


def build_proxy_url(host: str, user: str = None, password: str = None) -> str:
    """Формирование URL прокси-сервера."""
    if user and password:
        return f"http://{user}:{password}@{host}"
    elif user:
        return f"http://{user}@{host}"
    else:
        return f"http://{host}"

def create_desktop_shortcut():
    """Копирует ярлык на рабочий стол."""
    shortcut = Path("assets") / "[PRIMA] 00.00.00.lnk"
    desktop = Path.home() / "Desktop"

    if shortcut.exists():
        try:
            shutil.copy(shortcut, desktop)
            print("Ярлык скопирован на рабочий стол.")
        except Exception as e:
            print(f"Не удалось скопировать ярлык: {e}")
    else:
        print(f"Файл ярлыка не найден: {shortcut}")


def install_dependencies(proxy_url: Optional[str] = None) -> bool:
    """Установка зависимостей из requirements.txt.

    Args:
        proxy_url: URL прокси-сервера (опционально)

    Returns:
        bool: True если установка успешна, False в противном случае
    """
    requirements_file = Path(__file__).parent / "requirements.txt"

    if not requirements_file.exists():
        print(f"Файл {requirements_file} не найден!")
        return False

    print("\n" + "=" * 60)
    print("Установка зависимостей...")
    print("=" * 60)

    cmd = [
        sys.executable,
        "-m",
        "pip",
        "install",
        "-r",
        str(requirements_file),
        "--no-warn-script-location"
    ]

    if proxy_url:
        cmd.extend(["--proxy", proxy_url])
        print(f"Использование прокси: {proxy_url.split('@')[-1] if '@' in proxy_url else proxy_url}")

    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=300
        )

        # Фильтруем вывод, убирая "Requirement already satisfied"
        output_lines = result.stdout.split('\n')
        for line in output_lines:
            if line and "Requirement already satisfied" not in line:
                print(line)

        if result.stderr:
            error_lines = result.stderr.split('\n')
            for line in error_lines:
                if line and "WARNING" not in line:
                    print(line, file=sys.stderr)

        if result.returncode == 0:
            print("\n✓ Зависимости успешно установлены")
            return True
        else:
            print(f"\n✗ Ошибка установки (код возврата: {result.returncode})")
            return False

    except subprocess.TimeoutExpired:
        print("\n✗ Превышено время ожидания установки")
        return False
    except Exception as e:
        print(f"\n✗ Ошибка при установке зависимостей: {e}")
        return False


def setup():
    # Попытка установки без прокси
    print("\nПопытка установки зависимостей...")
    if install_dependencies():
        print("\n" + "=" * 60)
        print("✓ УСТАНОВКА ЗАВЕРШЕНА УСПЕШНО")
        print("=" * 60)
        input("\nНажмите Enter для выхода...")

    # Если не удалось, спрашиваем про прокси
    print("\n✗ Не удалось установить зависимости.")
    print("Возможно, требуется настройка прокси-сервера.\n")

    while True:
        use_proxy = input("Попробовать установку через прокси? (y/n): ").strip().lower()
        if use_proxy == 'n':
            print("\n✗ Установка отменена.")
            input("\nНажмите Enter для выхода...")
            return False
        elif use_proxy == 'y':
            break

    # Запрос данных прокси
    proxy_host, proxy_user, proxy_pass = get_proxy_credentials()

    if not proxy_host:
        print("\n✗ Адрес прокси не указан. Установка отменена.")
        input("\nНажмите Enter для выхода...")
        return False

    proxy_url = build_proxy_url(proxy_host, proxy_user, proxy_pass)

    # Попытка установки через прокси
    if install_dependencies(proxy_url):
        print("\n" + "=" * 60)
        print("✓ УСТАНОВКА ЗАВЕРШЕНА УСПЕШНО")
        print("=" * 60)
        return True
    else:
        print("\n✗ Установка не удалась даже с прокси.")
        print("Проверьте данные прокси-сервера и попробуйте снова.")
        input("\nНажмите Enter для выхода...")
        return False