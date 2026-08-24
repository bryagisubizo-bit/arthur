"""Small presentation helpers for the manual GitHub release-check activity state."""

from __future__ import annotations


LOADING_FRAMES = ("[·  ]", "[·· ]", "[···]", "[ ··]", "[  ·]")


def release_check_loading_text(frame_index: int) -> str:
    """Return one deterministic text frame for the release-check animation."""

    return f"Checking GitHub release metadata {LOADING_FRAMES[frame_index % len(LOADING_FRAMES)]}"
