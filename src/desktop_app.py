"""Desktop GUI for NoTouchPad using PySide6."""

import sys
from dataclasses import dataclass
from typing import Dict, List, Optional, Tuple

from camera_detector import CameraDetector, scan_available_cameras
from gesture_recognizer import GestureRecognizer, GestureType

try:
    from PySide6.QtCore import Qt, QTimer, QTime
    from PySide6.QtGui import QFont, QImage, QPixmap
    from PySide6.QtWidgets import (
        QApplication,
        QComboBox,
        QGridLayout,
        QGroupBox,
        QHBoxLayout,
        QLabel,
        QMainWindow,
        QPushButton,
        QTabWidget,
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
        self.preview_has_video = False
        self.camera_detector: Optional[CameraDetector] = None
        self.camera_timer = QTimer(self)
        self.camera_timer.timeout.connect(self._update_camera_preview)
        self.available_cameras: List[Tuple[int, bool]] = []
        self.camera_selector: Optional[QComboBox] = None
        self.gesture_recognizer: Optional[GestureRecognizer] = None
        self.last_detected_gesture: GestureType = GestureType.UNKNOWN
        self.gesture_indicator_labels: Dict[str, QLabel] = {}
        self.gesture_indicator_timers: Dict[str, QTimer] = {}

        self._build_ui()
        self._setup_timers()
        self._init_gesture_recognizer()
        self._init_camera()
        self._log("Interface desktop iniciada. Detecção automática habilitada.")
        self._resume_detection()

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

        self.tab_widget = QTabWidget()
        layout.addWidget(self.tab_widget, 1)

        self._build_detection_tab()
        self._build_simulation_tab()

        log_group = QGroupBox("📝 Log de Eventos")
        log_layout = QVBoxLayout(log_group)
        self.log_output = QTextEdit()
        self.log_output.setReadOnly(True)
        log_layout.addWidget(self.log_output)
        layout.addWidget(log_group)

        self.setCentralWidget(central)

    def _build_detection_tab(self) -> None:
        detection_widget = QWidget()
        detection_layout = QVBoxLayout(detection_widget)
        detection_layout.setSpacing(16)

        top_panel = QHBoxLayout()
        top_panel.setSpacing(16)
        detection_layout.addLayout(top_panel)

        preview_group = QGroupBox("📹 Preview da Câmera")
        preview_layout = QVBoxLayout(preview_group)
        self.camera_placeholder = QLabel(
            "Fluxo ao vivo: aguarde a detecção inicial\n\nGestos são reconhecidos automaticamente"
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
        camera_controls = QHBoxLayout()
        camera_controls.setSpacing(8)
        camera_controls.addWidget(QLabel("Câmera:"))
        self.camera_selector = QComboBox()
        self.camera_selector.currentIndexChanged.connect(self._on_camera_selected)
        camera_controls.addWidget(self.camera_selector, 1)
        self.refresh_cameras_btn = QPushButton("🔄 Atualizar")
        self.refresh_cameras_btn.clicked.connect(self._refresh_camera_devices)
        camera_controls.addWidget(self.refresh_cameras_btn)
        preview_layout.addLayout(camera_controls)
        top_panel.addWidget(preview_group)

        status_group = QGroupBox("📊 Status")
        status_layout = QVBoxLayout(status_group)
        status_layout.setSpacing(12)

        self.status_label = QLabel("Status: 🔴 Pausado")
        self.mode_label = QLabel("Simulação: Manual")
        self.gesture_label = QLabel("Gesto atual: Nenhum")
        self.command_label = QLabel("Comando enviado: Standby")

        for lbl in (self.status_label, self.mode_label, self.gesture_label, self.command_label):
            lbl.setStyleSheet("font-size: 14px;")
            status_layout.addWidget(lbl)

        self.progress_indicator = QLabel("○○○ Inicializando")
        self.progress_indicator.setAlignment(Qt.AlignCenter)
        self.progress_indicator.setStyleSheet("color: #a0a0a0; font-size: 14px")
        status_layout.addWidget(self.progress_indicator)

        top_panel.addWidget(status_group)

        gesture_group = QGroupBox("🖐️ Gestos Disponíveis")
        gesture_layout = QVBoxLayout(gesture_group)
        gesture_layout.setSpacing(12)
        self._build_gesture_rows(gesture_layout)
        detection_layout.addWidget(gesture_group)

        detection_controls = QHBoxLayout()
        detection_controls.setSpacing(10)
        self.resume_detection_btn = QPushButton("▶️ Retomar detecção")
        self.resume_detection_btn.clicked.connect(self._resume_detection)
        self.pause_detection_btn = QPushButton("⏸️ Pausar detecção")
        self.pause_detection_btn.clicked.connect(self._stop_detection)
        detection_controls.addWidget(self.resume_detection_btn)
        detection_controls.addWidget(self.pause_detection_btn)
        detection_layout.addLayout(detection_controls)

        self.tab_widget.addTab(detection_widget, "Detecção")

    def _build_simulation_tab(self) -> None:
        simulation_widget = QWidget()
        sim_layout = QVBoxLayout(simulation_widget)
        sim_layout.setSpacing(16)

        info_label = QLabel(
            "Esta aba oferece botões de teste e a simulação automática de comandos."
        )
        info_label.setWordWrap(True)
        sim_layout.addWidget(info_label)

        manual_group = QGroupBox("🎯 Acionamento manual")
        manual_layout = QVBoxLayout(manual_group)
        manual_layout.setSpacing(14)

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

        manual_layout.addLayout(gesture_grid)
        sim_layout.addWidget(manual_group)

        auto_group = QGroupBox("⚙️ Simulação automática")
        auto_layout = QHBoxLayout(auto_group)
        self.start_auto_btn = QPushButton("🔄 Iniciar simulação")
        self.start_auto_btn.clicked.connect(self._start_auto)
        self.stop_auto_btn = QPushButton("⏹️ Parar simulação")
        self.stop_auto_btn.clicked.connect(self._stop_auto_simulation)
        for btn in (self.start_auto_btn, self.stop_auto_btn):
            btn.setMinimumHeight(40)
            auto_layout.addWidget(btn)
        sim_layout.addWidget(auto_group)

        self.tab_widget.addTab(simulation_widget, "Simulação")

    def _build_gesture_rows(self, parent_layout: QVBoxLayout) -> None:
        for key, info in self.gestures.items():
            row = QHBoxLayout()
            row.setSpacing(12)

            indicator = QLabel()
            indicator.setFixedSize(20, 20)
            indicator.setStyleSheet(self._indicator_style(False))
            indicator.setToolTip(f"{info.name} → {info.command}")

            label = QLabel(info.name)
            label.setStyleSheet("font-size: 15px;")

            row.addWidget(indicator)
            row.addWidget(label, 1)
            row.addStretch()
            parent_layout.addLayout(row)
            parent_layout.addWidget(self._divider())

            self.gesture_indicator_labels[key] = indicator

        if parent_layout.count():
            divider_item = parent_layout.takeAt(parent_layout.count() - 1)
            divider_widget = divider_item.widget()
            if divider_widget:
                divider_widget.deleteLater()

    def _divider(self) -> QWidget:
        line = QWidget()
        line.setFixedHeight(1)
        line.setStyleSheet("background-color: #2a2a2a;")
        return line

    def _indicator_style(self, active: bool) -> str:
        border_color = "#2ecc71" if active else "#5e5e5e"
        fill_color = "#2ecc71" if active else "transparent"
        return (
            "min-width: 20px;"
            "min-height: 20px;"
            "max-width: 20px;"
            "max-height: 20px;"
            "border-radius: 10px;"
            f"border: 2px solid {border_color};"
            f"background-color: {fill_color};"
        )

    def _set_indicator_state(self, gesture_key: str, active: bool) -> None:
        label = self.gesture_indicator_labels.get(gesture_key)
        if not label:
            return
        label.setStyleSheet(self._indicator_style(active))

    def _activate_indicator(self, gesture_key: str, duration_ms: int = 2000) -> None:
        self._set_indicator_state(gesture_key, True)
        timer = self.gesture_indicator_timers.get(gesture_key)
        if timer:
            timer.stop()
        timer = QTimer(self)
        timer.setSingleShot(True)
        timer.timeout.connect(lambda k=gesture_key: self._set_indicator_state(k, False))
        timer.start(duration_ms)
        self.gesture_indicator_timers[gesture_key] = timer

    def _setup_timers(self) -> None:
        self.auto_timer = QTimer(self)
        self.auto_timer.timeout.connect(self._auto_step)

    def _init_gesture_recognizer(self) -> None:
        try:
            self.gesture_recognizer = GestureRecognizer()
            self._log("Reconhecimento de gestos ativado (MediaPipe).")
        except Exception as exc:  # pragma: no cover - fallback
            self.gesture_recognizer = None
            self._log(f"Reconhecimento de gestos indisponível: {exc}")

    def _init_camera(self) -> None:
        self.available_cameras = scan_available_cameras()
        self._populate_camera_selector()

        if not self.available_cameras:
            self.camera_placeholder.setText(
                "Nenhuma webcam detectada. Verifique conexões ou permissões e clique em Atualizar."
            )
            return

        preferred = self._pick_preferred_camera()
        if preferred is None:
            preferred = self.available_cameras[0][0]

        self._select_camera_in_combo(preferred)
        self._start_camera(preferred)

    def _log(self, message: str) -> None:
        timestamp = QTime.currentTime().toString("HH:mm:ss")
        entry = f"[{timestamp}] {message}"
        self.log_output.append(entry)
        print(entry, file=sys.stderr)

    def _update_camera_preview(self) -> None:
        if not self.camera_detector:
            return

        frame = self.camera_detector.capture_frame()
        if frame is None:
            if self.preview_has_video:
                self.camera_placeholder.setText("Câmera pausada. Tentando reconectar...")
                self.preview_has_video = False
            return

        height, width, _ = frame.shape
        image = QImage(frame.data, width, height, 3 * width, QImage.Format_RGB888)
        pixmap = QPixmap.fromImage(image).scaled(
            self.camera_placeholder.width(),
            self.camera_placeholder.height(),
            Qt.KeepAspectRatio,
            Qt.SmoothTransformation,
        )
        self.camera_placeholder.setPixmap(pixmap)
        self.preview_has_video = True
        self._process_gesture_frame(frame)

    def _process_gesture_frame(self, frame) -> None:
        if not self.gesture_recognizer or not self.is_running:
            return

        hands = self.gesture_recognizer.detect_hands(frame)
        if not hands:
            self._handle_no_gesture()
            return

        detected_any = False
        for hand in hands:
            if hand.gesture == GestureType.UNKNOWN:
                continue
            detected_any = True
            self._handle_detected_gesture(hand.gesture)

        if not detected_any:
            self._handle_no_gesture()

    def _handle_detected_gesture(self, gesture_type: GestureType) -> None:
        mapping = {
            GestureType.FIST: "punch",
            GestureType.OPEN_HAND: "open",
            GestureType.POINTING: "point",
            GestureType.THUMBS_UP: "thumbs",
            GestureType.PEACE: "stop",
        }

        key = mapping.get(gesture_type)
        if not key or key not in self.gestures:
            self.gesture_label.setText("Gesto atual: Desconhecido")
            self.command_label.setText("Comando enviado: --")
            return

        self._activate_indicator(key)

        info = self.gestures[key]
        if gesture_type != self.last_detected_gesture:
            self.last_detected_gesture = gesture_type
            self.gesture_label.setText(f"Gesto atual: {info.name}")
            self.command_label.setText(f"Comando enviado: {info.command}")
            self._log(f"Gestos: {info.name} detectado automaticamente")

    def _handle_no_gesture(self) -> None:
        if self.last_detected_gesture == GestureType.UNKNOWN:
            return
        self.last_detected_gesture = GestureType.UNKNOWN
        self.gesture_label.setText("Gesto atual: Nenhum")
        self.command_label.setText("Comando enviado: Standby")

    def _populate_camera_selector(self) -> None:
        if not self.camera_selector:
            return

        self.camera_selector.blockSignals(True)
        self.camera_selector.clear()
        for cam_idx, has_frame in self.available_cameras:
            status = "✅" if has_frame else "⚠️"
            label = f"{status} Câmera {cam_idx}"
            self.camera_selector.addItem(label, cam_idx)
        self.camera_selector.blockSignals(False)
        self.camera_selector.setEnabled(bool(self.available_cameras))
        if hasattr(self, "refresh_cameras_btn"):
            self.refresh_cameras_btn.setEnabled(True)

    def _pick_preferred_camera(self) -> Optional[int]:
        for cam_idx, has_frame in self.available_cameras:
            if has_frame:
                return cam_idx
        return self.available_cameras[0][0] if self.available_cameras else None

    def _select_camera_in_combo(self, camera_index: int) -> None:
        if not self.camera_selector:
            return
        self.camera_selector.blockSignals(True)
        for combo_row in range(self.camera_selector.count()):
            if self.camera_selector.itemData(combo_row) == camera_index:
                self.camera_selector.setCurrentIndex(combo_row)
                break
        self.camera_selector.blockSignals(False)

    def _start_camera(self, camera_index: int) -> None:
        if self.camera_detector is None:
            self.camera_detector = CameraDetector(camera_index=camera_index)
            initialized = self.camera_detector.initialize_camera()
        else:
            initialized = self.camera_detector.reinitialize(camera_index)

        self.preview_has_video = False

        if initialized:
            self.camera_placeholder.setText("Câmera inicializada. Carregando preview...")
            if not self.camera_timer.isActive():
                self.camera_timer.start(33)
        else:
            self.camera_placeholder.setText(
                "Não foi possível inicializar esta webcam. Escolha outra ou verifique permissões."
            )
            if self.camera_timer.isActive():
                self.camera_timer.stop()

    def _on_camera_selected(self, combo_index: int) -> None:
        if combo_index < 0 or not self.camera_selector:
            return
        camera_index = self.camera_selector.itemData(combo_index)
        if camera_index is None:
            return
        self._start_camera(int(camera_index))

    def _refresh_camera_devices(self) -> None:
        self.available_cameras = scan_available_cameras()
        self._populate_camera_selector()
        if self.available_cameras:
            preferred = self._pick_preferred_camera()
            if preferred is None:
                preferred = self.available_cameras[0][0]
            self._select_camera_in_combo(preferred)
            self._start_camera(preferred)
        else:
            self.camera_placeholder.setText(
                "Nenhuma webcam detectada. Reconecte o dispositivo e tente novamente."
            )
            if self.camera_detector:
                self.camera_detector.release_camera()
            self.camera_timer.stop()

    def _update_status(self, running: bool) -> None:
        self.is_running = running
        self.status_label.setText(f"Status: {'🟢 Detectando' if running else '🔴 Pausado'}")
        self.progress_indicator.setText("●●● Detectando" if running else "○○○ Pausado")

    def _set_mode(self, auto: bool) -> None:
        self.is_auto = auto
        self.mode_label.setText(f"Simulação: {'Automática' if auto else 'Manual'}")

    def _resume_detection(self) -> None:
        if self.is_running:
            return
        self._update_status(True)
        self.gesture_label.setText("Gesto atual: Aguardando detecção")
        self.command_label.setText("Comando enviado: --")
        self._log("Detecção de gestos ativada.")

    def _start_auto(self) -> None:
        self._set_mode(True)
        if not self.is_running:
            self._resume_detection()
        self.auto_timer.start(2000)
        self._log("Simulação automática iniciada.")

    def _stop_detection(self) -> None:
        self._update_status(False)
        self.gesture_label.setText("Gesto atual: Detecção pausada")
        self.command_label.setText("Comando enviado: --")
        self._log("Detecção pausada pelo usuário.")

    def _stop_auto_simulation(self) -> None:
        if not self.is_auto:
            return
        self.auto_timer.stop()
        self._set_mode(False)
        self._log("Simulação automática pausada.")

    def _trigger_manual_gesture(self, gesture_key: str) -> None:
        info = self.gestures[gesture_key]
        self._activate_indicator(gesture_key)
        self.gesture_label.setText(f"Gesto atual: {info.name}")
        self.command_label.setText(f"Comando enviado: {info.command}")
        if not self.preview_has_video:
            self.camera_placeholder.setText(
                f"{info.emoji}\n{info.name}\n→ {info.command}\n\n(Câmera indisponível)"
            )
        self._log(f"Manual: {info.name} → {info.command}")

    def _auto_step(self) -> None:
        if not self.is_auto:
            return
        key = self.gesture_cycle[self.cycle_index]
        self.cycle_index = (self.cycle_index + 1) % len(self.gesture_cycle)
        self._trigger_manual_gesture(key)

    def closeEvent(self, event) -> None:  # type: ignore[override]
        if self.camera_timer.isActive():
            self.camera_timer.stop()
        if self.camera_detector:
            self.camera_detector.release_camera()
        super().closeEvent(event)


def run_desktop_app() -> None:
    """Inicializa QApplication e roda a janela principal."""

    app = QApplication(sys.argv)
    app.setStyle("Fusion")
    window = DesktopWindow()
    window.show()
    sys.exit(app.exec())
