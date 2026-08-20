from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from installer_consent import apply_installer_defaults, load_installer_consent, normalise_installer_consent


class InstallerConsentTests(unittest.TestCase):
    def test_unknown_or_missing_values_default_to_false(self) -> None:
        choices = normalise_installer_consent({"microphone_wake_word": True, "unexpected": True})
        self.assertTrue(choices["microphone_wake_word"])
        self.assertFalse(choices["camera_features"])
        self.assertNotIn("unexpected", choices)

    def test_missing_or_invalid_file_means_no_installer_consent(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            path = Path(temporary) / "installer_permissions.json"
            self.assertFalse(any(load_installer_consent(path).values()))
            path.write_text("not json", encoding="utf-8")
            self.assertFalse(any(load_installer_consent(path).values()))

    def test_choices_do_not_start_listening_or_grant_os_permissions(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            path = Path(temporary) / "installer_permissions.json"
            path.write_text(json.dumps({"microphone_wake_word": True, "background_ready": True}), encoding="utf-8")
            config = apply_installer_defaults(
                {"voice": {}, "autonomy": {}, "privacy": {}, "integrations": {}},
                load_installer_consent(path),
            )
        self.assertTrue(config["voice"]["wake_word_listener_approved"])
        self.assertTrue(config["autonomy"]["background_ready"])
        self.assertFalse(config["autonomy"]["local_listening"])
        self.assertFalse(config["privacy"]["wake_word_background_enabled"])


if __name__ == "__main__":
    unittest.main()
