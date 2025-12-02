#!/usr/bin/env python3
"""
NoTouchPad - Main Entry Point
Gamepad controlado por webcam que transforma movimentos em comandos de controle

Author: Renato Castellani
Version: 1.0.0
"""

import sys
from pathlib import Path

# Adiciona o diretório src ao path para imports
sys.path.append(str(Path(__file__).parent))


def main():
    """Entrada principal: executa apenas a interface desktop PySide6."""

    print("🎮 NoTouchPad v1.0.0 - Iniciando...")

    try:
        print("🪟 Carregando interface desktop (PySide6)...")
        from desktop_app import run_desktop_app
    except ImportError as error:
        print("❌ PySide6 não está disponível no ambiente atual.")
        print("   Instale as dependências com o venv ativo:")
        print("   $ source notouchpad_build_env/bin/activate")
        print("   $ pip install -r requirements.txt")
        print(f"Detalhes: {error}")
        sys.exit(1)

    try:
        run_desktop_app()
    except KeyboardInterrupt:
        print("\n🛑 Encerrando NoTouchPad...")
    except Exception as error:
        print(f"❌ Erro crítico na interface desktop: {error}")
        sys.exit(1)
    else:
        print("👋 NoTouchPad encerrado.")

if __name__ == "__main__":
    main()

