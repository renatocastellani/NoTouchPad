"""
Desktop GUI for NoTouchPad using PySide6.
Provides a future-ready window to host webcam preview and gesture controls.
"""

import sys
from dataclasses import dataclass
from typing import Dict, List

try:
    from PySide6.QtCore import Qt, QTimer, QTime
    from PySide6.QtGui import QFont
    from PySide6.QtWidgets import (
        QApplication,
        QGridLayout,
        QGroupBox,
        QHBoxLayout,
        QLabel,
        QMainWindow,
        QPushButton,
        QTextEdit,
        QVBoxLayout,
        QWidget,
    )
except ImportError as exc:  # pragma: no cover - handled by caller
    raise ImportError(
        "PySide6 não encontrado. Instale com 'pip install PySide6' ou use a interface web."
    ) from exc


@dataclass
class GestureInfo:
    name: str
    description: str
    command: str
    emoji: str


def build_gestures() -> Dict[str, GestureInfo]:
    return {
        "punch": GestureInfo("✊ Punho", "Aciona ação principal", "Botão A", "✊"),
        "open": GestureInfo("✋ Mão Aberta", "Aciona ação secundária", "Botão B", "✋"),
        "point": GestureInfo("👆 Apontando", "Direciona movimento", "Analógico", "👆"),
        "thumbs": GestureInfo("👍 Joinha", "Abre menus", "Start", "👍"),
        "stop": GestureInfo("🤚 Pare", "Interrompe comandos", "Stop", "🤚"),
    }


class DesktopWindow(QMainWindow):
    """Janela principal do NoTouchPad."""

    def __init__(self) -> None:
        super().__init__()
        self.setWindowTitle("NoTouchPad v1.0.0 - Desktop")
        self.resize(1100, 720)

        self.gestures = build_gestures()
        self.gesture_cycle: List[str] = list(self.gestures.keys())
        self.cycle_index = 0
        self.is_running = False
        self.is_auto = False

        self._build_ui()
        self._setup_timers()
        self._log("Interface desktop iniciada. Selecione um modo para começar.")

    def _build_ui(self) -> None:
        central = QWidget()
        layout = QVBoxLayout(central)
        layout.setSpacing(16)
        layout.setContentsMargins(20, 20, 20, 20)

        header = QLabel("🎮 NoTouchPad")
        header.setAlignment(Qt.AlignCenter)
        header.setFont(QFont("Segoe UI", 26, QFont.Bold))
        layout.addWidget(header)

        subtitle = QLabel("Gamepad controlado por webcam - Interface Desktop")
        subtitle.setAlignment(Qt.AlignCenter)
        subtitle.setStyleSheet("color: #d0d0d0; font-size: 14px")
        layout.addWidget(subtitle)

        top_panel = QHBoxLayout()
        top_panel.setSpacing(16)
        layout.addLayout(top_panel)

        preview_group = QGroupBox("📹 Preview da Câmera")
        preview_layout = QVBoxLayout(preview_group)
        self.camera_placeholder = QLabel(
            "Em breve: vídeo em tempo real\n\nUse os botões para simular gestos"
        )
        self.camera_placeholder.setAlignment(Qt.AlignCenter)
        self.camera_placeholder.setMinimumHeight(320)
        self.camera_placeholder.setStyleSheet(
            "background-color: #1e1e1e;"
            "color: #f0f0f0;"
            "border-radius: 16px;"
            "font-size: 18px;"
        )
        preview_layout.addWidget(self.camera_placeholder)
        top_panel.addWidget(preview_group)

        status_group = QGroupBox("📊 Status")
        status_layout = QVBoxLayout(status_group)
        status_layout.setSpacing(12)

        self.status_label = QLabel("Status: 🔴 Parado")
        self.mode_label = QLabel("Modo: Manual")
        self.gesture_label = QLabel("Gesto atual: Nenhum")
        self.command_label = QLabel("Comando enviado: Standby")

        for lbl in (self.status_label, self.mode_label, self.gesture_label, self.command_label):
            lbl.setStyleSheet("font-size: 14px;")
            status_layout.addWidget(lbl)

        self.progress_indicator = QLabel("○○○ Aguardando")
        self.progress_indicator.setAlignment(Qt.AlignCenter)
        self.progress_indicator.setStyleSheet("color: #a0a0a0; font-size: 14px")
        status_layout.addWidget(self.progress_indicator)

        top_panel.addWidget(status_group)

        controls_group = QGroupBox("🎮 Controles")
        controls_layout = QVBoxLayout(controls_group)
        controls_layout.setSpacing(14)

        main_buttons_layout = QHBoxLayout()
        self.start_manual_btn = QPushButton("▶️ Modo Manual")
        self.start_manual_btn.clicked.connect(self._start_manual)
        self.start_auto_btn = QPushButton("🔄 Simulação Auto")
        self.start_auto_btn.clicked.connect(self._start_auto)
        self.stop_btn = QPushButton("⏹️ Parar")
        self.stop_btn.clicked.connect(self._stop_detection)

        for btn in (self.start_manual_btn, self.start_auto_btn, self.stop_btn):
            btn.setMinimumHeight(40)
            main_buttons_layout.addWidget(btn)

        controls_layout.addLayout(main_buttons_layout)

        gesture_grid = QGridLayout()
        gesture_grid.setSpacing(10)
        row = col = 0
        for key, info in self.gestures.items():
            btn = QPushButton(f"{info.emoji}  {info.name}\n{info.command}")
            btn.setMinimumHeight(70)
            btn.clicked.connect(lambda _, k=key: self._trigger_manual_gesture(k))
            gesture_grid.addWidget(btn, row, col)
            col += 1
            if col == 2:
                col = 0
                row += 1

        controls_layout.addLayout(gesture_grid)
        layout.addWidget(controls_group)

        log_group = QGroupBox("📝 Log de Eventos")
        log_layout = QVBoxLayout(log_group)
        self.log_output = QTextEdit()
        self.log_output.setReadOnly(True)
        log_layout.addWidget(self.log_output)
        layout.addWidget(log_group)

        self.setCentralWidget(central)

    def _setup_timers(self) -> None:
        self.auto_timer = QTimer(self)
        self.auto_timer.timeout.connect(self._auto_step)

    def _log(self, message: str) -> None:
        timestamp = QTime.currentTime().toString("HH:mm:ss")
        entry = f"[{timestamp}] {message}"
        self.log_output.append(entry)
        print(entry, file=sys.stderr)

    def _update_status(self, running: bool) -> None:
        self.is_running = running
        self.status_label.setText(f"Status: {'🟢 Ativo' if running else '🔴 Parado'}")
        self.progress_indicator.setText("●●● Detectando" if running else "○○○ Aguardando")

    def _set_mode(self, auto: bool) -> None:
        self.is_auto = auto
        self.mode_label.setText(f"Modo: {'Automático' if auto else 'Manual'}")

    def _start_manual(self) -> None:
        self.auto_timer.stop()
        self._update_status(True)
        self._set_mode(False)
        self.gesture_label.setText("Gesto atual: Aguardando gesto manual")
        self.command_label.setText("Comando enviado: --")
        self._log("Modo manual iniciado. Use os botões de gestos.")

    def _start_auto(self) -> None:
        self._set_mode(True)
        self._update_status(True)
        self.auto_timer.start(2000)
        self._log("Simulação automática iniciada.")

    def _stop_detection(self) -> None:
        self.auto_timer.stop()
        self._update_status(False)
        self.gesture_label.setText("Gesto atual: Nenhum")
        self.command_label.setText("Comando enviado: Standby")
        self._log("Detecção encerrada.")

    def _trigger_manual_gesture(self, gesture_key: str) -> None:
        if not self.is_running:
            self._start_manual()

        info = self.gestures[gesture_key]
        self.gesture_label.setText(f"Gesto atual: {info.name}")
        self.command_label.setText(f"Comando enviado: {info.command}")
        self.camera_placeholder.setText(
            f"{info.emoji}\n{info.name}\n→ {info.command}\n\n(Pré-visualização em desenvolvimento)"
        )
        self._log(f"Manual: {info.name} → {info.command}")

    def _auto_step(self) -> None:
        if not self.is_auto:
            return
        key = self.gesture_cycle[self.cycle_index]
        self.cycle_index = (self.cycle_index + 1) % len(self.gesture_cycle)
        self._trigger_manual_gesture(key)


def run_desktop_app() -> None:
    """Inicializa QApplication e roda a janela principal."""

    app = QApplication(sys.argv)
    app.setStyle("Fusion")
    window = DesktopWindow()
    window.show()
    sys.exit(app.exec())
