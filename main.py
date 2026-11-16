#!/usr/bin/env python3
"""ai-excited-01 entry: copies the bundled image to /output/entry.png.

Deterministic: the same bytes every run, no network, stdlib only.
"""
import os
import shutil
from pathlib import Path

HERE = Path(__file__).resolve().parent
OUT = Path(os.environ.get("MAKEFUN_OUTPUT_DIR", "/output"))


def main() -> None:
    src = HERE / "entry.png"
    if not src.is_file():
        raise SystemExit("entry.png missing next to main.py")
    if src.stat().st_size > 1_048_576:
        raise SystemExit("entry.png exceeds the 1 MiB gate")
    OUT.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(src, OUT / "entry.png")


if __name__ == "__main__":
    main()
