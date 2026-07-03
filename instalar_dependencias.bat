@echo off
title Instalador Bot MEGA ERP
color 0A

echo ===================================================
echo    INSTALADOR - Bot MEGA ERP
echo ===================================================
echo.
pause
echo.

echo [1/4] Verificando sistema...

ver | find "6.1." >nul
if %errorlevel% equ 0 set "WIN7=1"

if "%WIN7%"=="1" (
    echo   Windows 7 detectado
    set PY_VER=3.8.10
    set PY_FOLDER=Python38
) else (
    echo   Windows 8/10/11 detectado
    set PY_VER=3.11.8
    set PY_FOLDER=Python311
)

if exist "%ProgramFiles(x86)%" (
    echo   64-bit
    set PY_URL=https://www.python.org/ftp/python/%PY_VER%/python-%PY_VER%-amd64.exe
) else (
    echo   32-bit
    set PY_URL=https://www.python.org/ftp/python/%PY_VER%/python-%PY_VER%.exe
)

echo.
pause
echo.

echo [2/4] Verificando se Python ja esta instalado...

python --version >nul 2>&1
if %errorlevel% equ 0 goto PULAR_DOWNLOAD

if exist "%LOCALAPPDATA%\Programs\Python\%PY_FOLDER%\python.exe" goto PATH_ADICIONAR

echo   Python nao encontrado. Iniciando download...
echo.
pause
echo.

echo [3/4] Baixando Python %PY_VER%...
echo   URL: %PY_URL%

reg add "HKLM\SOFTWARE\Microsoft\.NETFramework\v4.0.30319" /v SchUseStrongCrypto /t REG_DWORD /d 1 /f >nul 2>&1
reg add "HKLM\SOFTWARE\WOW6432Node\Microsoft\.NETFramework\v4.0.30319" /v SchUseStrongCrypto /t REG_DWORD /d 1 /f >nul 2>&1

echo   Tentando bitsadmin...
bitsadmin /transfer "JobPython" "%PY_URL%" "%TEMP%\python_install.exe"

if not exist "%TEMP%\python_install.exe" (
    echo   bitsadmin falhou. Tentando PowerShell...
    powershell -Command "$wc = New-Object System.Net.WebClient; $wc.DownloadFile('%PY_URL%', '%TEMP%\python_install.exe')"
)

if not exist "%TEMP%\python_install.exe" (
    echo.
    echo   ERRO: Download falhou. Baixe manualmente:
    echo   %PY_URL%
    echo.
    pause
    exit /b 1
)

echo   Download OK. Instalando...
"%TEMP%\python_install.exe" /quiet InstallAllUsers=0 PrependPath=1 Include_pip=1 Include_test=0
del "%TEMP%\python_install.exe" >nul 2>&1
echo   Instalacao concluida!
echo.
pause
echo.

:PATH_ADICIONAR
echo   Atualizando PATH...
set "PY_DIR=%LOCALAPPDATA%\Programs\Python\%PY_FOLDER%"
set "PY_SCRIPTS=%PY_DIR%\Scripts"
setx PATH "%PY_DIR%;%PY_SCRIPTS%;%PATH%" >nul 2>&1
set "PATH=%PY_DIR%;%PY_SCRIPTS%;%PATH%"
echo   PATH atualizado!
echo.
pause
echo.

:PULAR_DOWNLOAD

echo [4/4] Instalando bibliotecas...

set "PY_DIR=%LOCALAPPDATA%\Programs\Python\%PY_FOLDER%"
if exist "%PY_DIR%\python.exe" ( set "PY_EXE=%PY_DIR%\python.exe" ) else ( set "PY_EXE=python" )

echo   Atualizando pip...
"%PY_EXE%" -m pip install --upgrade pip --quiet

echo   Instalando pywinauto...
"%PY_EXE%" -m pip install pywinauto

echo   Instalando comtypes...
"%PY_EXE%" -m pip install comtypes

echo   Instalando pyautogui...
"%PY_EXE%" -m pip install pyautogui

echo   Instalando Pillow...
"%PY_EXE%" -m pip install Pillow

echo   Instalando pywin32...
"%PY_EXE%" -m pip install pywin32

echo.
echo   Verificando...
"%PY_EXE%" -c "import pywinauto; import pyautogui; import PIL; print('OK!')"

if %errorlevel% equ 0 (
    echo.
    echo ===================================================
    echo    TUDO PRONTO!
    echo ===================================================
) else (
    echo.
    echo ===================================================
    echo    ERRO NA INSTALACAO DAS BIBLIOTECAS
    echo ===================================================
)

echo.
pause
