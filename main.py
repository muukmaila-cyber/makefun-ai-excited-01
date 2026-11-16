#!/usr/bin/env python3
"""ai-excited-01 v2 entry: copies the bundled image to /output/entry.png.

v2 image: a golden phoenix bursting from a burning baroque painting in a
dark library (1024x1024 JPEG, 350,466 bytes). Deterministic: the same bytes
every run, no network, stdlib only.
"""
import os
import shutil
import struct
from pathlib import Path

HERE = Path(__file__).resolve().parent
OUT = Path(os.environ.get("MAKEFUN_OUTPUT_DIR", "/output"))
MAX_BYTES = 1_048_576

JPEG_SOI = b"\xff\xd8\xff"
JPEG_EOI = b"\xff\xd9"
PNG_SIG = b"\x89PNG\r\n\x1a\n"


def _is_whole_image(data: bytes) -> bool:
    """True when data is a whole JPEG (SOI..EOI) or a whole PNG (signature)."""
    if data.startswith(JPEG_SOI) and data.endswith(JPEG_EOI):
        return True
    return data.startswith(PNG_SIG)


def _image_dimensions(data: bytes) -> tuple[int, int] | None:
    """(width, height) for a JPEG (SOF0/SOF2) or a PNG (IHDR), else None."""
    if data.startswith(PNG_SIG) and len(data) >= 24:
        width, height = struct.unpack(">II", data[16:24])
        return width, height
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
            if marker in (0xC0, 0xC2):  # SOF0/SOF2: precision, height, width
                height, width = struct.unpack(">HH", data[i + 5:i + 9])
                return width, height
            i += 2 + length
    return None


def main() -> None:
    src = HERE / "entry.png"
    if not src.is_file():
        raise SystemExit("entry.png missing next to main.py")
    data = src.read_bytes()
    if len(data) > MAX_BYTES:
        raise SystemExit("entry.png exceeds the 1 MiB gate")
    if not _is_whole_image(data):
        raise SystemExit("entry.png is not a whole JPEG or PNG")
    dims = _image_dimensions(data)
    if dims is not None and (dims[0] > 1024 or dims[1] > 1024):
        raise SystemExit(
            f"entry.png is {dims[0]}x{dims[1]}, over the 1024x1024 gate"
        )
    OUT.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(src, OUT / "entry.png")


if __name__ == "__main__":
    main()
