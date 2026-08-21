"""Regression checks for non-activating multimodal and environment contracts."""

from environment_hub import prepare_home_assistant_proposal, prepare_mqtt_proposal
from local_coordinate_server import LocalCoordinateServerConfig, coordinate_message, websocket_startup_contract
from multimodal_adapters import adapter_contract, list_adapter_contracts


def main():
    adapters = list_adapter_contracts()
    assert {adapter["default_state"] for adapter in adapters} == {"disabled"}
    assert {adapter["transport"] for adapter in adapters} == {"closed"}
    assert adapter_contract("vision_matrix")["input_kind"] == "camera frames"
    home = prepare_home_assistant_proposal("https://homeassistant.local:8123", "deep-focus", "focus")
    assert home["state"] == "proposal_only" and home["transport"] == "closed"
    mqtt = prepare_mqtt_proposal("mqtts://broker.example", "arthur/scenes/focus", "calm")
    assert mqtt["scope"] == "one explicit publication topic"
    contract = websocket_startup_contract(LocalCoordinateServerConfig())
    assert contract["action"] == "no_listener_started"
    message = coordinate_message({"schema": "arthur.coordinate.v1", "transport": "closed", "revision": 1})
    assert '"type":"arthur.coordinate.revision"' in message
    print("multimodal and environment foundation regression checks passed")


if __name__ == "__main__":
    main()
