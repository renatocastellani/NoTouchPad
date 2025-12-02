@echo off
REM NoTouchPad - Script de Instalação para Windows
REM Author: Renato Castellani
REM Version: 1.0.0

echo === NoTouchPad Installer ===
echo Instalando NoTouchPad...
echo.

REM Verifica se Python está instalado
python --version >nul 2>&1
if errorlevel 1 (
    echo X Python não encontrado!
    echo Por favor, instale Python 3.8+ antes de continuar.
    echo Download: https://www.python.org/downloads/
    pause
    exit /b 1
)

echo ✓ Python encontrado:
python --version

REM Verifica se pip está instalado
pip --version >nul 2>&1
if errorlevel 1 (
    echo X pip não encontrado!
    echo Instalando pip...
    python -m ensurepip --upgrade
)

echo ✓ pip encontrado:
pip --version

REM Pergunta sobre ambiente virtual
set /p create_venv="Criar ambiente virtual? (recomendado) [Y/n]: "
if /i not "%create_venv%"=="n" (
    echo Criando ambiente virtual...
    python -m venv notouchpad_env
    call notouchpad_env\Scripts\activate.bat
    echo ✓ Ambiente virtual criado e ativado
)

REM Atualiza pip
echo Atualizando pip...
python -m pip install --upgrade pip

REM Instala dependências
echo Instalando dependências...
pip install -r requirements.txt

REM Verifica instalação
echo Verificando instalação...
python -c "import cv2, mediapipe, pygame, pynput; print('✓ Todas as dependências instaladas com sucesso!')"

echo.
echo ✓ NoTouchPad instalado com sucesso!
echo.
echo Para executar:
if /i not "%create_venv%"=="n" (
    echo   notouchpad_env\Scripts\activate.bat
)
echo   python src\main.py
echo.
echo Para gerar executável:
echo   python build.py
echo.
pause
