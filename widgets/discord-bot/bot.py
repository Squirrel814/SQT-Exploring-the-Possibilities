#!/usr/bin/env python3
"""
Ratatoskr Grove Messenger — Discord bot scaffold (Phase 3 Chunk E).
Requires: DISCORD_BOT_TOKEN env var, discord.py

Run: python bot.py
"""

from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path

try:
    import discord
    from discord import app_commands
except ImportError:
    print("Install: pip install discord.py", file=sys.stderr)
    raise SystemExit(1)

ROOT = Path(__file__).resolve().parents[2]
ENGINE = ROOT / "sqt_engine_unified.py"


def fetch_circuit(bundle: bool = True) -> dict:
    cmd = [sys.executable, str(ENGINE), "--json"]
    if bundle:
        cmd.append("--bundle")
    cmd += ["--holidays", str(ROOT / "sqt-holidays.sample.json")]
    cmd += ["--themes", str(ROOT / "sqt-themes.sample.json")]
    out = subprocess.check_output(cmd, cwd=str(ROOT), timeout=5, text=True)
    return json.loads(out)


def embed_from_circuit(data: dict, mode: str = "teaser") -> discord.Embed:
    s = data.get("sqt", {})
    h = data.get("holiday")
    b = data.get("bundle", {})
    t = data.get("themes", {})
    color = int((t.get("palettes") or ["#2E5A44"])[0].lstrip("#"), 16)

    title = f"🌰 {h['name']}" if h else "🌰 Grove Day"
    title += f" — Year {s.get('year', 1)}, Lunation {s.get('lunation')}, Day {s.get('day')}"

    embed = discord.Embed(title=title, description=b.get("journal_prompt", "No bundle today."), color=color)
    embed.add_field(name="SQT Time", value=s.get("time", "—"), inline=True)
    if b.get("foraging_idea"):
        embed.add_field(name="Forage Today", value=b["foraging_idea"], inline=False)
    if mode == "full" and b.get("story_seed"):
        embed.add_field(name="Story Seed", value=b["story_seed"][:1024], inline=False)
    embed.set_footer(text="Ratatoskr Grove Messenger")
    return embed


class RatatoskrBot(discord.Client):
    def __init__(self):
        intents = discord.Intents.default()
        super().__init__(intents=intents)
        self.tree = app_commands.CommandTree(self)

    async def setup_hook(self):
        self.tree.copy_global_to(guild=None)
        await self.tree.sync()

    async def on_ready(self):
        print(f"Logged in as {self.user} (ID: {self.user.id})")


bot = RatatoskrBot()


@bot.tree.command(name="circuit", description="Today's Messenger's Circuit")
@app_commands.describe(mode="teaser or full bundle")
@app_commands.choices(mode=[
    app_commands.Choice(name="teaser", value="teaser"),
    app_commands.Choice(name="full", value="full"),
])
async def circuit(interaction: discord.Interaction, mode: app_commands.Choice[str] | None = None):
    await interaction.response.defer()
    try:
        data = fetch_circuit(bundle=True)
        m = (mode.value if mode else "teaser")
        embed = embed_from_circuit(data, m)
        await interaction.followup.send(embed=embed)
        if m == "full" and data.get("bundle", {}).get("art_prompt"):
            await interaction.followup.send(f"```\n{data['bundle']['art_prompt'][:1900]}\n```")
    except Exception as exc:
        await interaction.followup.send("The leylines are quiet. Try again in a moment.", ephemeral=True)
        print(exc, file=sys.stderr)


@bot.tree.command(name="forage", description="Today's foraging idea")
async def forage(interaction: discord.Interaction):
    await interaction.response.defer()
    data = fetch_circuit(bundle=True)
    b = data.get("bundle", {})
    embed = discord.Embed(
        title="Today's Forage",
        description=b.get("foraging_idea", "Gentle intentional action."),
        color=0x2E5A44,
    )
    await interaction.followup.send(embed=embed)


@bot.tree.command(name="holiday", description="Current SQT holiday or event")
async def holiday(interaction: discord.Interaction):
    await interaction.response.defer()
    data = fetch_circuit(bundle=False)
    h = data.get("holiday")
    s = data.get("sqt", {})
    t = data.get("themes", {})
    if not h:
        await interaction.followup.send("No active holiday — plain Grove day.")
        return
    embed = discord.Embed(title=h["name"], description=f"Type: {h['type']}", color=0x4CAF50)
    embed.add_field(name="SQT Position", value=f"Year {s['year']}, Lunation {s['lunation']}, Day {s['day']}")
    if t.get("motifs"):
        embed.add_field(name="Motifs", value=", ".join(t["motifs"][:5]), inline=False)
    await interaction.followup.send(embed=embed)


@bot.tree.command(name="lore-drop", description="Submit lore to the moderation burrow")
@app_commands.describe(content="Your story or reflection (max 2000 chars)", title="Optional title")
async def lore_drop(interaction: discord.Interaction, content: str, title: str | None = None):
    if len(content) > 2000:
        await interaction.response.send_message("Too long — keep under 2000 characters.", ephemeral=True)
        return
    data = fetch_circuit(bundle=False)
    entry = {
        "user_id": str(interaction.user.id),
        "title": (title or "")[:100],
        "content": content,
        "sqt_snapshot": data.get("sqt"),
        "holiday_id": (data.get("holiday") or {}).get("id"),
        "status": "pending",
    }
    queue_path = ROOT / "widgets" / "discord-bot" / "lore_queue.jsonl"
    with queue_path.open("a", encoding="utf-8") as f:
        f.write(json.dumps(entry, ensure_ascii=False) + "\n")
    await interaction.response.send_message("Your lore has been scattered to the moderation burrow.", ephemeral=True)


def main():
    token = os.environ.get("DISCORD_BOT_TOKEN")
    if not token:
        print("Set DISCORD_BOT_TOKEN environment variable.", file=sys.stderr)
        return 1
    bot.run(token)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())