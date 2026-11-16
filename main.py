#!/usr/bin/env python3
"""ai-excited-01 v3 entry: copies the bundled image to /output/entry.png.

v3 image: a golden origami phoenix unfolding out of a burning storybook
in an ornate golden frame in a dark library (1024x1024 JPEG, 333,193
bytes). Deterministic: the same bytes every run, no network, standard
library only.
"""
import os
import shutil
import struct
from pathlib import Path

HERE = Path(__file__).resolve().parent
OUT = Path(os.environ.get("MAKEFUN_OUTPUT_DIR", "/output"))
MAX_BYTES = 1_048_576
MAX_SIDE = 1024

JPEG_SOI = b"\xff\xd8\xff"
JPEG_EOI = b"\xff\xd9"
PNG_SIG = b"\x89PNG\r\n\x1a\n"
PNG_IEND_CHUNK = b"\x00\x00\x00\x00IEND\xaeB`\x82"


def _whole(data: bytes) -> bool:
    """True when data is a whole JPEG (SOI..EOI) or a whole PNG (ends IEND)."""
    if data.startswith(JPEG_SOI):
        return data.endswith(JPEG_EOI)
    if data.startswith(PNG_SIG):
        return data.endswith(PNG_IEND_CHUNK)
    return False


def _dims(data: bytes) -> tuple[int, int] | None:
    """(width, height) for a PNG (IHDR) or a JPEG (SOF0/SOF2), else None."""
    if data.startswith(PNG_SIG) and len(data) >= 24:
        return struct.unpack(">II", data[16:24])
    if data.startswith(JPEG_SOI):
        i = 2
        while i + 9 < len(data):
            if data[i] != 0xFF:
                return None
            marker = data[i + 1]
            if marker in (0xD8, 0xD9) or 0xD0 <= marker <= 0xD7:
                i += 2
                continue
            if i + 4 > len(data):
                return None
            length = struct.unpack(">H", data[i + 2:i + 4])[0]
            if marker in (0xC0, 0xC2):
                h, w = struct.unpack(">HH", data[i + 5:i + 9])
                return w, h
            i += 2 + length
    return None


def main() -> None:
    src = HERE / "entry.png"
    if not src.is_file():
        raise SystemExit("entry.png missing next to main.py")
    data = src.read_bytes()
    if len(data) > MAX_BYTES:
        raise SystemExit("entry.png exceeds the 1 MiB gate")
    if not _whole(data):
        raise SystemExit("entry.png is not a whole JPEG or PNG")
    dims = _dims(data)
    if dims is not None and (dims[0] > MAX_SIDE or dims[1] > MAX_SIDE):
        raise SystemExit(
            f"entry.png is {dims[0]}x{dims[1]}, over the {MAX_SIDE}x{MAX_SIDE} gate"
        )
    OUT.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(src, OUT / "entry.png")
    written = (OUT / "entry.png").read_bytes()
    if written != data:
        raise SystemExit("output bytes differ from entry.png")


if __name__ == "__main__":
    main()
