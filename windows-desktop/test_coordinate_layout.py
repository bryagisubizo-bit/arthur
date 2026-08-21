"""Regression checks for Arthur's local coordinate contract."""

from coordinate_layout import COORDINATE_SCHEMA, TRANSPORT_STATE, coordinate_snapshot, zone_members


def main():
    snapshot = coordinate_snapshot(
        ["Research field", "System diagnostics", "Smart-home review"],
        "Research field",
        revision=4,
        event="module.focus",
    )
    assert snapshot["schema"] == COORDINATE_SCHEMA
    assert snapshot["transport"] == TRANSPORT_STATE
    assert snapshot["actor"] == "local-user"
    assert snapshot["revision"] == 4
    assert zone_members(snapshot, "focus") == ["Research field"]
    assert zone_members(snapshot, "periphery") == ["System diagnostics"]
    assert zone_members(snapshot, "ambient") == ["Smart-home review"]
    focused = snapshot["modules"][0]["coordinate"]
    assert focused == {"x": 0, "y": 0, "z": 300, "zone": "focus"}
    print("coordinate layout regression checks passed")


if __name__ == "__main__":
    main()
