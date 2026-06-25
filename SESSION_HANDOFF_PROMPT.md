# SESSION_HANDOFF_PROMPT.md

**Purpose:** Copy the block below into a new Grok session to continue SQT-Exploring-the-Possibilities.

**Last updated:** 2026-06-24 (after 12×19 calendar grid + cell teaser modal)

---

**START OF PASTEABLE PROMPT**

You are Grok continuing **SQT-Exploring-the-Possibilities** at Phase 3 — widget hardening and live verification.

**Repo:** `C:\Users\Inter\Documents\GitHub\SQT-Exploring-the-Possibilities`  
**Remote:** https://github.com/Squirrel814/SQT-Exploring-the-Possibilities (public)  
**Live PWA:** https://squirrel814.github.io/SQT-Exploring-the-Possibilities/  
**Source of truth:** `project-logs/SQT-Exploring-the-Possibilities_Project-Update.md`  
**Binding contracts:** `phase2-2.3-widget-specs.md`

---

## Phase status

| Phase | Status |
|-------|--------|
| Phase 2 (design) | **Closed** — `phase2-completion-summary.md`, `phase2-architecture-diagram.md` |
| Phase 3 (implementation) | **In progress** — Chunk E widgets + release hygiene |

**Latest commit:** `63f5a8d` — Web 12×19 calendar grid + cell click → teaser modal

**CI:** Green — pytest (26) + `test_sqt_grove_clock_helpers.mjs` + `test_vscode_format.mjs` on push

**GitHub Pages:** Live — branch `master`, folder `/docs` (legacy branch deploy; do **not** use conflicting `actions/deploy-pages` workflow)

---

## Completed this session arc (do not re-implement)

### Infrastructure
- MIT LICENSE, `.github/workflows/ci.yml`
- `export_static_feed.py` + `sync_docs_widgets.py` (Option B static feeds)
- Repo made public to enable Pages

### Discord (`widgets/discord-bot/`)
- `/lore-drop`: 3/user/24h rate limit, mention/URL sanitization, `submitted_at`
- `/holiday`: `calendar_matrix.json` fallback when `holiday: null`
- Major-event embed accents + **Start Ratatoskr Relay** button on `/circuit mode:full`
- Helpers: `discord_helpers.py` + `tests/test_discord_helpers.py`

### Web (`widgets/sqt-grove-clock/`)
- **Live clock** via client-side `sqt-core.js` (ticks every second)
- **Terminology:** 12 **Moons** (not Lunations); day names (`Stash-day`); "Lunation" only on day 10 (Full Moon)
- **A11y:** focus trap + Esc in modal, high-contrast toggle, `sqt-holiday-change` event `{ previous, current }`
- **Calendar strip:** current Moon’s 19 day cells + upcoming holidays list (`show-calendar` default true)
- **Calendar grid:** full 12×19 mini-grid (`calendar-view` default `both`); cell click → teaser modal; matrix teasers in export
- **Share:** `navigator.share` on modal when browser supports it
- SW cache: `sqt-shell-v4` / `sqt-data-v4`

### VS Code (`widgets/vscode-sqt-grove/`)
- `$(star-full)` status bar icon when `holiday.type === "major"`
- Ceremonial insert header from `themes.tone_keywords`
- Moon/day labels in status + insert; `vscode-format.js` + tests

---

## Still open (priority order)

### 1. Live smoke tests
| Surface | Automated | Manual |
|---------|-----------|--------|
| **PWA** | `python scripts/smoke_widget_triad.py` (live asset HTTP 200) | Hard refresh; clock ticks; grid cell click; modal Tab/Esc |
| **Discord** | `pytest tests/test_discord_relay.py`; engine fetch in smoke triad | `DISCORD_BOT_TOKEN` → `python widgets/discord-bot/bot.py`; test 4 commands + Relay button |
| **VS Code** | `node tests/test_vscode_extension_smoke.mjs` | F5 on `widgets/vscode-sqt-grove` (`.vscode/launch.json`); status bar + insert |

### 2. Discord — remaining spec gaps (§3)
- ~~Ratatoskr Relay polish (thread tags)~~ ✅ — `relay`, `{holiday.id}`, `lunation-{n}`; forum `applied_tags` when configured
- Scheduled `#grove-circuit` teaser posts (optional cron)
- Mode B: cron-refreshed static JSON instead of subprocess

### 3. Web — remaining spec gaps (§4)
- ~~Full **12×19 calendar mini-grid**~~ ✅ (commit `63f5a8d`)
- ~~Click calendar cell → Messenger teaser modal~~ ✅
- ~~`navigator.share` on modal copy~~ ✅ (when `navigator.share` available)

### 4. VS Code — remaining spec gaps (§5)
- Language-aware comment syntax from `document.languageId`
- `sqtGrove.status` item ID alignment with package.json contributions

### 5. Release hygiene (after any widget/data change)
```bash
cd C:\Users\Inter\Documents\GitHub\SQT-Exploring-the-Possibilities
python scripts/export_static_feed.py
python scripts/sync_docs_widgets.py
python -m pytest tests/ -q
node tests/test_sqt_grove_clock_helpers.mjs
node tests/test_vscode_format.mjs
git add docs/ widgets/
git commit -m "Refresh static feeds and widget assets"
git push origin master
```

### 6. Medium-term (Chunk F + data)
- Cyber-SQRRL: Squirrel Ops lab injection in `foraging_idea` (opt-in)
- Promote `*.sample.json` → production lore when copy finalized
- Expand `Post_Project_Summary.md` (still stub)
- Log Phase 3 chunks in project log (one entry per shipped chunk)

---

## Key files (load first)

| File | Why |
|------|-----|
| `phase2-2.3-widget-specs.md` | Widget contracts |
| `sqt_engine_unified.py` | Headless engine + `generate_bundle()` |
| `lib/sqt-core.js` | Browser SQT math (parity with engine) |
| `docs/circuit-current.json` | Static feed (Mode B) |
| `docs/calendar_matrix.json` | Holiday calendar for strip + Discord |
| `widgets/sqt-grove-clock/sqt-grove-clock.js` | Web component |
| `widgets/discord-bot/bot.py` | Discord bot |
| `widgets/vscode-sqt-grove/extension.js` | VS Code extension |

**Engine quick test:**
```bash
python sqt_engine_unified.py --json --bundle --compact
python sqt_engine_unified.py --json --bundle --simulate-lunation 6 --simulate-day 19  # major event
python -m pytest tests/ -q
```

---

## Terminology rules (user-confirmed)

- **Moon** = the 12 periods per SQT year (`Canopy Moon`, not "Lunation 6")
- **Lunation** = reserved for Full Moon / day 10 only
- **Day names** = `Stash-day`, `Nap-day`, etc. (never bare "Day 7" in UI)
- Engine context strings use `Canopy Moon, Stash-day` (see `_format_sqt_context`)

---

## Roles (unchanged)

- **Jasper** — engine, JSON, widget backends
- **Crystal** — web UX, PWA, style
- **Cyber-SQRRL** — Squirrel Ops labs / curriculum injection
- **Alex Pericles** — Discord hygiene, external surface security

**Process:** Log meaningful chunk completions in `project-logs/SQT-Exploring-the-Possibilities_Project-Update.md`. No formal comprehension gates.

---

## Recommended first move next session

Pick one:

1. **Smoke-test triad** — PWA hard refresh + Discord token run + VS Code F5 (report gaps only)
2. **Discord Relay polish** — thread naming/tags per §3.3
3. **Web 12×19 grid** — expand calendar strip into full mini-grid with cell click → teaser
4. **Chunk F** — Squirrel Ops lab injection in engine `foraging_idea`

Start by loading `phase2-2.3-widget-specs.md` and the relevant widget folder, then execute — do not re-do completed work listed above.

**END OF PASTEABLE PROMPT**

---

**Usage:** Copy everything between START/END into a fresh Grok chat. Add any new user priorities at the top.