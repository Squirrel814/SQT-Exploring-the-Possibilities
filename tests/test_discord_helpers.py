"""Discord bot helper unit tests (phase2-2.3-widget-specs §3)."""

from __future__ import annotations

import json
from datetime import datetime, timedelta, timezone
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
HELPERS = ROOT / "widgets" / "discord-bot"
import sys

sys.path.insert(0, str(HELPERS))

from discord_helpers import (  # noqa: E402
    count_recent_lore_submissions,
    embed_color_for_holiday,
    find_next_holiday,
    lore_rate_limited,
    sanitize_lore_text,
    sqt_linear_index,
)


@pytest.fixture
def calendar_matrix():
    return json.loads((ROOT / "docs" / "calendar_matrix.json").read_text(encoding="utf-8"))


def test_sqt_linear_index():
    assert sqt_linear_index(1, 1) == 0
    assert sqt_linear_index(1, 19) == 18
    assert sqt_linear_index(2, 1) == 19


def test_find_next_holiday_from_plain_day(calendar_matrix):
    # Lunation 1 day 2 has no holiday; next is day 4 discerned_hoard
    nxt = find_next_holiday(calendar_matrix, lunation=1, day=2)
    assert nxt is not None
    assert nxt["holiday_id"] == "discerned_hoard"
    assert nxt["lunation"] == 1
    assert nxt["day"] == 4


def test_find_next_holiday_wraps_year(calendar_matrix):
    nxt = find_next_holiday(calendar_matrix, lunation=12, day=19)
    assert nxt is not None
    assert nxt["lunation"] == 1
    assert nxt["day"] == 1
    assert nxt["holiday_id"] == "whisperwake_first_message"


def test_sanitize_strips_mentions_and_urls():
    raw = "Hello <@123> see https://evil.example/x and <#999>"
    cleaned, urls = sanitize_lore_text(raw)
    assert "<@" not in cleaned
    assert "https://" not in cleaned
    assert urls == ["https://evil.example/x"]
    assert cleaned == "Hello see and"


def test_sanitize_strips_everyone_here():
    cleaned, _ = sanitize_lore_text("@everyone @here quiet grove")
    assert "@everyone" not in cleaned
    assert "@here" not in cleaned


def test_embed_color_tiers():
    assert embed_color_for_holiday({"type": "major"}) == 0xFF8F00
    assert embed_color_for_holiday({"type": "recurring"}) == 0x2E5A44
    assert embed_color_for_holiday({"type": "rare"}) == 0x37474F
    assert embed_color_for_holiday(None) == 0x8C6239


def test_lore_rate_limit(tmp_path):
    queue = tmp_path / "lore_queue.jsonl"
    now = datetime(2026, 6, 24, 12, 0, tzinfo=timezone.utc)
    user = "user-42"
    lines = []

    for hours_ago in (1, 2, 5):
        ts = (now - timedelta(hours=hours_ago)).isoformat()
        lines.append(json.dumps({"user_id": user, "submitted_at": ts}))
        lines.append(json.dumps({"user_id": "other", "submitted_at": ts}))
    queue.write_text("\n".join(lines) + "\n", encoding="utf-8")

    assert count_recent_lore_submissions(queue, user, now) == 3
    assert lore_rate_limited(queue, user, now)

    old_ts = (now - timedelta(hours=25)).isoformat()
    with queue.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps({"user_id": user, "submitted_at": old_ts}) + "\n")
    assert count_recent_lore_submissions(queue, user, now) == 3