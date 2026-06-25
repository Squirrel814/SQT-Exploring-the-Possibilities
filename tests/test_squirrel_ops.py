"""Chunk F — Squirrel Ops lab injection (opt-in --squirrel-ops)."""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
ENGINE = ROOT / "sqt_engine_unified.py"


def run_engine(*extra: str) -> dict:
    cmd = [
        sys.executable,
        str(ENGINE),
        "--json",
        "--compact",
        "--bundle",
        "--simulate-lunation",
        "6",
        "--simulate-day",
        "7",
        "--holidays",
        str(ROOT / "sqt-holidays.json"),
        "--themes",
        str(ROOT / "sqt-themes.json"),
        *extra,
    ]
    out = subprocess.check_output(cmd, cwd=str(ROOT), timeout=8, text=True)
    return json.loads(out)


def test_default_foraging_without_squirrel_ops():
    data = run_engine()
    forage = data["bundle"]["foraging_idea"]
    assert "Squirrel Ops Lab" not in forage
    assert "squirrel_ops_lab" not in data["bundle"]


def test_squirrel_ops_injects_leybridge_lab():
    data = run_engine("--squirrel-ops")
    bundle = data["bundle"]
    assert "Squirrel Ops Lab" in bundle["foraging_idea"]
    assert "Secure Integration Thread" in bundle["foraging_idea"]
    assert bundle.get("squirrel_ops_lab", {}).get("title") == "Secure Integration Thread"
    assert bundle["squirrel_ops_lab"]["holiday_id"] == "leybridge_threading"


def test_squirrel_ops_major_shadow_trial():
    cmd = [
        sys.executable,
        str(ENGINE),
        "--json",
        "--compact",
        "--bundle",
        "--squirrel-ops",
        "--simulate-lunation",
        "6",
        "--simulate-day",
        "19",
        "--holidays",
        str(ROOT / "sqt-holidays.json"),
        "--themes",
        str(ROOT / "sqt-themes.json"),
    ]
    data = json.loads(subprocess.check_output(cmd, cwd=str(ROOT), timeout=8, text=True))
    assert data["holiday"]["type"] == "major"
    assert "Shadow Walk" in data["bundle"]["foraging_idea"]


def test_squirrel_ops_plain_day_unchanged():
    cmd = [
        sys.executable,
        str(ENGINE),
        "--json",
        "--compact",
        "--bundle",
        "--squirrel-ops",
        "--simulate-lunation",
        "6",
        "--simulate-day",
        "8",
        "--holidays",
        str(ROOT / "sqt-holidays.json"),
        "--themes",
        str(ROOT / "sqt-themes.json"),
    ]
    data = json.loads(subprocess.check_output(cmd, cwd=str(ROOT), timeout=8, text=True))
    assert data["holiday"] is None
    assert "squirrel_ops_lab" not in data["bundle"]