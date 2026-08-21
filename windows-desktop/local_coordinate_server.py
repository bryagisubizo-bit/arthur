"""Optional coordinate-stream protocol foundation; no server starts on import.

The standard-library portion creates bounded JSON messages. The WebSocket entry
point remains intentionally unavailable until a future user-approved runtime
adapter supplies an explicit loopback binding, port, client allow-list, and
session duration.
"""

import json
from dataclasses import asdict, dataclass

from coordinate_layout import COORDINATE_SCHEMA, TRANSPORT_STATE


@dataclass(frozen=True)
class LocalCoordinateServerConfig:
    host: str = "127.0.0.1"
    port: int = 8765
    transport: str = TRANSPORT_STATE
    approved: bool = False


def coordinate_message(snapshot: dict) -> str:
    """Encode only a closed-transport coordinate revision for a future relay."""
    if snapshot.get("schema") != COORDINATE_SCHEMA or snapshot.get("transport") != TRANSPORT_STATE:
        raise ValueError("Only Arthur's closed local coordinate revisions may be prepared.")
    return json.dumps({"type": "arthur.coordinate.revision", "payload": snapshot}, separators=(",", ":"), sort_keys=True)


def websocket_startup_contract(config: LocalCoordinateServerConfig) -> dict:
    """Return a reviewable startup contract; never bind a port or start a server."""
    if config.host not in {"127.0.0.1", "localhost"}:
        raise ValueError("A future local coordinate relay must start loopback-only; remote binding is not supported by this foundation.")
    if not 1024 <= int(config.port) <= 65535:
        raise ValueError("Choose a non-privileged local port between 1024 and 65535.")
    return {
        "config": asdict(config),
        "state": "approval_required" if not config.approved else "runtime_adapter_required",
        "action": "no_listener_started",
        "requirements": ["fresh user consent", "named local client", "bounded session duration", "firewall review"],
    }
