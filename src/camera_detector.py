"""
Camera Detector Module
Responsável por capturar vídeo da webcam e detectar presença/movimentos

Author: Renato Castellani
Version: 1.0.0
"""

from __future__ import annotations

import time
from typing import List, Optional, Tuple

import cv2
import numpy as np

class CameraDetector:
    """Encapsula captura de vídeo com OpenCV."""

    def __init__(self, camera_index: int = 0, frame_size: Tuple[int, int] = (1280, 720)):
        self.camera_index = camera_index
        self.frame_size = frame_size
        self.capture: Optional[cv2.VideoCapture] = None
        self.is_active = False
        self.last_frame_timestamp: float = 0.0

    def initialize_camera(self) -> bool:
        """Inicializa a câmera e aplica configurações básicas."""

        self.release_camera()
        self.capture = cv2.VideoCapture(self.camera_index)

        if not self.capture.isOpened():  # type: ignore[union-attr]
            self.capture = None
            self.is_active = False
            return False

        width, height = self.frame_size
        self.capture.set(cv2.CAP_PROP_FRAME_WIDTH, width)
        self.capture.set(cv2.CAP_PROP_FRAME_HEIGHT, height)
        self.capture.set(cv2.CAP_PROP_FPS, 30)
        self.is_active = True
        return True

    def reinitialize(self, camera_index: int) -> bool:
        """Switch to a different camera index."""

        self.camera_index = camera_index
        return self.initialize_camera()

    def capture_frame(self) -> Optional[np.ndarray]:
        """Retorna um frame RGB normalizado ou None se indisponível."""

        if not self.capture or not self.is_active:
            return None

        ret, frame = self.capture.read()
        if not ret:
            self.is_active = False
            return None

        self.last_frame_timestamp = time.time()
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        return rgb_frame

    def release_camera(self) -> None:
        """Libera o dispositivo de captura se estiver em uso."""

        if self.capture:
            self.capture.release()
        self.capture = None
        self.is_active = False


def scan_available_cameras(max_devices: int = 5) -> List[Tuple[int, bool]]:
    """Return camera indices with a flag telling whether frames can be read."""

    available: List[Tuple[int, bool]] = []
    for index in range(max_devices):
        cap = cv2.VideoCapture(index)
        if cap is None or not cap.isOpened():
            continue

        has_frame = False
        has_variation = False
        for _ in range(3):
            ret, frame = cap.read()
            if ret and frame is not None:
                has_frame = True
                if _frame_has_variation(frame):
                    has_variation = True
                break

        available.append((index, has_frame and has_variation))
        cap.release()

    return available


def _frame_has_variation(frame: np.ndarray, threshold: float = 8.0) -> bool:
    """Rough check to ensure the frame isn't just a solid color or frozen image."""

    if frame is None or frame.size == 0:
        return False

    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    return float(gray.std()) >= threshold
