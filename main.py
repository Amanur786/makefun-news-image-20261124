#!/usr/bin/env python3
"""make.fun entry: "Sum up 24 November's world news in one image".

Writes the entry image to /output/entry.png. The image is committed in
this repository as entry.png (a one-page newspaper front page drawn with
Pillow by build_poster.py, summing up the real world news of Tuesday
24 November 2026); this program only copies it, byte for byte, so both
runs write identical bytes. Standard library only, no network.
"""

import os
import shutil
from pathlib import Path

HERE = Path(__file__).resolve().parent
OUT = Path(os.environ.get("MAKEFUN_OUTPUT_DIR", "/output"))


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(HERE / "entry.png", OUT / "entry.png")


if __name__ == "__main__":
    main()
