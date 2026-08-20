"""Optional local hand-gesture adapter for Arthur.

This module is deliberately disabled by default.  It uses a user-selected
camera only after the desktop UI has collected explicit consent.  Frames and
landmarks stay in process memory; this adapter does not write, upload, or
retain video, images, or biometric templates.
"""

from __future__ import annotations

import threading
import time
from dataclasses import dataclass
from typing import Callable, Optional


@dataclass(frozen=True)
class GestureEvent:
    name: str
    value: float = 0.0


def optional_dependency_status() -> tuple[bool, str]:
    try:
        import cv2  # noqa: F401
        import mediapipe  # noqa: F401
    except ImportError:
        return False, "Optional gesture packages are not installed. See requirements-gesture-optional.txt."
    return True, "Local camera gesture adapter is available."


class HandGestureClassifier:
    """Classifies a small, deliberate set of workspace-only gestures.

    Inputs are normalised hand-landmark points. The classifier does not
    identify a person and does not keep a history longer than the active
    listener session.
    """

    def __init__(self):
        self._previous_wrist_x: Optional[float] = None

    def classify(self, points: list[tuple[float, float]]) -> Optional[GestureEvent]:
        if len(points) < 21:
            return None
        wrist_x, wrist_y = points[0]
        thumb_x, thumb_y = points[4]
        index_x, index_y = points[8]
        middle_x, middle_y = points[12]
        index_knuckle_x, index_knuckle_y = points[5]
        open_palm = all(points[tip][1] < points[joint][1] - 0.10 for tip, joint in ((8, 6), (12, 10), (16, 14), (20, 18)))
        span = max((((middle_x - wrist_x) ** 2 + (middle_y - wrist_y) ** 2) ** 0.5), 0.001)
        pinch = (((thumb_x - index_x) ** 2 + (thumb_y - index_y) ** 2) ** 0.5) / span

        event: Optional[GestureEvent] = None
        if open_palm:
            event = GestureEvent("discard_request", 1.0)
        elif pinch < 0.34:
            event = GestureEvent("pinch", max(0.0, min(1.0, 1.0 - pinch)))
        elif index_y < index_knuckle_y - 0.16 and middle_y < wrist_y - 0.12:
            event = GestureEvent("select", 1.0)
        elif self._previous_wrist_x is not None:
            drift = wrist_x - self._previous_wrist_x
            if drift > 0.18:
                event = GestureEvent("swipe_right", drift)
            elif drift < -0.18:
                event = GestureEvent("swipe_left", abs(drift))
        self._previous_wrist_x = wrist_x
        return event


class GestureListener:
    """Runs an optional local camera loop and emits transient workspace gestures."""

    def __init__(self, on_event: Callable[[GestureEvent], None], on_status: Callable[[str], None], camera_index: int = 0):
        self.on_event = on_event
        self.on_status = on_status
        self.camera_index = camera_index
        self._thread: Optional[threading.Thread] = None
        self._stop = threading.Event()
        self._last_emitted = 0.0

    @property
    def running(self) -> bool:
        return self._thread is not None and self._thread.is_alive()

    def start(self) -> tuple[bool, str]:
        if self.running:
            return True, "Local gesture listener is already active."
        available, detail = optional_dependency_status()
        if not available:
            return False, detail
        self._stop.clear()
        self._thread = threading.Thread(target=self._run, daemon=True, name="arthur-local-gesture-listener")
        self._thread.start()
        return True, "Opening the selected local camera for transient hand tracking."

    def stop(self) -> None:
        self._stop.set()
        thread = self._thread
        if thread and thread.is_alive():
            thread.join(timeout=1.5)
        self._thread = None
        self.on_status("Local gesture camera stopped. No video or landmarks were retained.")

    def _emit(self, event: GestureEvent) -> None:
        now = time.monotonic()
        if now - self._last_emitted < 0.55:
            return
        self._last_emitted = now
        self.on_event(event)

    def _run(self) -> None:
        import cv2
        import mediapipe as mp

        capture = cv2.VideoCapture(self.camera_index)
        if not capture.isOpened():
            self.on_status("Arthur could not open the selected local camera. Check Windows camera permission and try again.")
            return
        classifier = HandGestureClassifier()
        hands_api = mp.solutions.hands
        self.on_status("Camera active locally. Arthur is processing transient hand landmarks only.")
        try:
            with hands_api.Hands(static_image_mode=False, max_num_hands=1, min_detection_confidence=0.7, min_tracking_confidence=0.65) as hands:
                while not self._stop.is_set():
                    ok, frame = capture.read()
                    if not ok:
                        self.on_status("Local gesture camera frame was unavailable; listener stopped.")
                        break
                    result = hands.process(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))
                    if not result.multi_hand_landmarks:
                        continue
                    landmarks = result.multi_hand_landmarks[0].landmark
                    event = classifier.classify([(point.x, point.y) for point in landmarks])
                    if event:
                        self._emit(event)
        except Exception as error:  # Optional device integration; report safely to the UI.
            self.on_status(f"Local gesture listener stopped: {error}")
        finally:
            capture.release()
