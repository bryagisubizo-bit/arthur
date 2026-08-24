"""Small, explicit provider-connection checks for Arthur's desktop API Vault.

No test runs until the user presses the live-test control and confirms the
outbound request. Results deliberately omit API-key material.
"""

from dataclasses import dataclass
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen


@dataclass(frozen=True)
class ConnectionTestResult:
    state: str
    detail: str


_APPROVED_TESTS = {
    "OpenAI": {
        "url": "https://api.openai.com/v1/models",
        "headers": lambda api_key: {"Authorization": f"Bearer {api_key}"},
    },
    "OpenAI Audio": {
        "url": "https://api.openai.com/v1/models",
        "headers": lambda api_key: {"Authorization": f"Bearer {api_key}"},
    },
    "OpenAI TTS": {
        "url": "https://api.openai.com/v1/models",
        "headers": lambda api_key: {"Authorization": f"Bearer {api_key}"},
    },
    "Anthropic": {
        "url": "https://api.anthropic.com/v1/models?limit=1",
        "headers": lambda api_key: {
            "x-api-key": api_key,
            "anthropic-version": "2023-06-01",
        },
    },
}


def approved_test_providers() -> frozenset[str]:
    """Return providers with a reviewed, read-only connection check."""
    return frozenset(_APPROVED_TESTS)


def setup_state(provider: str, api_key_present: bool) -> str:
    """Return a local-only readiness state without contacting a provider."""
    if provider == "Select provider":
        return "unconnected"
    if not api_key_present and provider not in {"Local Whisper", "Windows Voice", "Local detector", "Local music files", "Local singing model", "Disabled", "Home Assistant"}:
        return "key_required"
    if provider in _APPROVED_TESTS:
        return "adapter_ready"
    return "saved_locally"


def run_approved_connection_test(provider: str, api_key: str, opener=urlopen, timeout: float = 8.0) -> ConnectionTestResult:
    """Make one user-approved HTTPS request for a supported provider only."""
    test = _APPROVED_TESTS.get(provider)
    if not test:
        return ConnectionTestResult(
            "adapter_unavailable",
            "Arthur has saved the local settings, but no approved live-test adapter is installed for this provider. It is not connected.",
        )
    if not api_key.strip():
        return ConnectionTestResult("key_required", "A developer API key is required before Arthur can run this approved connection test.")

    request = Request(test["url"], headers=test["headers"](api_key.strip()), method="GET")
    try:
        with opener(request, timeout=timeout) as response:
            status = getattr(response, "status", response.getcode())
        if 200 <= int(status) < 300:
            return ConnectionTestResult("test_passed", "Approved connection test passed. Arthur reached the provider; this does not grant any automatic action permission.")
        return ConnectionTestResult("test_failed", f"The provider returned HTTP {status}. Arthur is not connected.")
    except HTTPError as error:
        return ConnectionTestResult("test_failed", f"The provider returned HTTP {error.code}. Check the key, project access, and provider account; Arthur is not connected.")
    except URLError:
        return ConnectionTestResult("test_failed", "Arthur could not reach the provider. Check internet access or firewall settings; Arthur is not connected.")
    except OSError:
        return ConnectionTestResult("test_failed", "Arthur could not start the approved connection test. Arthur is not connected.")
