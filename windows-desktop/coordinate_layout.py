"""Lightweight, local-only coordinate metadata for Arthur's Spatial Workspace.

The module intentionally returns JSON-ready dictionaries but never creates a
server, socket, desktop-automation action, or device connection. A future
approved adapter may consume this contract after its own consent and security
checks have passed.
"""

from dataclasses import asdict, dataclass
from typing import Iterable


COORDINATE_SCHEMA = "arthur.coordinate.v1"
TRANSPORT_STATE = "closed"


@dataclass(frozen=True)
class SpatialCoordinate:
    """A visual placement measured in workspace-relative, not screen, units."""

    x: int
    y: int
    z: int
    zone: str


# Supporting modules get stable, non-screen-specific offsets. The selected
# module always moves into the focus zone, so visual priority never depends on
# unrequested Windows window control.
_SUPPORTING_COORDINATES = {
    "System diagnostics": SpatialCoordinate(-72, -8, 40, "periphery"),
    "Private note": SpatialCoordinate(72, 8, 40, "periphery"),
    "Voice signal": SpatialCoordinate(-64, 58, 35, "periphery"),
    "Smart-home review": SpatialCoordinate(0, -70, 10, "ambient"),
}
_DEFAULT_PERIPHERY = SpatialCoordinate(64, -36, 35, "periphery")
_FOCUS_COORDINATE = SpatialCoordinate(0, 0, 300, "focus")


def coordinate_for(label: str, focused_label: str) -> SpatialCoordinate:
    """Return the zone and X/Y/Z metadata for one visible Arthur module."""
    if label == focused_label:
        return _FOCUS_COORDINATE
    return _SUPPORTING_COORDINATES.get(label, _DEFAULT_PERIPHERY)


def coordinate_snapshot(
    labels: Iterable[str],
    focused_label: str,
    revision: int,
    event: str,
) -> dict:
    """Build a bounded local revision suitable for a later *opt-in* relay.

    ``transport`` is deliberately pinned to ``closed``. Serialising this object
    does not transmit it; it merely lets the browser and desktop render the
    same reviewable spatial state.
    """
    visible = [str(label) for label in labels]
    modules = [
        {"id": label.lower().replace(" ", "-"), "label": label, "coordinate": asdict(coordinate_for(label, focused_label))}
        for label in visible
    ]
    return {
        "schema": COORDINATE_SCHEMA,
        "transport": TRANSPORT_STATE,
        "revision": max(0, int(revision)),
        "actor": "local-user",
        "event": str(event),
        "focused_module": focused_label if focused_label in visible else "",
        "modules": modules,
    }


def zone_members(snapshot: dict, zone: str) -> list[str]:
    """Read one reviewable priority zone from a coordinate snapshot."""
    return [
        str(module["label"])
        for module in snapshot.get("modules", [])
        if isinstance(module, dict) and module.get("coordinate", {}).get("zone") == zone
    ]
