"""Regression checks for Arthur's local, consent-first voice diagnostics."""

import tempfile
import unittest
from pathlib import Path
from unittest.mock import MagicMock, patch

from openwakeword_service import WakeWordListener
from voice_runtime import DiagnosticResult, VoiceRuntime, available_input_devices, diagnose_wake_word, microphone_readiness, test_microphone_activity


class VoiceRuntimeTests(unittest.TestCase):
    def test_missing_model_never_reports_wake_word_ready(self):
        with patch.dict("sys.modules", {"openwakeword": object(), "sounddevice": object()}):
            result = diagnose_wake_word("")
        self.assertFalse(result.ready)
        self.assertIn("model", result.headline.casefold())

    def test_unsupported_model_never_reports_ready(self):
        with patch.dict("sys.modules", {"openwakeword": object(), "sounddevice": object()}):
            with tempfile.TemporaryDirectory() as directory:
                model = Path(directory) / "unverified.txt"
                model.write_text("not a model", encoding="utf-8")
                result = diagnose_wake_word(str(model))
        self.assertFalse(result.ready)

    def test_existing_onnx_model_reports_ready_without_opening_microphone(self):
        with patch.dict("sys.modules", {"openwakeword": object(), "sounddevice": object()}):
            with tempfile.TemporaryDirectory() as directory:
                model = Path(directory) / "arthur.onnx"
                model.write_bytes(b"placeholder test model")
                result = diagnose_wake_word(str(model))
        self.assertTrue(result.ready)

    def test_speech_is_not_attempted_when_runtime_is_unavailable(self):
        runtime = VoiceRuntime()
        with patch.object(runtime, "diagnose_speech", return_value=DiagnosticResult(False, "Unavailable", "Install first")):
            result = runtime.speak("Arthur test")
        self.assertFalse(result.ready)
        self.assertEqual(result.headline, "Unavailable")

    def test_voice_preferences_bound_rate_volume_and_pitch_locally(self):
        runtime = VoiceRuntime()
        runtime.configure(voice_id="local-voice", rate=999, volume=3, pitch=-99)
        self.assertEqual(runtime._voice_id, "local-voice")
        self.assertEqual(runtime._rate, 260)
        self.assertEqual(runtime._volume, 1.0)
        self.assertEqual(runtime._pitch, -10)

    def test_microphone_activity_result_uses_only_transient_level(self):
        with patch("voice_runtime._microphone_activity_sample", return_value=0.08) as sample:
            result = test_microphone_activity(3, device=8)
        self.assertTrue(result.ready)
        self.assertIn("activity", result.headline.casefold())
        self.assertIn("not record", result.detail.casefold())
        sample.assert_called_once_with(3.0, device=8)

    def test_microphone_activity_reports_device_error_without_claiming_capture(self):
        with patch("voice_runtime._microphone_activity_sample", side_effect=RuntimeError("device unavailable")):
            result = test_microphone_activity(3)
        self.assertFalse(result.ready)
        self.assertIn("could not read", result.headline.casefold())
        self.assertIn("no audio was saved", result.detail.casefold())

    def test_microphone_readiness_checks_a_selected_input_without_opening_audio(self):
        sounddevice = MagicMock()
        sounddevice.query_devices.return_value = {"name": "Arthur microphone", "max_input_channels": 1}
        with patch.dict("sys.modules", {"sounddevice": sounddevice}):
            result = microphone_readiness(device=4)
        self.assertTrue(result.ready)
        sounddevice.query_devices.assert_called_once_with(device=4, kind="input")

    def test_available_inputs_excludes_non_input_devices(self):
        sounddevice = MagicMock()
        sounddevice.query_devices.return_value = [
            {"name": "Speakers", "max_input_channels": 0},
            {"name": "Headset microphone", "max_input_channels": 1},
        ]
        with patch.dict("sys.modules", {"sounddevice": sounddevice}):
            devices = available_input_devices()
        self.assertEqual(devices, [(1, "Headset microphone")])

    def test_listener_suspends_predictions_only_until_the_requested_time(self):
        listener = WakeWordListener()
        with patch("openwakeword_service.monotonic", side_effect=[10.0, 11.0, 14.5]):
            listener.suspend_detection(4.0)
            self.assertEqual(listener._suspended_until, 14.0)
            self.assertGreater(listener._suspended_until, 11.0)
            self.assertLess(listener._suspended_until, 14.5)


if __name__ == "__main__":
    unittest.main()
