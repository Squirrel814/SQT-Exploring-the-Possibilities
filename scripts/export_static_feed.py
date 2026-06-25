#!/usr/bin/env python3
"""Export static JSON feeds for GitHub Pages and widgets.

After exporting, run scripts/sync_docs_widgets.py to copy web component assets into docs/.
"""

from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from sqt_engine_unified import (
    SQT_DAYS_PER_LUNATION,
    SQT_LUNATIONS_PER_YEAR,
    SQTUnifiedEngine,
    compact_context,
)

TRIM_LUNATION = {
    1: "Sleepy", 2: "Pinecone", 3: "Scamper", 4: "Asher", 5: "Bark Stripper",
    6: "Canopy", 7: "Hollow Tree", 8: "Golden Leaf", 9: "Cache", 10: "Shadow",
    11: "Forage", 12: "Chattering",
}


def build_calendar_matrix(engine: SQTUnifiedEngine) -> dict:
    cells = []
    for lunation in range(1, SQT_LUNATIONS_PER_YEAR + 1):
        for day in range(1, SQT_DAYS_PER_LUNATION + 1):
            sqt = engine.forced_sqt_state(lunation, day)
            ctx = engine.detect_holiday(sqt)
            active = ctx.get("active")
            cell = {
                "lunation": lunation,
                "day": day,
                "holiday_id": active["id"] if active else None,
                "holiday_name": active["name"] if active else None,
                "type": active["type"] if active else None,
            }
            if active:
                bundle = engine.generate_bundle(sqt, active)
                cell["teaser"] = {
                    "journal_prompt": bundle["journal_prompt"],
                    "foraging_idea": bundle["foraging_idea"],
                }
            cells.append(cell)
    return {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "lunation_names": {str(k): v for k, v in TRIM_LUNATION.items()},
        "sqt_lunations_per_year": SQT_LUNATIONS_PER_YEAR,
        "sqt_days_per_lunation": SQT_DAYS_PER_LUNATION,
        "cells": cells,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Export SQT static JSON feeds")
    parser.add_argument("--output-dir", default=str(ROOT / "docs"), help="Output directory")
    parser.add_argument("--holidays", default=str(ROOT / "sqt-holidays.json"))
    parser.add_argument("--themes", default=str(ROOT / "sqt-themes.json"))
    args = parser.parse_args()

    out = Path(args.output_dir)
    out.mkdir(parents=True, exist_ok=True)

    engine = SQTUnifiedEngine(holidays_path=args.holidays, themes_path=args.themes)
    circuit = compact_context(engine.get_full_context(include_bundle=True))
    holiday_only = compact_context(engine.get_full_context(include_bundle=False, holiday_only=True))

    matrix = build_calendar_matrix(engine)

    (out / "circuit-current.json").write_text(
        json.dumps(circuit, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
    )
    (out / "circuit-holiday-only.json").write_text(
        json.dumps(holiday_only, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
    )
    (out / "calendar_matrix.json").write_text(
        json.dumps(matrix, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
    )
    print(f"Exported to {out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())