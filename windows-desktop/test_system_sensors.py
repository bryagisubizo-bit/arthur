"""Regression coverage for Arthur's local-only sensor snapshot normalisation."""

from types import SimpleNamespace

from system_sensors import collect_snapshot


class FakePsutil:
    def cpu_percent(self, interval=None):
        assert interval is None
        return 23.4

    def virtual_memory(self):
        return SimpleNamespace(percent=61.0)

    def disk_usage(self, path):
        return SimpleNamespace(free=10 * 1024**3, percent=70.0)

    def net_io_counters(self):
        return SimpleNamespace(bytes_sent=3 * 1024**2, bytes_recv=5 * 1024**2)

    def sensors_battery(self):
        return SimpleNamespace(percent=82.0, power_plugged=True)


def main():
    snapshot = collect_snapshot(psutil_module=FakePsutil(), thermal_reader=lambda: [("ACPI\\TZ0", 46.6)])
    assert snapshot["cpu"]["value"] == "23%"
    assert snapshot["storage"]["value"] == "10.0 GB free"
    assert snapshot["battery"]["detail"] == "Charging"
    assert snapshot["temperature"]["value"] == "47°C"
    assert snapshot["temperature"]["state"] == "available"
    assert snapshot["gpu"]["state"] == "unavailable"

    unavailable = collect_snapshot(psutil_module=None)
    assert all(reading["state"] == "unavailable" for reading in unavailable.values())
    assert "CPU/GPU temperature needs" in collect_snapshot(psutil_module=FakePsutil(), thermal_reader=lambda: [])["temperature"]["detail"]
    print("Arthur local sensor checks passed.")


if __name__ == "__main__":
    main()
