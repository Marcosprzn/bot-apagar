@echo off
title Instalador Bot MEGA ERP
color 0A

echo.
echo ===================================================
echo    INSTALADOR - Bot MEGA ERP
echo ===================================================
echo.

REM ====================================================
REM PASSO 1: Detectar Windows 7 e arquitetura
REM ====================================================
echo [1/4] Verificando sistema operacional e arquitetura...

REM Detecta Windows 7 (versao 6.1)
set "WIN7="
for /f "tokens=2 delims=." %%a in ('ver') do (
    if "%%a"=="1" set "WIN7=1"
)
if "%WIN7%"=="1" (
    echo     -> Windows 7 detectado (usando Python 3.8.10)
    set "PY_VER=3.8.10"
    set "PY_DIR_VER=Python38"
) else (
    echo     -> Windows 8/10/11 detectado (usando Python 3.11.8)
    set "PY_VER=3.11.8"
    set "PY_DIR_VER=Python311"
)

if exist "%ProgramFiles(x86)%" (
    echo     -> 64-bit detectado.
    set "PYTHON_URL=https://www.python.org/ftp/python/%PY_VER%/python-%PY_VER%-amd64.exe"
) else (
    echo     -> 32-bit detectado.
    set "PYTHON_URL=https://www.python.org/ftp/python/%PY_VER%/python-%PY_VER%.exe"
)

echo.

REM ====================================================
REM PASSO 2: Verificar se Python já está instalado
REM ====================================================
echo [2/4] Verificando se o Python ja esta instalado...

python --version >nul 2>&1
if %errorlevel% equ 0 (
    echo     -> Python ja esta instalado, pulando download.
    goto :instalar_libs
)

REM Verifica caminhos comuns antes de baixar
if exist "%LOCALAPPDATA%\Programs\Python\%PY_DIR_VER%\python.exe" (
    echo     -> Python encontrado localmente, adicionando ao PATH...
    goto :add_path
)

echo     -> Python nao encontrado. Iniciando download...
echo.

REM ====================================================
REM PASSO 3: Baixar Python
REM ====================================================
echo [3/4] Baixando o Python %PY_VER%...
echo     URL: %PYTHON_URL%
echo     Aguarde, isso pode demorar alguns minutos...
echo.

REM Tenta ativar TLS 1.2 no .NET (essencial no Windows 7)
reg add "HKLM\SOFTWARE\Microsoft\.NETFramework\v4.0.30319" /v SchUseStrongCrypto /t REG_DWORD /d 1 /f >nul 2>&1
reg add "HKLM\SOFTWARE\WOW6432Node\Microsoft\.NETFramework\v4.0.30319" /v SchUseStrongCrypto /t REG_DWORD /d 1 /f >nul 2>&1

REM Metodo 1: bitsadmin (mais compativel com Windows 7, usa WinHTTP nativo)
echo     Tentando com bitsadmin...
bitsadmin /transfer "JobPython" "%PYTHON_URL%" "%TEMP%\python_install.exe" >nul 2>&1

REM Metodo 2: PowerShell WebClient
if not exist "%TEMP%\python_install.exe" (
    echo     bitsadmin falhou. Tentando com PowerShell...
    powershell -Command "& { try{ [Net.ServicePointManager]::SecurityProtocol = 3072 -bor 768 -bor 192 } catch {}; (New-Object System.Net.WebClient).DownloadFile('%PYTHON_URL%', '%TEMP%\python_install.exe') }" >nul 2>&1
)

REM Metodo 3: curl.exe (disponivel no Windows 10+)
if not exist "%TEMP%\python_install.exe" (
    echo     PowerShell falhou. Tentando com curl.exe...
    curl -L -o "%TEMP%\python_install.exe" "%PYTHON_URL%" >nul 2>&1
)

if not exist "%TEMP%\python_install.exe" (
    echo.
    echo     ERRO: O download falhou. Verifique sua conexao.
    echo     Se estiver no Windows 7, instale o KB3140245 ou baixe manualmente:
    echo     %PYTHON_URL%
    echo.
    goto :fim_erro
)

echo     Download concluido! Instalando...
echo.

REM Instalacao silenciosa com PATH
REM PrependPath=1 = adiciona ao PATH do Windows automaticamente
"%TEMP%\python_install.exe" /quiet InstallAllUsers=0 PrependPath=1 Include_pip=1 Include_test=0

echo     Instalacao concluida!
del "%TEMP%\python_install.exe" >nul 2>&1

REM ====================================================
REM Adicionar Python ao PATH desta sessao
REM (o instalador ja adicionou permanentemente,
REM  mas precisamos atualizar a sessao atual do CMD)
REM ====================================================
:add_path
echo.
echo     Atualizando PATH desta sessao...
set "PY_DIR=%LOCALAPPDATA%\Programs\Python\%PY_DIR_VER%"
set "PY_SCRIPTS=%PY_DIR%\Scripts"
set "PATH=%PY_DIR%;%PY_SCRIPTS%;%PATH%"

REM Adiciona permanentemente ao PATH do usuario com setx
setx PATH "%PY_DIR%;%PY_SCRIPTS%;%PATH%" >nul 2>&1

echo     PATH atualizado!

REM ====================================================
REM PASSO 4: Instalar bibliotecas
REM ====================================================
:instalar_libs
echo.
echo [4/4] Instalando bibliotecas necessarias...
echo.

REM Tenta com python direto da sessao atual
set "PY_DIR=%LOCALAPPDATA%\Programs\Python\%PY_DIR_VER%"
if exist "%PY_DIR%\python.exe" (
    set "PYTHON_EXE=%PY_DIR%\python.exe"
) else (
    set "PYTHON_EXE=python"
)

echo     Atualizando pip...
"%PYTHON_EXE%" -m pip install --upgrade pip --quiet

echo     Instalando pywinauto...
"%PYTHON_EXE%" -m pip install pywinauto

echo     Instalando comtypes (necessario para o backend uia)...
"%PYTHON_EXE%" -m pip install comtypes

echo     Instalando pyautogui (deteccao de imagem)...
"%PYTHON_EXE%" -m pip install pyautogui

echo     Instalando Pillow (necessario para comparacao de imagens)...
"%PYTHON_EXE%" -m pip install Pillow

echo     Instalando pywin32 (controle de teclado/mouse)...
"%PYTHON_EXE%" -m pip install pywin32

echo.
echo     Verificando instalacao...
"%PYTHON_EXE%" -c "import pywinauto; import pyautogui; import PIL; print('Todas as bibliotecas OK!')"

if %errorlevel% equ 0 (
    echo.
    echo ===================================================
    echo    TUDO PRONTO! Pode fechar e executar o bot.py
    echo ===================================================
    goto :fim_ok
) else (
    echo.
    echo    ATENCAO: Houve um problema. Reinicie o PC e
    echo    tente executar este arquivo novamente.
    goto :fim_erro
)

:fim_ok
echo.
pause
exit /b 0

:fim_erro
echo.
echo Pressione qualquer tecla para fechar...
pause >nul
exit /b 1
