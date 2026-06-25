"""Python vs JavaScript SQT core math parity (12 lunations × 19 days)."""

from __future__ import annotations

import json
import subprocess
from pathlib import Path

import pytest

from sqt_engine_unified import (
    SQT_DAYS_PER_LUNATION,
    SQT_LUNATIONS_PER_YEAR,
    SQTUnifiedEngine,
    _simulate_reference_time,
    compute_moon_phase,
)

ROOT = Path(__file__).resolve().parent.parent
JS_RUNNER = ROOT / "tests" / "run_js_parity.mjs"


def _moon_phase_label(day: int) -> str:
    phase = compute_moon_phase(day)
    if "New Moon" in phase:
        return "New Moon"
    if "Waxing Crescent" in phase:
        return "Waxing Crescent"
    if "First Quarter" in phase:
        return "First Quarter"
    if "Waxing Gibbous" in phase:
        return "Waxing Gibbous"
    if "Full Moon" in phase:
        return "Full Moon"
    if "Waning Gibbous" in phase:
        return "Waning Gibbous"
    if "Last Quarter" in phase:
        return "Last Quarter"
    return "Waning Crescent"


def _js_states() -> list[dict]:
    result = subprocess.run(
        ["node", str(JS_RUNNER)],
        capture_output=True,
        text=True,
        check=True,
        cwd=str(ROOT),
    )
    return json.loads(result.stdout)


@pytest.fixture(scope="module")
def engine() -> SQTUnifiedEngine:
    return SQTUnifiedEngine(validate_schema=True)


def test_js_runner_available():
    subprocess.run(["node", "--version"], check=True, capture_output=True)


def test_parity_matrix(engine: SQTUnifiedEngine):
    js_rows = _js_states()
    assert len(js_rows) == SQT_LUNATIONS_PER_YEAR * SQT_DAYS_PER_LUNATION

    for row in js_rows:
        lun = row["lunation"]
        day = row["day"]
        py = engine.get_sqt_state(_simulate_reference_time(lun, day))
        assert py["lunation"] == row["lunation"], f"L{lun} D{day} lunation"
        assert py["day"] == row["day"], f"L{lun} D{day} day"
        assert py["lunation_name_display"] == row["lunation_name_display"]
        assert py["day_name_display"] == row["day_name_display"]
        assert _moon_phase_label(py["day"]) == row["moon_phase"]
        assert py["week_label"] == row["week_label"]