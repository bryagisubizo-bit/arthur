import unittest
from unittest.mock import patch

from app import SpatialWorkspacePage


class SpatialFirstSetupTests(unittest.TestCase):
    def test_installer_selected_method_is_limited_to_known_local_options(self) -> None:
        page = SpatialWorkspacePage.__new__(SpatialWorkspacePage)
        page.config = {"interaction": {"installer_spatial_room_protection": "password"}}
        self.assertEqual(page.installer_selected_access_method(), "password")
        page.config = {"interaction": {"installer_spatial_room_protection": "unexpected"}}
        self.assertEqual(page.installer_selected_access_method(), "")

    def test_first_room_entry_opens_the_installer_selected_password_setup(self) -> None:
        page = SpatialWorkspacePage.__new__(SpatialWorkspacePage)
        page.session_unlocked = False
        page.selected_access_method = lambda: ""
        page.installer_selected_access_method = lambda: "password"
        prompted = []
        page.configure_access = lambda preferred_method=None: prompted.append(preferred_method)
        with patch("app.QMessageBox.information"):
            self.assertFalse(page.request_access())
        self.assertEqual(prompted, ["password"])


if __name__ == "__main__":
    unittest.main()
