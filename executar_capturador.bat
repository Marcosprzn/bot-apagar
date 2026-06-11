@echo off
title Capturador MEGA ERP - Executar como Admin
color 0B

echo ===================================================
echo    Capturador MEGA ERP - Iniciando como Admin
echo ===================================================
echo.

set "PYTHON_EXE="

if exist "%LOCALAPPDATA%\Programs\Python\Python311\python.exe" (
    set "PYTHON_EXE=%LOCALAPPDATA%\Programs\Python\Python311\python.exe"
    goto :found_python
)
if exist "%LOCALAPPDATA%\Programs\Python\Python312\python.exe" (
    set "PYTHON_EXE=%LOCALAPPDATA%\Programs\Python\Python312\python.exe"
    goto :found_python
)
if exist "C:\Python311\python.exe" (
    set "PYTHON_EXE=C:\Python311\python.exe"
    goto :found_python
)

python --version >nul 2>&1
if %errorlevel% equ 0 (
    set "PYTHON_EXE=python"
    goto :found_python
)

echo ERRO: Python nao encontrado!
pause
exit /b 1

:found_python
set "BOT_DIR=%~dp0"
set "CAPTURADOR_SCRIPT=%BOT_DIR%capturar_elementos.py"

echo Solicitando permissao de Administrador para capturar a tela do MEGA ERP...
powershell -Command "Start-Process -FilePath '%PYTHON_EXE%' -ArgumentList '\"%CAPTURADOR_SCRIPT%\"' -Verb RunAs -Wait"

echo.
echo Capturador finalizado.
pause
