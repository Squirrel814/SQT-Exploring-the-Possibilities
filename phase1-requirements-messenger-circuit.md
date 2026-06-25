# Phase 1 — Messenger’s Circuit & Widget Requirements

**Status:** Refined for consolidated Phase 1  
**Aligned to:** Creative-Ideas.md, Phased_Plan v0.2 (consolidated), reference/sqt_engine_2.py, sqt-holidays.schema.json, sqt-themes.schema.json

**Purpose:** Define clear, actionable requirements for the core daily engine and delivery surfaces. This is analysis-level only — design and implementation belong in Phase 2.

## 1. The Messenger’s Circuit Prompt Engine Requirements

### Inputs (from Unified Engine)
- Current SQT stamp (year, lunation, day, time components)
- Active holiday context (recurring / major / rare)
- Active theme data from `sqt-themes.json`
- Optional: user project priorities / context (lightweight JSON)

### Output Bundle (always cohesive)
Must return a single thematically unified package containing:

1. **Journal Prompt** — Reflective, tied to day + holiday
2. **Mood Board** — Palette + imagery descriptors + ready image prompt + atmosphere
3. **Story Seed** — Short squirrel-protagonist narrative starter
4. **Art Prompt** — Detailed prompt following SQT Grove Style
5. **Foraging Idea** — Actionable micro-task (general / holiday-specific / project-aware)

### Modes (must support)
- Standard (default balanced bundle)
- Minimal Whisper
- Project-Deep (heavy user context influence)
- Storytelling (maintains evolving protagonist across days)
- Major Event (ceremonial, richer language)

### Implementation Rules
- **Tiered assembly** (adopted from review): 
  1. System Base Prompt (Ratatoskr voice anchor)
  2. Holiday/Event Specific Lexicon Block (from sqt-themes.json)
  3. User Variable Node (optional project context)
  4. Structural Output Anchor (strict schema for the 5-element bundle)
- All styling data (palettes, motifs, style_modifiers, tone_keywords) **must** come from `sqt-themes.json`
- Output **must** be available as structured data (JSON) in addition to rendered text so widgets can consume it cleanly
- The engine produces high-quality, ready-to-use prompt templates. It does **not** make direct LLM calls.

## 2. Widget Interface Requirements

### Common Requirements (all widgets)
- Must query the same canonical engine (headless JSON preferred)
- Must surface current holiday + link to full Circuit
- Must respect SQT purity (no Gregorian logic)
- Support Major Event special behavior

### A. Discord Bot ("Ratatoskr Grove Messenger")
- Commands:
  - `/circuit` — full or teaser bundle
  - `/forage` — focused foraging idea
  - `/holiday` or `/event` — current holiday lore
  - `/lore-drop` — user submission (moderated queue)
- Feature: Ratatoskr Relay (collaborative storytelling threads)
- Output format: Clean, embed-friendly responses

### B. Web Component `<sqt-grove-clock>`
- Live display of SQT time + active holiday indicator
- Mini calendar or upcoming events
- Modal with:
  - Full lore
  - Teaser bundle
  - One-click "Generate full Messenger’s Circuit"
- Attributes: `data-src` for holidays/themes, theming support
- Must work embedded (personal sites, Notion, etc.)

### C. VS Code Integration
- Status bar: `Year 1, Canopy • Day 7 • Leybridge Threading`
- Command: `Insert Messenger’s Circuit Bundle` (pastes as comment or markdown block)
- Hover tooltips with short lore + foraging suggestion

### Data Contracts
All widgets should be able to consume a consistent JSON response from the engine. Minimum recommended shape:

```json
{
  "sqt": {
    "year": 1,
    "lunation": 6,
    "day": 7,
    "time": "14:22:05"
  },
  "holiday": {
    "id": "leybridge_threading",
    "name": "Leybridge Threading",
    "type": "recurring"
  },
  "bundle": {
    "journal_prompt": "...",
    "mood_board": { "palette": [...], "image_prompt": "...", "atmosphere": "..." },
    "story_seed": "...",
    "art_prompt": "...",
    "foraging_idea": "..."
  },
  "themes": {
    "palettes": [...],
    "motifs": [...],
    "style_modifiers": "..."
  }
}
```

This shape directly supports the schemas and the tiered prompt assembly.

## 3. Success Criteria for Phase 1 Completion

- Engine can be called headlessly and returns consistent JSON (`sqt_engine_unified.py --json --bundle`)
- Schemas for holidays and themes are defined (`sqt-holidays.schema.json` and `sqt-themes.schema.json`)
- Prompt engine requirements clearly specify inputs, 5-element bundle, modes, and tiered assembly using themes data
- Widget interface requirements define Discord, `<sqt-grove-clock>`, and VS Code contracts with shared data shape
- All requirements are traceable back to Creative-Ideas.md and the consolidated Phased Plan

These items are now ready for review as part of the Phase 1 Phase Review / Gate (customized lighter language). Detailed design, sample data, and actual templates move to Phase 2.