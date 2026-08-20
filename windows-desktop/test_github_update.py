"""Regression checks for Arthur's manual-only GitHub release metadata helper."""

import hashlib
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest.mock import patch

from github_update import build_release_record, download_release_asset, fetch_latest_release, handoff_verified_installer, validate_repository


def main():
    assert validate_repository("bryagisubizo-bit/arthur") == "bryagisubizo-bit/arthur"
    try:
        validate_repository("https://github.com/owner/repo")
    except ValueError:
        pass
    else:
        raise AssertionError("Repository URLs must not be treated as an update source.")

    record = build_release_record({
        "tag_name": "v1.2.0",
        "name": "Arthur 1.2.0",
        "published_at": "2026-08-19T00:00:00Z",
        "html_url": "https://github.com/owner/repo/releases/tag/v1.2.0",
        "assets": [{"name": "Arthur-Setup.exe", "size": 1234, "browser_download_url": "https://github.com/owner/repo/releases/download/v1.2.0/Arthur-Setup.exe", "digest": "sha256:" + "a" * 64}],
    })
    assert record["tag"] == "v1.2.0"
    assert record["assets"][0]["name"] == "Arthur-Setup.exe"
    assert record["assets"][0]["digest"] == "sha256:" + "a" * 64

    payload = b"Arthur verified release fixture"
    digest = hashlib.sha256(payload).hexdigest()
    verified_release = {"assets": [{"name": "Arthur-Setup.exe", "size": len(payload), "download_url": "https://github.com/owner/repo/releases/download/v1.2.0/Arthur-Setup.exe", "digest": f"sha256:{digest}"}]}
    assert download_release_asset(verified_release, "Arthur-Setup.exe", approved=False)["kind"] == "download-not-approved"
    with TemporaryDirectory() as temporary_directory:
        def fake_retrieve(url, destination):
            Path(destination).write_bytes(payload)
            return str(destination), None

        with patch("github_update.urlretrieve", fake_retrieve):
            downloaded = download_release_asset(verified_release, "Arthur-Setup.exe", approved=True, destination_dir=Path(temporary_directory))
        assert downloaded["ok"] is True
        assert Path(downloaded["path"]).read_bytes() == payload
        assert handoff_verified_installer(downloaded["path"], approved=False)["kind"] == "install-not-approved"

    invalid = fetch_latest_release("not a repository")
    assert invalid["ok"] is False
    assert invalid["kind"] == "invalid-repository"
    print("Arthur GitHub update checks passed.")


if __name__ == "__main__":
    main()
