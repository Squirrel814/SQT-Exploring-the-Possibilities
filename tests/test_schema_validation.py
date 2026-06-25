from __future__ import annotations

from pathlib import Path

import pytest

from sqt_schema_validate import SchemaValidationError, validate_holidays_file, validate_themes_file

ROOT = Path(__file__).resolve().parent.parent


def test_sample_holidays_valid():
    validate_holidays_file(ROOT / "sqt-holidays.json")
    validate_holidays_file(ROOT / "sqt-holidays.sample.json")


def test_sample_themes_valid():
    validate_themes_file(ROOT / "sqt-themes.json")
    validate_themes_file(ROOT / "sqt-themes.sample.json")


def test_invalid_holidays_rejected():
    bad = {
        "recurring_holidays": [],
        "major_lunation_events": [],
        "rare_periodic_events": [{"id": "x"}],  # missing required fields
    }
    import json
    from sqt_schema_validate import validate_json

    with pytest.raises(SchemaValidationError):
        validate_json(bad, ROOT / "sqt-holidays.schema.json", label="bad")