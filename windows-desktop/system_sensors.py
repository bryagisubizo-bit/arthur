"""Local hardware diagnostics for Arthur's consent-controlled Sensor workspace.

The collector has no network client, does not retain readings, and never
installs or starts a third-party hardware-monitoring service. Windows exposes
some thermal zones inconsistently; unavailable is an honest supported result.
"""

from __future__ import annotations

import json
import os
import subprocess
import sys
from typing import Callable

try:
    import psutil as imported_psutil
except ImportError:  # pragma: no cover - covered through dependency injection
    imported_psutil = None


Reading = dict[str, str]
Snapshot = dict[str, Reading]
_DEFAULT_PSUTIL = object()


def _unavailable(detail: str) -> Reading:
    return {"value": "Unavailable", "detail": detail, "state": "unavailable"}


def _available(value: str, detail: str) -> Reading:
    return {"value": value, "detail": detail, "state": "available"}


def _windows_thermal_zones() -> list[tuple[str, float]]:
    """Read Windows ACPI thermal zones when the OS exposes them.

    This fixed local query has no user-controlled input, opens no network
    connection, and is intentionally not a substitute for CPU/GPU telemetry.
    """
    if os.name != "nt":
        return []
    command = (
        "$ErrorActionPreference='Stop'; "
        "Get-CimInstance -Namespace root/WMI -ClassName MSAcpi_ThermalZoneTemperature "
        "| Select-Object InstanceName,CurrentTemperature | ConvertTo-Json -Compress"
    )
    try:
        result = subprocess.run(
            ["powershell.exe", "-NoProfile", "-NonInteractive", "-Command", command],
            capture_output=True,
            check=False,
            text=True,
            timeout=4,
            creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0),
        )
        if result.returncode != 0 or not result.stdout.strip():
            return []
        rows = json.loads(result.stdout)
        if isinstance(rows, dict):
            rows = [rows]
        readings: list[tuple[str, float]] = []
        for row in rows if isinstance(rows, list) else []:
            raw = row.get("CurrentTemperature") if isinstance(row, dict) else None
            try:
                celsius = (float(raw) - 2732.0) / 10.0
            except (TypeError, ValueError):
                continue
            if -40.0 <= celsius <= 150.0:
                readings.append((str(row.get("InstanceName") or "ACPI thermal zone"), celsius))
        return readings
    except (OSError, ValueError, subprocess.SubprocessError, json.JSONDecodeError):
        return []


def _psutil_temperatures(module) -> list[tuple[str, float]]:
    try:
        groups = getattr(module, "sensors_temperatures", lambda: {})() or {}
    except (AttributeError, OSError):
        return []
    readings: list[tuple[str, float]] = []
    for group, values in groups.items():
        for reading in values:
            current = getattr(reading, "current", None)
            if current is not None:
                readings.append((str(group), float(current)))
    return readings


def collect_snapshot(
    *,
    psutil_module=_DEFAULT_PSUTIL,
    thermal_reader: Callable[[], list[tuple[str, float]]] | None = None,
) -> Snapshot:
    """Return a transient local status snapshot without storing or uploading it.

    Omitting ``psutil_module`` uses the optional local dependency. Passing
    ``None`` explicitly is reserved for deterministic unavailable-state checks.
    """
    module = imported_psutil if psutil_module is _DEFAULT_PSUTIL else psutil_module
    if module is None:
        unavailable = _unavailable("Arthur's optional local diagnostics dependency is unavailable.")
        return {key: dict(unavailable) for key in ("cpu", "memory", "storage", "battery", "network", "temperature", "gpu")}

    snapshot: Snapshot = {}
    try:
        snapshot["cpu"] = _available(f"{module.cpu_percent(interval=None):.0f}%", "Current local processor use")
        snapshot["memory"] = _available(f"{module.virtual_memory().percent:.0f}%", "Current local memory use")
        disk = module.disk_usage(os.path.abspath(os.sep))
        free_gib = disk.free / (1024**3)
        snapshot["storage"] = _available(f"{free_gib:.1f} GB free", f"{disk.percent:.0f}% of the system drive is used")
        counters = module.net_io_counters()
        snapshot["network"] = _available("Local adapter activity", f"{(counters.bytes_sent + counters.bytes_recv) / (1024**2):.1f} MB since Windows started")
        battery = module.sensors_battery()
        snapshot["battery"] = _available(f"{battery.percent:.0f}%", "Charging" if battery.power_plugged else "On battery") if battery else _unavailable("No battery is reported by this Windows device.")
    except (AttributeError, OSError):
        snapshot.update({key: _unavailable("Windows did not return this local reading.") for key in ("cpu", "memory", "storage", "battery", "network")})

    reader = thermal_reader or (_windows_thermal_zones if sys.platform == "win32" else lambda: _psutil_temperatures(module))
    temperatures = reader()
    if temperatures:
        source, maximum = max(temperatures, key=lambda reading: reading[1])
        snapshot["temperature"] = _available(f"{maximum:.0f}°C", f"Windows thermal zone: {source}")
    else:
        snapshot["temperature"] = _unavailable("Windows did not expose a thermal zone. CPU/GPU temperature needs a user-approved compatible local adapter.")
    snapshot["gpu"] = _unavailable("GPU telemetry needs a user-approved compatible local adapter; Arthur does not install one automatically.")
    return snapshot
