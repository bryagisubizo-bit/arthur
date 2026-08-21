"""Cloud-assisted operating-model contracts for Arthur.

This module is deliberately declarative: it validates an eventual gateway
proposal but never opens a network connection, reads a secret, or sends data.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass
from urllib.parse import urlparse


GATEWAY_SCHEMA = "arthur.cloud-gateway.v1"
DEFAULT_RESOURCE_POLICY = {
    "desktop_target": "Windows 11 · 8 GB RAM · 2.4 GHz CPU",
    "local_work": "Consent, native layout, bounded manual monitor mapping, and display-only state.",
    "cloud_work": "Approved text or selected metadata sent through a developer-configured HTTPS gateway.",
    "transport_default": "closed",
    "streaming_default": "off",
    "polling": "No background polling. Manual checks use exponential backoff in a future approved client.",
}


@dataclass(frozen=True)
class CloudGatewayProposal:
    provider_label: str
    endpoint: str
    credential_reference: str
    approved_data_classes: tuple[str, ...]
    streaming_requested: bool
    transport_state: str = "closed"

    def as_dict(self) -> dict:
        return asdict(self)


def validate_https_endpoint(endpoint: str) -> tuple[bool, str]:
    """Accept only an explicit HTTPS endpoint; no request is performed."""
    candidate = str(endpoint or "").strip()
    if not candidate:
        return False, "An explicit HTTPS gateway URL is required before a connection can be reviewed."
    parsed = urlparse(candidate)
    if parsed.scheme != "https" or not parsed.netloc:
        return False, "Arthur accepts HTTPS gateway URLs only; loopback and WebSocket transport require a separate approved design."
    return True, "HTTPS endpoint format is suitable for a later, separate connection review."


def create_gateway_proposal(
    provider_label: str,
    endpoint: str,
    credential_reference: str = "OS credential manager reference (not stored in Arthur settings)",
    approved_data_classes: tuple[str, ...] = (),
    streaming_requested: bool = False,
) -> CloudGatewayProposal:
    ok, detail = validate_https_endpoint(endpoint)
    if not ok:
        raise ValueError(detail)
    return CloudGatewayProposal(
        provider_label=str(provider_label or "Developer-configured provider").strip(),
        endpoint=str(endpoint).strip(),
        credential_reference=credential_reference,
        approved_data_classes=tuple(approved_data_classes),
        streaming_requested=bool(streaming_requested),
    )


def gateway_status(config: dict | None = None) -> str:
    settings = (config or {}).get("cloud_gateway", {})
    endpoint = str(settings.get("endpoint", "")).strip()
    if not endpoint:
        return "Closed. No cloud gateway URL or credential reference is configured; Arthur remains local-only."
    ok, _detail = validate_https_endpoint(endpoint)
    if not ok:
        return "Blocked. The saved gateway format is not HTTPS; Arthur will not connect."
    return "Prepared only. A gateway URL is recorded, but no credential, user content approval, request, stream, or connection is active."


def review_text() -> str:
    return (
        "Cloud assistance is optional. Local Arthur work remains consent, display layout, and bounded manual monitor mapping.\n\n"
        "Before any cloud request: choose one HTTPS endpoint, store a developer-owned API key or OAuth token in the OS credential manager, specify exact approved data classes, and approve each connection scope.\n\n"
        "Streaming is off by default. A future stream needs its own named client, session duration, reconnect/backoff policy, and stop control. This review does not contact a provider or expose data."
    )
