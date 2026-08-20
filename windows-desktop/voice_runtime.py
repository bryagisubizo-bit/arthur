"""Local, consent-first speech and wake-word diagnostics for Arthur.

This module never starts microphone capture by itself. It gives the desktop UI
small, observable checks so users can tell whether text-to-speech, microphone
access, and a selected openWakeWord model are ready before enabling listening.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Optional


SUPPORTED_WAKE_MODEL_SUFFIXES = {".onnx", ".tflite"}


@dataclass(frozen=True)
class DiagnosticResult:
    ready: bool
    headline: str
    detail: str


def diagnose_wake_word(model_path: str = "") -> DiagnosticResult:
    """Report the local prerequisites without opening the microphone."""
    try:
        import openwakeword  # noqa: F401
        import sounddevice  # noqa: F401
    except ImportError:
        return DiagnosticResult(
            False,
            "Wake-word packages are unavailable",
            "Install openWakeWord and sounddevice in Arthur's active Python environment, then restart Arthur.",
        )

    if not model_path.strip():
        return DiagnosticResult(
            False,
            "Select a verified wake-word model",
            "Installation alone does not create an Arthur model. Choose a local .onnx or .tflite model, then run a microphone check.",
        )

    path = Path(model_path).expanduser()
    if not path.is_file() or path.suffix.casefold() not in SUPPORTED_WAKE_MODEL_SUFFIXES:
        return DiagnosticResult(
            False,
            "Wake-word model is unavailable",
            "Choose an existing verified .onnx or .tflite wake-word model. On Windows, prefer the ONNX model format supplied by openWakeWord. Arthur will not start listening until one is selected.",
        )

    return DiagnosticResult(
        True,
        "Wake-word prerequisites are ready",
        "A verified local Arthur model is selected. Listening still requires a separate microphone permission, input-device check, and activation choice.",
    )


def available_input_devices() -> list[tuple[int, str]]:
    """List local input devices without opening, recording, or sending microphone audio."""
    try:
        import sounddevice as sd
    except ImportError:
        return []
    try:
        devices = sd.query_devices()
    except Exception:
        return []
    return [
        (index, str(device.get("name", f"Input {index}")))
        for index, device in enumerate(devices)
        if int(device.get("max_input_channels", 0)) > 0
    ]


def microphone_readiness(device: int | None = None) -> DiagnosticResult:
    """Check an explicitly selected local input device without opening or recording it."""
    try:
        import sounddevice as sd
    except ImportError:
        return DiagnosticResult(
            False,
            "Microphone support is unavailable",
            "Install sounddevice in Arthur's active Python environment, then restart Arthur. No microphone was opened.",
        )
    try:
        selected = sd.query_devices(device=device, kind="input")
    except Exception as exc:  # pragma: no cover - Windows drivers vary
        return DiagnosticResult(
            False,
            "Selected microphone is unavailable",
            f"Choose an available Windows input device and allow desktop microphone access. No audio was opened or saved. Detail: {exc}",
        )
    if int(selected.get("max_input_channels", 0)) < 1:
        return DiagnosticResult(
            False,
            "Selected device cannot capture input",
            "Choose a microphone or headset input in Arthur, then run the one-time activity test. No audio was opened or saved.",
        )
    return DiagnosticResult(
        True,
        "Selected microphone is ready to test",
        "Arthur identified the selected local input device. Use the separate three-second test to confirm activity; no audio has been opened, stored, or sent.",
    )


def _microphone_activity_sample(duration_seconds: float, device: int | None = None) -> float:
    """Capture a short, in-memory signal solely to measure local input activity."""
    import sounddevice as sd

    selected = sd.query_devices(device=device, kind="input")
    sample_rate = max(8_000, int(float(selected.get("default_samplerate", 16_000))))
    frame_count = max(1, int(sample_rate * duration_seconds))
    frames = sd.rec(frame_count, samplerate=sample_rate, channels=1, dtype="float32", device=device, blocking=True)
    return float(abs(frames).max())


def test_microphone_activity(duration_seconds: float = 3.0, device: int | None = None) -> DiagnosticResult:
    """Run an explicit short input check without saving, transcribing, or uploading audio."""
    duration = max(1.0, min(float(duration_seconds), 5.0))
    try:
        peak = _microphone_activity_sample(duration, device=device)
    except ImportError:
        return DiagnosticResult(
            False,
            "Microphone activity test is unavailable",
            "Install sounddevice in Arthur's active Python environment, then restart Arthur. No microphone was opened.",
        )
    except Exception as exc:  # pragma: no cover - hardware and Windows drivers vary
        return DiagnosticResult(
            False,
            "Arthur could not read the selected microphone",
            f"Check Windows microphone permission, the selected input device, and its driver. No audio was saved. Detail: {exc}",
        )

    if peak >= 0.002:
        return DiagnosticResult(
            True,
            "Local microphone activity detected",
            "Arthur measured a short local input level and immediately discarded it. This did not record, transcribe, retain, or upload speech.",
        )
    return DiagnosticResult(
        False,
        "No local microphone activity was detected",
        "Arthur opened the selected input only for this short test and discarded it. Check mute, volume, and Windows microphone permission; no speech was retained or sent.",
    )


class VoiceRuntime:
    """Best-effort local TTS wrapper with no cloud dependency or background work."""

    def __init__(self):
        self._engine = None
        self._voice_id = ""
        self._rate = 175
        self._volume = 1.0
        self._pitch = 0

    def available_voices(self) -> list[tuple[str, str]]:
        """List locally installed speech voices without storing biometric information."""
        status = self.diagnose_speech()
        if not status.ready:
            return []
        try:
            import pyttsx3

            engine = self._engine or pyttsx3.init()
            voices = engine.getProperty("voices") or []
            return [(str(getattr(voice, "id", "")), str(getattr(voice, "name", "Local Windows voice"))) for voice in voices]
        except Exception:
            return []

    def configure(self, *, voice_id: str = "", rate: int = 175, volume: float = 1.0, pitch: int = 0) -> None:
        """Save local rendering preferences; pitch remains best-effort because SAPI voices vary."""
        self._voice_id = voice_id.strip()
        self._rate = max(100, min(int(rate), 260))
        self._volume = max(0.0, min(float(volume), 1.0))
        self._pitch = max(-10, min(int(pitch), 10))

    def diagnose_speech(self) -> DiagnosticResult:
        try:
            import pyttsx3  # noqa: F401
        except ImportError:
            return DiagnosticResult(
                False,
                "Windows voice runtime is unavailable",
                "Install the local pyttsx3 package in Arthur's environment, then restart Arthur.",
            )
        return DiagnosticResult(
            True,
            "Local Windows voice is ready",
            "Arthur can test a short local acknowledgement without sending text or audio to a cloud provider.",
        )

    def speak(self, text: str) -> DiagnosticResult:
        status = self.diagnose_speech()
        if not status.ready:
            return status
        try:
            import pyttsx3

            if self._engine is None:
                self._engine = pyttsx3.init()
            self._engine.setProperty("rate", self._rate)
            self._engine.setProperty("volume", self._volume)
            if self._voice_id:
                self._engine.setProperty("voice", self._voice_id)
            # pyttsx3 does not expose a portable pitch property. Some SAPI voice
            # engines accept it, while others ignore it; failure must not block speech.
            if self._pitch:
                try:
                    self._engine.setProperty("pitch", self._pitch)
                except Exception:
                    pass
            self._engine.say(text)
            self._engine.runAndWait()
            return DiagnosticResult(True, "Arthur spoke locally", "The acknowledgement used the local Windows speech engine.")
        except Exception as exc:  # pragma: no cover - platform voice drivers vary
            return DiagnosticResult(False, "Arthur could not use the selected Windows voice", str(exc))
