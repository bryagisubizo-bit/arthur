"""Consent-aware speech-output route descriptions for Arthur's local Voice Studio.

This module does not synthesize audio, download models, connect a provider, or record audio.
It makes the engine path explicit before voice_runtime performs any separately approved output.
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class VoiceSynthesisRoute:
    key: str
    label: str
    detail: str
    boundary: str


ROUTES = {
    "local_windows_tts": VoiceSynthesisRoute(
        "local_windows_tts",
        "Local Windows speech engine",
        "Approved reply text is sent to the installed local speech engine.",
        "No neural voice model is downloaded and the microphone is not started.",
    ),
    "developer_neural_tts": VoiceSynthesisRoute(
        "developer_neural_tts",
        "Developer-configured neural voice provider",
        "A separately tested provider may synthesize approved reply text.",
        "Selecting this route does not connect a provider or transmit text.",
    ),
}


def describe_route(key: str | None) -> VoiceSynthesisRoute | None:
    """Return a known route only; callers must not infer a safe fallback."""
    return ROUTES.get(key or "")
