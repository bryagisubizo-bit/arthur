"""Regression checks for local-camera face-access storage boundaries.

These tests deliberately avoid importing optional camera packages or opening a
camera. They verify only that recovery metadata is hashed and that deletion
removes every locally retained face-access artifact.
"""

from pathlib import Path
from tempfile import TemporaryDirectory

import face_access


def main() -> None:
    vault: dict[str, str] = {}
    original_get = face_access.get_secret
    original_set = face_access.set_secret
    original_delete = face_access.delete_secret
    original_path = face_access.TEMPLATE_PATH
    try:
        face_access.get_secret = lambda label: vault.get(label, "")
        face_access.set_secret = lambda label, value: (vault.__setitem__(label, value) or True)
        face_access.delete_secret = lambda label: vault.pop(label, None)
        with TemporaryDirectory() as directory:
            face_access.TEMPLATE_PATH = Path(directory) / "spatial_face_template.enc"
            recovery = "Arthur-local-face-recovery"
            ok, detail = face_access.set_recovery_secret(recovery)
            assert ok is True
            assert "verifier" in detail
            assert recovery not in vault[face_access.RECOVERY_LABEL]
            assert vault[face_access.RECOVERY_LABEL].startswith("scrypt-v1$")
            assert face_access.verify_recovery_secret(recovery) is True
            assert face_access.verify_recovery_secret("wrong recovery secret") is False

            assert face_access.face_lockout_status(now=100.0) == (0, 0)
            assert face_access.register_face_failure(now=100.0) == (1, 0)
            assert face_access.register_face_failure(now=101.0) == (2, 0)
            attempts, cooldown = face_access.register_face_failure(now=102.0)
            assert attempts == face_access.MAX_FAILED_ATTEMPTS
            assert cooldown == face_access.LOCKOUT_SECONDS
            assert face_access.face_lockout_status(now=132.0) == (30, face_access.MAX_FAILED_ATTEMPTS)
            assert face_access.face_lockout_status(now=163.0) == (0, 0)

            face_access.TEMPLATE_PATH.parent.mkdir(parents=True, exist_ok=True)
            face_access.TEMPLATE_PATH.write_bytes(b"encrypted-test-template")
            vault[face_access.FACE_KEY_LABEL] = "test-key-present"
            assert face_access.has_enrollment() is True
            face_access.delete_enrollment()
            assert face_access.TEMPLATE_PATH.exists() is False
            assert face_access.has_enrollment() is False
            assert face_access.FACE_KEY_LABEL not in vault
            assert face_access.RECOVERY_LABEL not in vault
            assert face_access.LOCKOUT_LABEL not in vault
    finally:
        face_access.get_secret = original_get
        face_access.set_secret = original_set
        face_access.delete_secret = original_delete
        face_access.TEMPLATE_PATH = original_path


if __name__ == "__main__":
    main()
