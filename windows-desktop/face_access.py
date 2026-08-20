"""Optional, local-only camera face access for Arthur's protected Spatial room.

This experimental adapter is deliberately separate from Windows Hello. It opens a
user-selected camera only after explicit enrolment or verification approval,
processes frames in memory, and stores no image or video. Its compact OpenCV
LBPH recognizer model is encrypted locally; the encryption key and the hashed
recovery secret live in the operating-system credential manager.

It is not equivalent to Windows Hello and must not be used as the only
protection for highly sensitive data.
"""

from __future__ import annotations

import base64
import hashlib
import hmac
import json
import math
import os
import tempfile
import time
from pathlib import Path

from secure_store import delete_secret, get_secret, set_secret


FACE_KEY_LABEL = "SPATIAL_ROOM_FACE_TEMPLATE_KEY"
RECOVERY_LABEL = "SPATIAL_ROOM_FACE_RECOVERY_VERIFIER"
LOCKOUT_LABEL = "SPATIAL_ROOM_FACE_LOCKOUT"
TEMPLATE_PATH = Path(__file__).resolve().parent / "data" / "biometrics" / "spatial_face_template.enc"
SAMPLE_COUNT = 14
MATCH_FRAMES_REQUIRED = 5
MATCH_CONFIDENCE_MAX = 62.0
MAX_FAILED_ATTEMPTS = 3
LOCKOUT_SECONDS = 60


def _encode(value: bytes) -> str:
    return base64.urlsafe_b64encode(value).decode("ascii")


def _decode(value: str) -> bytes:
    return base64.urlsafe_b64decode(value.encode("ascii"))


def _optional_modules():
    try:
        import cv2  # type: ignore
        import numpy as np  # type: ignore
        from cryptography.fernet import Fernet  # type: ignore
    except ImportError as error:
        return None, None, None, f"Optional local-camera face packages are missing ({error.name})."
    if not hasattr(cv2, "face") or not hasattr(cv2.face, "LBPHFaceRecognizer_create"):
        return None, None, None, "OpenCV contrib face support is missing. Install the reviewed local-camera face requirements."
    return cv2, np, Fernet, "Optional local-camera face adapter is ready for your explicit approval."


def optional_dependency_status() -> tuple[bool, str]:
    cv2, _np, _fernet, detail = _optional_modules()
    return cv2 is not None, detail


def _lockout_state() -> dict[str, float | int]:
    """Read only counter/timer metadata; this never stores a frame or face data."""
    try:
        stored = json.loads(get_secret(LOCKOUT_LABEL) or "{}")
        return {
            "failed_attempts": max(0, int(stored.get("failed_attempts", 0))),
            "locked_until": max(0.0, float(stored.get("locked_until", 0))),
        }
    except (TypeError, ValueError, json.JSONDecodeError):
        return {"failed_attempts": 0, "locked_until": 0.0}


def _save_lockout_state(failed_attempts: int, locked_until: float) -> None:
    set_secret(LOCKOUT_LABEL, json.dumps({"failed_attempts": int(failed_attempts), "locked_until": float(locked_until)}))


def face_lockout_status(now: float | None = None) -> tuple[int, int]:
    """Return remaining cooldown seconds and the current failed-attempt count."""
    current_time = time.time() if now is None else float(now)
    state = _lockout_state()
    locked_until = float(state["locked_until"])
    if locked_until and locked_until <= current_time:
        if state["failed_attempts"]:
            delete_secret(LOCKOUT_LABEL)
        return 0, 0
    if not locked_until:
        return 0, int(state["failed_attempts"])
    return max(1, math.ceil(locked_until - current_time)), int(state["failed_attempts"])


def register_face_failure(now: float | None = None) -> tuple[int, int]:
    """Record a completed non-match and apply a short local-only cooldown if needed."""
    current_time = time.time() if now is None else float(now)
    remaining, attempts = face_lockout_status(current_time)
    if remaining:
        return attempts, remaining
    attempts += 1
    if attempts >= MAX_FAILED_ATTEMPTS:
        _save_lockout_state(attempts, current_time + LOCKOUT_SECONDS)
        return attempts, LOCKOUT_SECONDS
    _save_lockout_state(attempts, 0.0)
    return attempts, 0


def clear_face_failures() -> None:
    """Clear local failed-attempt metadata after a successful check or reset."""
    delete_secret(LOCKOUT_LABEL)


def _cipher(create: bool = False):
    _cv2, _np, Fernet, detail = _optional_modules()
    if Fernet is None:
        return None, detail
    raw_key = get_secret(FACE_KEY_LABEL)
    if not raw_key and create:
        raw_key = Fernet.generate_key().decode("ascii")
        if not set_secret(FACE_KEY_LABEL, raw_key):
            return None, "Arthur could not save the local template-encryption key in Windows Credential Manager."
    if not raw_key:
        return None, "No local face-template encryption key is available. Enrol again or use another access method."
    try:
        return Fernet(raw_key.encode("ascii")), "Local encrypted template store is available."
    except (ValueError, TypeError):
        return None, "The local face-template key is invalid. Delete and enrol again."


def has_enrollment() -> bool:
    return TEMPLATE_PATH.exists() and bool(get_secret(FACE_KEY_LABEL)) and bool(get_secret(RECOVERY_LABEL))


def set_recovery_secret(value: str) -> tuple[bool, str]:
    if len(value) < 12:
        return False, "Choose a recovery secret with at least 12 characters. It is needed only to recover from a failed local face check."
    salt = os.urandom(16)
    derived = hashlib.scrypt(value.encode("utf-8"), salt=salt, n=2**14, r=8, p=1)
    payload = f"scrypt-v1${_encode(salt)}${_encode(derived)}"
    if not set_secret(RECOVERY_LABEL, payload):
        return False, "Arthur could not save the recovery-secret verifier in Windows Credential Manager."
    return True, "Recovery secret verifier saved locally."


def verify_recovery_secret(value: str) -> bool:
    stored = get_secret(RECOVERY_LABEL)
    try:
        scheme, encoded_salt, encoded_hash = stored.split("$", 2)
        if scheme != "scrypt-v1":
            return False
        candidate = hashlib.scrypt(value.encode("utf-8"), salt=_decode(encoded_salt), n=2**14, r=8, p=1)
        return hmac.compare_digest(candidate, _decode(encoded_hash))
    except (ValueError, TypeError):
        return False


def _write_encrypted_template(model_bytes: bytes) -> tuple[bool, str]:
    cipher, detail = _cipher(create=True)
    if cipher is None:
        return False, detail
    TEMPLATE_PATH.parent.mkdir(parents=True, exist_ok=True)
    encrypted = cipher.encrypt(model_bytes)
    temporary = TEMPLATE_PATH.with_suffix(".tmp")
    try:
        temporary.write_bytes(encrypted)
        try:
            temporary.chmod(0o600)
        except OSError:
            pass
        temporary.replace(TEMPLATE_PATH)
        return True, "Encrypted local face template saved. No raw camera image or video was retained."
    except OSError as error:
        return False, f"Arthur could not save the encrypted local face template: {error}"


def _read_model_file() -> tuple[bytes | None, str]:
    cipher, detail = _cipher()
    if cipher is None:
        return None, detail
    try:
        return cipher.decrypt(TEMPLATE_PATH.read_bytes()), "Encrypted local face template loaded for this check."
    except Exception:
        return None, "Arthur could not read the encrypted local face template. Delete and enrol again."


def delete_enrollment() -> None:
    """Permanently erase the encrypted template, its key, and recovery verifier."""
    try:
        TEMPLATE_PATH.unlink(missing_ok=True)
    except OSError:
        pass
    delete_secret(FACE_KEY_LABEL)
    delete_secret(RECOVERY_LABEL)
    clear_face_failures()


def _cascade(cv2):
    path = Path(cv2.data.haarcascades) / "haarcascade_frontalface_default.xml"
    detector = cv2.CascadeClassifier(str(path))
    return detector if not detector.empty() else None


def camera_acceptance_test(camera_index: int = 0, max_seconds: float = 5.0) -> tuple[bool, str]:
    """Run a visible, user-started local camera readiness check without enrolment.

    The test opens the selected camera only for this window, displays a clear
    camera-active indicator, and drops every frame immediately. Escape or Q
    cancels the test with no image, model, or log retained.
    """
    cv2, _np, _Fernet, detail = _optional_modules()
    if cv2 is None:
        return False, detail
    camera = cv2.VideoCapture(int(camera_index))
    if not camera.isOpened():
        return False, f"Arthur could not open local camera {camera_index}. Check Windows camera permissions and retry the acceptance test."
    frames_seen = 0
    started = time.monotonic()
    try:
        while time.monotonic() - started < max(1.0, float(max_seconds)):
            ok, frame = camera.read()
            if not ok:
                continue
            frames_seen += 1
            preview = frame.copy()
            cv2.putText(preview, "ARTHUR CAMERA ACTIVE — readiness test; ESC cancels; no video saved", (12, 28), cv2.FONT_HERSHEY_SIMPLEX, 0.48, (78, 214, 255), 2)
            cv2.imshow("Arthur local camera acceptance test — no video saved", preview)
            if cv2.waitKey(1) & 0xFF in (27, ord("q")):
                return False, "Local camera acceptance test was cancelled. No image, video, model, or failed frame was saved."
    finally:
        camera.release()
        cv2.destroyAllWindows()
    if frames_seen:
        return True, "Local camera readiness test passed. Arthur displayed the camera-active preview and retained no image, video, model, or failed frame."
    return False, "Arthur could not read a local camera frame. Check the camera shutter, Windows privacy permission, and selected camera index; no frame was saved."


def enroll(camera_index: int = 0) -> tuple[bool, str]:
    """Capture transient samples and save only an encrypted local recognizer model.

    The preview window shows a clear camera-active notice. Escape or Q cancels
    without keeping a raw camera frame; a model is written only after enough
    face samples were observed.
    """
    cv2, np, _Fernet, detail = _optional_modules()
    if cv2 is None or np is None:
        return False, detail
    detector = _cascade(cv2)
    if detector is None:
        return False, "Arthur could not load the local face detector. Reinstall the optional local-camera face requirements."
    camera = cv2.VideoCapture(int(camera_index))
    if not camera.isOpened():
        return False, f"Arthur could not open local camera {camera_index}. Check Windows camera permissions and retry."
    samples = []
    started = time.monotonic()
    try:
        while len(samples) < SAMPLE_COUNT and time.monotonic() - started < 25:
            ok, frame = camera.read()
            if not ok:
                continue
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            faces = detector.detectMultiScale(gray, scaleFactor=1.15, minNeighbors=5, minSize=(90, 90))
            preview = frame.copy()
            for x, y, width, height in faces[:1]:
                crop = cv2.resize(gray[y:y + height, x:x + width], (160, 160))
                samples.append(crop)
                cv2.rectangle(preview, (x, y), (x + width, y + height), (78, 214, 255), 2)
            cv2.putText(preview, f"ARTHUR CAMERA ACTIVE — enrolment {len(samples)}/{SAMPLE_COUNT}; ESC cancels", (12, 28), cv2.FONT_HERSHEY_SIMPLEX, 0.52, (78, 214, 255), 2)
            cv2.imshow("Arthur local face enrolment — no video saved", preview)
            if cv2.waitKey(1) & 0xFF in (27, ord("q")):
                return False, "Local face enrolment was cancelled. No image, video, or template was saved."
    finally:
        camera.release()
        cv2.destroyAllWindows()
    if len(samples) < SAMPLE_COUNT:
        return False, "Arthur could not collect enough clear local face samples. Improve lighting, face the camera, and try again. No image or template was saved."
    recognizer = cv2.face.LBPHFaceRecognizer_create()
    recognizer.train(samples, np.array([1] * len(samples), dtype=np.int32))
    with tempfile.NamedTemporaryFile(suffix=".yml", delete=False) as temporary:
        model_path = Path(temporary.name)
    try:
        recognizer.write(str(model_path))
        return _write_encrypted_template(model_path.read_bytes())
    finally:
        model_path.unlink(missing_ok=True)


def verify(camera_index: int = 0) -> tuple[bool, str]:
    """Run a brief, visible, local comparison against the encrypted model."""
    cv2, _np, _Fernet, detail = _optional_modules()
    if cv2 is None:
        return False, detail
    model_bytes, detail = _read_model_file()
    if model_bytes is None:
        return False, detail
    detector = _cascade(cv2)
    if detector is None:
        return False, "Arthur could not load the local face detector. Reinstall the optional local-camera face requirements."
    with tempfile.NamedTemporaryFile(suffix=".yml", delete=False) as temporary:
        model_path = Path(temporary.name)
        temporary.write(model_bytes)
    recognizer = cv2.face.LBPHFaceRecognizer_create()
    try:
        recognizer.read(str(model_path))
    except Exception:
        model_path.unlink(missing_ok=True)
        return False, "Arthur could not load the encrypted local face template. Delete and enrol again."
    camera = cv2.VideoCapture(int(camera_index))
    if not camera.isOpened():
        model_path.unlink(missing_ok=True)
        return False, f"Arthur could not open local camera {camera_index}. Check Windows camera permissions and retry."
    matches = 0
    started = time.monotonic()
    try:
        while matches < MATCH_FRAMES_REQUIRED and time.monotonic() - started < 12:
            ok, frame = camera.read()
            if not ok:
                continue
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            faces = detector.detectMultiScale(gray, scaleFactor=1.15, minNeighbors=5, minSize=(90, 90))
            preview = frame.copy()
            for x, y, width, height in faces[:1]:
                crop = cv2.resize(gray[y:y + height, x:x + width], (160, 160))
                label, confidence = recognizer.predict(crop)
                if label == 1 and confidence <= MATCH_CONFIDENCE_MAX:
                    matches += 1
                cv2.rectangle(preview, (x, y), (x + width, y + height), (78, 214, 255), 2)
            cv2.putText(preview, f"ARTHUR CAMERA ACTIVE — verify {matches}/{MATCH_FRAMES_REQUIRED}; ESC cancels", (12, 28), cv2.FONT_HERSHEY_SIMPLEX, 0.52, (78, 214, 255), 2)
            cv2.imshow("Arthur local face verification — no video saved", preview)
            if cv2.waitKey(1) & 0xFF in (27, ord("q")):
                return False, "Local face verification was cancelled. No camera frame was saved."
    finally:
        camera.release()
        cv2.destroyAllWindows()
        model_path.unlink(missing_ok=True)
    if matches >= MATCH_FRAMES_REQUIRED:
        return True, "Local camera face check verified this Arthur session. No camera frame was saved."
    return False, "Local camera face check did not verify this session. Improve lighting, retry, or use the recovery secret to reset access."
