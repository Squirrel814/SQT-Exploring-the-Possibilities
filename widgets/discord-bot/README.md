# Ratatoskr Grove Messenger (Discord bot scaffold)

Slash commands: `/circuit`, `/forage`, `/holiday`, `/lore-drop`

```bash
pip install -r requirements.txt
set DISCORD_BOT_TOKEN=your_token_here
python bot.py
```

**Faster slash-command testing:** set `DISCORD_GUILD_ID` to your server ID — commands sync instantly to that guild instead of waiting on global propagation.

Calls `sqt_engine_unified.py --json --bundle --compact` from repo root. See `phase2-2.3-widget-specs.md`.

**Ratatoskr Relay** (major events, `/circuit mode:full`):
- Thread name: `relay-{holiday_id}-lunation-{n}`
- Tags: `relay`, `{holiday_id}`, `lunation-{n}` (footer on text-channel threads; forum channels use `applied_tags` when those tag names exist)

**Smoke (no token):** `python scripts/smoke_widget_triad.py` and `pytest tests/test_discord_relay.py -q`