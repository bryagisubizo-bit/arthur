"""Lightweight desktop regression checks for the distributable Arthur prototype.

Run with: python test_desktop_smoke.py
The offscreen Qt platform keeps this usable in CI or during a build check.
"""

import json
import os
from datetime import datetime
from pathlib import Path

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

source_path = Path(__file__).with_name("app.py")
compile(source_path.read_text(encoding="utf-8"), str(source_path), "exec")

from PySide6.QtWidgets import QApplication
from PySide6.QtCore import Qt

from app import DEFAULT_CONFIG, CommandPlanner, FirstRunDialog, FirstRunTutorialDialog, MainWindow, PRIMARY_SYSTEM_LANGUAGE_PLACEHOLDER, PROVIDER_OPTIONS, SPEECH_RECOGNITION_ROUTE_PLACEHOLDER, VOICE_SYNTHESIS_ROUTE_PLACEHOLDER, is_time_in_window, profile_language_choices, render_greeting_script


def main():
    assert "appearance" in DEFAULT_CONFIG
    assert "autonomy" in DEFAULT_CONFIG
    assert DEFAULT_CONFIG["updates"]["manual_check_only"] is True
    assert "Defensive security & compliance" in PROVIDER_OPTIONS
    assert "URLScan.io" in PROVIDER_OPTIONS["Defensive security & compliance"]
    assert "Have I Been Pwned" in PROVIDER_OPTIONS["Defensive security & compliance"]
    assert "Philips Hue" in PROVIDER_OPTIONS["Smart Home"]
    assert "MQTT" in PROVIDER_OPTIONS["Smart Home"]

    allowed = CommandPlanner().plan("show my disk space")
    blocked = CommandPlanner().plan("scan the network for targets")
    assert allowed.allowed
    assert not blocked.allowed

    application = QApplication.instance() or QApplication([])
    window = MainWindow()
    assert window.nav_list.count() == 16
    assert window.pages.count() == 16
    assert window.nav_labels[0] == "Command desk"
    assert window.nav_labels[2] == "Spatial workspace"
    assert window.nav_labels[3] == "Symptom support"
    assert window.nav_labels[6] == "Voice signal"
    assert window.nav_labels[10] == "Language library"
    assert window.nav_labels[11] == "API vault"
    assert window.nav_labels[12] == "System sensors"
    assert window.profile_page.heading.text() == "Personal Protocol"
    assert window.config["profile"]["active_conversation_language"] == ""
    assert window.profile_page.speech_route.itemText(0) == SPEECH_RECOGNITION_ROUTE_PLACEHOLDER
    assert window.profile_page.speech_route.currentData() == ""
    assert window.profile_page.synthesis_route.itemText(0) == VOICE_SYNTHESIS_ROUTE_PLACEHOLDER
    assert window.profile_page.synthesis_route.currentData() == ""
    assert window.language_library_page.catalogue_list.count() > 80
    assert "Selected: " in window.language_library_page.active_label.text()
    assert window.language_library_page.save_colloquial_draft_button.text() == "Save private local draft"
    assert window.language_library_page.import_identifier_table_button.text() == "Choose local ISO 639-3 table"
    assert window.language_library_page.preview_colloquial_review_button.text() == "Prepare review preview"
    assert window.language_library_page.preview_source_confirmation_button.text() == "Prepare source-confirmed preview"
    assert window.language_library_page.source_evidence_kind.currentData() == "community-language-program"
    assert "catalogue entries available" in window.language_library_page.import_identifier_status.text()
    assert "not community reviewed" in window.language_library_page.colloquial_status.text()
    assert "No bundled source-confirmed example" in window.language_library_page.source_confirmed_examples.text()
    window.language_library_page.catalogue_search.setText("Navajo")
    assert window.language_library_page.catalogue_list.count() == 1
    assert "Diné Bizaad" in window.language_library_page.catalogue_list.item(0).text()
    assert "No bundled source-confirmed example" in window.language_library_page.source_confirmed_examples.text()
    assert "No research request prepared" in window.language_library_page.query_result.text()
    first_run = FirstRunDialog(window)
    assert "Bogitech" in first_run.windowTitle()
    assert first_run.native_language.itemData(0) == ""
    assert first_run.native_language.itemText(0) == PRIMARY_SYSTEM_LANGUAGE_PLACEHOLDER
    assert first_run.native_language.currentData() == ""
    assert first_run.speech_route.itemText(0) == SPEECH_RECOGNITION_ROUTE_PLACEHOLDER
    assert first_run.speech_route.currentData() == ""
    assert "This choice does not install software" in first_run.speech_route_note.text()
    assert first_run.synthesis_route.itemText(0) == VOICE_SYNTHESIS_ROUTE_PLACEHOLDER
    assert first_run.synthesis_route.currentData() == ""
    assert "does not download a model" in first_run.synthesis_route_note.text()
    assert "Diné Bizaad (Navajo)" in profile_language_choices()
    first_run.close()
    assert window.config["security"]["defensive_lookup_enabled"] is False
    assert window.config["interaction"]["spatial_room_access_method"] == ""
    assert window.config["sensors"]["enabled"] is False
    assert window.sensors_page.enabled.isChecked() is False
    assert "Local sensor diagnostics are off" in window.sensors_page.status.text()
    assert window.sensors_page.refresh_button.isEnabled() is False
    assert window.updates_page.manual_only.isChecked() is True
    assert window.updates_page.manual_only.isEnabled() is False
    assert window.voice_studio.listener is None
    assert window.voice_studio.pitch.minimum() == -10
    assert window.voice_studio.pitch.maximum() == 10
    assert window.voice_studio.arrival_greeting.isChecked() is True
    assert window.voice_studio.first_interaction_greeting.isChecked() is True
    assert window.voice_studio.wake_greeting.isChecked() is True
    assert "local desktop assistant" in window.voice_studio.introduction_text().lower()
    assert window.voice_studio.introduction_test_button.text() == "Replay Arthur's introduction"
    assert any(button.text() == "Test microphone activity (3 sec)" for button in window.voice_studio.findChildren(type(window.voice_studio.introduction_test_button)))
    assert any(button.text() == "Check microphone readiness" for button in window.voice_studio.findChildren(type(window.voice_studio.introduction_test_button)))
    assert any(button.text() == "Open Windows microphone privacy settings" for button in window.voice_studio.findChildren(type(window.voice_studio.introduction_test_button)))
    assert window.voice_studio.microphone.count() >= 1
    assert "Speech-recognition route is not selected" in window.voice_studio.speech_route_status.text()
    assert "Speech-output route is not selected" in window.voice_studio.synthesis_route_status.text()
    assert window.voice_studio.greeting_script_kind.currentData() == "opening"
    assert window.voice_studio.greeting_script.toPlainText()
    assert window.voice_studio.time_of_day_greetings.isChecked() is False
    assert window.voice_studio.do_not_disturb.isChecked() is False
    assert "Do Not Disturb is off" in window.voice_studio.quiet_hours_status.text()
    assert is_time_in_window("23:00", "22:00", "07:00") is True
    assert is_time_in_window("12:00", "22:00", "07:00") is False
    custom = json.loads(json.dumps(DEFAULT_CONFIG))
    custom["profile"]["display_name"] = "Aline"
    custom["profile"]["title"] = "Madam"
    custom["voice"]["time_of_day_greetings_enabled"] = True
    assert render_greeting_script(custom, "opening", datetime(2026, 1, 1, 9, 0)) == "Good morning, Madam Aline. Arthur is ready when you are."
    assert "Visual results remain gated" in window.dashboard.focus_cue.text()
    assert window.voice_studio.pause_listener(persist=False) is False
    assert window.spatial_page.air_gestures.isChecked() is False
    assert window.spatial_page.hello_setup_button.text() == "Open Windows Hello sign-in settings"
    assert window.spatial_page.face_test_button.text() == "Run visible local camera readiness test"
    assert window.spatial_page.face_audio_cue.isChecked() is False
    assert window.spatial_page.face_lockout_timer.isActive() is True
    assert "no recent local face-check failures" in window.spatial_page.face_lockout_label.text().lower()
    assert "no transport is open" in window.spatial_page.context_sync_status.text().lower()
    assert "Research field" in window.spatial_page.context_focus_label.text()
    assert "camera, microphone, provider, and network connections remain off" in window.spatial_page.context_sync_status.text().lower()
    assert "choose exactly one method" in window.spatial_page.hello_privacy_note.text().lower()
    assert "starts only after separate consent and enrolment" in window.spatial_page.hello_privacy_note.text().lower()
    assert "stores no raw image or video" in window.spatial_page.hello_privacy_note.text().lower()
    assert "short local cooldown" in window.spatial_page.hello_privacy_note.text().lower()
    assert "choose one access method" in window.spatial_page.access_status.text().lower()
    assert "not label a disease" in window.symptom_support_page.result.text().lower()
    assert window.symptom_support_page.condition_lookup_button.text() == "Find reviewed source"
    assert window.symptom_support_page.article_summary_button.text() == "Create short local reading note"
    assert "Opening any source link is your choice" in window.symptom_support_page.condition_reference.text()
    assert window.page_scroll.horizontalScrollBarPolicy() == Qt.ScrollBarPolicy.ScrollBarAlwaysOff
    tutorial = FirstRunTutorialDialog(window)
    assert tutorial.windowTitle() == "Arthur — first-run tutorial"
    tutorial.close()
    window.close()
    application.processEvents()
    print("Arthur desktop smoke checks passed.")


if __name__ == "__main__":
    main()
