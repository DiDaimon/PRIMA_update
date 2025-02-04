set TMP=.tmp
set VENV_DIR=.venv
set PYTHON="%VENV_DIR%\Scripts\Python.exe"
%PYTHON% -c "" >%TMP%/stdout.txt 2>%TMP%/stderr.txt
%PYTHON% prima_update.py %*

D:
cd D:\User\PRIMA_Updated\
start D:\User\PRIMA_Updated\PRIMA.exe
timeout 10