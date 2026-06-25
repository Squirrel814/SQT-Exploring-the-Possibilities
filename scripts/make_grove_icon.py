#!/usr/bin/env python3
"""Generate 128×128 PNG icon for VS Code extension and Discord/PWA assets."""

from __future__ import annotations

import struct
import zlib
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


def _chunk(tag: bytes, data: bytes) -> bytes:
    return struct.pack(">I", len(data)) + tag + data + struct.pack(">I", zlib.crc32(tag + data) & 0xFFFFFFFF)


def write_png(path: Path, size: int = 128) -> None:
    """Minimal acorn-on-grove icon without external deps."""
    bg = (0x2E, 0x5A, 0x44, 0xFF)
    cap = (0x4A, 0xF6, 0x26, 0xFF)
    body = (0x8C, 0x62, 0x39, 0xFF)
    cx, cy = size // 2, size // 2
    rows = []
    for y in range(size):
        row = b"\x00"
        for x in range(size):
            dx, dy = x - cx, y - (cy + 6)
            # acorn cap (ellipse top)
            cap_dist = ((x - cx) / (size * 0.22)) ** 2 + ((y - (cy - 14)) / (size * 0.16)) ** 2
            body_dist = ((x - cx) / (size * 0.18)) ** 2 + ((y - (cy + 10)) / (size * 0.22)) ** 2
            if cap_dist <= 1.0:
                row += bytes(cap)
            elif body_dist <= 1.0:
                row += bytes(body)
            else:
                row += bytes(bg)
        rows.append(row)
    raw = b"".join(rows)
    compressed = zlib.compress(raw, 9)
    ihdr = struct.pack(">IIBBBBB", size, size, 8, 6, 0, 0, 0)
    png = b"\x89PNG\r\n\x1a\n" + _chunk(b"IHDR", ihdr) + _chunk(b"IDAT", compressed) + _chunk(b"IEND", b"")
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(png)


def main() -> int:
    targets = [
        ROOT / "widgets" / "vscode-sqt-grove" / "icon.png",
        ROOT / "docs" / "icon-128.png",
    ]
    for target in targets:
        write_png(target)
        print(f"Wrote {target}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())