"""Consent-gated Windows accessibility bridge contracts for Arthur.

This module deliberately prepares scoped review and navigation plans only.  It
does not enumerate applications, capture screens, read text, access password
fields, send data, click, type, copy, or manipulate another application.
Actual UI Automation integration is intentionally a separately installed and
separately approved future adapter.
"""

from __future__ import annotations

from dataclasses import dataclass


MAX_SCOPE_TITLE_LENGTH = 120
ALLOWED_ACTIONS = (
    "inspect_accessible_controls",
    "navigate_visible_interface",
    "click",
    "type",
    "clipboard",
    "file_selection",
    "communication",
)
BLOCKED_ACTIONS = ("read_password", "bypass_security_prompt", "background_control", "screen_capture")


@dataclass(frozen=True)
class ApplicationScope:
    """A single user-named desktop application scope; never discovered silently."""

    title: str
    approved: bool = False


def create_scope(title: str, approved: bool = False) -> ApplicationScope:
    """Validate a manually entered visible application title without inspecting it."""
    cleaned = str(title or "").strip()
    if not cleaned:
        raise ValueError("Enter the title of one currently visible application window.")
    if len(cleaned) > MAX_SCOPE_TITLE_LENGTH:
        raise ValueError("The application title is too long for a deliberate review scope.")
    return ApplicationScope(title=cleaned, approved=bool(approved))


def approve_scope(scope: ApplicationScope, confirmed: bool) -> ApplicationScope:
    """Record an in-memory approval for one named application only."""
    if not confirmed:
        return ApplicationScope(title=scope.title, approved=False)
    return ApplicationScope(title=scope.title, approved=True)


def bridge_status(scope: ApplicationScope | None = None) -> str:
    """Describe the local bridge state without touching another application."""
    if scope is None:
        return "Closed. Arthur has not enumerated applications, read controls, captured a screen, or prepared an action."
    if not scope.approved:
        return f"Scope entered for {scope.title!r}, but inspection is still blocked until you approve that exact application."
    return f"Approved review scope: {scope.title!r}. Inspection, clicks, typing, clipboard, files, and communication remain separately blocked."


def prepare_navigation_plan(scope: ApplicationScope | None, goal: str) -> dict:
    """Return a reviewable plan, never an executable cross-application command."""
    if scope is None or not scope.approved:
        return {
            "state": "blocked",
            "detail": "Choose and approve one visible application before Arthur may prepare an accessibility navigation plan.",
            "steps": (),
        }
    clean_goal = str(goal or "review visible interface").strip() or "review visible interface"
    return {
        "state": "prepared",
        "application": scope.title,
        "goal": clean_goal,
        "steps": (
            "Review accessible controls exposed by the approved application only.",
            "Show the proposed navigation path for user review.",
            "Require a separate confirmation before every click, typed value, clipboard use, file choice, or communication action.",
        ),
        "detail": "Plan prepared locally. The named application is not inspected and no action was executed.",
    }


def action_readiness(scope: ApplicationScope | None, action: str, confirmed: bool = False) -> dict:
    """Make all consequential app actions fail closed in this foundation release."""
    requested = str(action or "").strip()
    if requested not in ALLOWED_ACTIONS:
        return {"state": "blocked", "detail": "That action is outside Arthur’s approved application-bridge contract."}
    if scope is None or not scope.approved:
        return {"state": "blocked", "detail": "Approve one specific application before reviewing any interaction."}
    if requested in {"click", "type", "clipboard", "file_selection", "communication"}:
        return {"state": "confirmation_required", "detail": f"{requested.replace('_', ' ').title()} requires a separate visible confirmation at execution time."}
    return {
        "state": "prepared" if confirmed else "review_required",
        "detail": "Accessible-control inspection remains an optional local adapter; this release does not open it automatically.",
    }


def emergency_stop() -> dict:
    """Return the fail-closed state used when a user clears an app bridge session."""
    return {
        "state": "stopped",
        "detail": "Application bridge session cleared. No inspection, action queue, capture, or background control remains active.",
    }


def optional_dependency_status() -> tuple[bool, str]:
    """Report the optional adapter availability without importing or using it at startup."""
    try:
        import pywinauto  # noqa: F401
    except ImportError:
        return False, "Optional pywinauto adapter is not installed. Arthur remains in plan-review mode."
    return True, "Optional pywinauto adapter is installed but remains disabled until an approved application inspection is requested."
