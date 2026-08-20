"""Prepare Arthur's professional hawk source artwork for Windows packaging.

The generated master artwork stays outside the source tree. This script creates
the bundled 512px RGBA PNG consumed by the ICO packaging step.
"""

from pathlib import Path

from PIL import Image


ROOT = Path(__file__).resolve().parents[1]
SOURCE = Path("/home/ubuntu/webdev-static-assets/arthur-professional-hawk.png")
TARGET = ROOT / "assets" / "arthur_hawk.png"


def main() -> None:
    if not SOURCE.exists():
        raise SystemExit(f"Missing professional hawk artwork: {SOURCE}")
    with Image.open(SOURCE) as image:
        prepared = image.convert("RGBA").resize((512, 512), Image.Resampling.LANCZOS)
        prepared.save(TARGET, format="PNG", optimize=True)
    print(f"Prepared {TARGET}")


if __name__ == "__main__":
    main()
