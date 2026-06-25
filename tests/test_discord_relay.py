"""Ratatoskr Relay helpers + bot engine smoke (no Discord token required)."""

from __future__ import annotations

import sys
from pathlib import Path
from types import SimpleNamespace

import pytest

ROOT = Path(__file__).resolve().parents[1]
HELPERS = ROOT / "widgets" / "discord-bot"
sys.path.insert(0, str(HELPERS))

from discord_helpers import (  # noqa: E402
    fetch_circuit,
    relay_opener_message,
    relay_tag_names,
    relay_thread_name,
    resolve_forum_tag_ids,
)


def test_relay_tag_names():
    assert relay_tag_names("shadow_trial", 6) == ["relay", "shadow_trial", "lunation-6"]


def test_relay_thread_name():
    assert relay_thread_name("shadow_trial", 6) == "relay-shadow_trial-lunation-6"


def test_relay_opener_includes_tags():
    opener = relay_opener_message("Fog in the Grove.", "shadow_trial", 6)
    assert "Fog in the Grove." in opener
    assert "Continue the tale" in opener
    assert "`relay`" in opener
    assert "`shadow_trial`" in opener
    assert "`lunation-6`" in opener


def test_resolve_forum_tag_ids_case_insensitive():
    tags = [
        SimpleNamespace(name="Relay", id=10),
        SimpleNamespace(name="shadow_trial", id=20),
        SimpleNamespace(name="lunation-6", id=30),
        SimpleNamespace(name="other", id=99),
    ]
    ids = resolve_forum_tag_ids(tags, relay_tag_names("shadow_trial", 6))
    assert ids == [10, 20, 30]


def test_resolve_forum_tag_ids_skips_unknown():
    tags = [SimpleNamespace(name="relay", id=10)]
    assert resolve_forum_tag_ids(tags, relay_tag_names("shadow_trial", 6)) == [10]


def test_fetch_circuit_live_engine():
    data = fetch_circuit(ROOT, timeout=5)
    assert "sqt" in data
    assert data["sqt"]["lunation"] >= 1
    assert "bundle" in data
    assert data["bundle"].get("journal_prompt")


def test_fetch_circuit_major_simulate():
    """Major-event path used by Relay button on /circuit mode:full."""
    engine = ROOT / "sqt_engine_unified.py"
    import json
    import subprocess

    cmd = [
        sys.executable,
        str(engine),
        "--json",
        "--compact",
        "--bundle",
        "--simulate-lunation",
        "6",
        "--simulate-day",
        "19",
        "--holidays",
        str(ROOT / "sqt-holidays.json"),
        "--themes",
        str(ROOT / "sqt-themes.json"),
    ]
    out = subprocess.check_output(cmd, cwd=str(ROOT), timeout=5, text=True)
    data = json.loads(out)
    assert data["holiday"]["type"] == "major"
    assert data["bundle"]["story_seed"]