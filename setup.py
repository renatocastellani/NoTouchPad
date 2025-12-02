#!/usr/bin/env python3
"""
NoTouchPad Setup Script
Script de instalação e distribuição do NoTouchPad

Author: Renato Castellani
Version: 1.0.0
"""

from setuptools import setup, find_packages
from pathlib import Path

# Lê o README
this_directory = Path(__file__).parent
long_description = (this_directory / "README.md").read_text()

setup(
    name="notouchpad",
    version="1.0.0",
    author="Renato Castellani",
    author_email="seu-email@exemplo.com",  # TODO: Adicionar email real
    description="Gamepad controlado por webcam que transforma movimentos em comandos de controle",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/renatocastellani/NoTouchPad",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: End Users/Desktop",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Topic :: Games/Entertainment",
        "Topic :: Multimedia :: Video :: Capture",
    ],
    python_requires=">=3.8",
    install_requires=[
        "opencv-python>=4.8.0",
        "mediapipe>=0.10.0",
        "numpy>=1.24.0",
        "pygame>=2.5.0",
        "pynput>=1.7.6",
        "PySide6>=6.6.0",
        "Pillow>=10.0.0",
        "requests>=2.31.0",
    ],
    extras_require={
        "dev": [
            "pyinstaller>=6.0.0",
            "pytest>=7.4.0",
            "black>=23.0.0",
            "flake8>=6.0.0",
            "mypy>=1.5.0",
        ],
    },
    entry_points={
        "console_scripts": [
            "notouchpad=src.main:main",
        ],
    },
    include_package_data=True,
    package_data={
        "src": ["assets/*"],
    },
)
