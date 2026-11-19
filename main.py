#!/usr/bin/env python3
"""Write the 18 November 2026 world-news page to /output/entry.png.

The page is drawn once, by tools/make_page.py, and shipped in this repository as
entry.png; this program copies it out byte for byte. Two runs therefore write the
same bytes, which is what the bounty's determinism check wants.

    mkdir -p out && MAKEFUN_OUTPUT_DIR=out python3 main.py
"""

import hashlib
import os
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
IMAGE = HERE / "entry.png"
OUTPUT_NAME = "entry.png"
MAX_BYTES = 1024 * 1024
SIDE = 1024
PNG_MAGIC = b"\x89PNG\r\n\x1a\n"


def output_dir() -> Path:
    """The grader mounts /output; MAKEFUN_OUTPUT_DIR stands in outside it."""
    return Path(os.environ.get("MAKEFUN_OUTPUT_DIR", "/output"))


def png_size(data: bytes) -> tuple[int, int]:
    """Read width and height from the IHDR chunk, refusing anything else."""
    if not data.startswith(PNG_MAGIC):
        raise ValueError("not a PNG")
    if data[12:16] != b"IHDR":
        raise ValueError("the first chunk is not IHDR")
    return int.from_bytes(data[16:20], "big"), int.from_bytes(data[20:24], "big")


def main() -> int:
    data = IMAGE.read_bytes()
    try:
        width, height = png_size(data)
    except ValueError as exc:
        print(f"{IMAGE.name}: {exc}", file=sys.stderr)
        return 1

    if (width, height) != (SIDE, SIDE):
        print(f"{IMAGE.name} is {width}x{height}; the judge takes {SIDE}x{SIDE}", file=sys.stderr)
        return 1
    if len(data) > MAX_BYTES:
        print(f"{IMAGE.name} is {len(data)} bytes; the cap is {MAX_BYTES}", file=sys.stderr)
        return 1

    if "--check" in sys.argv[1:]:
        print(f"{IMAGE.name}: {width}x{height}, {len(data)} bytes, "
              f"sha256 {hashlib.sha256(data).hexdigest()[:16]}")
        return 0

    out = output_dir()
    out.mkdir(parents=True, exist_ok=True)
    target = out / OUTPUT_NAME
    target.write_bytes(data)
    print(f"wrote {target} ({len(data)} bytes)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
