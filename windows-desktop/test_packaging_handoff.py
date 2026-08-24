"""Regression checks for Arthur's Windows packaging handoff.

These assertions do not attempt to cross-compile a Windows executable on Linux.
They confirm that the files delivered to a Windows builder retain the expected,
explicit PyInstaller and Inno Setup paths and do not contain obvious secrets.
"""

from __future__ import annotations

import re
import unittest
from pathlib import Path

from PIL import Image


ROOT = Path(__file__).resolve().parent


class PackagingHandoffTests(unittest.TestCase):
    def test_build_script_runs_tests_pyinstaller_and_inno_setup_when_available(self) -> None:
        script = (ROOT / "build_windows.bat").read_text(encoding="utf-8")
        self.assertIn("for %%F in (test_*.py)", script)
        self.assertIn("python -m PyInstaller --noconfirm --clean Arthur.spec", script)
        self.assertIn("ISCC.exe", script)
        self.assertIn("Inno Setup 7\\ISCC.exe", script)
        self.assertIn("installer\\output\\ArthurSetup-0.1.6.exe", script)

    def test_installer_points_at_the_pyinstaller_payload(self) -> None:
        installer = (ROOT / "installer" / "ArthurSetup.iss").read_text(encoding="utf-8")
        self.assertIn('Source: "..\\dist\\Arthur\\*"', installer)
        self.assertIn('#ifndef MyAppVersion', installer)
        self.assertIn('#define MyAppVersion "0.1.6"', installer)
        self.assertIn('#endif', installer)
        self.assertIn("OutputBaseFilename=ArthurSetup-{#MyAppVersion}", installer)
        self.assertIn('Filename: "{app}\\Arthur.exe"', installer)
        self.assertIn("#ifexist \"..\\dist\\Arthur\\Arthur.exe\"", installer)
        self.assertIn("Arthur.exe is missing.", installer)
        self.assertIn("Arthur permissions review", installer)
        self.assertIn("local system sensor diagnostics", installer)
        self.assertIn('"local_sensor_diagnostics"', installer)
        self.assertIn('"spatial_room_protection_intent_id"', installer)
        self.assertIn("installer_permissions.json", installer)
        self.assertIn("SetupIconFile=..\\assets\\arthur_hawk.ico", installer)
        self.assertIn("False,\n    False\n  );", installer)

    def test_blue_hawk_icon_is_packaged_for_window_and_tray(self) -> None:
        app_source = (ROOT / "app.py").read_text(encoding="utf-8")
        hawk_svg = (ROOT / "assets" / "arthur_hawk.svg").read_text(encoding="utf-8")
        self.assertIn('self.setWindowIcon(QIcon(str(bundled_path("assets/arthur_hawk.ico"))))', app_source)
        self.assertIn('self.tray.setIcon(QIcon(str(bundled_path("assets/arthur_hawk.ico"))))', app_source)
        self.assertIn('fill="#083B8E"', hawk_svg)
        self.assertGreater((ROOT / "assets" / "arthur_hawk.png").stat().st_size, 0)
        self.assertGreater((ROOT / "assets" / "arthur_hawk.ico").stat().st_size, 0)

        with Image.open(ROOT / "assets" / "arthur_hawk.png") as source:
            self.assertEqual(source.size, (512, 512))
            self.assertEqual(source.mode, "RGBA")

        required_sizes = {(16, 16), (24, 24), (32, 32), (48, 48), (64, 64), (128, 128), (256, 256)}
        with Image.open(ROOT / "assets" / "arthur_hawk.ico") as icon:
            self.assertTrue(required_sizes.issubset(icon.ico.sizes()))

    def test_wake_word_runtime_is_collected_for_the_windows_installer(self) -> None:
        spec = (ROOT / "Arthur.spec").read_text(encoding="utf-8")
        self.assertIn('collect_data_files("openwakeword")', spec)
        self.assertIn('collect_submodules("openwakeword")', spec)
        self.assertIn('"onnxruntime"', spec)
        self.assertIn('"sounddevice"', spec)

    def test_build_handoff_contains_no_obvious_live_secret(self) -> None:
        payload = "\n".join(
            (ROOT / relative).read_text(encoding="utf-8")
            for relative in ("build_windows.bat", "installer/ArthurSetup.iss", "requirements.txt")
        )
        self.assertNotRegex(payload, re.compile(r"(?:sk-|api[_-]?key\s*[:=]\s*)[A-Za-z0-9_-]{16,}", re.IGNORECASE))


if __name__ == "__main__":
    unittest.main()
