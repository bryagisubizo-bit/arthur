from urllib.error import HTTPError, URLError

from provider_connection import approved_test_providers, run_approved_connection_test, setup_state


class FakeResponse:
    def __init__(self, status=200):
        self.status = status

    def getcode(self):
        return self.status

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc, traceback):
        return False


def test_setup_state_is_local_and_never_claims_a_connection():
    assert setup_state("Select provider", False) == "unconnected"
    assert setup_state("OpenAI", False) == "key_required"
    assert setup_state("OpenAI", True) == "adapter_ready"
    assert setup_state("Anthropic", True) == "adapter_ready"
    assert setup_state("OpenAI Audio", True) == "adapter_ready"
    assert setup_state("OpenAI TTS", True) == "adapter_ready"
    assert "Anthropic" in approved_test_providers()


def test_approved_openai_test_uses_one_authorised_request_without_exposing_key():
    seen = {}

    def opener(request, timeout):
        seen["url"] = request.full_url
        seen["authorization"] = request.get_header("Authorization")
        seen["timeout"] = timeout
        return FakeResponse(200)

    result = run_approved_connection_test("OpenAI", "test-secret", opener=opener)
    assert result.state == "test_passed"
    assert "test-secret" not in result.detail
    assert seen["url"] == "https://api.openai.com/v1/models"
    assert seen["authorization"] == "Bearer test-secret"
    assert seen["timeout"] == 8.0


def test_unsupported_or_rejected_tests_remain_explicitly_unconnected():
    unsupported = run_approved_connection_test("Luxand", "test-secret")
    assert unsupported.state == "adapter_unavailable"
    assert "not connected" in unsupported.detail.lower()

    def rejected(*_args, **_kwargs):
        raise HTTPError("https://api.openai.com/v1/models", 401, "Unauthorized", None, None)

    result = run_approved_connection_test("OpenAI", "test-secret", opener=rejected)
    assert result.state == "test_failed"
    assert "401" in result.detail
    assert "not connected" in result.detail.lower()


def test_anthropic_test_uses_documented_auth_headers_without_leaking_the_key():
    seen = {}

    def opener(request, timeout):
        seen["url"] = request.full_url
        seen["key"] = request.get_header("X-api-key")
        seen["version"] = request.get_header("Anthropic-version")
        return FakeResponse(200)

    result = run_approved_connection_test("Anthropic", "test-secret", opener=opener)
    assert result.state == "test_passed"
    assert seen == {
        "url": "https://api.anthropic.com/v1/models?limit=1",
        "key": "test-secret",
        "version": "2023-06-01",
    }
    assert "test-secret" not in result.detail


def test_network_failure_does_not_be_misrepresented_as_a_connection():
    def unavailable(*_args, **_kwargs):
        raise URLError("offline")

    result = run_approved_connection_test("OpenAI", "test-secret", opener=unavailable)
    assert result.state == "test_failed"
    assert "not connected" in result.detail.lower()


def main():
    test_setup_state_is_local_and_never_claims_a_connection()
    test_approved_openai_test_uses_one_authorised_request_without_exposing_key()
    test_unsupported_or_rejected_tests_remain_explicitly_unconnected()
    test_anthropic_test_uses_documented_auth_headers_without_leaking_the_key()
    test_network_failure_does_not_be_misrepresented_as_a_connection()
    print("Provider connection checks passed.")


if __name__ == "__main__":
    main()
