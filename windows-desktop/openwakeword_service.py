"""Optional local wake-word listener for Arthur.

This module is deliberately disabled until the developer enables it. It does not
send microphone audio to a cloud provider. A production build should select and
ship a verified wake-word model, expose a mute switch, and keep the listener
stopped until the user grants microphone permission.
"""

from __future__ import annotations

from pathlib import Path
from time import monotonic
from typing import Callable, Optional


class WakeWordListener:
    def __init__(self, model_path: Optional[str] = None, wake_word: str = "Arthur", input_device: Optional[int] = None):
        self.model_path = Path(model_path) if model_path else None
        self.wake_word = wake_word
        self.input_device = input_device
        self.running = False
        self.on_detected: Optional[Callable[[str], None]] = None
        self.on_audio_level: Optional[Callable[[float], None]] = None
        self.on_error: Optional[Callable[[str], None]] = None
        self._stream = None
        self._model = None
        self._last_detection = 0.0
        self._suspended_until = 0.0
        self._last_error = ""

    def suspend_detection(self, seconds: float) -> None:
        """Ignore wake predictions briefly while Arthur is speaking, then resume automatically."""
        self._suspended_until = max(self._suspended_until, monotonic() + max(0.0, float(seconds)))

    def _report_error(self, message: str) -> None:
        if message == self._last_error:
            return
        self._last_error = message
        if self.on_error:
            self.on_error(message)

    def start(self) -> None:
        if self.running:
            return
        try:
            from openwakeword.model import Model
            import sounddevice as sd
        except ImportError as exc:
            raise RuntimeError(
                "Install openwakeword and sounddevice before enabling local wake-word listening."
            ) from exc

        model_kwargs = {}
        if self.model_path and self.model_path.exists():
            model_kwargs["wakeword_models"] = [str(self.model_path)]
        self._model = Model(**model_kwargs)

        def callback(indata, frames, time_info, status):
            del frames, time_info
            if self._model is None:
                return
            try:
                if status:
                    self._report_error(f"Microphone stream status: {status}")
                if self.on_audio_level:
                    # Transient amplitude only: no audio buffer, recording, or upload.
                    self.on_audio_level(min(1.0, float(abs(indata[:, 0]).max()) / 32768.0))
                if monotonic() < self._suspended_until:
                    return
                scores = self._model.predict(indata[:, 0])
                now = monotonic()
                if scores and max(scores.values()) >= 0.75 and now - self._last_detection >= 1.5:
                    self._last_detection = now
                    if self.on_detected:
                        self.on_detected(self.wake_word)
            except Exception as exc:
                # Audio callbacks must not crash the desktop process, but a user
                # should see a concise diagnostic instead of a silent failure.
                self._report_error(f"Wake-word processing error: {exc}")
                return

        self._stream = sd.InputStream(
            samplerate=16000,
            channels=1,
            dtype="int16",
            device=self.input_device,
            callback=callback,
            blocksize=1280,
        )
        self._stream.start()
        self.running = True

    def stop(self) -> None:
        if self._stream is not None:
            self._stream.stop()
            self._stream.close()
        self._stream = None
        self._model = None
        self.running = False
