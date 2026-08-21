"""Regression checks for Arthur’s manual, reversible monitor-placement foundation."""

from monitor_workspace import (
    LOW_RESOURCE_POLICY,
    apply_approved_placement,
    discover_monitors,
    monitor_snapshot,
    placement_preview,
    resource_budget,
)


class FakeMonitor:
    def __init__(self, name, x, y, width, height, primary=False):
        self.name = name
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.is_primary = primary


def main():
    monitors = discover_monitors(lambda: [FakeMonitor("Desk", 0, 0, 1920, 1080, True), FakeMonitor("Side", 1920, 0, 1280, 1024)])
    assert len(monitors) == 2
    assert monitors[0]["id"] == "display-1"
    snapshot = monitor_snapshot(monitors)
    assert snapshot["transport"] == "closed"
    assert snapshot["sample_mode"] == "manual-once"
    preview = placement_preview(4512, monitors[1])
    assert preview["action"] == "preview-only"
    assert preview["requires_confirmation"] is True
    assert preview["target"]["x"] >= 1920
    calls = []
    assert apply_approved_placement(preview, confirmed=False, mover=lambda plan: calls.append(plan))["state"] == "not-applied"
    assert not calls
    assert apply_approved_placement(preview, confirmed=True, mover=lambda plan: calls.append(plan))["state"] == "applied"
    assert calls == [preview]
    assert resource_budget(10, 25)["state"] == "within-budget"
    assert resource_budget(LOW_RESOURCE_POLICY["cpu_soft_limit_percent"], 10)["state"] == "conserve"


if __name__ == "__main__":
    main()
