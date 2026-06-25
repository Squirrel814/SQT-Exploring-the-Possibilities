#!/usr/bin/env python3
"""
Ratatoskr Grove Messenger — Discord bot scaffold (Phase 3 Chunk E).
Requires: DISCORD_BOT_TOKEN env var, discord.py

Run: python bot.py
"""

from __future__ import annotations

import asyncio
import json
import os
import sys
from datetime import datetime, timezone
from pathlib import Path

try:
    import discord
    from discord import app_commands
except ImportError:
    print("Install: pip install discord.py", file=sys.stderr)
    raise SystemExit(1)

from discord_helpers import (
    embed_color_for_holiday,
    fetch_circuit,
    find_next_holiday,
    load_calendar_matrix,
    lore_rate_limited,
    relay_opener_message,
    relay_tag_names,
    relay_thread_name,
    resolve_forum_tag_ids,
    sanitize_lore_text,
)

ROOT = Path(__file__).resolve().parents[2]
ENGINE = ROOT / "sqt_engine_unified.py"
CALENDAR_MATRIX = ROOT / "docs" / "calendar_matrix.json"
LORE_QUEUE = Path(__file__).resolve().parent / "lore_queue.jsonl"
ENGINE_TIMEOUT = 3


def embed_from_circuit(data: dict, mode: str = "teaser") -> discord.Embed:
    s = data.get("sqt", {})
    h = data.get("holiday")
    b = data.get("bundle", {})
    t = data.get("themes", {})
    color = embed_color_for_holiday(h, t)

    if h:
        title = f"🌰 {h['name']}"
        if h.get("type") == "major":
            title += " 🌕 Major Lunation Event"
    else:
        title = "🌰 Grove Day — no holiday active"

    title += f" — Year {s.get('year', 1)}, Lunation {s.get('lunation')}, Day {s.get('day')}"

    if mode == "full":
        title = f"The Messenger's Circuit — {h['name'] if h else 'Grove Day'}"
        if h and h.get("type") == "major":
            title += " 🌕 Major Lunation Event"

    embed = discord.Embed(title=title, description=b.get("journal_prompt", "No bundle today."), color=color)
    embed.add_field(name="SQT Time", value=s.get("time", "—"), inline=True)
    if b.get("foraging_idea"):
        embed.add_field(name="Forage Today", value=b["foraging_idea"], inline=False)
    if mode == "full":
        if b.get("story_seed"):
            embed.add_field(name="Story Seed", value=b["story_seed"][:1024], inline=False)
        mood = b.get("mood_board") or {}
        if mood.get("atmosphere"):
            embed.add_field(name="Atmosphere", value=mood["atmosphere"][:1024], inline=False)
    if h and h.get("type") == "rare":
        embed.set_footer(text="Rare event in the Grove • Ratatoskr Grove Messenger")
    else:
        footer = "Ratatoskr Grove Messenger"
        if mode == "teaser":
            footer += " • /circuit mode:full for complete bundle"
        embed.set_footer(text=footer)
    return embed


class RelayStartView(discord.ui.View):
    def __init__(self, story_seed: str, holiday_id: str, lunation: int):
        super().__init__(timeout=300)
        self.story_seed = story_seed
        self.holiday_id = holiday_id
        self.lunation = lunation

    @discord.ui.button(label="Start Ratatoskr Relay", style=discord.ButtonStyle.primary, emoji="🌰")
    async def start_relay(self, interaction: discord.Interaction, button: discord.ui.Button):
        if not interaction.channel:
            await interaction.response.send_message("Cannot open a relay here.", ephemeral=True)
            return

        thread_name = relay_thread_name(self.holiday_id, self.lunation)
        opener = relay_opener_message(self.story_seed, self.holiday_id, self.lunation)
        tag_names = relay_tag_names(self.holiday_id, self.lunation)
        parent = interaction.channel.parent if isinstance(interaction.channel, discord.Thread) else interaction.channel

        try:
            if isinstance(parent, discord.ForumChannel):
                applied = resolve_forum_tag_ids(parent.available_tags, tag_names)
                thread = await parent.create_thread(
                    name=thread_name,
                    content=opener,
                    applied_tags=applied or None,
                    auto_archive_duration=1440,
                )
            else:
                thread = await interaction.channel.create_thread(
                    name=thread_name,
                    type=discord.ChannelType.public_thread,
                    auto_archive_duration=1440,
                )
                await thread.send(opener)
        except discord.HTTPException as exc:
            await interaction.response.send_message(
                f"Could not open relay thread: {exc.text}",
                ephemeral=True,
            )
            return

        await interaction.response.send_message(f"Relay opened in {thread.mention}", ephemeral=True)
        self.stop()


class RatatoskrBot(discord.Client):
    def __init__(self):
        intents = discord.Intents.default()
        super().__init__(intents=intents)
        self.tree = app_commands.CommandTree(self)
        self._guild_sync_id: str | None = None

    async def setup_hook(self):
        guild_id = os.environ.get("DISCORD_GUILD_ID")
        if guild_id:
            guild = discord.Object(id=int(guild_id))
            self.tree.copy_global_to(guild=guild)
            try:
                await self.tree.sync(guild=guild)
                self._guild_sync_id = guild_id
                print(f"Synced slash commands to guild {guild_id}")
                return
            except discord.Forbidden:
                print(
                    f"[warn] Guild sync failed for {guild_id} — Missing Access (50001).\n"
                    "  → Re-invite Ratatoskr with scopes: bot + applications.commands\n"
                    "  → Pick the correct server in the invite URL\n"
                    "  → Falling back to global command sync...",
                    file=sys.stderr,
                )
            except discord.HTTPException as exc:
                print(f"[warn] Guild sync failed: {exc} — falling back to global sync...", file=sys.stderr)

        await self.tree.sync()
        print("Synced global slash commands (may take up to ~1h to appear everywhere)")

    async def on_ready(self):
        print(f"Logged in as {self.user} (ID: {self.user.id})")
        await self._report_guild_membership()

    async def _report_guild_membership(self) -> None:
        """Guild cache is often empty on first on_ready — fetch or wait before warning."""
        target_id = self._guild_sync_id or os.environ.get("DISCORD_GUILD_ID")
        if target_id:
            cached = self.get_guild(int(target_id))
            if cached:
                print(f"Joined servers: {cached.name} ({cached.id})")
                return
            try:
                fetched = await self.fetch_guild(int(target_id))
                print(f"Joined servers: {fetched.name} ({fetched.id})")
                return
            except (discord.NotFound, discord.Forbidden):
                print(
                    f"[warn] Guild {target_id} not reachable — re-invite Ratatoskr "
                    "(scopes: bot + applications.commands).",
                    file=sys.stderr,
                )
                return
            except discord.HTTPException:
                pass

        if not self.guilds:
            await asyncio.sleep(2)
        if self.guilds:
            names = ", ".join(f"{g.name} ({g.id})" for g in self.guilds)
            print(f"Joined servers: {names}")
        elif self._guild_sync_id:
            print(
                f"[info] Commands synced to guild {self._guild_sync_id} — "
                "Ratatoskr is connected (guild name pending in cache).",
            )
        else:
            print(
                "[warn] Ratatoskr is not in any server yet — generate an invite URL in the Developer Portal.",
                file=sys.stderr,
            )


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
        data = fetch_circuit(ROOT, ENGINE, bundle=True, timeout=ENGINE_TIMEOUT)
        m = (mode.value if mode else "teaser")
        embed = embed_from_circuit(data, m)
        view = None
        h = data.get("holiday") or {}
        b = data.get("bundle", {})
        if m == "full" and h.get("type") == "major" and b.get("story_seed"):
            view = RelayStartView(b["story_seed"], h.get("id", "major"), data.get("sqt", {}).get("lunation", 0))
        await interaction.followup.send(embed=embed, view=view)
        if m == "full":
            art = b.get("art_prompt")
            mood = b.get("mood_board") or {}
            image_prompt = mood.get("image_prompt")
            if art:
                await interaction.followup.send(f"```\n{art[:1900]}\n```")
            if image_prompt:
                await interaction.followup.send(f"**Image Prompt**\n```\n{image_prompt[:1900]}\n```")
    except Exception as exc:
        await interaction.followup.send("The leylines are quiet. Try again in a moment.", ephemeral=True)
        print(exc, file=sys.stderr)


@bot.tree.command(name="forage", description="Today's foraging idea")
async def forage(interaction: discord.Interaction):
    await interaction.response.defer()
    data = fetch_circuit(ROOT, ENGINE, bundle=True, timeout=ENGINE_TIMEOUT)
    b = data.get("bundle", {})
    t = data.get("themes", {})
    palettes = t.get("palettes") or ["#2E5A44", "#4CAF50"]
    color = int(str(palettes[1] if len(palettes) > 1 else palettes[0]).lstrip("#"), 16)
    embed = discord.Embed(
        title="Today's Forage",
        description=b.get("foraging_idea", "Gentle intentional action."),
        color=color,
    )
    await interaction.followup.send(embed=embed)


@bot.tree.command(name="holiday", description="Current SQT holiday or event")
async def holiday(interaction: discord.Interaction):
    await interaction.response.defer()
    data = fetch_circuit(ROOT, ENGINE, bundle=False, timeout=ENGINE_TIMEOUT)
    h = data.get("holiday")
    s = data.get("sqt", {})
    t = data.get("themes", {})

    if not h:
        try:
            matrix = load_calendar_matrix(CALENDAR_MATRIX)
            nxt = find_next_holiday(matrix, s.get("lunation", 1), s.get("day", 1))
        except (OSError, json.JSONDecodeError, KeyError):
            nxt = None

        if nxt:
            embed = discord.Embed(
                title="No active holiday",
                description=(
                    f"Plain Grove day. Next up: **{nxt['holiday_name']}** "
                    f"(Lunation {nxt['lunation']}, Day {nxt['day']})"
                ),
                color=embed_color_for_holiday(None),
            )
            embed.add_field(
                name="SQT Position",
                value=f"Year {s.get('year', 1)}, Lunation {s.get('lunation')}, Day {s.get('day')}",
            )
            if nxt.get("type"):
                embed.add_field(name="Next Type", value=nxt["type"], inline=True)
            await interaction.followup.send(embed=embed)
            return

        await interaction.followup.send("No active holiday — plain Grove day.")
        return

    embed = discord.Embed(
        title=h["name"],
        description=f"Type: {h['type']}",
        color=embed_color_for_holiday(h, t),
    )
    embed.add_field(
        name="SQT Position",
        value=f"Year {s.get('year', 1)}, Lunation {s.get('lunation')}, Day {s.get('day')}",
    )
    if t.get("motifs"):
        embed.add_field(name="Motifs", value=", ".join(t["motifs"][:5]), inline=False)
    await interaction.followup.send(embed=embed)


@bot.tree.command(name="lore-drop", description="Submit lore to the moderation burrow")
@app_commands.describe(content="Your story or reflection (max 2000 chars)", title="Optional title")
async def lore_drop(interaction: discord.Interaction, content: str, title: str | None = None):
    if len(content) > 2000:
        await interaction.response.send_message("Too long — keep under 2000 characters.", ephemeral=True)
        return

    if lore_rate_limited(LORE_QUEUE, str(interaction.user.id)):
        await interaction.response.send_message(
            "The burrow is full for today — three lore drops per squirrel per day.",
            ephemeral=True,
        )
        return

    cleaned, urls = sanitize_lore_text(content)
    if not cleaned:
        await interaction.response.send_message(
            "Your lore needs words the Grove can hold (mentions and links are stripped).",
            ephemeral=True,
        )
        return

    data = fetch_circuit(ROOT, ENGINE, bundle=False, timeout=ENGINE_TIMEOUT)
    entry = {
        "submitted_at": datetime.now(timezone.utc).isoformat(),
        "user_id": str(interaction.user.id),
        "title": (title or "")[:100],
        "content": cleaned,
        "urls_logged": urls,
        "sqt_snapshot": data.get("sqt"),
        "holiday_id": (data.get("holiday") or {}).get("id"),
        "status": "pending",
    }
    with LORE_QUEUE.open("a", encoding="utf-8") as f:
        f.write(json.dumps(entry, ensure_ascii=False) + "\n")
    await interaction.response.send_message("Your lore has been scattered to the moderation burrow.", ephemeral=True)


def _load_dotenv() -> None:
    """Load DISCORD_BOT_TOKEN from widgets/discord-bot/.env or repo .env (gitignored)."""
    try:
        from dotenv import load_dotenv
    except ImportError:
        return
    bot_dir = Path(__file__).resolve().parent
    for path in (bot_dir / ".env", bot_dir / "discord-bot.env", ROOT / ".env"):
        if path.is_file():
            load_dotenv(path)
            return


def main():
    _load_dotenv()
    token = os.environ.get("DISCORD_BOT_TOKEN")
    if not token:
        print(
            "Set DISCORD_BOT_TOKEN:\n"
            "  PowerShell: $env:DISCORD_BOT_TOKEN = 'your_token'\n"
            "  Or copy .env.example to .env in widgets/discord-bot/ and paste the token there.",
            file=sys.stderr,
        )
        return 1
    bot.run(token)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())