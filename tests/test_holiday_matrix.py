"""12 lunations × 19 days holiday detection matrix (SQT time model)."""

from __future__ import annotations

from pathlib import Path

import pytest

from sqt_engine_unified import SQT_DAYS_PER_LUNATION, SQT_LUNATIONS_PER_YEAR, SQTUnifiedEngine

ROOT = Path(__file__).resolve().parent.parent
HOLIDAYS = str(ROOT / "sqt-holidays.sample.json")
THEMES = str(ROOT / "sqt-themes.sample.json")

# Known active holidays at specific cells (year 1 simulation)
EXPECTED_ACTIVE = {
    (1, 1): ("whisperwake_first_message", "recurring"),
    (1, 6): ("ratatoskr_argument", "rare"),
    (3, 13): ("burrow_rebuild", "rare"),
    (3, 19): ("the_hoardkeeper\u2019s_joyful_reckoning", "major"),
    (4, 9): ("whisper_storm", "rare"),
    (5, 7): ("leyline_surge", "rare"),
    (6, 7): ("leybridge_threading", "recurring"),
    (6, 12): ("hidden_cache_reveal", "rare"),
    (6, 19): ("shadow_trial", "major"),
    (11, 11): ("shadowforage_eclipse", "rare"),
}


@pytest.fixture(scope="module")
def engine() -> SQTUnifiedEngine:
    return SQTUnifiedEngine(holidays_path=HOLIDAYS, themes_path=THEMES)


def test_sqt_time_constants():
    assert SQT_LUNATIONS_PER_YEAR == 12
    assert SQT_DAYS_PER_LUNATION == 19


def test_matrix_size(engine: SQTUnifiedEngine):
    """Full SQT lunation calendar: 12 × 19 = 228 cells."""
    cells = 0
    for lunation in range(1, SQT_LUNATIONS_PER_YEAR + 1):
        for day in range(1, SQT_DAYS_PER_LUNATION + 1):
            sqt = engine.forced_sqt_state(lunation, day)
            ctx = engine.detect_holiday(sqt)
            assert sqt["lunation"] == lunation
            assert sqt["day"] == day
            active = ctx.get("active")
            if active:
                assert active["type"] in ("recurring", "major", "rare")
                assert active["id"]
            cells += 1
    assert cells == 12 * 19


@pytest.mark.parametrize("lunation,day,holiday_id,holiday_type", [
    (lun, day, hid, htype) for (lun, day), (hid, htype) in EXPECTED_ACTIVE.items()
])
def test_known_holidays(
    engine: SQTUnifiedEngine,
    lunation: int,
    day: int,
    holiday_id: str,
    holiday_type: str,
):
    sqt = engine.forced_sqt_state(lunation, day)
    ctx = engine.detect_holiday(sqt)
    active = ctx["active"]
    assert active is not None, f"L{lunation} D{day} expected {holiday_id}"
    assert active["id"] == holiday_id
    assert active["type"] == holiday_type


def test_major_events_all_four_lunations(engine: SQTUnifiedEngine):
    for lunation in (3, 6, 9, 12):
        sqt = engine.forced_sqt_state(lunation, 19)
        ctx = engine.detect_holiday(sqt)
        assert ctx["major"] is not None
        assert ctx["active"]["type"] == "major"


def test_rare_events_have_themes_when_active(engine: SQTUnifiedEngine):
    for (lunation, day), (hid, htype) in EXPECTED_ACTIVE.items():
        if htype != "rare":
            continue
        sqt = engine.forced_sqt_state(lunation, day)
        ctx = engine.detect_holiday(sqt)
        assert ctx["active"]["id"] == hid
        themes = engine.get_themes(hid)
        assert themes["palettes"], f"{hid} missing palettes"
        bundle = engine.generate_bundle(sqt, ctx["active"])
        assert bundle["journal_prompt"]