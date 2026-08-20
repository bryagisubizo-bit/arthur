"""Secure provider-secret storage for Arthur.

On Windows, keyring normally uses Windows Credential Manager. The project never
writes provider secrets to arthur_config.json. If no secure backend is available,
secrets can still be supplied through environment variables for development.
"""

import os

SERVICE_NAME = "ArthurDesktopAssistant"

try:
    import keyring
except ImportError:  # pragma: no cover - handled by the dependency installer
    keyring = None


def env_name(label: str) -> str:
    cleaned = "".join(ch if ch.isalnum() else "_" for ch in label.upper())
    return f"ARTHUR_{cleaned}_API_KEY"


def get_secret(label: str) -> str:
    value = os.getenv(env_name(label), "").strip()
    if value:
        return value
    if keyring is None:
        return ""
    try:
        return keyring.get_password(SERVICE_NAME, label) or ""
    except Exception:
        return ""


def set_secret(label: str, value: str) -> bool:
    value = value.strip()
    if not value:
        return True
    if keyring is None:
        return False
    try:
        keyring.set_password(SERVICE_NAME, label, value)
        return True
    except Exception:
        return False


def delete_secret(label: str) -> None:
    if keyring is None:
        return
    try:
        keyring.delete_password(SERVICE_NAME, label)
    except Exception:
        pass
