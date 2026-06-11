@echo off
setlocal
echo ===================================================
echo   Instalador de Dependencias - Bot MEGA ERP
echo ===================================================
echo.

:: Verifica a arquitetura do Windows
echo Verificando arquitetura do sistema...
if "%PROCESSOR_ARCHITECTURE%"=="AMD64" (
    set "PYTHON_URL=https://www.python.org/ftp/python/3.11.8/python-3.11.8-amd64.exe"
    echo Sistema 64-bit detectado.
) else (
    set "PYTHON_URL=https://www.python.org/ftp/python/3.11.8/python-3.11.8.exe"
    echo Sistema 32-bit detectado.
)

set "INSTALLER=python-installer.exe"

:: Verifica se o Python ja esta instalado
python --version >nul 2>&1
if %errorlevel% equ 0 (
    echo Python ja esta instalado! Pulando a instalacao do Python...
    goto install_libs
)

echo.
echo Baixando o instalador do Python... aguarde.
curl -# -o %INSTALLER% %PYTHON_URL%

echo.
echo Instalando o Python... Esta operacao pode demorar alguns minutos.
:: /quiet: instalacao silenciosa
:: PrependPath=1: adiciona o Python as variaveis de ambiente (PATH)
start /wait %INSTALLER% /quiet InstallAllUsers=0 PrependPath=1 Include_test=0

echo Instalacao do Python concluida.
del %INSTALLER%

:install_libs
echo.
echo Instalando/Atualizando a biblioteca 'pywinauto'...

:: Usando o py launcher caso o python nao tenha entrado no PATH imediatamente
py -m pip install --upgrade pip
py -m pip install pywinauto

if %errorlevel% neq 0 (
    echo.
    echo ATENCAO: Pode haver um problema com o PATH do Windows.
    echo Caso o pip tenha falhado, feche esta janela e abra novamente, ou reinicie o PC.
) else (
    echo.
    echo Bibliotecas instaladas com sucesso!
)

echo.
echo ===================================================
echo   Processo Concluido! 
echo   Pressione qualquer tecla para sair.
echo ===================================================
pause >nul
