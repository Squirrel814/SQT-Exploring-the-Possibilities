"""Track B — Messenger's Circuit delivery modes."""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
ENGINE = ROOT / "sqt_engine_unified.py"

from sqt_engine_unified import (  # noqa: E402
    resolve_circuit_mode,
    shape_bundle_for_mode,
    VALID_CIRCUIT_MODES,
)


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


def test_valid_modes_frozenset():
    assert "standard" in VALID_CIRCUIT_MODES
    assert "whisper" in VALID_CIRCUIT_MODES
    assert "project-deep" in VALID_CIRCUIT_MODES


def test_resolve_major_auto_ceremonial():
    major = {"id": "shadow_trial", "type": "major"}
    assert resolve_circuit_mode("standard", major) == "ceremonial"
    assert resolve_circuit_mode("teaser", major) == "teaser"


def test_whisper_mode_omits_extra_fields():
    bundle = {
        "journal_prompt": "Listen.",
        "foraging_idea": "Act.",
        "story_seed": "Once.",
        "art_prompt": "Draw.",
        "mood_board": {"atmosphere": "calm"},
    }
    shaped = shape_bundle_for_mode(bundle, {}, "whisper", None)
    assert set(shaped.keys()) == {"journal_prompt"}


def test_teaser_mode_journal_and_forage_only():
    bundle = {
        "journal_prompt": "Listen.",
        "foraging_idea": "Act.",
        "story_seed": "Once.",
    }
    shaped = shape_bundle_for_mode(bundle, {}, "teaser", None)
    assert "journal_prompt" in shaped
    assert "foraging_idea" in shaped
    assert "story_seed" not in shaped


def test_project_deep_injects_context():
    bundle = {"journal_prompt": "J", "foraging_idea": "F"}
    shaped = shape_bundle_for_mode(
        bundle, {}, "project-deep", None, project_context="SQT widgets"
    )
    assert "SQT widgets" in shaped["journal_prompt"]
    assert shaped.get("project_context") == "SQT widgets"


def test_cli_whisper_mode():
    data = run_engine("--circuit-mode", "whisper")
    assert data.get("circuit_mode") == "whisper"
    b = data["bundle"]
    assert "journal_prompt" in b
    assert "story_seed" not in b
    assert "foraging_idea" not in b


def test_cli_teaser_mode():
    data = run_engine("--circuit-mode", "teaser")
    assert data["circuit_mode"] == "teaser"
    assert "foraging_idea" in data["bundle"]
    assert "story_seed" not in data["bundle"]


def test_cli_storytelling_mode():
    data = run_engine("--circuit-mode", "storytelling")
    assert "story_seed" in data["bundle"]
    assert "continues" in data["bundle"]["story_seed"].lower()


def test_major_event_ceremonial_header():
    data = run_engine("--simulate-lunation", "6", "--simulate-day", "19", "--circuit-mode", "standard")
    assert data["circuit_mode"] == "ceremonial"
    b = data["bundle"]
    assert "ceremonial_header" in b or "[" in b.get("story_seed", "")