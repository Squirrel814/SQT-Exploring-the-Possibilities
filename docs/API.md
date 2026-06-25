# SQT Public JSON API (static feed — Mode C)

**Base URL:** https://squirrel814.github.io/SQT-Exploring-the-Possibilities/

No API key required. Responses are pre-generated JSON committed to `/docs` (Option B policy). Refresh via `python scripts/export_static_feed.py` on release.

## Stable v1 paths

| Endpoint | Description |
|----------|-------------|
| `/v1/circuit/current.json` | Full circuit: `sqt`, `holiday`, `bundle`, `themes`, `circuit_mode` |
| `/v1/circuit/holiday.json` | SQT + holiday only (no bundle) |
| `/v1/calendar/matrix.json` | 12 Moons × 19 days matrix with holiday teasers |
| `/v1/burrowkins/current.json` | Active Burrowkins hook for current SQT moment |

## Legacy paths (unchanged)

| File | Same as |
|------|---------|
| `circuit-current.json` | `v1/circuit/current.json` |
| `circuit-holiday-only.json` | `v1/circuit/holiday.json` |
| `calendar_matrix.json` | `v1/calendar/matrix.json` |
| `burrowkins-hooks.json` | `v1/burrowkins/current.json` |

## Circuit modes (CLI / engine)

Pass `--circuit-mode` when generating locally:

| Mode | Bundle fields |
|------|---------------|
| `standard` | All 5 elements (auto → `ceremonial` on major holidays) |
| `teaser` | `journal_prompt` + `foraging_idea` |
| `whisper` | `journal_prompt` only |
| `ceremonial` | All 5 + `ceremonial_header` on major/rich days |
| `storytelling` | All 5; `story_seed` prefixed for continuity |
| `project-deep` | All 5 + `--project-context` bias |

```bash
python sqt_engine_unified.py --json --bundle --compact --circuit-mode teaser
python sqt_engine_unified.py --json --bundle --compact --circuit-mode project-deep --project-context "Burrowkins leyline work"
```

## CORS

GitHub Pages serves JSON with permissive access for browser `fetch()` from personal sites and embeds.

## Contract

Shape matches `phase1-requirements-messenger-circuit.md` and `phase2-2.3-widget-specs.md` §2. Widgets should prefer `--compact` output (no `_extended`).