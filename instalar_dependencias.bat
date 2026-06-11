@echo off
setlocal enabledelayedexpansion
echo ===================================================
echo   Instalador de Dependencias - Bot MEGA ERP
echo ===================================================
echo.

:: -------------------------------------------------------
:: 1. DETECTAR ARQUITETURA
:: -------------------------------------------------------
echo Verificando arquitetura do sistema...
if /i "%PROCESSOR_ARCHITECTURE%"=="AMD64" (
    set "ARCH=64"
    set "PYTHON_URL=https://www.python.org/ftp/python/3.11.8/python-3.11.8-amd64.exe"
    echo Sistema 64-bit detectado.
) else if /i "%PROCESSOR_ARCHITEW6432%"=="AMD64" (
    set "ARCH=64"
    set "PYTHON_URL=https://www.python.org/ftp/python/3.11.8/python-3.11.8-amd64.exe"
    echo Sistema 64-bit detectado (processo 32-bit).
) else (
    set "ARCH=32"
    set "PYTHON_URL=https://www.python.org/ftp/python/3.11.8/python-3.11.8.exe"
    echo Sistema 32-bit detectado.
)

set "INSTALLER=%TEMP%\python-installer.exe"

:: -------------------------------------------------------
:: 2. VERIFICAR SE PYTHON JA ESTA INSTALADO
:: -------------------------------------------------------
echo.
echo Verificando se o Python ja esta instalado...

:: Caminho padrao onde o Python e instalado para o usuario atual
set "PYTHON_DIR=%LOCALAPPDATA%\Programs\Python\Python311"
set "PYTHON_EXE=%PYTHON_DIR%\python.exe"
set "PIP_EXE=%PYTHON_DIR%\Scripts\pip.exe"

if exist "%PYTHON_EXE%" (
    echo Python ja encontrado em: %PYTHON_EXE%
    goto add_to_path
)

:: Verifica tambem via comando (caso esteja em outro diretorio no PATH)
python --version >nul 2>&1
if %errorlevel% equ 0 (
    echo Python ja esta no PATH do sistema.
    for /f "tokens=*" %%i in ('where python') do set "PYTHON_EXE=%%i"
    goto install_libs
)

:: -------------------------------------------------------
:: 3. BAIXAR E INSTALAR PYTHON
:: -------------------------------------------------------
echo Python nao encontrado. Iniciando download...
echo URL: %PYTHON_URL%
echo.
curl -# -L -o "%INSTALLER%" "%PYTHON_URL%"
if %errorlevel% neq 0 (
    echo ERRO: Falha no download. Verifique sua conexao com a internet.
    pause
    exit /b 1
)

echo.
echo Instalando Python 3.11 (modo silencioso)...
echo Isso pode demorar alguns minutos, aguarde...

:: Instalacao silenciosa:
::   InstallAllUsers=0  -> instala apenas para o usuario atual (nao precisa de admin)
::   PrependPath=1      -> adiciona ao PATH automaticamente
::   Include_pip=1      -> instala o pip
::   Include_test=0     -> nao instala modulos de teste (mais rapido)
::   Include_launcher=1 -> instala o launcher 'py'
"%INSTALLER%" /quiet InstallAllUsers=0 PrependPath=1 Include_pip=1 Include_test=0 Include_launcher=1

if %errorlevel% neq 0 (
    echo ERRO: A instalacao do Python falhou. Tente executar como Administrador.
    del "%INSTALLER%" >nul 2>&1
    pause
    exit /b 1
)

del "%INSTALLER%" >nul 2>&1
echo Instalacao do Python concluida!

:: -------------------------------------------------------
:: 4. ADICIONAR AO PATH DA SESSAO ATUAL
:: (o instalador adicionou ao PATH permanente, mas a sessao
::  atual do CMD ainda nao enxerga - precisamos atualizar manualmente)
:: -------------------------------------------------------
:add_to_path
echo.
echo Configurando PATH para esta sessao...

set "PYTHON_DIR=%LOCALAPPDATA%\Programs\Python\Python311"
set "PYTHON_SCRIPTS=%PYTHON_DIR%\Scripts"
set "PYTHON_EXE=%PYTHON_DIR%\python.exe"
set "PIP_EXE=%PYTHON_SCRIPTS%\pip.exe"

:: Adiciona ao PATH desta sessao
set "PATH=%PYTHON_DIR%;%PYTHON_SCRIPTS%;%PATH%"

:: Verifica se o python agora esta acessivel
if not exist "%PYTHON_EXE%" (
    echo AVISO: Python nao encontrado em %PYTHON_DIR%
    echo Tentando localizar em outros locais comuns...

    :: Tenta encontrar em Program Files (instalacao para todos os usuarios)
    if exist "C:\Program Files\Python311\python.exe" (
        set "PYTHON_EXE=C:\Program Files\Python311\python.exe"
        set "PIP_EXE=C:\Program Files\Python311\Scripts\pip.exe"
        set "PATH=C:\Program Files\Python311;C:\Program Files\Python311\Scripts;%PATH%"
        echo Encontrado em: C:\Program Files\Python311
    ) else (
        echo ERRO: Nao foi possivel localizar o Python instalado.
        echo Por favor, abra um novo CMD e execute: pip install pywinauto
        pause
        exit /b 1
    )
)

:: -------------------------------------------------------
:: 5. INSTALAR BIBLIOTECAS
:: -------------------------------------------------------
:install_libs
echo.
echo -------------------------------------------------------
echo Instalando bibliotecas necessarias...
echo -------------------------------------------------------

"%PYTHON_EXE%" -m pip install --upgrade pip
if %errorlevel% neq 0 (
    echo AVISO: Falha ao atualizar o pip, tentando continuar...
)

echo.
echo Instalando pywinauto...
"%PYTHON_EXE%" -m pip install pywinauto
if %errorlevel% neq 0 (
    echo ERRO: Falha ao instalar pywinauto.
    pause
    exit /b 1
)

:: Instala tambem o comtypes que o pywinauto usa com backend uia
echo.
echo Instalando comtypes (dependencia do pywinauto/uia)...
"%PYTHON_EXE%" -m pip install comtypes
if %errorlevel% neq 0 (
    echo AVISO: Falha ao instalar comtypes, pode nao ser necessario.
)

:: -------------------------------------------------------
:: 6. VERIFICACAO FINAL
:: -------------------------------------------------------
echo.
echo -------------------------------------------------------
echo Verificando instalacao...
"%PYTHON_EXE%" -c "import pywinauto; print('pywinauto OK - versao:', pywinauto.__version__)"
if %errorlevel% equ 0 (
    echo.
    echo ===================================================
    echo   TUDO PRONTO! Dependencias instaladas com sucesso.
    echo   Voce ja pode executar o bot.py normalmente.
    echo ===================================================
) else (
    echo.
    echo ERRO: A verificacao falhou. Tente reiniciar o computador
    echo e executar este script novamente.
)

echo.
pause
