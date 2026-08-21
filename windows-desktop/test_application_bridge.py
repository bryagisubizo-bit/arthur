from application_bridge import (
    ALLOWED_ACTIONS,
    action_readiness,
    approve_scope,
    bridge_status,
    create_scope,
    emergency_stop,
    prepare_navigation_plan,
)


def main() -> None:
    scope = create_scope("Untitled - Notepad")
    assert scope.approved is False
    assert "blocked" in bridge_status(scope).lower()
    assert prepare_navigation_plan(scope, "open the File menu")["state"] == "blocked"

    approved = approve_scope(scope, confirmed=True)
    plan = prepare_navigation_plan(approved, "open the File menu")
    assert plan["state"] == "prepared"
    assert "not inspected" in plan["detail"].lower()
    assert action_readiness(approved, "click")["state"] == "confirmation_required"
    assert action_readiness(approved, "inspect_accessible_controls")["state"] == "review_required"
    assert "type" in ALLOWED_ACTIONS
    assert emergency_stop()["state"] == "stopped"
    print("application bridge contract checks passed")


if __name__ == "__main__":
    main()
