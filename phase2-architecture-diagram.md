# Phase 2 Architecture Diagram

**Updated:** Phase 2 complete — implementation boundaries added (2026-06-24)

## Implementation Boundaries

| Layer | Artifact | Design | Implemented | Spec-only / gap |
|-------|----------|--------|-------------|-----------------|
| Reference | `reference/sqt_engine_2.py` | ✅ | ✅ | — |
| Engine | `sqt_engine_unified.py` | ✅ | ✅ | LLM enrichment layer |
| Validation | `sqt_schema_validate.py` + tests | ✅ | ✅ | — |
| Data | `sqt-holidays.sample.json` | ✅ | ✅ | Production lore files |
| Data | `sqt-themes.sample.json` | ✅ | ✅ | — |
| JS parity | `lib/sqt-core.js` | ✅ | ✅ | — |
| Static export | `scripts/export_static_feed.py` | ✅ | ✅ | — |
| Docs sync | `scripts/sync_docs_widgets.py` | ✅ | ✅ | — |
| PWA shell | `docs/index.html`, manifest, SW | ✅ | ✅ | Pages enable (Settings) |
| Discord | `widgets/discord-bot/bot.py` | ✅ | ⚠️ scaffold | Relay, rate limits, sanitization |
| Web | `widgets/sqt-grove-clock/` | ✅ | ⚠️ scaffold | Calendar grid, full a11y |
| VS Code | `widgets/vscode-sqt-grove/` | ✅ | ⚠️ scaffold | Major-event UX |
| Curriculum | Squirrel Ops labs | ✅ | 📝 design | Full Time is Relative module |
| Future API | Mode C HTTP feed | ✅ | — | Not started |

Legend: **✅** runnable · **⚠️** partial scaffold · **📝** documented only · **—** not started

---

## High-Level Data Flow

```mermaid
graph TD
    REF[reference/sqt_engine_2.py<br/>read-only snapshot] -.->|fidelity| ENG
    ENG[sqt_engine_unified.py<br/>IMPLEMENTED] --> HD[sqt-holidays.sample.json]
    ENG --> TH[sqt-themes.sample.json]
    ENG --> JSON[(Canonical JSON<br/>sqt + holiday + bundle + themes)]
    JSON --> MODE_A[Mode A: subprocess<br/>IMPLEMENTED]
    JSON --> MODE_B[Mode B: circuit-current.json<br/>IMPLEMENTED]
    JSON --> MODE_C[Mode C: HTTP feed<br/>SPEC ONLY]
    MODE_A --> DISCORD[Discord Bot<br/>SCAFFOLD]
    MODE_B --> WEB["Web Component<br/>SCAFFOLD"]
    MODE_A --> VSCODE[VS Code Extension<br/>SCAFFOLD]
    MODE_B --> PWA[PWA / GitHub Pages<br/>IMPLEMENTED shell]
    EXPORT[export_static_feed.py<br/>IMPLEMENTED] --> MODE_B
    EXPORT --> CAL[calendar_matrix.json]
    CAL --> WEB
    DISCORD --> LORE[/lore-drop queue<br/>PARTIAL]
    DISCORD -.-> RELAY[Ratatoskr Relay<br/>SPEC ONLY]
    WEB --> SHARE[Share / Copy bundle<br/>PARTIAL]
```

Solid nodes = implemented or runnable. Dashed = spec-only or not built.

---

## Widget Boundary Layer

```mermaid
graph LR
    subgraph Contracts
        SPEC[phase2-2.3-widget-specs.md<br/>COMPLETE]
    end
    subgraph Discord
        C1[/circuit/ ✅]
        C2[/forage/ ✅]
        C3[/holiday/ ⚠️]
        C4[/lore-drop/ ⚠️]
        C5[Relay ○]
    end
    subgraph Web
        W1[Status clock ✅]
        W2[Holiday badge ✅]
        W3[Circuit modal ✅]
        W4[Calendar mini ○]
    end
    subgraph VSCode
        V1[Status bar ✅]
        V2[insertBundle ✅]
        V3[insertForage ✅]
        V4[Major UX ○]
    end
    SPEC --> Discord
    SPEC --> Web
    SPEC --> VSCode
    JSON --> C1 & C2 & C3 & C4
    JSON --> W1 & W2 & W3
    JSON --> V1 & V2 & V3
```

✅ implemented · ⚠️ partial vs spec · ○ spec-only

---

## Module Boundaries

| Layer | Owner | Segment | Deliverable | Phase 3 |
|-------|-------|---------|-------------|---------|
| Engine | Jasper | 2.1 | `sqt_engine_unified.py` | Maintain |
| Themes & bundles | Crystal + Jasper | 2.2 | `sqt-grove-style-guide.md`, themes JSON | Expand lore |
| Widget contracts | Crystal + Jasper | 2.3 | `phase2-2.3-widget-specs.md` | Harden scaffolds |
| Static / PWA | Jasper + Crystal | 2.3 | `docs/`, PWA outline | Enable Pages |
| Curriculum | Cyber-SQRRL | 2.4 | Squirrel Ops labs in `design_notes.md` | Pilot injection |
| CI / release | Jasper | 3 | `.github/workflows/ci.yml`, export+sync | Automate |

---

## Data Contract (widget-facing)

All three widgets read the same four top-level keys. Production UI uses `--compact` (omits `_extended`, `_note`).

```
sqt_engine_unified.py --json --bundle --compact
  → sqt { year, lunation, day, time }
  → holiday { id, name, type } | null
  → themes { palettes, motifs, style_modifiers, tone_keywords }
  → bundle { journal_prompt, mood_board, story_seed, art_prompt, foraging_idea }
```

---

## Resolved Design Questions

| Question | Decision | Status |
|----------|----------|--------|
| Widget data source | Canonical engine JSON; static export for embeds | ✅ Implemented |
| Trimmed vs display names | Trimmed default; `_extended.sqt_full` when available | ✅ Implemented |
| Bundle depth per surface | Teaser default; full on explicit action | ⚠️ Partial in widgets |
| Upstream repo changes | None — engine work stays in this repo | ✅ Invariant |
| Template vs LLM bundles | Template-only in engine (Variant 1) | ✅ Implemented |
| Static feed policy | Option B — commit `docs/*.json` with `generated_at` | ✅ Documented |

---

## Open Questions (Phase 3+)

- Ratatoskr Relay persistence across lunation boundaries?
- LLM enrichment layer (optional) vs template-only bundles?
- Discord scheduled post cadence: SQT day boundary vs fixed Earth cron?
- When to promote `*.sample.json` to production lore files?

---

**Phase 2 close-out:** See `phase2-completion-summary.md` for segment table, 2.4 decision matrices, and handoff chunks.

*Lightweight Reference: See Post_Project_Summary.md*