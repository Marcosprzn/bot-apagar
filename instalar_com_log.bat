@echo off
title Instalador Bot MEGA ERP - COM LOG
color 0A

set "LOG=%TEMP%\instalador_log_%RANDOM%.txt"

echo ===================================================
echo    EXECUTANDO INSTALADOR COM LOG
echo ===================================================
echo.
echo   Log sera salvo em:
echo   %LOG%
echo.
echo   Acompanhe a instalacao na proxima janela.
echo   Ao finalizar, volte aqui e veja o resultado.
echo.
pause

REM Executa o instalador capturando tudo
start /wait "" cmd /c "instalar_dependencias.bat" >> "%LOG%" 2>&1

echo.
echo ===================================================
echo    INSTALACAO FINALIZADA
echo ===================================================
echo.
echo   Log completo salvo em:
echo   %LOG%
echo.
echo   Deseja exibir o log agora?
echo   [1] Sim
echo   [2] Nao
echo.
choice /c 12 /n
if errorlevel 2 goto FIM
if errorlevel 1 type "%LOG%" | more

echo.
echo   Log salvo em: %LOG%
echo.
pause
goto :EOF

:FIM
echo.
echo   Log disponivel em: %LOG%
echo.
pause