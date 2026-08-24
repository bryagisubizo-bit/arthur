"""Regression checks for persistent, truthful API Vault status feedback."""

import os

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

from PySide6.QtWidgets import QApplication

from app import IntegrationCard


def main():
    application = QApplication.instance() or QApplication([])
    card = IntegrationCard(
        "Main AI / Conversation",
        ["Select provider", "OpenAI", "Anthropic"],
        {"provider": "Anthropic", "connection_state": "adapter_ready"},
    )
    assert card.live_test.isEnabled()
    assert "reviewed test" in card.connection_detail.text().lower()

    card.connection_state = "adapter_unavailable"
    card.last_connection_detail = "No reviewed test exists for this provider."
    card.refresh_connection_status()
    assert card.status.text() == "No live-test adapter"
    assert card.connection_detail.text() == "No reviewed test exists for this provider."

    card.mark_dirty()
    assert card.status.text() == "Unsaved"
    assert "save or check" in card.connection_detail.text().lower()
    application.quit()
    print("API Vault feedback checks passed.")


if __name__ == "__main__":
    main()
