"""Consent-first specifications for Arthur's future multimodal adapters.

These are deliberately declarative. They do not enumerate devices, request a
Windows permission, open a microphone/camera/screen stream, or contact a
provider. The installed application must obtain fresh user approval before an
adapter becomes eligible for a separate runtime implementation.
"""

from dataclasses import asdict, dataclass


@dataclass(frozen=True)
class AdapterSpec:
    identifier: str
    label: str
    input_kind: str
    default_state: str
    transport: str
    activation_requirement: str
    credential_requirement: str


ADAPTERS = (
    AdapterSpec(
        "speech_stream",
        "Speech-to-text and text-to-speech pipeline",
        "microphone / speaker",
        "disabled",
        "closed",
        "Select a route, approve microphone or speech-output use, and approve the chosen local engine or provider connection.",
        "No key for a local engine; a developer-owned provider key is required only for an approved provider route.",
    ),
    AdapterSpec(
        "vision_matrix",
        "Local camera vision matrix",
        "camera frames",
        "disabled",
        "closed",
        "Unlock the Spatial Room, select a camera, approve a visible local camera session, then start a time-bounded session.",
        "No key for a local-only adapter; a developer-owned key is required only before an approved external vision provider receives selected data.",
    ),
    AdapterSpec(
        "screen_share",
        "Explicit screen or window share",
        "selected display or window",
        "disabled",
        "closed",
        "Choose the exact display or window in the operating-system picker for each session and review the sharing boundary.",
        "No key for local capture; a developer-owned key is required only before approved external analysis.",
    ),
    AdapterSpec(
        "coordinate_stream",
        "Local coordinate revision relay",
        "Arthur layout JSON",
        "disabled",
        "closed",
        "Approve a local listener port, trusted client list, session lifetime, and local firewall boundary before a separate relay starts.",
        "No API key for a local listener; an authenticated relay credential is required before any remote synchronization.",
    ),
)


def list_adapter_contracts() -> list[dict]:
    """Return JSON-ready disabled adapter descriptions for UI and tests."""
    return [asdict(adapter) for adapter in ADAPTERS]


def adapter_contract(identifier: str) -> dict | None:
    """Return one non-activating adapter contract when it is declared."""
    return next((asdict(adapter) for adapter in ADAPTERS if adapter.identifier == identifier), None)
