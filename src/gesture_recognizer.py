"""Reconhecedor de gestos baseado em MediaPipe para o NoTouchPad."""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import List

import cv2
import mediapipe as mp
import numpy as np


class GestureType(Enum):
    UNKNOWN = "unknown"
    FIST = "fist"
    OPEN_HAND = "open_hand"
    POINTING = "pointing"
    THUMBS_UP = "thumbs_up"
    PEACE = "peace"


@dataclass
class HandPosition:
    x: float
    y: float
    gesture: GestureType
    score: float = 0.0
    handedness: str = "Unknown"


class GestureRecognizer:
    """Faz interface entre MediaPipe e o app, convertendo frames em gestos simples."""

    def __init__(
        self,
        max_num_hands: int = 1,
        min_detection_confidence: float = 0.5,
        min_tracking_confidence: float = 0.5,
    ) -> None:
        self._mp_hands = mp.solutions.hands
        self._hands = self._mp_hands.Hands(
            static_image_mode=False,
            max_num_hands=max_num_hands,
            model_complexity=0,
            min_detection_confidence=min_detection_confidence,
            min_tracking_confidence=min_tracking_confidence,
        )

    def detect_hands(self, frame: np.ndarray) -> List[HandPosition]:
        if frame is None or frame.size == 0:
            return []

        # MediaPipe espera RGB.
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        rgb_frame.flags.writeable = False
        results = self._hands.process(rgb_frame)
        rgb_frame.flags.writeable = True

        if not results.multi_hand_landmarks:
            return []

        detected: List[HandPosition] = []
        for idx, hand_landmarks in enumerate(results.multi_hand_landmarks):
            handed_label = "Unknown"
            score = 0.0
            if results.multi_handedness and idx < len(results.multi_handedness):
                handed = results.multi_handedness[idx].classification[0]
                handed_label = handed.label
                score = handed.score

            gesture = self._recognize_gesture(hand_landmarks, handed_label)
            xs = [lm.x for lm in hand_landmarks.landmark]
            ys = [lm.y for lm in hand_landmarks.landmark]
            detected.append(
                HandPosition(
                    x=float(np.mean(xs)),
                    y=float(np.mean(ys)),
                    gesture=gesture,
                    score=score,
                    handedness=handed_label,
                )
            )

        return detected

    def _recognize_gesture(self, landmarks, handed_label: str) -> GestureType:
        finger_states = self._extract_finger_states(landmarks, handed_label)
        extended_count = sum(finger_states.values())

        if extended_count == 0:
            return GestureType.FIST

        if extended_count == 5:
            return GestureType.OPEN_HAND

        index_up = finger_states.get("index", False)
        middle_up = finger_states.get("middle", False)
        thumb_up = finger_states.get("thumb", False)

        if extended_count == 1 and index_up:
            return GestureType.POINTING

        if extended_count == 1 and thumb_up:
            return GestureType.THUMBS_UP

        if extended_count == 2 and index_up and middle_up:
            return GestureType.PEACE

        return GestureType.UNKNOWN

    def _extract_finger_states(self, landmarks, handed_label: str) -> dict:
        mp_hl = self._mp_hands.HandLandmark
        fingers = {
            "index": self._is_finger_extended(landmarks, mp_hl.INDEX_FINGER_TIP, mp_hl.INDEX_FINGER_PIP),
            "middle": self._is_finger_extended(landmarks, mp_hl.MIDDLE_FINGER_TIP, mp_hl.MIDDLE_FINGER_PIP),
            "ring": self._is_finger_extended(landmarks, mp_hl.RING_FINGER_TIP, mp_hl.RING_FINGER_PIP),
            "pinky": self._is_finger_extended(landmarks, mp_hl.PINKY_TIP, mp_hl.PINKY_PIP),
        }
        fingers["thumb"] = self._is_thumb_extended(landmarks, handed_label)
        return fingers

    @staticmethod
    def _is_finger_extended(landmarks, tip_idx, pip_idx, threshold: float = 0.02) -> bool:
        tip = landmarks.landmark[tip_idx]
        pip = landmarks.landmark[pip_idx]
        return (pip.y - tip.y) > threshold

    @staticmethod
    def _is_thumb_extended(landmarks, handed_label: str, threshold: float = 0.02) -> bool:
        mp_hl = mp.solutions.hands.HandLandmark
        tip = landmarks.landmark[mp_hl.THUMB_TIP]
        mcp = landmarks.landmark[mp_hl.THUMB_MCP]

        if handed_label.lower() == "right":
            return (mcp.x - tip.x) > threshold
        if handed_label.lower() == "left":
            return (tip.x - mcp.x) > threshold
        # fallback: compara distância ao punho
        wrist = landmarks.landmark[mp_hl.WRIST]
        return abs(tip.x - wrist.x) > abs(mcp.x - wrist.x) + threshold

    def close(self) -> None:
        self._hands.close()

    def __del__(self) -> None:  # pragma: no cover - segurança extra
        try:
            self.close()
        except Exception:
            pass
