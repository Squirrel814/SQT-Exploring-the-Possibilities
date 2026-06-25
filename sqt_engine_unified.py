#!/usr/bin/env python3
"""
sqt_engine_unified.py — Headless SQT engine for this exploration repository.

Rewrites reference/sqt_engine_2.py (upstream snapshot) with:
- Pure calculation (no Tkinter)
- Holiday + theme loading from JSON
- generate_bundle() — 5-element Messenger's Circuit output
- Widget-ready JSON contract (phase1-requirements-messenger-circuit.md)

Usage:
  python sqt_engine_unified.py --json
  python sqt_engine_unified.py --json --bundle
  python sqt_engine_unified.py --json --holiday
  python sqt_engine_unified.py --json --simulate-lunation 6 --simulate-day 7 --bundle
"""

from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

from sqt_schema_validate import SchemaValidationError, validate_holidays_file, validate_themes_file

# =============================================================================
# EXACT CONSTANTS — fidelity locked to reference/sqt_engine_2.py
# =============================================================================
SQT_NAME = "Squirrel Quantum Time"
SQT_EPOCH = datetime(2026, 1, 18, 20, 52, 0, tzinfo=timezone.utc)
EARTH_HOURS_PER_SQT_DAY = 37.301826
SEC_PER_SQT_DAY = EARTH_HOURS_PER_SQT_DAY * 3600
LUNAR_CYCLE_SECONDS = 29.53059 * 24 * 3600
SQT_LUNATIONS_PER_YEAR = 12
SQT_DAYS_PER_LUNATION = 19

SQT_LUNATIONS_DISPLAY: Dict[int, str] = {
    1: "Sleepy Moon", 2: "Pinecone Moon", 3: "Scamper Moon",
    4: "Asher Moon", 5: "Bark Stripper Moon", 6: "Canopy Moon",
    7: "Hollow Tree Moon", 8: "Golden Leaf Moon", 9: "Cache Moon",
    10: "Shadow Moon", 11: "Forage Moon", 12: "Chattering Moon",
}

SQT_UNIQUE_DAYS_DISPLAY: Dict[int, Tuple[str, str]] = {
    1: ("Truffle-day", "Week 1: The First Nibble"),
    2: ("Sprout-day", "Week 1: The First Nibble"),
    3: ("Sap-day", "Week 1: The First Nibble"),
    4: ("Twig-day", "Week 1: The First Nibble"),
    5: ("Fern-day", "Week 2: The High Canopy"),
    6: ("Chitter-day", "Week 2: The High Canopy"),
    7: ("Stash-day", "Week 2: The High Canopy"),
    8: ("Thicket-day", "Week 2: The High Canopy"),
    9: ("Moss-day", "Week 2: The High Canopy"),
    10: ("Cache-Day", "Week 3: The Great Acorn"),
    11: ("Forage-day", "Week 3: The Great Acorn"),
    12: ("Oak-day", "Week 3: The Great Acorn"),
    13: ("Timber-day", "Week 3: The Great Acorn"),
    14: ("Swindle-day", "Week 3: The Great Acorn"),
    15: ("Scurry-day", "Week 4: The Deep Burrow"),
    16: ("Bark-day", "Week 4: The Deep Burrow"),
    17: ("Willow-day", "Week 4: The Deep Burrow"),
    18: ("Drey-day", "Week 4: The Deep Burrow"),
    19: ("Nap-day", "Week 4: The Deep Burrow"),
}

WEEK_DEFINITIONS = [
    {"start": 1, "end": 4, "label": "Week 1: The First Nibble"},
    {"start": 5, "end": 9, "label": "Week 2: The High Canopy"},
    {"start": 10, "end": 14, "label": "Week 3: The Great Acorn"},
    {"start": 15, "end": 19, "label": "Week 4: The Deep Burrow"},
]

TRIM_LUNATION_OVERRIDES = {6: "Canopy"}
TRIM_DAY_OVERRIDES = {7: "Stash", 10: "Cache"}

ENGINE_VERSION = "sqt-unified-0.2-phase2.2"


def _trim_lunation(num: int, display: str) -> str:
    if num in TRIM_LUNATION_OVERRIDES:
        return TRIM_LUNATION_OVERRIDES[num]
    return display.replace(" Moon", "")


def _trim_day(day: int, display: str) -> str:
    if day in TRIM_DAY_OVERRIDES:
        return TRIM_DAY_OVERRIDES[day]
    return display.replace("-day", "").replace("-Day", "")


def compute_moon_phase(day: int) -> str:
    if day == 1 or day == 19:
        return "New Moon 🌑"
    if 2 <= day <= 4:
        return "Waxing Crescent 🌒"
    if day == 5:
        return "First Quarter 🌓"
    if 6 <= day <= 9:
        return "Waxing Gibbous 🌔"
    if day == 10:
        return "Full Moon 🌕"
    if 11 <= day <= 14:
        return "Waning Gibbous 🌖"
    if day == 15:
        return "Last Quarter 🌗"
    return "Waning Crescent 🌘"


def _get_week_info(day: int) -> Tuple[int, str]:
    for idx, w in enumerate(WEEK_DEFINITIONS):
        if w["start"] <= day <= w["end"]:
            return idx + 1, w["label"]
    return 4, WEEK_DEFINITIONS[-1]["label"]


class SQTUnifiedEngine:
    """Headless engine: SQT math + holidays + Messenger's Circuit bundles."""

    def __init__(
        self,
        holidays_path: Optional[str] = None,
        themes_path: Optional[str] = None,
        use_trimmed: bool = True,
        validate_schema: bool = True,
    ):
        self.use_trimmed = use_trimmed
        self.validate_schema = validate_schema
        self.holidays: Dict[str, Any] = {}
        self.themes: Dict[str, Any] = {}
        self._holidays_raw: Dict[str, Any] = {}
        self._themes_raw: Dict[str, Any] = {}

        if holidays_path:
            self.load_holidays(holidays_path)
        if themes_path:
            self.load_themes(themes_path)

    def load_holidays(self, path: str) -> None:
        p = Path(path)
        if not p.exists():
            print(f"[warn] Holidays file not found: {path}", file=sys.stderr)
            self._holidays_raw = {}
            return
        with p.open(encoding="utf-8") as f:
            data = json.load(f)
        if self.validate_schema:
            validate_holidays_file(p)
        self._holidays_raw = data
        self.holidays = {
            "recurring": {h["id"]: h for h in data.get("recurring_holidays", [])},
            "major": data.get("major_lunation_events", []),
            "rare": data.get("rare_periodic_events", []),
        }

    def load_themes(self, path: str) -> None:
        p = Path(path)
        if not p.exists():
            print(f"[warn] Themes file not found: {path}", file=sys.stderr)
            self._themes_raw = {}
            return
        with p.open(encoding="utf-8") as f:
            data = json.load(f)
        if self.validate_schema:
            validate_themes_file(p)
        self._themes_raw = data
        self.themes = data

    def forced_sqt_state(self, lunation: int, day: int) -> Dict[str, Any]:
        """SQT state for a specific lunation (1–12) and day (1–19) in year 1."""
        sqt = self.get_sqt_state(_simulate_reference_time(lunation, day))
        sqt["lunation"] = lunation
        sqt["day"] = day
        return sqt

    def get_sqt_state(self, reference_time: Optional[datetime] = None) -> Dict[str, Any]:
        now = reference_time or datetime.now(timezone.utc)
        elapsed = (now - SQT_EPOCH).total_seconds()

        if elapsed < 0:
            return {"error": "Before SQT Epoch", "reference_time": now.isoformat()}

        total_lunations = elapsed / LUNAR_CYCLE_SECONDS
        current_lunation_raw = int(total_lunations)
        position_in_lunation = total_lunations - current_lunation_raw

        sqt_year = (current_lunation_raw // 12) + 1
        lunation_num = (current_lunation_raw % 12) + 1
        sqt_day = max(1, min(SQT_DAYS_PER_LUNATION, int(position_in_lunation * SQT_DAYS_PER_LUNATION) + 1))

        day_display, week_label = SQT_UNIQUE_DAYS_DISPLAY.get(
            sqt_day, ("Unknown-day", "Unknown Week")
        )
        week_num, _ = _get_week_info(sqt_day)
        lunation_display = SQT_LUNATIONS_DISPLAY.get(lunation_num, "Unknown Lunation")

        if self.use_trimmed:
            lunation_name = _trim_lunation(lunation_num, lunation_display)
            day_name = _trim_day(sqt_day, day_display)
        else:
            lunation_name = lunation_display
            day_name = day_display

        seconds_into_lunation = position_in_lunation * LUNAR_CYCLE_SECONDS
        seconds_into_day = seconds_into_lunation % SEC_PER_SQT_DAY
        h = int(seconds_into_day // 3600)
        m = int((seconds_into_day % 3600) // 60)
        s = int(seconds_into_day % 60)
        time_hms = f"{h:02d}:{m:02d}:{s:02d}"

        return {
            "year": sqt_year,
            "lunation": lunation_num,
            "lunation_name": lunation_name,
            "lunation_name_display": lunation_display,
            "day": sqt_day,
            "day_name": day_name,
            "day_name_display": day_display,
            "week_num": week_num,
            "week_label": week_label,
            "time": time_hms,
            "moon_phase": compute_moon_phase(sqt_day),
            "position_in_lunation": round(position_in_lunation, 6),
            "reference_time": now.isoformat(),
        }

    def _compute_moon_phase_key(self, day: int) -> str:
        phase = compute_moon_phase(day)
        if "New Moon" in phase:
            return "new_moon"
        if "Full Moon" in phase:
            return "full"
        if "Waxing" in phase:
            return "waxing"
        if "Waning" in phase:
            return "waning"
        return "any"

    def detect_holiday(self, sqt: Dict[str, Any]) -> Dict[str, Any]:
        if "error" in sqt:
            return {"active": None, "recurring": [], "major": None, "rare": []}

        lun = sqt["lunation"]
        day = sqt["day"]
        results: Dict[str, Any] = {"recurring": [], "major": None, "rare": []}

        for h in self.holidays.get("recurring", {}).values():
            if day in h.get("days", []):
                results["recurring"].append({
                    "id": h["id"],
                    "name": h["name"],
                    "type": "recurring",
                    "core_feeling": h.get("core_feeling", ""),
                })

        for m in self.holidays.get("major", []):
            if m.get("lunation") == lun and m.get("day", 19) == day:
                raw_id = m.get("event_name", "").lower().replace(" ", "_").replace("'", "").replace("the_", "")
                if not raw_id.startswith("the_") and raw_id not in ("hoardkeepers_joyful_reckoning", "shadow_trial"):
                    raw_id = "the_" + raw_id if "the_" not in raw_id else raw_id
                if "burrow_rebirth" in raw_id and not raw_id.startswith("the_"):
                    raw_id = "the_burrow_rebirth"
                if "messenger" in raw_id and "circuit" in raw_id:
                    raw_id = "the_messengers_circuit_complete"
                results["major"] = {
                    "id": raw_id,
                    "name": m["event_name"],
                    "type": "major",
                    "heros_journey_stage": m.get("heros_journey_stage", ""),
                    "tone": m.get("tone", ""),
                }
                break

        moon_key = self._compute_moon_phase_key(day)
        for r in self.holidays.get("rare", []):
            trig = r.get("trigger_type")
            cond = r.get("condition", {})
            match = False
            if trig == "static_interval":
                interval = cond.get("interval_lunation") or cond.get("every_n_lunations")
                if interval and (lun % interval == 0) and day == cond.get("target_day"):
                    match = True
            elif trig == "conditional_predicate":
                if day == cond.get("target_day"):
                    req = cond.get("moon_phase_requirement", "any")
                    if req == "any" or req == moon_key:
                        match = True
            if match:
                results["rare"].append({
                    "id": r["id"],
                    "name": r["name"],
                    "type": "rare",
                    "core_theme": r.get("core_theme", ""),
                })

        active = None
        if results["major"]:
            active = results["major"]
        elif results["rare"]:
            active = results["rare"][0]
        elif results["recurring"]:
            active = results["recurring"][0]

        results["active"] = active
        return results

    def _get_theme_record(self, holiday_id: Optional[str]) -> Dict[str, Any]:
        if not holiday_id or not self.themes:
            return {}
        for section in ("holiday_themes", "major_event_themes", "rare_event_themes"):
            record = self.themes.get(section, {}).get(holiday_id)
            if record:
                return record
        return {}

    def get_themes(self, holiday_id: Optional[str]) -> Dict[str, Any]:
        theme = self._get_theme_record(holiday_id)
        global_style = self.themes.get("global_style", {}) if self.themes else {}
        return {
            "palettes": theme.get("palettes") or global_style.get("base_palette", []),
            "motifs": theme.get("motifs", []),
            "style_modifiers": theme.get("style_modifiers") or global_style.get("style_base", ""),
            "tone_keywords": theme.get("tone_keywords", [])
                or ([theme.get("tone", "")] if theme.get("tone") else []),
        }

    def _format_sqt_context(self, sqt: Dict[str, Any]) -> str:
        return (
            f"Year {sqt.get('year', 1)}, "
            f"{sqt.get('lunation_name', 'Unknown')} lunation, "
            f"{sqt.get('day_name', 'Unknown')}-day"
        )

    def generate_bundle(
        self,
        sqt: Dict[str, Any],
        holiday: Optional[Dict[str, Any]] = None,
        mode: str = "standard",
    ) -> Dict[str, Any]:
        """
        Assemble the 5-element Messenger's Circuit bundle from theme seeds.
        Template-based — no LLM calls.
        """
        hid = holiday.get("id") if holiday else None
        theme = self._get_theme_record(hid)
        themes = self.get_themes(hid)
        ctx = self._format_sqt_context(sqt)
        holiday_name = holiday.get("name", "") if holiday else ""
        ceremonial = theme.get("ceremonial_boost", False) or (holiday or {}).get("type") == "major"

        journal_seed = theme.get("journal_prompt_seed", "What message arrives for you today?")
        if ceremonial and mode == "standard":
            journal_prompt = f"{journal_seed} ({ctx} — {holiday_name})"
        elif holiday_name:
            journal_prompt = f"{journal_seed} Reflect on {holiday_name} during {ctx}."
        else:
            journal_prompt = f"{journal_seed} ({ctx})"

        palettes = themes["palettes"]
        mood_hints = theme.get("mood_board_hints", "")
        art_seed = theme.get("art_prompt_seed", "")
        style_mod = themes["style_modifiers"]

        mood_board = {
            "palette": palettes,
            "image_prompt": art_seed or mood_hints or f"SQT Grove scene, {ctx}, {style_mod}",
            "atmosphere": mood_hints or style_mod or "Warm forest stillness",
        }

        story_seed = theme.get("story_seed_seed", "")
        if not story_seed:
            if holiday_name:
                story_seed = (
                    f"On {ctx}, a squirrel in the Grove pauses for {holiday_name}. "
                    "Ratatoskr's whisper carries a new thread of the story..."
                )
            else:
                story_seed = (
                    f"On {ctx}, a squirrel pauses beneath the canopy "
                    "and listens for the day's message..."
                )

        art_prompt = art_seed or (
            f"A squirrel in the SQT Grove on {ctx}"
            + (f" during {holiday_name}," if holiday_name else ",")
            + f" {style_mod}, whimsical storybook illustration"
        )

        forage_bias = theme.get("forage_bias", "gentle intentional action")
        if holiday_name:
            foraging_idea = f"Today ({holiday_name}): {forage_bias.capitalize()}."
        else:
            foraging_idea = f"Forage today: {forage_bias.capitalize()}."

        return {
            "journal_prompt": journal_prompt,
            "mood_board": mood_board,
            "story_seed": story_seed,
            "art_prompt": art_prompt,
            "foraging_idea": foraging_idea,
        }

    def _widget_holiday(self, holiday_ctx: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        active = holiday_ctx.get("active")
        if not active:
            return None
        return {
            "id": active["id"],
            "name": active["name"],
            "type": active["type"],
        }

    def _widget_sqt(self, sqt: Dict[str, Any]) -> Dict[str, Any]:
        return {
            "year": sqt["year"],
            "lunation": sqt["lunation"],
            "day": sqt["day"],
            "time": sqt["time"],
        }

    def get_full_context(
        self,
        reference_time: Optional[datetime] = None,
        include_bundle: bool = True,
        holiday_only: bool = False,
    ) -> Dict[str, Any]:
        sqt = self.get_sqt_state(reference_time)
        if "error" in sqt:
            return {
                "version": ENGINE_VERSION,
                "generated_at": datetime.now(timezone.utc).isoformat(),
                "error": sqt["error"],
            }

        holiday_ctx = self.detect_holiday(sqt)
        active = holiday_ctx.get("active")
        widget_holiday = self._widget_holiday(holiday_ctx)
        themes = self.get_themes(active.get("id") if active else None)

        payload: Dict[str, Any] = {
            "version": ENGINE_VERSION,
            "generated_at": datetime.now(timezone.utc).isoformat(),
            "sqt": self._widget_sqt(sqt),
            "holiday": widget_holiday,
            "themes": themes,
        }

        if not holiday_only and include_bundle:
            payload["bundle"] = self.generate_bundle(sqt, active)

        payload["_extended"] = {
            "sqt_full": sqt,
            "holiday_detection": holiday_ctx,
        }

        return payload

    def to_json(self, context: Dict[str, Any], pretty: bool = False) -> str:
        indent = 2 if pretty else None
        return json.dumps(context, indent=indent, ensure_ascii=False)


def _simulate_reference_time(lun: int, day: int) -> datetime:
    position = (day - 1) / 19.0
    total_lun = (lun - 1) + position
    target_elapsed = total_lun * LUNAR_CYCLE_SECONDS
    return SQT_EPOCH + timedelta(seconds=target_elapsed + 3600)


def main(argv: Optional[List[str]] = None) -> int:
    parser = argparse.ArgumentParser(
        description="SQT Unified Engine — headless rewrite of reference/sqt_engine_2.py"
    )
    parser.add_argument("--json", action="store_true", help="Machine-readable JSON output")
    parser.add_argument("--pretty", action="store_true", help="Pretty-print JSON")
    parser.add_argument("--bundle", action="store_true", help="Include Messenger's Circuit bundle (default with --json)")
    parser.add_argument("--holiday", action="store_true", help="SQT + holiday only (no bundle)")
    parser.add_argument("--bundle-stub", action="store_true", help=argparse.SUPPRESS)  # legacy alias
    parser.add_argument("--simulate-lunation", type=int, help="Force lunation (1-12)")
    parser.add_argument("--simulate-day", type=int, help="Force day (1-19)")
    parser.add_argument("--holidays", default="sqt-holidays.sample.json")
    parser.add_argument("--themes", default="sqt-themes.sample.json")
    parser.add_argument("--no-trim", action="store_true", help="Use display names instead of trimmed")
    parser.add_argument("--skip-schema-validation", action="store_true", help="Load JSON without jsonschema enforcement")

    args = parser.parse_args(argv)
    include_bundle = args.bundle or args.bundle_stub or (args.json and not args.holiday)

    try:
        engine = SQTUnifiedEngine(
            holidays_path=args.holidays,
            themes_path=args.themes,
            use_trimmed=not args.no_trim,
            validate_schema=not args.skip_schema_validation,
        )
    except SchemaValidationError as exc:
        print(f"[error] {exc}", file=sys.stderr)
        return 1

    ref_time = None
    if args.simulate_lunation is not None or args.simulate_day is not None:
        ref_time = _simulate_reference_time(
            args.simulate_lunation or 6,
            args.simulate_day or 7,
        )

    ctx = engine.get_full_context(
        ref_time,
        include_bundle=include_bundle,
        holiday_only=args.holiday,
    )

    if args.simulate_lunation or args.simulate_day:
        lun = args.simulate_lunation or ctx["_extended"]["sqt_full"]["lunation"]
        day = args.simulate_day or ctx["_extended"]["sqt_full"]["day"]
        forced_sqt = engine.get_sqt_state(_simulate_reference_time(lun, day))
        forced_sqt["lunation"] = lun
        forced_sqt["day"] = day
        holiday_ctx = engine.detect_holiday(forced_sqt)
        active = holiday_ctx.get("active")
        ctx["sqt"] = engine._widget_sqt(forced_sqt)
        ctx["holiday"] = engine._widget_holiday(holiday_ctx)
        ctx["themes"] = engine.get_themes(active.get("id") if active else None)
        if include_bundle and not args.holiday:
            ctx["bundle"] = engine.generate_bundle(forced_sqt, active)
        ctx["_extended"] = {"sqt_full": forced_sqt, "holiday_detection": holiday_ctx}
        ctx["_note"] = "Simulated lunation/day for design validation."

    if args.json or args.pretty:
        print(engine.to_json(ctx, pretty=args.pretty or (not args.json and args.pretty)))
    else:
        s = ctx["sqt"]
        h = ctx.get("holiday")
        print("=== SQT Unified Engine ===")
        print(f"Year {s['year']}, Lunation {s['lunation']}, Day {s['day']}")
        print(f"Time: {s['time']}")
        if h:
            print(f"Holiday: {h['name']} ({h['type']})")
        else:
            print("Holiday: (none)")
        if ctx.get("bundle"):
            print("\n--- Bundle ---")
            print(f"  Journal: {ctx['bundle']['journal_prompt'][:80]}...")
        print("\n(Use --json for full machine output)")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())