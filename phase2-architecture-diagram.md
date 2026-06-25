# Phase 2 Architecture Diagram

**Updated:** Segment 2.3 — widget integration layer added

## High-Level Data Flow

```mermaid
graph TD
    REF[reference/sqt_engine_2.py<br/>read-only snapshot] -.->|fidelity| ENG
    ENG[sqt_engine_unified.py<br/>--json --bundle] --> HD[sqt-holidays.sample.json]
    ENG --> TH[sqt-themes.sample.json]
    ENG --> JSON[(Canonical JSON<br/>sqt + holiday + bundle + themes)]
    JSON --> MODE_A[Mode A: subprocess]
    JSON --> MODE_B[Mode B: circuit-current.json]
    JSON --> MODE_C[Mode C: HTTP feed future]
    MODE_A --> DISCORD[Discord Bot<br/>Ratatoskr Grove Messenger]
    MODE_B --> WEB["Web Component<br/>&lt;sqt-grove-clock&gt;"]
    MODE_A --> VSCODE[VS Code Extension<br/>sqt-grove]
    MODE_B --> PWA[PWA / GitHub Pages]
    EXPORT[export_static_feed.py<br/>Phase 3] --> MODE_B
    EXPORT --> CAL[calendar_matrix.json]
    CAL --> WEB
    DISCORD --> LORE[/lore-drop queue/]
    DISCORD --> RELAY[Ratatoskr Relay threads]
    WEB --> SHARE[Share / Copy bundle]
```

## Widget Boundary Layer (Segment 2.3)

```mermaid
graph LR
    subgraph Contracts
        SPEC[phase2-2.3-widget-specs.md]
    end
    subgraph Discord
        C1[/circuit/]
        C2[/forage/]
        C3[/holiday/]
        C4[/lore-drop/]
    end
    subgraph Web
        W1[Status clock]
        W2[Holiday badge]
        W3[Circuit modal]
        W4[Calendar mini]
    end
    subgraph VSCode
        V1[Status bar]
        V2[insertBundle]
        V3[insertForage]
    end
    SPEC --> Discord
    SPEC --> Web
    SPEC --> VSCode
    JSON --> C1 & C2 & C3
    JSON --> W1 & W2 & W3
    JSON --> V1 & V2 & V3
```

## Module Boundaries

| Layer | Owner | Segment | Deliverable |
|-------|-------|---------|-------------|
| Engine | Jasper | 2.1 | `sqt_engine_unified.py` |
| Themes & bundles | Crystal + Jasper | 2.2 | `sqt-grove-style-guide.md`, themes JSON |
| **Widget contracts** | **Crystal + Jasper** | **2.3** | **`phase2-2.3-widget-specs.md`** |
| Static / PWA | Jasper + Crystal | 2.3 | `phase2-2.3-pwa-outline.md` |
| Curriculum | Cyber-SQRRL | 2.4 | Squirrel Ops labs in design_notes |

## Data Contract (widget-facing)

All three widgets read the same four top-level keys. Implementation must not parse `_extended` for production UI.

```
sqt_engine_unified.py --json --bundle
  → sqt { year, lunation, day, time }
  → holiday { id, name, type } | null
  → themes { palettes, motifs, style_modifiers, tone_keywords }
  → bundle { journal_prompt, mood_board, story_seed, art_prompt, foraging_idea }
```

## Resolved Design Questions (2.3)

| Question | Decision |
|----------|----------|
| Widget data source | Canonical engine JSON; static export for embeds |
| Trimmed vs display names | Trimmed default in status lines; `_extended.sqt_full` when available |
| Bundle depth per surface | Teaser default (Discord, web preview); full on explicit action |
| Upstream repo changes | None — all engine work stays in this exploration repo |

## Open Questions (Phase 3)

- Ratatoskr Relay persistence across lunation boundaries?
- LLM enrichment layer (optional) vs template-only bundles?
- Discord scheduled post cadence: SQT day boundary vs fixed Earth cron?

*Lightweight Reference: See Post_Project_Summary.md*