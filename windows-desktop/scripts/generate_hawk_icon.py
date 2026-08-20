"""Create the Windows .ico from Arthur's bundled PNG hawk asset.

Run only during packaging. The desktop app never runs this script.
"""
from pathlib import Path

from PIL import Image


ROOT = Path(__file__).resolve().parents[1]
ASSETS = ROOT / "assets"
SOURCE = ASSETS / "arthur_hawk.png"
TARGET = ASSETS / "arthur_hawk.ico"


def main() -> None:
    if not SOURCE.exists():
        raise SystemExit(f"Missing hawk source image: {SOURCE}")
    with Image.open(SOURCE).convert("RGBA") as image:
        image.save(TARGET, format="ICO", sizes=[(16, 16), (24, 24), (32, 32), (48, 48), (64, 64), (128, 128), (256, 256)])
    print(f"Generated {TARGET}")


if __name__ == "__main__":
    main()
