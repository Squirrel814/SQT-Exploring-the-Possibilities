#!/usr/bin/env python3
"""Smoke-test triad reporter — PWA assets, Discord engine path, VS Code feeds.

Manual steps still required for DISCORD_BOT_TOKEN live bot and VS Code F5 UI.
"""

from __future__ import annotations

import json
import os
import subprocess
import sys
import urllib.error
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
PWA_BASE = "https://squirrel814.github.io/SQT-Exploring-the-Possibilities/"
PWA_ASSETS = (
    "circuit-current.json",
    "calendar_matrix.json",
    "sqt-grove-clock.js",
    "sw.js",
    "v1/circuit/current.json",
    "burrowkins-hooks.json",
)


def check_pwa_assets() -> list[str]:
    lines = []
    for name in PWA_ASSETS:
        url = PWA_BASE + name
        try:
            with urllib.request.urlopen(url, timeout=15) as resp:
                ok = 200 <= resp.status < 300
        except urllib.error.URLError as exc:
            ok = False
            lines.append(f"  FAIL {name}: {exc}")
            continue
        lines.append(f"  {'OK' if ok else 'FAIL'} {name} HTTP")
    return lines


def check_discord_engine() -> list[str]:
    sys.path.insert(0, str(ROOT / "widgets" / "discord-bot"))
    from discord_helpers import fetch_circuit, relay_tag_names  # noqa: E402

    lines = []
    token = os.environ.get("DISCORD_BOT_TOKEN")
    lines.append(f"  {'OK' if token else 'SKIP'} DISCORD_BOT_TOKEN set (live bot requires token)")

    data = fetch_circuit(ROOT, timeout=5)
    lines.append(f"  OK engine fetch — Lunation {data['sqt']['lunation']} Day {data['sqt']['day']}")
    if data.get("bundle", {}).get("foraging_idea"):
        lines.append("  OK bundle.foraging_idea present")

    tags = relay_tag_names("shadow_trial", 6)
    lines.append(f"  OK relay tags: {', '.join(tags)}")
    return lines


def check_vscode_feeds() -> list[str]:
    lines = []
    circuit = ROOT / "docs" / "circuit-current.json"
    if not circuit.exists():
        lines.append("  FAIL docs/circuit-current.json missing")
        return lines

    data = json.loads(circuit.read_text(encoding="utf-8"))
    lines.append(f"  OK static feed — Y{data['sqt']['year']} M{data['sqt']['lunation']} D{data['sqt']['day']}")

    ext = ROOT / "widgets" / "vscode-sqt-grove" / "extension.js"
    src = ext.read_text(encoding="utf-8")
    lines.append(
        f"  {'OK' if '--compact' in src else 'FAIL'} extension.js uses --compact engine flag"
    )

    launch = ROOT / "widgets" / "vscode-sqt-grove" / ".vscode" / "launch.json"
    lines.append(f"  {'OK' if launch.exists() else 'SKIP'} .vscode/launch.json for F5")
    return lines


def run_node_smoke(script: str) -> str:
    try:
        subprocess.run(
            ["node", str(ROOT / "tests" / script)],
            cwd=str(ROOT),
            check=True,
            capture_output=True,
            text=True,
            timeout=30,
        )
        return "OK"
    except subprocess.CalledProcessError as exc:
        return f"FAIL ({exc.stderr or exc.stdout or exc})"


def main() -> int:
    print("=== Smoke triad ===\n")
    print("PWA (live Pages):")
    for line in check_pwa_assets():
        print(line)

    print("\nDiscord (engine + relay helpers):")
    for line in check_discord_engine():
        print(line)

    print("\nVS Code (static feed + formatters):")
    for line in check_vscode_feeds():
        print(line)
    print(f"  {run_node_smoke('test_vscode_extension_smoke.mjs')} test_vscode_extension_smoke.mjs")

    print("\nPytest relay suite:")
    try:
        subprocess.run(
            [sys.executable, "-m", "pytest", "tests/test_discord_relay.py", "-q"],
            cwd=str(ROOT),
            check=True,
        )
        print("  OK test_discord_relay.py")
    except subprocess.CalledProcessError:
        print("  FAIL test_discord_relay.py")
        return 1

    if not os.environ.get("DISCORD_BOT_TOKEN"):
        print("\nManual: set DISCORD_BOT_TOKEN and run: python widgets/discord-bot/bot.py")
    print("Manual: F5 in widgets/vscode-sqt-grove (Extension Development Host)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())