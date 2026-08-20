"""Local regression checks for the protected Spatial-room password verifier."""

import spatial_access


def main() -> None:
    vault: dict[str, str] = {}
    original_get = spatial_access.get_secret
    original_set = spatial_access.set_secret
    original_delete = spatial_access.delete_secret
    try:
        spatial_access.get_secret = lambda label: vault.get(label, "")
        spatial_access.set_secret = lambda label, value: (vault.__setitem__(label, value) or True)
        spatial_access.delete_secret = lambda label: vault.pop(label, None)

        assert spatial_access.has_password() is False
        ok, detail = spatial_access.set_password("ArthurRoom42!")
        assert ok is True
        assert "Credential Manager" in detail
        assert spatial_access.has_password() is True
        assert "ArthurRoom42!" not in vault[spatial_access.PASSWORD_LABEL]
        assert vault[spatial_access.PASSWORD_LABEL].startswith("scrypt-v1$")
        assert spatial_access.verify_password("ArthurRoom42!") is True
        assert spatial_access.verify_password("not-the-password") is False
        spatial_access.clear_password()
        assert spatial_access.has_password() is False
        too_short, _ = spatial_access.set_password("short")
        assert too_short is False
    finally:
        spatial_access.get_secret = original_get
        spatial_access.set_secret = original_set
        spatial_access.delete_secret = original_delete


if __name__ == "__main__":
    main()
