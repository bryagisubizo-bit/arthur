"""Regression checks for redacted shared API-layer resolution."""

import unittest

from api_layer import API_LAYER_ROOM, api_layer_status, resolve_api_room


class ApiLayerTests(unittest.TestCase):
    def test_shared_room_is_not_ready_until_the_api_layer_is_enabled_and_saved(self):
        config = {
            "integrations": {
                API_LAYER_ROOM: {"provider": "OpenAI", "enabled": False, "api_key_present": True},
                "Speech-to-Text": {"provider": "Custom", "enabled": True, "use_api_layer": True},
            }
        }
        status = api_layer_status(config)
        resolution = resolve_api_room(config, "Speech-to-Text")
        self.assertFalse(status.ready)
        self.assertEqual(status.shared_rooms, ("Speech-to-Text",))
        self.assertFalse(resolution.ready)
        self.assertTrue(resolution.inherited_from_api_layer)
        self.assertEqual(resolution.credential_room, API_LAYER_ROOM)

    def test_enabled_api_layer_resolves_shared_rooms_without_returning_secret_data(self):
        config = {
            "integrations": {
                API_LAYER_ROOM: {
                    "provider": "OpenAI",
                    "endpoint": "https://gateway.example.test/v1",
                    "enabled": True,
                    "api_key_present": True,
                },
                "Main AI / Conversation": {"provider": "OpenAI", "enabled": True, "use_api_layer": True},
            }
        }
        status = api_layer_status(config)
        resolution = resolve_api_room(config, "Main AI / Conversation")
        self.assertTrue(status.ready)
        self.assertTrue(resolution.ready)
        self.assertEqual(resolution.endpoint, "https://gateway.example.test/v1")
        self.assertEqual(resolution.credential_room, API_LAYER_ROOM)
        self.assertNotIn("key", resolution.__dict__)

    def test_direct_room_keeps_its_own_credential_boundary(self):
        config = {
            "integrations": {
                "Internet Research": {"provider": "Tavily", "enabled": True, "api_key_present": True}
            }
        }
        resolution = resolve_api_room(config, "Internet Research")
        self.assertTrue(resolution.ready)
        self.assertFalse(resolution.inherited_from_api_layer)
        self.assertEqual(resolution.credential_room, "Internet Research")


if __name__ == "__main__":
    unittest.main()
