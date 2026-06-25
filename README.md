# SQT-Exploring-the-Possibilities

**Exploration side-quest for Squirrel Quantum Time (SQT).**

Structured test of the v2 Grok-Agents Memory Ecosystem handoff process while designing **The Messenger's Circuit** — holidays, daily oracle bundle, and widget contracts for the [Squirrel-Quantum-Time](https://github.com/squirrel814/Squirrel-Quantum-Time) vision.

## Current Phase

**Phase 3 — Implementation** **archived** (good enough, Track A distillation complete) — Phases 4–7 optional

| Segment | Status |
|---------|--------|
| 2.1 Engine & Data Foundation | Complete |
| 2.2 Themes, Style & Prompt Core | Complete |
| 2.3 Widget Specs | Complete |
| 2.4 Variants | Complete |

See `phase2-schedule.md` for the segment table. Segment 2.5 was removed (accidental process drift).

## Engine (This Repo Only)

- **`reference/sqt_engine_2.py`** — Read-only upstream snapshot (precision source)
- **`sqt_engine_unified.py`** — Headless rewrite with holidays + `generate_bundle()` + widget JSON

```bash
pip install -r requirements-dev.txt
python sqt_engine_unified.py --json --bundle --compact
python sqt_engine_unified.py --json --simulate-lunation 6 --simulate-day 7 --bundle
python -m pytest tests/ -q
python scripts/export_static_feed.py
python scripts/sync_docs_widgets.py
```

This repo does **not** modify the upstream Squirrel-Quantum-Time repository.

## Static feeds & docs sync (Option B)

`docs/circuit-current.json`, `docs/circuit-holiday-only.json`, and `docs/calendar_matrix.json` are **committed to git** with a `generated_at` timestamp. Regenerate on each release or deploy:

```bash
python scripts/export_static_feed.py    # engine JSON → docs/
python scripts/sync_docs_widgets.py       # widgets/sqt-grove-clock/ → docs/
```

Widget JS/CSS in `docs/` must stay in sync with `widgets/sqt-grove-clock/` — always run `sync_docs_widgets.py` after editing the web component.

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
| `sqt-holidays.json` / `sqt-themes.json` | Production lore (canonical) |
| `sqt-holidays.sample.json` / `sqt-themes.sample.json` | Design snapshots → `scripts/promote_lore.py` |
| `sqt-grove-style-guide.md` | Visual + prompt direction |
| `phase2-completion-summary.md` | Phase 2 close-out, 2.4 decisions, Phase 3 handoff |
| `phase2-architecture-diagram.md` | Data flow + implemented vs spec boundaries |
| `SESSION_HANDOFF_PROMPT.md` | Paste into new agent sessions |
| `Post_Project_Summary.md` | Phase 3 archive + Memory Island distillation source |

## Widget Specs & Scaffolds (Phase 3 Chunk E)

| Path | Role |
|------|------|
| `phase2-2.3-widget-specs.md` | Binding contracts |
| `widgets/discord-bot/` | Ratatoskr Grove Messenger (`DISCORD_BOT_TOKEN`) |
| `widgets/sqt-grove-clock/` | `<sqt-grove-clock>` web component (source of truth) |
| `widgets/vscode-sqt-grove/` | VS Code status bar + insert bundle |
| `docs/` | PWA demo (manifest, SW, static JSON feeds) |
| `lib/sqt-core.js` | JS engine parity with Python (12×19 lunations) |
| `scripts/sync_docs_widgets.py` | Copy widget assets into `docs/` |

## Tests & Validation

- **CI:** `.github/workflows/ci.yml` runs `pytest` on push/PR (Python 3.11 + Node 20 for JS parity)
- **Schema:** `jsonschema` enforced on engine load (`--skip-schema-validation` to bypass)
- **Holiday matrix:** `tests/test_holiday_matrix.py` — all **12 lunations × 19 days**
- **Python/JS parity:** `tests/test_sqt_parity.py` — requires Node.js locally
- **Bundle field:** canonical key is `foraging_idea` (not `forage_idea`)

## GitHub Pages (PWA demo)

Static site is served from the `/docs` folder.

**If Settings → Pages shows no Source dropdown:** the repo must be **public** (free plan) or on **GitHub Pro** (private). Change visibility under **Settings → General → Danger zone**.

1. Open repo **Settings → Pages**
2. **Build and deployment → Source:** **Deploy from a branch**
3. **Branch:** `master` · **Folder:** `/docs` → Save
4. Site publishes at `https://squirrel814.github.io/SQT-Exploring-the-Possibilities/` (GitHub runs `pages build and deployment` automatically — no custom workflow needed)

Before each deploy, refresh committed feeds and widget assets:

```bash
python scripts/export_static_feed.py
python scripts/sync_docs_widgets.py
git add docs/ && git commit -m "Refresh static feeds and widget assets"
```

## License

MIT — see [LICENSE](LICENSE).

## Lore promotion

```bash
python scripts/promote_lore.py --force   # after editing *.sample.json
```

## Next Steps (Phase 3)

1. Manual PWA pass in browser (see `Post_Project_Summary.md` § PWA Verification)
2. VS Code F5 extension UI smoke
3. Discord Ratatoskr — resume when wanted (scaffold + partial live smoke OK)

---

*For the squirrels. For better time. For the acorns.*