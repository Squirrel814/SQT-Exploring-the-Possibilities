"""Pure helpers for Ratatoskr Grove Messenger (testable without discord.py)."""

from __future__ import annotations

import json
import re
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

LORE_RATE_LIMIT = 3
LORE_RATE_WINDOW = timedelta(hours=24)

EMBED_COLORS = {
    "recurring": 0x2E5A44,
    "major": 0xFF8F00,
    "rare": 0x37474F,
    None: 0x8C6239,
}

MENTION_PATTERN = re.compile(r"<@!?\d+>|<#\d+>|<@&\d+>")
URL_PATTERN = re.compile(
    r"https?://[^\s<>]+|www\.[^\s<>]+",
    re.IGNORECASE,
)


def sqt_linear_index(lunation: int, day: int, days_per_lunation: int = 19) -> int:
    return (lunation - 1) * days_per_lunation + (day - 1)


def find_next_holiday(
    matrix: dict,
    lunation: int,
    day: int,
) -> Optional[dict]:
    """Return the next calendar cell with a holiday after the current SQT position."""
    cells = matrix.get("cells") or []
    if not cells:
        return None

    days_per = matrix.get("sqt_days_per_lunation", 19)
    current = sqt_linear_index(lunation, day, days_per)
    total = len(cells)

    for offset in range(1, total + 1):
        cell = cells[(current + offset) % total]
        if cell.get("holiday_id"):
            return cell
    return None


def sanitize_lore_text(text: str) -> Tuple[str, List[str]]:
    """Strip Discord mentions and remove URLs (returned separately for logging)."""
    urls = URL_PATTERN.findall(text)
    cleaned = MENTION_PATTERN.sub("", text)
    cleaned = URL_PATTERN.sub("", cleaned)
    cleaned = cleaned.replace("@everyone", "").replace("@here", "")
    cleaned = re.sub(r"\s+", " ", cleaned).strip()
    return cleaned, urls


def count_recent_lore_submissions(
    queue_path: Path,
    user_id: str,
    now: Optional[datetime] = None,
) -> int:
    if not queue_path.exists():
        return 0

    now = now or datetime.now(timezone.utc)
    cutoff = now - LORE_RATE_WINDOW
    count = 0

    with queue_path.open(encoding="utf-8") as handle:
        for line in handle:
            line = line.strip()
            if not line:
                continue
            try:
                entry = json.loads(line)
            except json.JSONDecodeError:
                continue
            if str(entry.get("user_id")) != str(user_id):
                continue
            submitted = entry.get("submitted_at")
            if not submitted:
                continue
            try:
                ts = datetime.fromisoformat(submitted.replace("Z", "+00:00"))
            except ValueError:
                continue
            if ts.tzinfo is None:
                ts = ts.replace(tzinfo=timezone.utc)
            if ts >= cutoff:
                count += 1
    return count


def lore_rate_limited(queue_path: Path, user_id: str, now: Optional[datetime] = None) -> bool:
    return count_recent_lore_submissions(queue_path, user_id, now) >= LORE_RATE_LIMIT


def embed_color_for_holiday(holiday: Optional[Dict[str, Any]], themes: Optional[Dict[str, Any]] = None) -> int:
    if holiday:
        tier = holiday.get("type")
        if tier in EMBED_COLORS:
            return EMBED_COLORS[tier]
    if themes:
        palettes = themes.get("palettes") or []
        if palettes:
            return int(str(palettes[0]).lstrip("#"), 16)
    return EMBED_COLORS[None]


def load_calendar_matrix(path: Path) -> dict:
    with path.open(encoding="utf-8") as handle:
        return json.load(handle)