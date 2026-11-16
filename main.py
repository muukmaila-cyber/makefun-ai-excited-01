#!/usr/bin/env python3
"""ai-excited-01 v5 entry point.

Writes the bundled image to /output/entry.png (or $MAKEFUN_OUTPUT_DIR).

The v5 image, "Whale Leaves the Painting with a Note": a colossal blue
whale bursts out of a golden-framed seascape painting into a cozy living
room, holding out a note reading "For you - stay safe" toward the viewer,
while a grandmother, a boy and a cat flee below amid splashing water,
flying frame splinters and shafts of golden light. 1024x1024 JPEG.

Deterministic: the same bytes on every run. No network. Standard library
only.
"""
import os
import shutil
import struct
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
SRC = HERE / "entry.png"
OUT = Path(os.environ.get("MAKEFUN_OUTPUT_DIR", "/output"))
MAX_BYTES = 1_048_576
MAX_SIDE = 1024

JPEG_SOI = b"\xff\xd8\xff"
JPEG_EOI = b"\xff\xd9"
PNG_SIG = b"\x89PNG\r\n\x1a\n"
PNG_IEND = b"\x00\x00\x00\x00IEND\xaeB`\x82"


def _is_whole_image(data: bytes) -> bool:
    """True for a whole JPEG (SOI..EOI) or a whole PNG (sig..IEND)."""
    if data.startswith(JPEG_SOI):
        return data.endswith(JPEG_EOI)
    if data.startswith(PNG_SIG):
        return data.endswith(PNG_IEND)
    return False


def _image_dimensions(data: bytes) -> tuple[int, int] | None:
    """(width, height) for a PNG (IHDR) or a JPEG (SOF0/SOF1/SOF2)."""
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
            size = struct.unpack(">H", data[i + 2:i + 4])[0]
            if marker in (0xC0, 0xC1, 0xC2):
                height, width = struct.unpack(">HH", data[i + 5:i + 9])
                return width, height
            i += 2 + size
    return None


def main() -> int:
    if not SRC.is_file():
        print("entry.png missing next to main.py", file=sys.stderr)
        return 1
    data = SRC.read_bytes()
    if len(data) > MAX_BYTES:
        print(f"entry.png is {len(data)} bytes, over the 1 MiB gate",
              file=sys.stderr)
        return 1
    if not _is_whole_image(data):
        print("entry.png is not a whole JPEG or PNG", file=sys.stderr)
        return 1
    dims = _image_dimensions(data)
    if dims is None:
        print("entry.png dimensions unreadable", file=sys.stderr)
        return 1
    if dims[0] > MAX_SIDE or dims[1] > MAX_SIDE:
        print(f"entry.png is {dims[0]}x{dims[1]}, over the "
              f"{MAX_SIDE}x{MAX_SIDE} gate", file=sys.stderr)
        return 1
    # Deterministic copy: the bundled bytes are written verbatim after
    # passing the 1 MiB size gate and the 1024x1024 dimension gate, then
    # re-read and compared so the output is byte-identical on every run.
    OUT.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(SRC, OUT / "entry.png")
    written = (OUT / "entry.png").read_bytes()
    if written != data:
        print("output bytes differ from entry.png", file=sys.stderr)
        return 1
    print(f"wrote {OUT / 'entry.png'} "
          f"({len(data)} bytes, {dims[0]}x{dims[1]})")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
