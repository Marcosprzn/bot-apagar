@echo off
title Bot MEGA ERP - Executar como Admin
color 0A

echo ===================================================
echo    Bot MEGA ERP - Iniciando como Administrador
echo ===================================================
echo.

REM Detecta o caminho do Python (tenta varios locais comuns)
set "PYTHON_EXE="

for %%v in (Python313 Python312 Python311 Python310 Python39 Python38) do (
    if exist "%LOCALAPPDATA%\Programs\Python\%%v\python.exe" (
        set "PYTHON_EXE=%LOCALAPPDATA%\Programs\Python\%%v\python.exe"
        goto :found_python
    )
)

if exist "C:\Python311\python.exe" (
    set "PYTHON_EXE=C:\Python311\python.exe"
    goto :found_python
)

if exist "C:\Python38\python.exe" (
    set "PYTHON_EXE=C:\Python38\python.exe"
    goto :found_python
)

REM Tenta o python do PATH
python --version >nul 2>&1
if %errorlevel% equ 0 (
    set "PYTHON_EXE=python"
    goto :found_python
)

echo ERRO: Python nao encontrado!
echo Execute primeiro o arquivo instalar_dependencias.bat
echo.
pause
exit /b 1

:found_python
echo Python encontrado: %PYTHON_EXE%
echo.

REM Pega o diretorio onde este .bat esta localizado
set "BOT_DIR=%~dp0"
set "BOT_SCRIPT=%BOT_DIR%novobot.py"

if not exist "%BOT_SCRIPT%" (
    echo ERRO: novobot.py nao encontrado em: %BOT_SCRIPT%
    echo Certifique-se que o executar_bot.bat esta na mesma pasta que o novobot.py
    echo.
    pause
    exit /b 1
)

echo Script: %BOT_SCRIPT%
echo.
echo Solicitando permissao de Administrador...
echo (O Windows vai pedir confirmacao - clique em SIM)
echo.

REM Eleva o processo para Administrador via PowerShell
REM O bot precisa rodar como admin pois o MEGA ERP eh um processo elevado
powershell -Command "Start-Process -FilePath '%PYTHON_EXE%' -ArgumentList '\"%BOT_SCRIPT%\"' -Verb RunAs -Wait"

echo.
echo Bot finalizado.
pause
