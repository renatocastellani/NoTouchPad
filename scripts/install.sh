#!/bin/bash
# NoTouchPad - Script de Instalação para Linux/Mac
# Author: Renato Castellani
# Version: 1.0.0

set -e  # Para em caso de erro

echo "=== NoTouchPad Installer ==="
echo "Instalando NoTouchPad..."

# Verifica se Python está instalado
if ! command -v python3 &> /dev/null; then
    echo "✗ Python 3 não encontrado!"
    echo "Por favor, instale Python 3.8+ antes de continuar."
    exit 1
fi

echo "✓ Python 3 encontrado: $(python3 --version)"

# Verifica se pip está instalado
if ! command -v pip3 &> /dev/null; then
    echo "✗ pip3 não encontrado!"
    echo "Instalando pip..."
    python3 -m ensurepip --upgrade
fi

echo "✓ pip3 encontrado: $(pip3 --version)"

# Cria ambiente virtual (opcional)
read -p "Criar ambiente virtual? (recomendado) [Y/n]: " create_venv
if [[ $create_venv != "n" && $create_venv != "N" ]]; then
    echo "Criando ambiente virtual..."
    python3 -m venv notouchpad_env
    source notouchpad_env/bin/activate
    echo "✓ Ambiente virtual criado e ativado"
fi

# Atualiza pip
echo "Atualizando pip..."
pip install --upgrade pip

# Instala dependências
echo "Instalando dependências..."
pip install -r requirements.txt

# Verifica instalação
echo "Verificando instalação..."
python3 -c "import cv2, mediapipe, pygame, pynput; print('✓ Todas as dependências instaladas com sucesso!')"

echo ""
echo "✓ NoTouchPad instalado com sucesso!"
echo ""
echo "Para executar:"
if [[ $create_venv != "n" && $create_venv != "N" ]]; then
    echo "  source notouchpad_env/bin/activate"
fi
echo "  python3 src/main.py"
echo ""
echo "Para gerar executável:"
echo "  python3 build.py"
echo ""
