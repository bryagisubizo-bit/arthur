"""Regression checks for the optional OS-managed Windows Hello boundary."""

import windows_hello


def main() -> None:
    available, detail = windows_hello.availability()
    assert isinstance(available, bool)
    assert isinstance(detail, str) and detail

    original_availability = windows_hello.availability
    try:
        windows_hello.availability = lambda: (False, "Password fallback required.")
        verified, result = windows_hello.verify("Open Arthur’s protected Spatial workspace")
        assert verified is False
        assert result == "Password fallback required."
    finally:
        windows_hello.availability = original_availability


if __name__ == "__main__":
    main()
