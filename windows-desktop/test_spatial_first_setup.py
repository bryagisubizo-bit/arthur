import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

import app
from app import SpatialWorkspacePage, refresh_installer_spatial_intent


class SpatialFirstSetupTests(unittest.TestCase):
    def test_installer_selected_method_is_limited_to_known_local_options(self) -> None:
        page = SpatialWorkspacePage.__new__(SpatialWorkspacePage)
        page.config = {"interaction": {"installer_spatial_room_protection": "password"}}
        self.assertEqual(page.installer_selected_access_method(), "password")
        page.config = {"interaction": {"installer_spatial_room_protection": "unexpected"}}
        self.assertEqual(page.installer_selected_access_method(), "")

    def test_first_room_entry_opens_the_installer_selected_password_setup(self) -> None:
        page = SpatialWorkspacePage.__new__(SpatialWorkspacePage)
        page.config = {"interaction": {}}
        page.session_unlocked = False
        page.selected_access_method = lambda: ""
        page.installer_selected_access_method = lambda: "password"
        prompted = []
        page.configure_access = lambda preferred_method=None: prompted.append(preferred_method)
        with patch("app.QMessageBox.information"):
            self.assertFalse(page.request_access())
        self.assertEqual(prompted, ["password"])

    def test_new_installer_password_intent_clears_stale_face_route_without_camera_checks(self) -> None:
        refreshed = refresh_installer_spatial_intent(
            {
                "interaction": {
                    "spatial_room_access_method": "local_camera_face",
                    "installer_spatial_room_protection": "local_camera_face",
                    "installer_spatial_room_protection_intent_id": "v0.1.5-old",
                }
            },
            {
                "spatial_room_protection": "password",
                "spatial_room_protection_intent_id": "v0.1.6-password",
            },
        )
        interaction = refreshed["interaction"]
        self.assertEqual(interaction["spatial_room_access_method"], "")
        self.assertEqual(interaction["installer_spatial_room_protection"], "password")
        self.assertEqual(interaction["spatial_room_pending_setup_intent_id"], "v0.1.6-password")

        page = SpatialWorkspacePage.__new__(SpatialWorkspacePage)
        page.config = refreshed
        page.session_unlocked = False
        page.face_dependency_status = lambda: (_ for _ in ()).throw(AssertionError("password setup must not inspect cv2"))
        page.face_is_configured = lambda: (_ for _ in ()).throw(AssertionError("password setup must not inspect face enrolment"))
        page.verify_face = lambda: (_ for _ in ()).throw(AssertionError("password setup must not verify a face"))
        prompted = []
        page.configure_access = lambda preferred_method=None: prompted.append(preferred_method)

        with patch("app.QMessageBox.information"):
            self.assertFalse(page.request_access())
        self.assertEqual(prompted, ["password"])

    def test_load_config_consumes_new_password_intent_over_a_saved_face_method(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            config_path = root / "arthur_config.json"
            consent_path = root / "installer_permissions.json"
            config_path.write_text(
                json.dumps(
                    {
                        "interaction": {
                            "spatial_room_access_method": "local_camera_face",
                            "installer_spatial_room_protection": "local_camera_face",
                            "installer_spatial_room_protection_intent_id": "v0.1.5-face",
                        }
                    }
                ),
                encoding="utf-8",
            )
            consent_path.write_text(
                json.dumps(
                    {
                        "spatial_room_protection": "password",
                        "spatial_room_protection_intent_id": "v0.1.6-password",
                    }
                ),
                encoding="utf-8",
            )
            with patch.object(app, "DATA_DIR", root), patch.object(app, "CONFIG_FILE", config_path), patch.object(app, "INSTALLER_CONSENT_FILE", consent_path):
                loaded = app.load_config()

            interaction = loaded["interaction"]
            self.assertEqual(interaction["spatial_room_access_method"], "")
            self.assertEqual(interaction["installer_spatial_room_protection"], "password")
            self.assertEqual(interaction["spatial_room_pending_setup_intent_id"], "v0.1.6-password")
            persisted = json.loads(config_path.read_text(encoding="utf-8"))
            self.assertEqual(persisted["interaction"]["spatial_room_access_method"], "")


if __name__ == "__main__":
    unittest.main()
