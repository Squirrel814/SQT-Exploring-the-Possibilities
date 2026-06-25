# SQT-Exploring-the-Possibilities

**Exploration side-quest for Squirrel Quantum Time (SQT).**

Structured test of the v2 Grok-Agents Memory Ecosystem handoff process while designing **The Messenger's Circuit** — holidays, daily oracle bundle, and widget contracts for the [Squirrel-Quantum-Time](https://github.com/squirrel814/Squirrel-Quantum-Time) vision.

## Current Phase

**Phase 2 — Segment 2.5 next** (Polish & Phase 2 exit package)

| Segment | Status |
|---------|--------|
| 2.1 Engine & Data Foundation | Complete |
| 2.2 Themes, Style & Prompt Core | Complete |
| 2.3 Widget Specs | Complete |
| 2.4 Variants | Partial |
| 2.5 Polish & Review | Not started |

See `phase2-schedule.md` for the full segment table.

## Engine (This Repo Only)

- **`reference/sqt_engine_2.py`** — Read-only upstream snapshot (precision source)
- **`sqt_engine_unified.py`** — Headless rewrite with holidays + `generate_bundle()` + widget JSON

```bash
pip install -r requirements-dev.txt
python sqt_engine_unified.py --json --bundle
python sqt_engine_unified.py --json --simulate-lunation 6 --simulate-day 7 --bundle
python -m pytest tests/ -q
python scripts/export_static_feed.py
```

This repo does **not** modify the upstream Squirrel-Quantum-Time repository.

## Process (v2 Handoff Test)

- Log entries: `project-logs/SQT-Exploring-the-Possibilities_Project-Update.md`
- Format template: `Project_Update_Log_Template.md` (local copy; canonical at Grok-Agents shared templates)
- SQT stamps: `python C:\Projects\Grok-Agents\scripts\sqt_agent_clock.py --agent [Name]`
- Lightweight refs: `Post_Project_Summary.md`

## Key Artifacts

| File | Role |
|------|------|
| `SQT-Exploring-the-Possibilities_Phased_Plan.md` | Master roadmap (Phases 0–7) |
| `Creative-Ideas.md` | Full creative vision |
| `phase1-requirements-messenger-circuit.md` | Widget + bundle JSON contract |
| `sqt_engine_unified.py` | Runnable engine |
| `sqt-holidays.sample.json` / `sqt-themes.sample.json` | Sample data |
| `sqt-grove-style-guide.md` | Visual + prompt direction |
| `SESSION_HANDOFF_PROMPT.md` | Paste into new agent sessions |
| `Post_Project_Summary.md` | Memory island distillation target (stub) |

## Widget Specs & Scaffolds (Phase 3 Chunk E started)

| Path | Role |
|------|------|
| `phase2-2.3-widget-specs.md` | Binding contracts |
| `widgets/discord-bot/` | Ratatoskr Grove Messenger (`DISCORD_BOT_TOKEN`) |
| `widgets/sqt-grove-clock/` | `<sqt-grove-clock>` web component |
| `widgets/vscode-sqt-grove/` | VS Code status bar + insert bundle |
| `docs/` | PWA demo (manifest, SW, static JSON feeds) |
| `lib/sqt-core.js` | JS engine parity with Python (12×19 lunations) |

## Tests & Validation

- **Schema:** `jsonschema` enforced on engine load (`--skip-schema-validation` to bypass)
- **Holiday matrix:** `tests/test_holiday_matrix.py` — all **12 lunations × 19 days**
- **Python/JS parity:** `tests/test_sqt_parity.py` — requires Node.js

## Next Steps (Segment 2.5)

1. Phase 2 exit package + architecture review
2. Phase 3 chunking: `export_static_feed.py`, widget skeletons
3. Fix rare-event sample data (Shadowforage Eclipse trigger)

---

*For the squirrels. For better time. For the acorns.*