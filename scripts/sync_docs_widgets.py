#!/usr/bin/env python3
"""Copy widget sources from widgets/ into docs/ for GitHub Pages."""

from __future__ import annotations

import argparse
import shutil
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
WIDGET_DIR = ROOT / "widgets" / "sqt-grove-clock"
CORE_DIR = ROOT / "lib"
DOCS_DIR = ROOT / "docs"

SYNC_FILES = (
    ("sqt-grove-clock.js", WIDGET_DIR),
    ("sqt-grove-clock.css", WIDGET_DIR),
    ("sqt-core.js", CORE_DIR),
)


def sync_docs_widgets(docs_dir: Path = DOCS_DIR, widget_dir: Path = WIDGET_DIR) -> list[Path]:
    docs_dir.mkdir(parents=True, exist_ok=True)
    copied: list[Path] = []
    for name, src_dir in SYNC_FILES:
        src = src_dir / name
        if not src.is_file():
            raise FileNotFoundError(f"Missing widget source: {src}")
        dest = docs_dir / name
        shutil.copy2(src, dest)
        copied.append(dest)
    core = CORE_DIR / "sqt-core.js"
    if core.is_file():
        widget_core = widget_dir / "sqt-core.js"
        shutil.copy2(core, widget_core)
        if widget_core not in copied:
            copied.append(widget_core)
    return copied


def main() -> int:
    parser = argparse.ArgumentParser(description="Sync sqt-grove-clock assets into docs/")
    parser.add_argument("--docs-dir", default=str(DOCS_DIR), help="GitHub Pages output directory")
    parser.add_argument("--widget-dir", default=str(WIDGET_DIR), help="Widget source directory")
    args = parser.parse_args()

    copied = sync_docs_widgets(Path(args.docs_dir), Path(args.widget_dir))
    for path in copied:
        print(f"Synced {path.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())