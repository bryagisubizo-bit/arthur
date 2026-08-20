"""Safe import of Arthur's optional-capability choices made in the installer.

The Inno Setup wizard writes a small JSON record to the current user's AppData
folder.  It records intent only: Windows remains responsible for microphone,
camera, notification, and startup permissions, and Arthur never starts
listening merely because this record exists.
"""

from __future__ import annotations

import json
from copy import deepcopy
from pathlib import Path
from typing import Any


CONSENT_KEYS = (
    "microphone_wake_word",
    "camera_features",
    "background_ready",
    "network_provider_setup",
    "reviewed_pc_actions",
)

SPATIAL_PROTECTION_METHODS = (
    "password",
    "windows_hello",
    "local_camera_face",
)


def normalise_installer_consent(payload: Any) -> dict[str, bool | str]:
    """Keep only known consent keys and one installer-selected room method."""
    source = payload if isinstance(payload, dict) else {}
    normalised: dict[str, bool | str] = {key: bool(source.get(key, False)) for key in CONSENT_KEYS}
    selected = source.get("spatial_room_protection", "")
    normalised["spatial_room_protection"] = selected if selected in SPATIAL_PROTECTION_METHODS else ""
    return normalised


def load_installer_consent(path: Path) -> dict[str, bool | str]:
    """Load the installer record defensively; malformed files mean no consent."""
    try:
        return normalise_installer_consent(json.loads(path.read_text(encoding="utf-8")))
    except (OSError, TypeError, ValueError, json.JSONDecodeError):
        return normalise_installer_consent({})


def apply_installer_defaults(config: dict[str, Any], consent: dict[str, bool | str]) -> dict[str, Any]:
    """Apply intent as visible local defaults without granting OS permissions."""
    updated = deepcopy(config)
    choices = normalise_installer_consent(consent)
    updated["installer_permissions"] = choices

    voice = updated.setdefault("voice", {})
    autonomy = updated.setdefault("autonomy", {})
    privacy = updated.setdefault("privacy", {})
    integrations = updated.setdefault("integrations", {})
    interaction = updated.setdefault("interaction", {})

    # A microphone choice only permits Arthur to offer the user-controlled
    # wake-word setup.  It never starts the listener and cannot bypass Windows.
    voice["wake_word_listener_approved"] = choices["microphone_wake_word"]
    autonomy["local_listening"] = False
    privacy["wake_word_background_enabled"] = False

    # Background-ready is a UI preference, not Windows login/startup permission.
    autonomy["background_ready"] = choices["background_ready"]

    # Network choice only enables provider setup screens; it never calls a provider.
    integrations["network_provider_setup_approved"] = choices["network_provider_setup"]

    # This is deliberately not the active access method. A password still needs
    # to be created, Windows Hello still needs Windows verification, and local
    # camera access still needs separate visible enrolment. Arthur uses it only
    # to take the user to the selected setup flow on the first room entry.
    interaction["installer_spatial_room_protection"] = choices["spatial_room_protection"]

    # Camera and PC-control choices remain informational until their separate,
    # in-app consent flows are completed.
    return updated
