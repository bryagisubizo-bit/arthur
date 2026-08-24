"""Local API Vault resolution for Arthur's desktop capability rooms.

The layer keeps provider configuration shareable within Arthur without exposing
credentials to feature pages. Actual outbound requests remain owned by each
feature's reviewed adapter and must retain that feature's approval boundary.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Mapping


API_LAYER_ROOM = "API Layer"
LOCAL_PROVIDERS = {
    "Disabled",
    "Home Assistant",
    "Local detector",
    "Local music files",
    "Local singing model",
    "Local Whisper",
    "Windows Voice",
}


@dataclass(frozen=True)
class ApiLayerStatus:
    """A redacted readiness view intended for feature pages and the UI."""

    ready: bool
    provider: str
    endpoint: str
    shared_rooms: tuple[str, ...]
    detail: str


@dataclass(frozen=True)
class ApiRoomResolution:
    """A resolved, credential-free route for a capability room."""

    room: str
    ready: bool
    provider: str
    endpoint: str
    credential_room: str
    inherited_from_api_layer: bool
    detail: str


def _record(config: Mapping[str, Any], room: str) -> Mapping[str, Any]:
    integrations = config.get("integrations", {})
    candidate = integrations.get(room, {}) if isinstance(integrations, Mapping) else {}
    return candidate if isinstance(candidate, Mapping) else {}


def _provider_requires_key(provider: str) -> bool:
    return bool(provider) and provider not in {"Select provider", *LOCAL_PROVIDERS}


def _room_is_ready(record: Mapping[str, Any]) -> bool:
    provider = str(record.get("provider", "")).strip()
    if not bool(record.get("enabled", False)) or provider == "Select provider" or not provider:
        return False
    return not _provider_requires_key(provider) or bool(record.get("api_key_present", False))


def api_layer_status(config: Mapping[str, Any]) -> ApiLayerStatus:
    """Return the API-layer readiness state without reading or returning a key."""

    layer = _record(config, API_LAYER_ROOM)
    provider = str(layer.get("provider", "")).strip()
    endpoint = str(layer.get("endpoint", "")).strip()
    integrations = config.get("integrations", {})
    shared_rooms = tuple(
        name
        for name, record in (integrations.items() if isinstance(integrations, Mapping) else ())
        if name != API_LAYER_ROOM and isinstance(record, Mapping) and bool(record.get("use_api_layer", False))
    )
    if not _room_is_ready(layer):
        return ApiLayerStatus(
            ready=False,
            provider=provider,
            endpoint=endpoint,
            shared_rooms=shared_rooms,
            detail="Configure, enable, and save the API Layer room before shared capability rooms can use it.",
        )
    return ApiLayerStatus(
        ready=True,
        provider=provider,
        endpoint=endpoint,
        shared_rooms=shared_rooms,
        detail="The shared API Layer is configured locally. Individual features still decide when an approved adapter may make a request.",
    )


def resolve_api_room(config: Mapping[str, Any], room: str) -> ApiRoomResolution:
    """Resolve a room's direct or inherited provider route without returning secrets."""

    record = _record(config, room)
    provider = str(record.get("provider", "")).strip()
    endpoint = str(record.get("endpoint", "")).strip()
    if bool(record.get("use_api_layer", False)) and room != API_LAYER_ROOM:
        layer = api_layer_status(config)
        if not layer.ready:
            return ApiRoomResolution(
                room=room,
                ready=False,
                provider=provider or layer.provider,
                endpoint=layer.endpoint,
                credential_room=API_LAYER_ROOM,
                inherited_from_api_layer=True,
                detail=f"{room} is set to use the API Layer, but the shared layer is not ready.",
            )
        return ApiRoomResolution(
            room=room,
            ready=True,
            provider=provider or layer.provider,
            endpoint=layer.endpoint,
            credential_room=API_LAYER_ROOM,
            inherited_from_api_layer=True,
            detail=f"{room} inherits the API Layer connection. Credentials remain in the operating-system credential manager.",
        )
    ready = _room_is_ready(record)
    return ApiRoomResolution(
        room=room,
        ready=ready,
        provider=provider,
        endpoint=endpoint,
        credential_room=room,
        inherited_from_api_layer=False,
        detail=(
            f"{room} has a saved direct provider route."
            if ready
            else f"{room} needs an enabled provider and, where required, a saved credential."
        ),
    )
