# Ready-to-Execute Handoff Packages — End of Phase 1 Target

**Project:** SQT-Exploring-the-Possibilities  
**Version:** Aligned to Phased_Plan v0.2  
**Date:** 2026-06-24

---

## For Jasper (Python / JSON / Engine Specialist)

**Lead Responsibilities:**
- Unified SQT engine library (`sqt_engine_unified.py`)
- Structured JSON output mode
- Holiday detection logic from `sqt-holidays.json`
- Core Messenger’s Circuit prompt assembly (template-based)
- Headless CLI + library interface
- Backend contracts for widgets (Discord, local server, static export)

**Specific Phase 1/2 Micro-Tasks:**
1. Rewrite `reference/sqt_engine_2.py` into `sqt_engine_unified.py` (headless, this repo only).
2. Implement loading + validation against `sqt-holidays.schema.json`.
3. Add `--json`, `--bundle`, `--holiday` CLI flags.
4. Build initial prompt orchestrator that combines SQT state + holiday + themes → 5-element bundle.
5. Create static export script that generates `calendar_matrix.json` for GitHub Pages.
6. Define clean data contracts (JSON shapes) for widgets.

**Success Criteria:**
- Can run `python sqt_engine_unified.py --json` and get reliable output
- Holiday detection works across full 12-lunation simulation
- First version of bundle generation produces coherent output

**References:**
- `reference/sqt_engine_2.py`
- `sqt-holidays.schema.json`
- `phase1-requirements-messenger-circuit.md`
- Creative-Ideas.md (Integration Architecture section)

**Handoff From:** Zeenah / Current Phase 1 work

---

## For Crystal (Visuals, Style, Widget UX)

**Lead Responsibilities:**
- SQT Grove Style Guide
- `sqt-themes.json` content (palettes, motifs, style_modifiers)
- Mood board examples and art prompt quality
- Widget UI/UX (especially `<sqt-grove-clock>` and Discord response styling)
- PWA assets (manifest, icons, service worker strategy)

**Specific Phase 1/2 Micro-Tasks:**
1. Draft SQT Grove Style Guide (whimsical storybook + warm forest + acorn/leyline/Ratatoskr motifs).
2. Populate `sqt-themes.json` with data for all recurring holidays + the 4 Major Events.
3. Create 3–5 example full bundle outputs (text + mood board descriptions).
4. Design the web component modal and VS Code insertion format.
5. Produce manifest.json + basic service worker for the dashboard.

**Success Criteria:**
- Themes file is rich enough to drive consistent prompt generation
- Visual direction is clear for any generative art work
- Widgets feel like part of one cohesive Grove

**References:**
- Creative-Ideas.md (SQT Grove Style notes)
- `sqt-themes.schema.json`
- `phase1-requirements-messenger-circuit.md`

---

## For Cyber-SQRRL (Curriculum & Squirrel Ops)

**Lead Responsibilities:**
- "Time is Relative" curriculum modules
- Squirrel Ops metaphors mapped to real technical practices
- Educational variants of the Messenger’s Circuit and holidays
- Practical lab ideas woven into daily Foraging Ideas

**Specific Phase 1/2 Micro-Tasks:**
1. Map the 5 recurring holidays + 4 Major Events to progressive cybersecurity / systems concepts.
2. Create a starter catalog of "Foraging as Lab" examples (e.g., file integrity on Discerned Hoard day).
3. Draft high-level structure for a "Time is Relative" curriculum module.
4. Define how Project-Deep / Curriculum mode should modify bundle output.

**Success Criteria:**
- At least 8–10 concrete lab ideas tied to specific days/holidays
- Clear metaphor dictionary (Caching = knowledge management, Leylines = cross-domain connections, etc.)

**References:**
- Creative-Ideas.md (Curriculum sections)
- phase1-requirements-messenger-circuit.md (Curriculum Track section)

---

## Coordination Notes (Zeenah)

- All three specialists should work from the same data contracts defined by Jasper.
- Use `design_notes.md` as the shared working space for examples and variants.
- Log every significant decision with SQT stamps.
- Target: Complete these packages + remaining Phase 1 items → Phase Review / Gate → Phase 2.

**Next Recommended Handoff:** Jasper to begin engine unification + schema implementation spike after user approval of this package.

---

*All work follows the v2 handoff process. See project log for stamped entries.*