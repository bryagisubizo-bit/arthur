"""Regression checks for Arthur's offline packaged-runtime readiness reporting."""

import unittest
from pathlib import Path
from unittest.mock import patch

from runtime_assets import packaged_runtime_readiness


class RuntimeAssetsTests(unittest.TestCase):
    def test_readiness_reports_missing_packaged_modules_without_downloading(self):
        with patch("runtime_assets.find_spec", side_effect=lambda name: object() if name != "cv2" else None):
            result = packaged_runtime_readiness()
        self.assertFalse(result.ready)
        self.assertEqual(result.missing_modules, ("cv2",))
        self.assertIn("will not download", result.detail)

    def test_readiness_requires_at_least_one_packaged_wake_word_model(self):
        with patch("runtime_assets.find_spec", return_value=object()):
            with patch("runtime_assets.openwakeword_model_paths", return_value=()):
                result = packaged_runtime_readiness()
        self.assertFalse(result.ready)
        self.assertEqual(result.model_count, 0)

    def test_readiness_confirms_packaged_models_are_available_offline(self):
        with patch("runtime_assets.find_spec", return_value=object()):
            with patch("runtime_assets.openwakeword_model_paths", return_value=(Path("one.onnx"), Path("two.tflite"))):
                result = packaged_runtime_readiness()
        self.assertTrue(result.ready)
        self.assertEqual(result.model_count, 2)
        self.assertEqual(result.missing_modules, ())


if __name__ == "__main__":
    unittest.main()
