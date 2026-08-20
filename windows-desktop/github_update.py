"""Small, manual-only GitHub Releases metadata client for Arthur.

This module supports a manual, two-step release process only: the user first
approves a single download with a release-provided SHA-256 digest, then may
separately approve handing the verified local installer to Windows. It never
polls, schedules retries, or automatically launches an installer.
"""

from __future__ import annotations

import json
import hashlib
import os
import re
from pathlib import Path
from typing import Any
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen, urlretrieve


REPOSITORY_PATTERN = re.compile(r"^[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+$")


def validate_repository(repository: str) -> str:
    """Return a normalized owner/repository value or raise ValueError."""
    normalized = repository.strip().strip("/")
    if not REPOSITORY_PATTERN.fullmatch(normalized):
        raise ValueError("Use the GitHub owner/repository format, for example octocat/Hello-World.")
    return normalized


def build_release_record(payload: dict[str, Any]) -> dict[str, Any]:
    """Extract the small, display-safe subset Arthur needs from GitHub metadata."""
    assets = payload.get("assets") or []
    display_assets = [
        {
            "name": str(asset.get("name", "Unnamed asset")),
            "size": int(asset.get("size") or 0),
            "download_url": str(asset.get("browser_download_url") or ""),
            "digest": str(asset.get("digest") or ""),
            "content_type": str(asset.get("content_type") or ""),
        }
        for asset in assets
        if isinstance(asset, dict)
    ]
    return {
        "tag": str(payload.get("tag_name") or "Unversioned release"),
        "name": str(payload.get("name") or payload.get("tag_name") or "GitHub release"),
        "published_at": str(payload.get("published_at") or "Not provided"),
        "page_url": str(payload.get("html_url") or ""),
        "assets": display_assets,
    }


def fetch_latest_release(repository: str, token: str = "", timeout_seconds: int = 8) -> dict[str, Any]:
    """Fetch GitHub release metadata for one manual check; never fetch assets."""
    try:
        normalized = validate_repository(repository)
    except ValueError as error:
        return {"ok": False, "kind": "invalid-repository", "message": str(error)}

    headers = {
        "Accept": "application/vnd.github+json",
        "User-Agent": "Arthur-Desktop-Manual-Release-Check",
        "X-GitHub-Api-Version": "2022-11-28",
    }
    if token.strip():
        headers["Authorization"] = f"Bearer {token.strip()}"
    request = Request(f"https://api.github.com/repos/{normalized}/releases/latest", headers=headers)
    try:
        with urlopen(request, timeout=timeout_seconds) as response:  # nosec B310 - fixed HTTPS API origin
            payload = json.loads(response.read().decode("utf-8"))
    except HTTPError as error:
        if error.code == 404:
            return {
                "ok": False,
                "kind": "no-release",
                "message": "No published GitHub Release was found. Publish a versioned release before Arthur can offer update metadata.",
            }
        return {"ok": False, "kind": "http-error", "message": f"GitHub returned HTTP {error.code}. No update was downloaded."}
    except URLError:
        return {"ok": False, "kind": "network-error", "message": "Arthur could not reach GitHub. No background retry was scheduled."}
    except (TimeoutError, json.JSONDecodeError):
        return {"ok": False, "kind": "read-error", "message": "Arthur could not read GitHub release metadata. No update was downloaded."}

    if not isinstance(payload, dict):
        return {"ok": False, "kind": "read-error", "message": "GitHub returned unexpected release metadata."}
    return {"ok": True, "kind": "release", "release": build_release_record(payload)}


def _sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as file:
        for chunk in iter(lambda: file.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _select_verified_asset(release: dict[str, Any], asset_name: str) -> dict[str, Any] | None:
    for asset in release.get("assets") or []:
        if isinstance(asset, dict) and asset.get("name") == asset_name:
            return asset
    return None


def download_release_asset(
    release: dict[str, Any],
    asset_name: str,
    *,
    approved: bool,
    destination_dir: Path | None = None,
) -> dict[str, Any]:
    """Download one chosen GitHub asset only after explicit approval.

    GitHub's release API supplies a SHA-256 digest on supported assets. Arthur
    refuses an installer asset lacking that digest instead of treating an
    unverified binary as an update. Callers should render this result and ask a
    second, independent question before calling ``handoff_verified_installer``.
    """
    if not approved:
        return {"ok": False, "kind": "download-not-approved", "message": "Download was not approved. No release asset was requested."}
    asset = _select_verified_asset(release, asset_name)
    if asset is None:
        return {"ok": False, "kind": "unknown-asset", "message": "That release asset is not part of the latest metadata record."}
    safe_name = Path(str(asset.get("name") or "")).name
    url = str(asset.get("download_url") or "")
    digest_record = str(asset.get("digest") or "")
    if not safe_name or safe_name != asset.get("name") or not url.startswith("https://"):
        return {"ok": False, "kind": "invalid-asset", "message": "Release asset metadata is incomplete or unsafe. No download was started."}
    if not digest_record.lower().startswith("sha256:") or len(digest_record.split(":", 1)[1]) != 64:
        return {"ok": False, "kind": "digest-unavailable", "message": "GitHub did not supply a SHA-256 digest for this asset. Arthur will not download an unverified installer."}

    target_dir = destination_dir or (Path.home() / "Downloads" / "Arthur Updates")
    target_dir.mkdir(parents=True, exist_ok=True)
    destination = target_dir / safe_name
    try:
        urlretrieve(url, destination)  # nosec B310 - HTTPS URL supplied by the selected GitHub release asset
        actual_digest = _sha256_file(destination)
    except (OSError, URLError) as error:
        if destination.exists():
            destination.unlink(missing_ok=True)
        return {"ok": False, "kind": "download-error", "message": f"Arthur could not download the chosen release asset: {error}"}

    expected_digest = digest_record.split(":", 1)[1].lower()
    if actual_digest.lower() != expected_digest:
        destination.unlink(missing_ok=True)
        return {"ok": False, "kind": "digest-mismatch", "message": "The downloaded asset did not match GitHub's SHA-256 digest and was deleted."}
    return {
        "ok": True,
        "kind": "downloaded-verified",
        "message": "The asset was downloaded and verified. It has not been launched.",
        "path": str(destination),
        "sha256": actual_digest,
    }


def handoff_verified_installer(path: str | Path, *, approved: bool) -> dict[str, Any]:
    """Hand a verified installer to Windows only after a second explicit approval."""
    if not approved:
        return {"ok": False, "kind": "install-not-approved", "message": "Installer launch was not approved. Nothing was started."}
    installer = Path(path).expanduser().resolve()
    if installer.suffix.lower() not in {".exe", ".msi"} or not installer.is_file():
        return {"ok": False, "kind": "invalid-installer", "message": "Arthur can hand off only an existing verified .exe or .msi installer."}
    if os.name != "nt":
        return {"ok": False, "kind": "windows-only", "message": "Installer handoff is available only in the Windows desktop build."}
    os.startfile(str(installer))  # type: ignore[attr-defined]  # nosec B606 - local user-approved verified installer
    return {"ok": True, "kind": "installer-started", "message": "Windows was asked to open the verified installer. Arthur does not elevate or answer the installer's prompts."}
