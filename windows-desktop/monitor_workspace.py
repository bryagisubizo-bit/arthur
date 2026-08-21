"""Explicitly approved Windows monitor mapping and reversible placement helpers.

This module is deliberately dormant until Arthur's user opens the Spatial
Workspace, unlocks it, requests a monitor refresh, selects a numeric process
identifier, previews the target rectangle, and confirms one move.  It has no
background loop, cloud client, clipboard reader, screen capture, process
launcher, or automatic window movement.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Callable, Iterable, Mapping


MONITOR_SCHEMA = "arthur.monitor-map.v1"
PLACEMENT_SCHEMA = "arthur.window-placement.v1"
LOW_RESOURCE_POLICY = {
    "polling": "manual-only",
    "cpu_soft_limit_percent": 65,
    "memory_soft_limit_percent": 75,
    "cloud_transport": "closed",
}


@dataclass(frozen=True)
class MonitorRect:
    """One locally observed desktop rectangle, without a screen capture."""

    id: str
    label: str
    x: int
    y: int
    width: int
    height: int
    primary: bool = False


def discover_monitors(enumerator: Callable[[], Iterable[object]] | None = None) -> list[dict]:
    """Return a one-time local monitor map only when called by a visible review action."""
    if enumerator is None:
        try:
            from screeninfo import get_monitors  # type: ignore
        except ImportError:
            return []
        enumerator = get_monitors

    monitors: list[dict] = []
    for index, monitor in enumerate(enumerator()):
        x = int(getattr(monitor, "x", 0))
        y = int(getattr(monitor, "y", 0))
        width = int(getattr(monitor, "width", 0))
        height = int(getattr(monitor, "height", 0))
        if width <= 0 or height <= 0:
            continue
        label = str(getattr(monitor, "name", "") or f"Display {index + 1}")
        monitors.append(
            asdict(
                MonitorRect(
                    id=f"display-{index + 1}",
                    label=label,
                    x=x,
                    y=y,
                    width=width,
                    height=height,
                    primary=bool(getattr(monitor, "is_primary", False)),
                )
            )
        )
    return monitors


def monitor_snapshot(monitors: Iterable[Mapping[str, object]]) -> dict:
    """Serialize an observed map as local metadata, never image pixels or a transport message."""
    return {
        "schema": MONITOR_SCHEMA,
        "transport": "closed",
        "sample_mode": "manual-once",
        "monitors": [dict(monitor) for monitor in monitors],
    }


def resource_budget(cpu_percent: float | None = None, memory_percent: float | None = None) -> dict:
    """Return one bounded resource reading; callers must not schedule recurring sampling."""
    if cpu_percent is None or memory_percent is None:
        try:
            import psutil  # type: ignore

            cpu_percent = psutil.cpu_percent(interval=None) if cpu_percent is None else cpu_percent
            memory_percent = psutil.virtual_memory().percent if memory_percent is None else memory_percent
        except ImportError:
            return {**LOW_RESOURCE_POLICY, "state": "unknown", "detail": "Optional psutil is unavailable; Arthur will not sample resources continuously."}
    cpu = max(0.0, float(cpu_percent))
    memory = max(0.0, float(memory_percent))
    constrained = cpu >= LOW_RESOURCE_POLICY["cpu_soft_limit_percent"] or memory >= LOW_RESOURCE_POLICY["memory_soft_limit_percent"]
    return {
        **LOW_RESOURCE_POLICY,
        "state": "conserve" if constrained else "within-budget",
        "cpu_percent": cpu,
        "memory_percent": memory,
        "detail": "Reduce visual detail and defer optional cloud work." if constrained else "One local reading is within Arthur’s soft budget.",
    }


def placement_preview(process_id: int, monitor: Mapping[str, object]) -> dict:
    """Build a centered target rectangle only; no window lookup or movement occurs here."""
    pid = int(process_id)
    if pid <= 0:
        raise ValueError("A positive numeric process identifier is required.")
    width = int(monitor.get("width", 0))
    height = int(monitor.get("height", 0))
    if width <= 0 or height <= 0:
        raise ValueError("The selected monitor has no usable dimensions.")
    target_width = max(320, round(width * 0.72))
    target_height = max(240, round(height * 0.78))
    target_width = min(target_width, width)
    target_height = min(target_height, height)
    return {
        "schema": PLACEMENT_SCHEMA,
        "transport": "closed",
        "action": "preview-only",
        "requires_confirmation": True,
        "process_id": pid,
        "monitor_id": str(monitor.get("id", "")),
        "monitor_label": str(monitor.get("label", "Selected display")),
        "target": {
            "x": int(monitor.get("x", 0)) + (width - target_width) // 2,
            "y": int(monitor.get("y", 0)) + (height - target_height) // 2,
            "width": target_width,
            "height": target_height,
        },
    }


def apply_approved_placement(
    preview: Mapping[str, object],
    *,
    confirmed: bool,
    mover: Callable[[Mapping[str, object]], None] | None = None,
) -> dict:
    """Apply exactly one preview only after a caller has obtained explicit confirmation."""
    if not confirmed:
        return {"state": "not-applied", "detail": "No confirmation was provided; no window moved."}
    if preview.get("schema") != PLACEMENT_SCHEMA or preview.get("action") != "preview-only":
        return {"state": "not-applied", "detail": "The placement preview is invalid; no window moved."}
    if mover is None:
        return {"state": "adapter-missing", "detail": "pywin32 is not available; the approved preview was not applied."}
    mover(preview)
    return {"state": "applied", "detail": "One confirmed local placement was applied. Arthur did not create a background rule."}


def pywin32_mover(preview: Mapping[str, object]) -> None:
    """Use pywin32 only from a confirmed UI action; never call this from a timer or background worker."""
    import win32con  # type: ignore
    import win32gui  # type: ignore

    target = preview["target"]
    process_id = int(preview["process_id"])
    matches: list[int] = []

    def collect(handle: int, _unused: object) -> None:
        if win32gui.IsWindowVisible(handle):
            _thread_id, owner_pid = win32gui.GetWindowThreadProcessId(handle)
            if owner_pid == process_id:
                matches.append(handle)

    win32gui.EnumWindows(collect, None)
    if not matches:
        raise RuntimeError("No visible top-level window was found for that process identifier.")
    win32gui.SetWindowPos(
        matches[0],
        0,
        int(target["x"]),
        int(target["y"]),
        int(target["width"]),
        int(target["height"]),
        win32con.SWP_NOZORDER | win32con.SWP_SHOWWINDOW,
    )
