#!/usr/bin/env python3
"""Promote sqt-holidays.sample.json / sqt-themes.sample.json → production lore files."""

from __future__ import annotations

import argparse
import json
import sys
from datetime import date, timezone
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from sqt_schema_validate import validate_holidays_file, validate_themes_file


def promote(name: str, force: bool) -> Path:
    src = ROOT / f"sqt-{name}.sample.json"
    dst = ROOT / f"sqt-{name}.json"
    if not src.exists():
        raise FileNotFoundError(src)
    if dst.exists() and not force:
        print(f"[skip] {dst.name} exists (use --force to overwrite)")
        return dst

    data = json.loads(src.read_text(encoding="utf-8"))
    data["_lore_meta"] = {
        "version": data.get("_lore_meta", {}).get("version", "1.0.0"),
        "promoted_at": datetime.now(timezone.utc).date().isoformat(),
        "status": "production",
        "source": src.name,
        "note": "Canonical lore for engine, static feeds, and widgets",
    }
    dst.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    return dst


def main() -> int:
    parser = argparse.ArgumentParser(description="Promote sample lore JSON to production")
    parser.add_argument("--force", action="store_true", help="Overwrite existing production files")
    args = parser.parse_args()

    for name in ("holidays", "themes"):
        dst = promote(name, args.force)
        if name == "holidays":
            validate_holidays_file(dst)
        else:
            validate_themes_file(dst)
        print(f"Validated {dst.name}")

    print("Run: python scripts/export_static_feed.py")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())