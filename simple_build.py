#!/usr/bin/env python3
"""Simple standalone packager for NoTouchPad."""

from __future__ import annotations

import platform
import shutil
import sys
import zipfile
from pathlib import Path
from typing import Iterable

APP_NAME = "NoTouchPad"
APP_VERSION = "1.0.0"
ROOT_DIR = Path(__file__).resolve().parent
SRC_DIR = ROOT_DIR / "src"
DIST_DIR = ROOT_DIR / "dist"
VENV_SOURCE_DIR = ROOT_DIR / "notouchpad_build_env"
BUNDLED_VENV_NAME = "venv"
ASSET_DIRS = ("assets",)
COPY_FILES = (
    "README.md",
    "requirements.txt",
    "requirements-minimal.txt",
)
IGNORE_PATTERNS = shutil.ignore_patterns("__pycache__", "*.pyc", ".DS_Store")


def ensure_project_layout() -> None:
    if not SRC_DIR.exists():
        print("Error: src directory not found.")
        sys.exit(1)


def package_name() -> str:
    system = platform.system().lower() or "unknown"
    return f"{APP_NAME}-{system}"


def clean_previous_outputs(target_dir: Path, zip_path: Path) -> None:
    if target_dir.exists():
        shutil.rmtree(target_dir)
        print(f"Removed old package: {target_dir}")
    if zip_path.exists():
        zip_path.unlink()
        print(f"Removed old archive: {zip_path.name}")


def copy_src_tree(dest_dir: Path) -> None:
    shutil.copytree(SRC_DIR, dest_dir / "src", ignore=IGNORE_PATTERNS)
    print("Source tree copied.")


def copy_optional_dirs(dest_dir: Path, folders: Iterable[str]) -> None:
    for folder in folders:
        source = ROOT_DIR / folder
        if source.exists():
            shutil.copytree(source, dest_dir / folder, ignore=IGNORE_PATTERNS)
            print(f"Copied folder: {folder}")


def copy_support_files(dest_dir: Path, files: Iterable[str]) -> None:
    for file_name in files:
        source = ROOT_DIR / file_name
        if source.exists():
            shutil.copy2(source, dest_dir / source.name)
            print(f"Copied file: {source.name}")


def copy_virtualenv(dest_dir: Path) -> bool:
    if not VENV_SOURCE_DIR.exists():
        print("Warning: project virtual environment not found; package will rely on system Python.")
        return False

    target = dest_dir / BUNDLED_VENV_NAME
    if target.exists():
        shutil.rmtree(target)
    shutil.copytree(VENV_SOURCE_DIR, target, symlinks=True)
    print("Bundled virtual environment copied.")
    return True


def create_launcher(dest_dir: Path) -> Path:
    system = platform.system().lower()
    if system == "windows":
        content = (
            "@echo off\n"
            "setlocal enabledelayedexpansion\n"
            "cd /d \"%~dp0\"\n"
            "echo NoTouchPad standalone launcher\n"
            "set VENV_PY=%~dp0venv\\Scripts\\python.exe\n"
            "if exist \"%VENV_PY%\" (set PYTHON_BIN=\"%VENV_PY%\") else (set PYTHON_BIN=python)\n"
            "echo Usando interpretador: %PYTHON_BIN%\n"
            "%PYTHON_BIN% src\\main.py %*\n"
            "set exit_code=%ERRORLEVEL%\n"
            "echo.\n"
            "echo Application finished with exit code %exit_code%\n"
            "echo Press any key to close...\n"
            "pause > nul\n"
            "exit /b %exit_code%\n"
        )
        launcher_path = dest_dir / "NoTouchPad.bat"
    else:
        content = (
            "#!/usr/bin/env bash\n"
            "set -e\n"
            "BASE_DIR=\"$(cd \"$(dirname \"$0\")\" && pwd)\"\n"
            "VENV_PY=\"$BASE_DIR/venv/bin/python\"\n"
            "PYTHON_BIN=python3\n"
            "if [ -x \"$VENV_PY\" ]; then\n"
            "  PYTHON_BIN=\"$VENV_PY\"\n"
            "fi\n"
            "cd \"$BASE_DIR\"\n"
            "echo \"NoTouchPad standalone launcher\"\n"
            "echo \"Inicializando interface desktop (PySide6).\"\n"
            "echo \"Usando interpretador: $PYTHON_BIN\"\n"
            "\"$PYTHON_BIN\" src/main.py \"$@\"\n"
            "exit_code=$?\n"
            "echo\n"
            "read -r -p \"Application finished (exit code $exit_code). Press Enter to close...\"\n"
            "exit \"$exit_code\"\n"
        )
        launcher_path = dest_dir / "NoTouchPad.sh"

    launcher_path.write_text(content, encoding="utf-8")
    if system != "windows":
        launcher_path.chmod(0o755)
    print(f"Launcher created: {launcher_path.name}")
    return launcher_path


def write_usage_doc(dest_dir: Path) -> None:
    text = f"""{APP_NAME} v{APP_VERSION} - Standalone Package\n\n"""
    text += "Contents:\n"
    text += "  - src/: Python sources with desktop UI.\n"
    text += "  - README.md: project overview.\n"
    text += "  - requirements*.txt: optional dependency lists.\n"
    text += "  - venv/: virtual environment bundled with PySide6.\n"
    text += "\nUsage:\n"
    text += "Windows:\n"
    text += "  1. Double click NoTouchPad.bat.\n"
    text += "  2. O launcher usa automaticamente o venv incluso (./venv).\n"
    text += "  3. Sem o venv, ele tenta o Python do sistema.\n"
    text += "\nLinux/Mac:\n"
    text += "  1. Execute ./NoTouchPad.sh a partir do diretório do pacote.\n"
    text += "  2. O script prioriza ./venv/bin/python e cai para python3 se necessário.\n"
    text += "  3. Mantenha o terminal aberto para ver logs e encerrar.\n"
    text += "\nTips:\n"
    text += "  - O venv foi copiado do ambiente de build; reinstale dependências nele se atualizar o projeto.\n"
    text += "  - Para reduzir tamanho, você pode remover ./venv e usar um Python próprio (instale PySide6).\n"
    text += "  - A estrutura mantém os fontes acessíveis para customizações.\n"

    (dest_dir / "LEIA-ME.txt").write_text(text, encoding="utf-8")
    print("Usage document created.")


def create_zip(package_dir: Path, zip_path: Path) -> None:
    with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as archive:
        for file_path in package_dir.rglob("*"):
            if file_path.is_file():
                archive.write(file_path, file_path.relative_to(DIST_DIR))
    print(f"Archive created: {zip_path.name}")


def verify_package(package_dir: Path) -> None:
    required_items = (
        package_dir / "src" / "main.py",
        package_dir / "README.md",
        package_dir / "LEIA-ME.txt",
    )
    missing = [item for item in required_items if not item.exists()]
    if missing:
        raise RuntimeError(f"Missing items: {', '.join(str(item) for item in missing)}")

    if not any((package_dir / name).exists() for name in ("NoTouchPad.bat", "NoTouchPad.sh")):
        raise RuntimeError("Launcher script not created.")

    print("Basic package verification passed.")


def main() -> int:
    ensure_project_layout()
    DIST_DIR.mkdir(exist_ok=True)
    pkg_name = package_name()
    package_dir = DIST_DIR / pkg_name
    zip_path = DIST_DIR / f"{pkg_name}.zip"

    clean_previous_outputs(package_dir, zip_path)
    package_dir.mkdir(parents=True, exist_ok=True)
    copy_src_tree(package_dir)
    copy_optional_dirs(package_dir, ASSET_DIRS)
    copy_support_files(package_dir, COPY_FILES)
    copy_virtualenv(package_dir)
    create_launcher(package_dir)
    write_usage_doc(package_dir)
    verify_package(package_dir)
    create_zip(package_dir, zip_path)

    print("Standalone package ready.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
