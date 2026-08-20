"""Regression checks for Arthur's explicit, local-only openWakeWord setup handoff."""

from __future__ import annotations

import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parent


class WakeWordSetupTests(unittest.TestCase):
    def test_setup_script_installs_local_runtime_and_downloads_official_models(self) -> None:
        script = (ROOT / "SETUP_OPENWAKEWORD_WINDOWS.ps1").read_text(encoding="utf-8")
        self.assertIn("openwakeword>=0.6,<1", script)
        self.assertIn("sounddevice>=0.5,<1", script)
        self.assertIn("openwakeword.utils.download_models()", script)
        self.assertIn("It never opens the microphone", script)

    def test_setup_script_does_not_claim_to_create_an_arthur_model(self) -> None:
        script = (ROOT / "SETUP_OPENWAKEWORD_WINDOWS.ps1").read_text(encoding="utf-8")
        self.assertIn("do not create an Arthur wake word", script)
        self.assertIn("separately reviewed Arthur .onnx model", script)

    def test_windows_guide_recommends_onnx_and_explicit_activation(self) -> None:
        guide = (ROOT / "OPENWAKEWORD_WINDOWS_SETUP.md").read_text(encoding="utf-8")
        self.assertIn("recommending `.onnx` on Windows", guide)
        self.assertIn("Enable local wake-word listener", guide)
        self.assertIn("does not save audio", guide)


if __name__ == "__main__":
    unittest.main()
