"""Read-only packaged-runtime readiness checks for Arthur's desktop build.

Dependencies and openWakeWord models are prepared during the Windows build, not
silently downloaded on every user startup. This keeps startup reliable offline
and avoids changing a user's runtime environment after installation.
"""

from __future__ import annotations

from dataclasses import dataclass
from importlib.util import find_spec
from pathlib import Path
from typing import Iterable


REQUIRED_RUNTIME_MODULES = ("openwakeword", "sounddevice", "pyttsx3", "cv2")


@dataclass(frozen=True)
class RuntimeReadiness:
    ready: bool
    available_modules: tuple[str, ...]
    missing_modules: tuple[str, ...]
    model_count: int
    detail: str


def openwakeword_model_paths() -> tuple[Path, ...]:
    """Find packaged local wake-word assets without downloading or opening audio."""

    try:
        import openwakeword
    except ImportError:
        return ()
    root = Path(openwakeword.__file__).resolve().parent / "resources" / "models"
    if not root.is_dir():
        return ()
    return tuple(sorted(path for path in root.iterdir() if path.suffix.casefold() in {".onnx", ".tflite"}))


def packaged_runtime_readiness(required_modules: Iterable[str] = REQUIRED_RUNTIME_MODULES) -> RuntimeReadiness:
    """Report whether the installer contains the normal local runtime components."""

    modules = tuple(required_modules)
    available = tuple(module for module in modules if find_spec(module) is not None)
    missing = tuple(module for module in modules if module not in available)
    models = openwakeword_model_paths() if "openwakeword" in available else ()
    if missing:
        return RuntimeReadiness(
            ready=False,
            available_modules=available,
            missing_modules=missing,
            model_count=len(models),
            detail=f"The packaged runtime is missing: {', '.join(missing)}. Rebuild or reinstall Arthur; it will not download packages during startup.",
        )
    if not models:
        return RuntimeReadiness(
            ready=False,
            available_modules=available,
            missing_modules=(),
            model_count=0,
            detail="The packaged openWakeWord runtime has no local model assets. Rebuild Arthur with the runtime-asset preparation step.",
        )
    return RuntimeReadiness(
        ready=True,
        available_modules=available,
        missing_modules=(),
        model_count=len(models),
        detail=f"Packaged local runtime ready: {', '.join(available)}; {len(models)} openWakeWord model asset(s) available locally.",
    )
