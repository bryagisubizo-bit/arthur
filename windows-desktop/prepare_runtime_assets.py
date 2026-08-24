"""Build-time preparation of Arthur's local desktop runtime assets.

Run from the configured Windows virtual environment before PyInstaller. The
installer then includes the resulting dependencies and model data so a user
does not need a network download at every startup.
"""

from __future__ import annotations

import json
from pathlib import Path


def main() -> int:
    import cv2  # noqa: F401 - verifies the packaged OpenCV import works.
    import openwakeword

    openwakeword.utils.download_models()
    model_root = Path(openwakeword.__file__).resolve().parent / "resources" / "models"
    models = sorted(path.name for path in model_root.glob("*") if path.suffix.casefold() in {".onnx", ".tflite"})
    if not models:
        raise RuntimeError("openWakeWord finished setup but no local model assets were found.")
    manifest = {
        "modules": ["openwakeword", "sounddevice", "pyttsx3", "cv2"],
        "wake_word_models": models,
    }
    Path("runtime_manifest.json").write_text(json.dumps(manifest, indent=2), encoding="utf-8")
    print(f"Prepared {len(models)} local openWakeWord model asset(s) for the Arthur installer.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
