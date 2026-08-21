from cloud_gateway import DEFAULT_RESOURCE_POLICY, create_gateway_proposal, gateway_status, validate_https_endpoint


def main() -> None:
    ok, detail = validate_https_endpoint("https://gateway.example.test/v1")
    assert ok and "review" in detail.lower()
    assert not validate_https_endpoint("http://gateway.example.test/v1")[0]
    assert not validate_https_endpoint("wss://gateway.example.test")[0]
    proposal = create_gateway_proposal("Developer gateway", "https://gateway.example.test/v1", approved_data_classes=("approved text",))
    assert proposal.transport_state == "closed"
    assert proposal.streaming_requested is False
    assert "credential manager" in proposal.credential_reference.lower()
    assert "closed" in gateway_status({}).lower()
    assert "prepared only" in gateway_status({"cloud_gateway": {"endpoint": "https://gateway.example.test/v1"}}).lower()
    assert DEFAULT_RESOURCE_POLICY["streaming_default"] == "off"
    print("cloud gateway contract checks passed")


if __name__ == "__main__":
    main()
