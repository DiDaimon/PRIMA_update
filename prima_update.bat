@echo off
:: Скрипт: prima_updater.bat
:: Назначение: Запуск скрипта prima_updater.py

:: Настройки
set VENV_DIR=.venv
set PYTHON=%VENV_DIR%\Scripts\Python.exe
set PRIMA_DIR=D:\User\PRIMA_Updated\
set PRIMA_EXE=%PRIMA_DIR%PRIMA.exe

:: Перейти в директорию скрипта
pushd %~dp0

:: Смена кодировки на UTF-8 для корректного вывода сообщений на русском языке
chcp 65001

:: Проверка наличия виртуального окружения
if not exist "%PYTHON%" (
    echo [INFO] Виртуальное окружение не найдено. Создаю .venv...

    :: Проверка доступности python
    where python >nul 2>&1
    if %errorlevel% neq 0 (
        echo [ERROR] Python не установлен или не добавлен в PATH.
        echo Установите Python с https://www.python.org и перезапустите скрипт.
        timeout /t 15 >nul
        exit /b 1
    )

    :: Создание виртуального окружения
    python -m venv %VENV_DIR%

    if %errorlevel% neq 0 (
        echo [ERROR] Не удалось создать виртуальное окружение.
        timeout /t 15 >nul
        exit /b 1
    )

    echo [SUCCESS] Виртуальное окружение создано.
)
%PYTHON% prima_update.py %*

:: Запуск PRIMA
if exist %PRIMA_EXE% (
    echo Запуск PRIMA.exe...
    start %PRIMA_EXE%
) else (
    echo PRIMA.exe не найден в %PRIMA_DIR%
    echo Проверьте путь к PRIMA.exe
    timeout 5
    exit /b 1
    )
timeout 5
popd
exit /b 0