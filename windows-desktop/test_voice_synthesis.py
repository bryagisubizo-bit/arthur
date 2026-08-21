from pathlib import Path

from voice_synthesis import describe_route


def main() -> None:
    local = describe_route("local_windows_tts")
    assert local is not None
    assert "microphone" in local.boundary.lower()
    provider = describe_route("developer_neural_tts")
    assert provider is not None
    assert "does not connect" in provider.boundary.lower()
    assert describe_route("unknown") is None
    guide = Path(__file__).with_name("VOICE_SYNTHESIS.md").read_text(encoding="utf-8")
    assert "Approved reply text → speech units / selected engine → audio output" in guide
    assert "does not provide voice cloning" in guide
    print("voice synthesis route checks passed")


if __name__ == "__main__":
    main()
