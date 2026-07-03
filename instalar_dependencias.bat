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

:INSTALAR_BIBLIOTECAS

echo [4/4] Instalando bibliotecas...
echo.

set "PY_DIR=%LOCALAPPDATA%\Programs\Python\%PY_FOLDER%"
if exist "%PY_DIR%\python.exe" ( set "PY_EXE=%PY_DIR%\python.exe" ) else ( set "PY_EXE=python" )

echo   Atualizando pip...
"%PY_EXE%" -m pip install --upgrade pip --quiet
echo.

set LIVROS=pywinauto comtypes pyautogui Pillow pywin32

for %%L in (%LIVROS%) do (
    echo   Instalando %%L...
    "%PY_EXE%" -m pip install %%L
    if errorlevel 1 (
        echo   [FALHOU] %%L - tentando alternativa...
        if "%%L"=="pywin32" "%PY_EXE%" -m pip install pywin32==306
        if "%%L"=="comtypes" "%PY_EXE%" -m pip install comtypes==1.1.11
    )
    echo.
)

echo   Registrando pywin32 no Windows...
"%PY_EXE%" -c "import win32api" >nul 2>&1
if errorlevel 1 (
    "%PY_EXE%" -c "import sys; exec(open(sys.prefix + '/Scripts/pywin32_postinstall.py').read())" -install >nul 2>&1
)

echo   Verificando instalacao...
"%PY_EXE%" -c "import pywinauto; import comtypes; import pyautogui; import PIL; import win32api; print('OK!')"

if %errorlevel% equ 0 (
    echo.
    echo ===================================================
    echo    TUDO PRONTO!
    echo ===================================================
) else (
    echo.
    echo ===================================================
    echo    ALGUMAS BIBLIOTECAS FALHARAM
    echo ===================================================
    echo    Tente instalar manualmente:
    echo    "%PY_EXE%" -m pip install pywinauto comtypes pyautogui Pillow pywin32
    echo.
    "%PY_EXE%" -c "import win32api; print('win32api OK')"
    "%PY_EXE%" -c "import pywinauto; print('pywinauto OK')"
    "%PY_EXE%" -c "import pyautogui; print('pyautogui OK')"
)

echo.
pause
