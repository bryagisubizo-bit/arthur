"""Local access control for Arthur's protected Spatial workspace.

The password verifier is stored only in the operating-system credential manager
through ``secure_store``. Arthur deliberately does not enroll, retain, upload,
or compare faces. A user selects either this password method or OS-managed
Windows Hello for protected-room access.
"""

from __future__ import annotations

import base64
import hashlib
import hmac
import os

from secure_store import delete_secret, get_secret, set_secret


PASSWORD_LABEL = "SPATIAL_ROOM_PASSWORD_VERIFIER"


def _encode(value: bytes) -> str:
    return base64.urlsafe_b64encode(value).decode("ascii")


def _decode(value: str) -> bytes:
    return base64.urlsafe_b64decode(value.encode("ascii"))


def has_password() -> bool:
    """Return whether an OS-credential-manager password verifier exists."""
    return bool(get_secret(PASSWORD_LABEL))


def set_password(password: str) -> tuple[bool, str]:
    """Store a salted scrypt verifier, never the plaintext password."""
    if len(password) < 10:
        return False, "Choose a Spatial-room password with at least 10 characters."
    salt = os.urandom(16)
    derived = hashlib.scrypt(password.encode("utf-8"), salt=salt, n=2**14, r=8, p=1)
    payload = f"scrypt-v1${_encode(salt)}${_encode(derived)}"
    if not set_secret(PASSWORD_LABEL, payload):
        return False, "Arthur could not access Windows Credential Manager, so it did not save a room password."
    return True, "Spatial-room password saved in Windows Credential Manager."


def clear_password() -> None:
    """Remove an unused local verifier after an explicit switch to Windows Hello."""
    delete_secret(PASSWORD_LABEL)


def verify_password(password: str) -> bool:
    """Verify a local password against its keyring-backed salted verifier."""
    stored = get_secret(PASSWORD_LABEL)
    try:
        scheme, encoded_salt, encoded_hash = stored.split("$", 2)
        if scheme != "scrypt-v1":
            return False
        candidate = hashlib.scrypt(password.encode("utf-8"), salt=_decode(encoded_salt), n=2**14, r=8, p=1)
        return hmac.compare_digest(candidate, _decode(encoded_hash))
    except (ValueError, TypeError):
        return False
