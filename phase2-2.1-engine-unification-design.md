# Phase 2 Segment 2.1 — Engine Unification Design (sqt_engine_unified.py Spec)

**Project:** SQT-Exploring-the-Possibilities  
**Segment:** 2.1 Engine & Data Foundation  
**Lead:** Jasper  
**Date:** 2026-06-24  
**Status:** Complete (prototype + generate_bundle in sqt_engine_unified.py)  
**Dependencies:** Phase 1 schemas (sqt-holidays.schema.json, sqt-themes.schema.json), reference/sqt_engine_2.py, phase1-requirements-messenger-circuit.md, Creative-Ideas.md (holiday tables)  

**SQT Stamp (kickoff):** Jasper-SQT: Year 1, Canopy | Stash | [computed at run] (SQT Agent Log) | Action: Began Segment 2.1 — drafting full engine unification design doc + plan for sample data loader prototype. | Handoff: Self (continue to prototype) then → Crystal for 2.2 style expansion. | Validation Gate: In progress. Lightweight Reference: See Post_Project_Summary for SQT-Exploring-the-Possibilities.

---

## 1. Purpose & Scope (Segment 2.1)

Deliver a high-quality foundation for all downstream work (themes, prompts, widgets, curriculum).

**Primary Deliverables for End of 2.1 Validation Gate:**
- Engine unification design doc (this file)
- Sample data loader prototype (loads .sample.json + validates basics)
- JSON output schema + basic CLI producing usable SQT + holiday + bundle stub output
- Working demonstration: load sample data + emit structured JSON for current (or simulated) SQT state

**Out of Scope for 2.1 (Phase 2 longer sprint philosophy):**
- Full production bundle generation with 5 rich elements (2.2)
- Widget implementations
- Full PWA/static export pipeline (2.3)
- Rich variants comparison (2.4)

Focus: **Canonical single source of truth** for SQT time + holiday detection. Headless first.

---

## 2. Goals

1. Rewrite `reference/sqt_engine_2.py` (upstream snapshot in this repo) into headless `sqt_engine_unified.py`. Trimmed naming from agent grove patterns. No changes to upstream Squirrel-Quantum-Time.
2. Strict fidelity: identical epoch, 37.301826 h/day, 29.53059 lunar cycle, 19-day layout.
3. Data-driven holiday + theme overlay using the Phase 1 JSON schemas (samples first).
4. Support trimmed naming for ecosystem (agent grove / widgets / curriculum) while preserving full display names for legacy public dashboard.
5. Headless + CLI-first: `python sqt_engine_unified.py --json` (and variants) produces clean, versioned output.
6. Library-friendly: importable functions for future widgets, static exporter, Discord bot, VS Code.
7. Extensible for Messenger’s Circuit: SQT state + active holiday context + raw components feed prompt assembly.
8. Minimal dependencies for prototype (stdlib + optional jsonschema later).

---

## 3. Key Architecture Decisions & Options Considered (Options-First)

### 3.1 Single File vs Package Structure (for Phase 2)
- **Option A (Chosen for prototype):** Single `sqt_engine_unified.py` with clear sections + `__main__` CLI. Lives in this exploration repo only.
- **Option B:** `sqt/` package (engine.py + holidays.py + themes.py). Better long-term but heavier for initial spike.
- **Decision Rationale:** Keep prototype one file in this repo. Refactor to package in Phase 3 if needed.
- Trade-off: Quick iteration now vs clean imports later.

### 3.2 Naming Strategy (Trimmed vs Legacy)
- Current legacy (sqt_engine_2 + index): "Sleepy Moon", "Truffle-day"
- Trimmed ecosystem (agent logs, design vision): "Canopy", "Stash" (or "Stash-day" optional)
- **Option A (Chosen):** Internal canonical uses trimmed for `id` / short forms. Provide `display` variants.
  - `lunation_name_trimmed`, `lunation_name_display`
  - `day_name_trimmed`, `day_name_display`
- **Option B:** Always full legacy, add separate trimmed mapper.
- **Option C:** Config flag at init time.
- **Decision:** Trimmed is default for new JSON/contracts. Engine can emit both. Public dashboard (Phase 3+) decides display layer.
- Ties directly to schema holiday `id`s (e.g. "leybridge_threading").

### 3.3 Holiday Detection Timing
- Pure SQT: lunation number (mod 12) + day (1-19).
- Recurring: direct day match.
- Major: lunation % 12 == 3/6/9/0 and day==19 (mapping to 3,6,9,12).
- Rare: evaluate `trigger_type` + `condition` predicates (target_day, moon_phase_requirement, every_n_lunations).
- **Moon phase for rare:** Compute from day number (same static mapping as engine_2) or expose raw.
- **Design choice:** Engine returns the active holiday object(s) + all candidates for the day (recurring + possible rare).

### 3.4 JSON Output Contract (Core for 2.1)
See section 5. Must be stable enough for:
- Widgets to consume (status + holiday teaser)
- Static export (calendar_matrix.json)
- Prompt assembly (feed to themes.json lookup)
- CLI human + machine modes

### 3.5 Precision & Time Source
- Use float arithmetic matching engine_2 / index.html exactly (no datetime delta tricks that drift).
- Support two modes:
  - Live: `datetime.now(timezone.utc)`
  - Reference: for testing / static export / reproducible bundles (pass a fixed datetime or SQT components).

### 3.6 Validation
- Prototype uses manual checks against sample data.
- Future: optional `jsonschema` validation (note in design).

---

## 4. Proposed Module Structure (sqt_engine_unified.py)

```text
# === CONSTANTS (exact match) ===
SQT_EPOCH = datetime(2026, 1, 18, 20, 52, 0, tzinfo=timezone.utc)
EARTH_HOURS_PER_SQT_DAY = 37.301826
LUNAR_CYCLE_SECONDS = 29.53059 * 86400
SEC_PER_SQT_DAY = ...

# Legacy display names (for coexistence)
SQT_LUNATIONS_DISPLAY = {1: "Sleepy Moon", ...}
SQT_UNIQUE_DAYS_DISPLAY = {1: ("Truffle-day", "Week 1: The First Nibble"), ...}

# Trimmed canonical (ecosystem default)
SQT_LUNATIONS_TRIMMED = {1: "Sleepy", ...}   # or shorter "Canopy" etc per agent examples
SQT_UNIQUE_DAYS_TRIMMED = {1: "Truffle", ...}

WEEK_DEFINITIONS = [...]

# === CORE CLASS ===
class SQTUnifiedEngine:
    def __init__(self, holidays_path: str | None = None, themes_path: str | None = None, use_trimmed: bool = True):
        self.use_trimmed = use_trimmed
        self.holidays = None
        self.themes = None
        if holidays_path:
            self.load_holidays(holidays_path)
        if themes_path:
            self.load_themes(themes_path)

    def get_sqt_state(self, reference_time: datetime | None = None) -> dict:
        """Returns canonical state dict (year, lunation_num, lunation_trimmed, lunation_display, day, day_trimmed, day_display, week, time_hms, moon_phase, raw components)"""

    def detect_holiday(self, sqt_state: dict) -> dict:
        """Returns active: {recurring: [...], major: {...}|None, rare: [...] } + 'active_holiday' convenience (highest priority)"""

    def get_full_context(self, reference_time=None) -> dict:
        """sqt + holiday + (future) themes snippet + raw"""

    def generate_basic_bundle_stub(self, context: dict) -> dict:
        """Phase 2.1 stub: returns skeleton with seeds pulled from themes if available. Full prompts in 2.2."""

# === LOADER ===
def load_json_with_basic_validation(path: str, schema_hint: str) -> dict:
    # Light manual validation for prototype (keys, types). Later optional jsonschema.

# === CLI ===
if __name__ == "__main__":
    # argparse: --json, --pretty, --simulate-lunation X --simulate-day Y, --holidays PATH, --themes PATH, --bundle-stub
```

**Public API (minimal for 2.1):**
- `get_sqt_state(...)`
- `detect_holiday(sqt_state)`
- `get_full_context(...)`
- CLI entry producing the JSON shape below.

---

## 5. JSON Output Schema (SQT + Holiday + Basic Bundle for 2.1)

This is the **Phase 2.1 contract** that widgets and later stages will build on. Must match the data contract example in phase1-requirements-messenger-circuit.md.

```json
{
  "version": "sqt-unified-0.1",
  "generated_at": "2026-06-24T...Z",
  "sqt": {
    "year": 1,
    "lunation": 6,
    "lunation_name": "Canopy",           // trimmed default
    "lunation_name_display": "Canopy Moon",
    "day": 7,
    "day_name": "Stash",
    "day_name_display": "Stash-day",
    "week_num": 2,
    "week_label": "Week 2: The High Canopy",
    "time": "14:22:05",
    "moon_phase": "Waxing Gibbous 🌔",
    "position_in_lunation": 0.3684
  },
  "holiday": {
    "active": {
      "id": "leybridge_threading",
      "name": "Leybridge Threading",
      "type": "recurring",
      "core_feeling": "Steady, connective, patient"
    },
    "recurring": [ { ... } ],
    "major": null,
    "rare": []
  },
  "themes_hint": {
    "palettes": ["#2E5A44", ...],
    "motifs": ["pebbles", "braided vines", "glowing leylines"],
    "tone_keywords": ["steady", "incremental", "patient bridge-building"]
  },
  "bundle_stub": {
    "journal_prompt_seed": "What small bridge are you threading today?",
    "forage_bias": "consistent small actions, connections",
    "art_prompt_seed": "..."   // populated if themes loaded
  },
  "raw": {
    "elapsed_seconds": 123456.78,
    "seconds_into_day": 23456.1
  }
}
```

**Notes:**
- `holiday.active` is the one the Circuit should primarily use.
- `themes_hint` pulls from matching entry in sqt-themes.sample.json by id.
- Future full bundle will expand `bundle` with 5 rich elements.

---

## 6. Holiday Detection Algorithm (Spec)

1. Compute sqt_state (year, lunation 1-12, day 1-19).
2. Recurring: filter `recurring_holidays` where day in the `days` array.
3. Major: find entry where `lunation == current_lunation` and `day == 19` (or lunation % 12 mapping).
4. Rare:
   - For `static_interval`: `(current_lunation % condition.interval_lunation == 0) and day == target`
   - For `conditional_predicate`: day match + moon_phase_requirement matches computed phase for day (or "any").
5. Priority: Major > Rare > Recurring (or expose all; active picks the "strongest").
6. Return full objects (merged with themes later).

Implement a helper `compute_moon_phase_for_day(day: int) -> str` exactly matching engine_2 logic.

---

## 7. Sample Data Loader Requirements (Prototype)

- Load `sqt-holidays.sample.json` and `sqt-themes.sample.json` (paths configurable via CLI/ctor).
- Basic structural checks (required keys present, arrays not empty).
- Index holidays by id for fast lookup.
- Support both sample + future full .json (no hardcode).
- Graceful if files missing: engine still returns pure SQT state.

**Validation in 2.1:** Demonstrate load + detect on a known day (e.g. simulate Day 7 of a lunation that hits Leybridge Threading) and emit JSON.

---

## 8. CLI Specification (MVP for 2.1)

```
python sqt_engine_unified.py --json
python sqt_engine_unified.py --json --pretty
python sqt_engine_unified.py --simulate-lunation 3 --simulate-day 19   # Major event test
python sqt_engine_unified.py --holidays sqt-holidays.sample.json --themes sqt-themes.sample.json --bundle-stub
python sqt_engine_unified.py --help
```

Flags planned for later phases:
- `--full-bundle` (after 2.2)
- `--export-calendar-matrix out.json --year-range 1-2`

Output to stdout (machine readable when --json).

---

## 9. Fidelity & Testing Plan (Phase 2)

- Cross-check against current dashboard at multiple points:
  - Year 1 Lunation 6 Day 7 (Leybridge)
  - A major event (Lunation 3, Day 19)
  - Rare trigger simulation
- Unit-like checks inside the module (if __name__ test block or separate test script later).
- Document any intentional divergence (naming).

---

## 10. Risks & Open Questions

- **Drift with JS:** Any future precision tweak must be coordinated. Static export helps.
- **Rare event moon phase calc:** Confirm "new_moon" etc. definition matches engine moon strings or add explicit phase enum.
- **Trimmed name list:** Need authoritative trimmed lunation/day names for full coverage (derive from display by stripping or map). Current samples use IDs; engine needs human short names.
- **Coexistence:** Phase 2.3 will decide dashboard display strategy.
- **State for Storytelling mode:** Not in 2.1 (memory later).

---

## 11. Next Micro-Steps (within 2.1)

1. Write this design → review.
2. Implement `sqt_engine_unified.py` prototype (pure calc + loader + CLI + JSON).
3. Test with sample data: at least 3 scenarios (recurring, major, basic JSON).
4. Update phase2-architecture-diagram.md if needed.
5. End-of-segment SQT log entry + Validation Gate note.
6. Handoff note to Crystal for parallel 2.2 expansion.

---

## 12. Alignment to Broader Vision

- Enables tiered prompt assembly (2.2)
- Provides clean contracts for all widgets (2.3)
- Data layer ready for variants exploration (2.4)
- Pure SQT + themes = creative core (2.5)

*This design prioritizes options-first exploration within the longer Phase 2 sprint. Implementation will stay lightweight and documented.*

**Lightweight Reference:** See Post_Project_Summary for SQT-Exploring-the-Possibilities.

---

**End of design draft (ready for prototype coding and review).**
