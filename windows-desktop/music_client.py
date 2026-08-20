"""Optional music search and playback adapter.

The endpoints are configurable and are not called automatically. Playback must be
initiated by an explicit user command and should use a user-selected player or
approved local playback mechanism.
"""

from __future__ import annotations

from dataclasses import dataclass
from urllib.parse import quote

import requests


@dataclass
class MusicResult:
    title: str
    song_id: str
    source_url: str = ""


class BhariyaMusicClient:
    def __init__(self, base_url: str, timeout: float = 12.0):
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout

    def prepare(self, song_name_or_url: str) -> dict:
        url = f"{self.base_url}/music/api/prepare/{quote(song_name_or_url, safe='') }"
        response = requests.get(url, timeout=self.timeout)
        response.raise_for_status()
        return response.json()

    def fetch(self, song_id: str) -> dict:
        url = f"{self.base_url}/music/api/fetch/{quote(song_id, safe='') }"
        response = requests.get(url, timeout=self.timeout)
        response.raise_for_status()
        return response.json()

    def audio_url(self, song_id: str) -> str:
        return f"{self.base_url}/music/api/audio/{quote(song_id, safe='')}"
