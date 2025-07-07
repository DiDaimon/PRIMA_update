
@echo off

set PYTHON=python
set GIT=git
set VENV_DIR=.venv
set TMP=.tmp

:: Создаём директории если их нет
mkdir "%VENV_DIR%" 2>NUL
mkdir "%TMP%" 2>NUL

:: Копируем ярлык на рабочий стол
xcopy /y "[PRIMA] 00.00.00.lnk" "%USERPROFILE%\Desktop\" >NUL 2>NUL

:: Проверяем Python
%PYTHON% -c "" >%TMP%\stdout.txt 2>%TMP%\stderr.txt
if %ERRORLEVEL% == 0 goto :check_pip
echo Couldn't launch python
goto :show_stdout_stderr

:check_pip
%PYTHON% -m pip --help >%TMP%\stdout.txt 2>%TMP%\stderr.txt
if %ERRORLEVEL% == 0 goto :start_venv
echo Install pip
goto :show_stdout_stderr

:start_venv
:: Проверяем существует ли виртуальное окружение
if exist "%VENV_DIR%\Scripts\Python.exe" goto :activate_venv

:: Создаём виртуальное окружение
for /f "delims=" %%i in ('CALL %PYTHON% -c "import sys; print(sys.executable)"') do set PYTHON_FULLNAME="%%i"
echo Creating venv in directory %VENV_DIR% using python %PYTHON_FULLNAME%
%PYTHON_FULLNAME% -m venv "%VENV_DIR%" >%TMP%\stdout.txt 2>%TMP%\stderr.txt
if %ERRORLEVEL% == 0 goto :activate_venv
echo Unable to create venv in directory "%VENV_DIR%"
goto :show_stdout_stderr

:activate_venv
set PYTHON="%VENV_DIR%\Scripts\Python.exe"
echo Using virtual environment: %PYTHON%

:: Обновляем git репозиторий (если это git репозиторий)
if exist ".git" (
    echo Updating git repository...
    %GIT% pull origin main >%TMP%\stdout.txt 2>%TMP%\stderr.txt
    if %ERRORLEVEL% neq 0 (
        echo Git pull failed, continuing anyway...
    ) else (
        echo Git repository updated successfully
    )
)

:: Устанавливаем зависимости
echo Installing requirements...
%PYTHON% -m pip install --upgrade pip >%TMP%\stdout.txt 2>%TMP%\stderr.txt
if exist "requirements\requirements.txt" (
    %PYTHON% -m pip install -r "requirements\requirements.txt" --no-warn-script-location | findstr /V "Requirement already satisfied"
) else if exist "requirements.txt" (
    %PYTHON% -m pip install -r "requirements.txt" --no-warn-script-location | findstr /V "Requirement already satisfied"
) else (
    echo No requirements file found
)

echo All OK
goto :endofscript

:show_stdout_stderr
echo.
echo exit code: %errorlevel%
for /f %%i in ("%TMP%\stdout.txt") do set size=%%~zi
if %size% gtr 0 (
    echo.
    echo stdout:
    type %TMP%\stdout.txt
)

for /f %%i in ("%TMP%\stderr.txt") do set size=%%~zi
if %size% gtr 0 (
    echo.
    echo stderr:
    type %TMP%\stderr.txt
)
goto :endofscript

:endofscript
echo.
echo Install completed. Press any key to exit.
pause >NUL
