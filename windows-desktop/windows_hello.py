"""Optional Windows Hello verification bridge for the protected Spatial room.

Arthur never receives a face image, facial template, or biometric comparison
result beyond the Windows-provided verification outcome. Users enroll their
face or PIN in Windows Settings; the operating system owns that biometric data.
"""

from __future__ import annotations

import asyncio


def availability() -> tuple[bool, str]:
    try:
        from winrt.windows.security.credentials.ui import UserConsentVerifier  # noqa: F401
    except ImportError:
        return False, "Windows Hello adapter is optional and not installed. Install it or choose password access for the Spatial room."
    return True, "Windows Hello adapter is installed. Configure face or PIN in Windows Settings before using it."


async def _verify_async(message: str) -> tuple[bool, str]:
    from winrt.windows.security.credentials.ui import UserConsentVerifier, UserConsentVerificationResult

    result = await UserConsentVerifier.request_verification_async(message)
    if result == UserConsentVerificationResult.VERIFIED:
        return True, "Windows Hello verified this local session."
    return False, f"Windows Hello did not verify this session ({result.name}). Retry Windows Hello, check Windows Settings, or change the room access method after verification."


def verify(message: str = "Open Arthur’s protected Spatial workspace") -> tuple[bool, str]:
    """Ask the OS to verify the current Windows Hello user.

    It does not open a camera from Arthur, scan a face, or cache any biometric
    value. On unsupported platforms, it returns a clear unavailable state.
    """
    enabled, detail = availability()
    if not enabled:
        return False, detail
    try:
        return asyncio.run(_verify_async(message))
    except Exception as error:  # Windows feature availability varies by device
        return False, f"Windows Hello was unavailable: {error}. Check Windows Hello setup or choose password access after you regain access."
