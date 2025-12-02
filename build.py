#!/usr/bin/env python3
"""
NoTouchPad Build Script
Script para gerar executáveis standalone com PyInstaller

Author: Renato Castellani
Version: 1.0.0
"""

import os
import sys
import shutil
import platform
from pathlib import Path

def clean_build_dirs():
    """
    Limpa diretórios de build anteriores
    """
    dirs_to_clean = ['build', 'dist', '__pycache__']
    
    for dir_name in dirs_to_clean:
        if os.path.exists(dir_name):
            shutil.rmtree(dir_name)
            print(f"Removido: {dir_name}")

def build_executable():
    """
    Gera executável usando PyInstaller
    """
    import PyInstaller.__main__
    
    # Determina o sistema operacional
    system = platform.system().lower()
    
    # Nome do executável
    exe_name = f"NoTouchPad-{system}"
    if system == "windows":
        exe_name += ".exe"
    
    # Parâmetros do PyInstaller
    pyinstaller_args = [
        '--name', exe_name,
        '--onefile',
        '--windowed',  # Sem console no Windows
        '--add-data', 'src;src' if system == "windows" else 'src:src',
        '--hidden-import', 'tkinter',
        '--hidden-import', 'threading',
        # Comentados por enquanto (dependências não instaladas):
        # '--hidden-import', 'cv2',
        # '--hidden-import', 'mediapipe', 
        # '--hidden-import', 'pygame',
        # '--hidden-import', 'pynput',
        # '--hidden-import', 'numpy',
        # '--hidden-import', 'PIL',
        # '--icon', 'assets/icon.ico',  # TODO: Criar ícone
        'src/main.py'
    ]
    
    # Ajusta separadores para Linux/Mac
    if system != "windows":
        for i, arg in enumerate(pyinstaller_args):
            if ';' in arg and '--add-data' in pyinstaller_args[i-1]:
                pyinstaller_args[i] = arg.replace(';', ':')
    
    print(f"Gerando executável para {system}...")
    print(f"Comando: pyinstaller {' '.join(pyinstaller_args)}")
    
    try:
        PyInstaller.__main__.run(pyinstaller_args)
        print(f"\n✓ Executável gerado com sucesso: dist/{exe_name}")
        return True
    except Exception as e:
        print(f"\n✗ Erro ao gerar executável: {e}")
        return False

def main():
    """
    Função principal do script de build
    """
    print("=== NoTouchPad Build Script ===")
    print(f"Sistema: {platform.system()} {platform.release()}")
    print(f"Python: {sys.version}")
    
    # Verifica se PyInstaller está instalado
    try:
        import PyInstaller
        print(f"PyInstaller: {PyInstaller.__version__}")
    except ImportError:
        print("✗ PyInstaller não encontrado. Instale com: pip install pyinstaller")
        return 1
    
    # Limpa diretórios anteriores
    print("\nLimpando diretórios de build...")
    clean_build_dirs()
    
    # Gera executável
    print("\nIniciando build...")
    if build_executable():
        print("\n✓ Build concluído com sucesso!")
        print("\nPróximos passos:")
        print("1. Teste o executável em dist/")
        print("2. Faça upload para GitHub Releases")
        print("3. Compartilhe com os usuários!")
        return 0
    else:
        print("\n✗ Build falhou!")
        return 1

if __name__ == "__main__":
    sys.exit(main())
