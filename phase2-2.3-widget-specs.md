# Phase 2 Segment 2.3 — Widget Interface Specifications

**Project:** SQT-Exploring-the-Possibilities  
**Segment:** 2.3 Widget Specs & Integration Design  
**Leads:** Crystal (UX) + Jasper (contracts)  
**Status:** Complete (design contracts — implementation in Phase 3)  
**Date:** 2026-06-24  
**Validated against:** `sqt_engine_unified.py --json --bundle` (v `sqt-unified-0.2-phase2.2`)

**Dependencies:** `phase1-requirements-messenger-circuit.md`, `sqt-grove-style-guide.md`, `sqt_engine_unified.py`, `sqt-holidays.sample.json`, `sqt-themes.sample.json`

---

## 1. Purpose

Binding interface contracts for the three core community widgets. All widgets consume the **same canonical engine JSON** — no widget-specific holiday logic, no Gregorian calendar dependencies.

**Scope:** Design contracts only. No runnable widget code in this segment.

**Out of scope (Phase 3):** Bot tokens, extension marketplace publish, production CDN hosting.

---

## 2. Shared Data Layer

### 2.1 Canonical Engine Response

Widgets consume the widget-facing fields from `sqt_engine_unified.py`. Use `--compact` (or `compact_context()`) to omit `_extended` and `_note`. Ignore `version` for rendering unless debugging.

```json
{
  "sqt": {
    "year": 1,
    "lunation": 6,
    "day": 7,
    "time": "00:59:59"
  },
  "holiday": {
    "id": "leybridge_threading",
    "name": "Leybridge Threading",
    "type": "recurring"
  },
  "themes": {
    "palettes": ["#2E5A44", "#DFD4B5", "#8C6239"],
    "motifs": ["pebbles", "braided vines", "glowing leylines"],
    "style_modifiers": "Chalk storybook illustration...",
    "tone_keywords": ["steady", "incremental", "patient bridge-building"]
  },
  "bundle": {
    "journal_prompt": "...",
    "mood_board": {
      "palette": ["#2E5A44", "#DFD4B5", "#8C6239"],
      "image_prompt": "...",
      "atmosphere": "..."
    },
    "story_seed": "...",
    "art_prompt": "...",
    "foraging_idea": "..."
  }
}
```

| Field | Type | Nullable | Widget use |
|-------|------|----------|------------|
| `sqt.year` | int | no | Status displays |
| `sqt.lunation` | int (1–12) | no | Calendar, tooltips |
| `sqt.day` | int (1–19) | no | Calendar, tooltips |
| `sqt.time` | string `HH:MM:SS` | no | Live clock display |
| `holiday` | object | **yes** (`null`) | Badge, embed title, lore panel |
| `holiday.id` | string | — | Deep links, theme lookup |
| `holiday.name` | string | — | Human label |
| `holiday.type` | `recurring` \| `major` \| `rare` | — | Visual tier (badge color) |
| `themes` | object | no (may be sparse) | Colors, embed sidebar |
| `bundle` | object | omit if `--holiday` | Full Circuit content |

**Trimmed names:** Widget status lines use `_extended.sqt_full` only when available (static export includes it). Fallback format: `Year {year}, Lunation {lunation}, Day {day}`.

### 2.2 Data Access Modes (all widgets)

| Mode | When | Mechanism |
|------|------|-----------|
| **A — Local subprocess** | Dev, VS Code, self-hosted bot | `python sqt_engine_unified.py --json --bundle` |
| **B — Static JSON file** | GitHub Pages, embeds, Discord cron | `circuit-current.json` (see §7) |
| **C — HTTP feed** | Future public API | `GET /v1/circuit/current` returns same shape |

**Rule:** Modes A and B must produce byte-identical `sqt` + `holiday` + `bundle` + `themes` for the same reference time.

### 2.3 Holiday Visual Tiers

| `holiday.type` | Badge color (CSS var) | Discord embed accent | Behavior flag |
|----------------|----------------------|----------------------|---------------|
| `recurring` | `--sqt-badge-recurring: #4CAF50` | `#2E5A44` | Standard bundle |
| `major` | `--sqt-badge-major: #FFD54F` | `#FF8F00` | `ceremonial: true` — richer embed, optional thread prompt |
| `rare` | `--sqt-badge-rare: #78909C` | `#37474F` | Optional “rare event” footer |
| `null` | `--sqt-badge-none: #8C6239` | `#8C6239` | Grove day — no holiday header |

### 2.4 Bundle Delivery Modes (all widgets)

| Mode | Fields included | Use case |
|------|-----------------|----------|
| **Teaser** | `journal_prompt` + `foraging_idea` + holiday name | Discord default, modal preview |
| **Standard** | All 5 bundle elements | `/circuit`, web modal, VS Code insert |
| **Minimal Whisper** | `journal_prompt` only | Quiet opt-in surfaces |
| **Major Ceremonial** | Standard + `themes.tone_keywords` header + longer story_seed | `holiday.type === "major"` |

---

## 3. Discord Bot — “Ratatoskr Grove Messenger”

### 3.1 Identity

| Property | Value |
|----------|-------|
| Bot name | Ratatoskr Grove Messenger |
| Application ID | TBD (Phase 3) |
| Guild scope | Configurable; supports global slash commands |
| Data source | Mode A (server-side subprocess) or Mode B (cron-refreshed static file) |

### 3.2 Slash Commands

#### `/circuit [mode]`

| Param | Type | Default | Values |
|-------|------|---------|--------|
| `mode` | string (optional) | `teaser` | `teaser`, `full` |

**Response — `teaser` (default):**

```
Embed:
  title: "🌰 Leybridge Threading — Year 1, Lunation 6, Day 7"
  description: {bundle.journal_prompt}
  fields:
    - name: "Forage Today"
      value: {bundle.forage_idea}
    - name: "SQT Time"
      value: "{sqt.time}"
  color: {themes.palettes[0] as int}
  footer: "Ratatoskr Grove Messenger • /circuit mode:full for complete bundle"
```

**Response — `full`:**

```
Embed (primary):
  title: "The Messenger's Circuit — {holiday.name || 'Grove Day'}"
  description: {bundle.journal_prompt}
  fields:
    - Story Seed → {bundle.story_seed} (truncate 1024)
    - Foraging → {bundle.forage_idea}
    - Atmosphere → {bundle.mood_board.atmosphere}
  color: accent by holiday.type

Follow-up message (ephemeral option):
  Art Prompt (code block): {bundle.art_prompt}
  Image Prompt (code block): {bundle.mood_board.image_prompt}
```

**Major event (`holiday.type === "major"`):** Add embed thumbnail placeholder (motif icon); append `🌕 Major Lunation Event` to title; offer "Start Ratatoskr Relay" button (creates thread).

**Errors:**

| Condition | User message |
|-----------|--------------|
| Engine timeout (>3s) | "The leylines are quiet. Try again in a moment." |
| `holiday: null` | Title: "Grove Day — no holiday active"; still return bundle |

---

#### `/forage [focus]`

| Param | Type | Default |
|-------|------|---------|
| `focus` | string | `holiday` |

Values: `holiday` (uses `bundle.forage_idea`), `general` (first line of journal_prompt reframed).

**Response:** Single embed, title "Today's Forage", body = foraging_idea, color from palette[1].

---

#### `/holiday` (alias `/event`)

**Response:**

```
Embed:
  title: {holiday.name} || "No active holiday"
  description: From sqt-holidays lookup: core_feeling / core_theme / heros_journey_stage
  fields:
    - SQT Position → "Year {year}, Lunation {lunation}, Day {day}"
    - Type → {holiday.type}
    - Motifs → {themes.motifs joined}
  color: tier color
```

If `holiday` is null: show next upcoming holiday from precomputed `calendar_matrix.json` (§7).

---

#### `/lore-drop <content> [title]`

| Param | Type | Required |
|-------|------|----------|
| `content` | string (max 2000) | yes |
| `title` | string (max 100) | no |

**Does not call engine for generation.** Attaches metadata:

```json
{
  "submitted_at": "ISO8601",
  "sqt_snapshot": { "year", "lunation", "day" },
  "holiday_id": "leybridge_threading | null",
  "user_id": "discord_snowflake",
  "title": "...",
  "content": "...",
  "status": "pending"
}
```

**Response (ephemeral):** "Your lore has been scattered to the moderation burrow."

**Moderation queue:** JSON file or sqlite; Alex Pericles review surface in Phase 3.

**Rate limit:** 3 submissions / user / 24h.

---

### 3.3 Ratatoskr Relay (threads)

**Trigger:** Major events, or manual `/circuit mode:full` button on major days.

**Bot posts thread opener:**

```
{bundle.story_seed}

Continue the tale — what does the squirrel do next?
```

Thread auto-tags: `relay`, `{holiday.id}`, `lunation-{n}`.

### 3.4 Security & Hygiene (Alex Pericles)

- Sanitize all `/lore-drop` input (strip mentions, URLs logged not rendered)
- Subprocess: argv only, no shell; timeout 3s; cwd = repo root
- Bot token in `.env` — never in repo
- No user JSON executed as code

### 3.5 Scheduled Delivery (optional)

Cron every 37.3h SQT day boundary (or daily Earth cron approximating): post teaser to `#grove-circuit` channel.

---

## 4. Web Component — `<sqt-grove-clock>`

### 4.1 Custom Element Definition

```html
<sqt-grove-clock
  src="https://example.com/circuit-current.json"
  refresh="60"
  theme="grove"
  show-calendar="true"
  bundle-mode="teaser"
  lunation-labels="trimmed"
></sqt-grove-clock>
```

### 4.2 Attributes

| Attribute | Default | Description |
|-----------|---------|-------------|
| `src` | `./circuit-current.json` | URL to canonical JSON (Mode B) |
| `refresh` | `60` | Poll interval seconds; `0` = fetch once |
| `theme` | `grove` | `grove` \| `minimal` \| `high-contrast` |
| `show-calendar` | `true` | Mini 12×19 grid or upcoming-only strip |
| `bundle-mode` | `teaser` | `teaser` \| `full` \| `none` (clock only) |
| `lunation-labels` | `trimmed` | `trimmed` \| `display` — uses `_extended.sqt_full` when present |
| `calendar-src` | `./calendar_matrix.json` | Upcoming holidays static file (§7) |

### 4.3 Shadow DOM Structure

```
sqt-grove-clock
└── .sqt-clock-root [role="region" aria-label="Squirrel Quantum Time"]
    ├── .sqt-time-display
    │   ├── .sqt-stamp      → "Year 1 · Canopy · Day 7 · 00:59:59"
    │   └── .sqt-holiday-badge [if holiday]
    ├── .sqt-calendar-mini  [optional, aria-label="SQT calendar"]
    └── .sqt-modal-trigger  → button "Open today's Circuit"
```

### 4.4 CSS Custom Properties (theming)

```css
:host {
  --sqt-bg: #2E5A44;
  --sqt-fg: #DFD4B5;
  --sqt-accent: #4AF626;
  --sqt-font: 'Georgia', 'Palatino', serif;
  --sqt-radius: 8px;
  /* overridden from themes.palettes[0..2] on data load */
}
```

Host page may override vars; component never breaks Grove palette fallbacks from `sqt-grove-style-guide.md`.

### 4.5 Modal Flow

```
[Click badge or "Open Circuit"]
  → Modal opens (focus trap, Esc closes)
  → Section 1: Holiday lore (name, type, motifs chips)
  → Section 2: Teaser (journal_prompt + foraging_idea)
  → Section 3 [if bundle-mode=full]: Accordion
        - Mood Board (palette swatches + atmosphere)
        - Story Seed
        - Art Prompt (copy button)
  → Actions: [Copy Journal] [Copy Full Bundle] [Share]
```

**Share:** `navigator.share` if available; else clipboard markdown:

```markdown
## Leybridge Threading — SQT Year 1, Lunation 6, Day 7

**Journal:** What small bridge are you threading today?...

**Forage:** Today (Leybridge Threading): Consistent small actions...
```

### 4.6 Events (dispatched on host)

| Event | `detail` |
|-------|----------|
| `sqt-loaded` | full payload |
| `sqt-holiday-change` | `{ previous, current }` |
| `sqt-bundle-open` | `{ mode }` |
| `sqt-error` | `{ message, src }` |

### 4.7 Accessibility

- `role="region"` + `aria-live="polite"` on time display (updates on refresh)
- Holiday badge: `aria-label="Active holiday: Leybridge Threading, recurring"`
- Modal: `role="dialog"`, `aria-modal="true"`, focus return on close
- Calendar cells: `aria-label="Lunation 6, Day 7, Leybridge Threading"`
- High-contrast theme: WCAG AA minimum for text/background

### 4.8 Embed Constraints

- No framework dependency (vanilla custom element + optional CSS file)
- Bundle size target: <15 KB gzipped (JS only; excludes fetched JSON)
- Works in Notion embed, GitHub Pages, static site generators

---

## 5. VS Code Extension — “SQT Grove”

### 5.1 Package Identity

```json
{
  "name": "sqt-grove",
  "displayName": "SQT Grove — Messenger's Circuit",
  "engines": { "vscode": "^1.85.0" },
  "activationEvents": ["onStartupFinished"],
  "main": "./out/extension.js"
}
```

### 5.2 Contributions

```json
{
  "contributes": {
    "commands": [
      {
        "command": "sqt-grove.insertBundle",
        "title": "SQT Grove: Insert Messenger's Circuit Bundle"
      },
      {
        "command": "sqt-grove.insertForage",
        "title": "SQT Grove: Insert Foraging Idea"
      },
      {
        "command": "sqt-grove.refresh",
        "title": "SQT Grove: Refresh SQT Status"
      }
    ],
    "configuration": {
      "title": "SQT Grove",
      "properties": {
        "sqtGrove.enginePath": {
          "type": "string",
          "default": "",
          "description": "Path to sqt_engine_unified.py (empty = workspace search)"
        },
        "sqtGrove.staticJsonPath": {
          "type": "string",
          "default": "",
          "description": "Optional circuit-current.json (overrides subprocess)"
        },
        "sqtGrove.insertFormat": {
          "type": "string",
          "enum": ["markdown", "comment-block"],
          "default": "markdown"
        },
        "sqtGrove.pythonPath": {
          "type": "string",
          "default": "python"
        }
      }
    }
  }
}
```

### 5.3 Status Bar

**Item ID:** `sqtGrove.status`  
**Alignment:** right  
**Priority:** 50  

**Text format (trimmed):**

```
$(squirrel) Y1 Canopy · D7 · Leybridge
```

If no holiday:

```
$(squirrel) Y1 Canopy · D7
```

**Tooltip (markdown):**

```markdown
**SQT** Year 1, Canopy lunation, Stash-day (7)
**Time** 00:59:59
**Holiday** Leybridge Threading (recurring)

_Forage:_ Today (Leybridge Threading): Consistent small actions, connections.

[Insert Full Bundle](command:sqt-grove.insertBundle)
```

Motifs rendered as subtle tooltip footer when present.

**Refresh:** Every 60s + on `sqt-grove.refresh` command.

### 5.4 Insert Bundle — Output Templates

**Markdown (`insertFormat: markdown`):**

```markdown
<!-- sqt-grove: Y1-L6-D7 leybridge_threading -->
## Messenger's Circuit — Leybridge Threading
*Year 1, Canopy · Day 7 · 00:59:59*

### Journal
{bundle.journal_prompt}

### Story Seed
{bundle.story_seed}

### Foraging
{bundle.forage_idea}

### Mood
{bundle.mood_board.atmosphere}
*Palette:* `#2E5A44` `#DFD4B5` `#8C6239`

### Art Prompt
{bundle.art_prompt}
```

**Comment block (for code files):**

```
// ═══ SQT Grove · Leybridge Threading · Y1 L6 D7 ═══
// Journal: {journal_prompt one line}
// Forage: {foraging_idea}
// Story: {story_seed truncated 120}
// ═══
```

Language-aware comment syntax: detect from `document.languageId`.

### 5.5 Engine Invocation

```
1. If sqtGrove.staticJsonPath set and file exists → read JSON
2. Else resolve enginePath (setting → workspace root sqt_engine_unified.py)
3. spawn(pythonPath, [engine, '--json', '--bundle'], { cwd: repoRoot, timeout: 3000 })
4. Parse stdout JSON; cache 60s
5. On failure → status bar shows "$(error) SQT offline" + output channel log
```

### 5.6 Major Event Behavior

When `holiday.type === "major"`: status bar icon switches to `$(star-full)`; insert template adds ceremonial header from `themes.tone_keywords`.

---

## 6. Cross-Widget Consistency Matrix

| Feature | Discord | Web Component | VS Code |
|---------|---------|---------------|---------|
| SQT time display | embed field | live clock | status bar |
| Holiday badge | embed title | badge chip | status + tooltip |
| Teaser bundle | `/circuit` default | modal preview | — |
| Full bundle | `/circuit mode:full` | modal accordion | insert command |
| Forage only | `/forage` | modal section | insertForage |
| User content | `/lore-drop` | share clipboard | — |
| Major event UX | relay thread | gold badge + modal | star icon |
| Data mode A | server subprocess | — | subprocess |
| Data mode B | cron JSON | `src` attribute | staticJsonPath |

---

## 7. Static Export Pipeline (GitHub Pages)

### 7.1 Export Script Contract (Phase 3: `scripts/export_static_feed.py`)

**Inputs:** `--holidays`, `--themes`, `--output-dir`  
**Outputs:**

| File | Contents | Refresh |
|------|----------|---------|
| `circuit-current.json` | Full engine `--json --bundle` response | Every deploy / cron |
| `circuit-holiday-only.json` | `--json --holiday` response | Same |
| `calendar_matrix.json` | 12 lunations × 19 days → `{ lunation, day, holiday_id, holiday_name, type }` | On holidays file change |

**`calendar_matrix.json` shape:**

```json
{
  "generated_at": "ISO8601",
  "lunation_names": { "1": "Sleepy", "...": "..." },
  "cells": [
    { "lunation": 6, "day": 7, "holiday_id": "leybridge_threading", "holiday_name": "Leybridge Threading", "type": "recurring" }
  ]
}
```

### 7.2 GitHub Pages Layout

```
/docs
  index.html              ← embed demo <sqt-grove-clock>
  circuit-current.json
  calendar_matrix.json
  sqt-grove-clock.js
  sqt-grove-clock.css
```

### 7.3 CORS

Static JSON served with `Access-Control-Allow-Origin: *` for third-party embeds.

---

## 8. PWA Manifest & Service Worker Outline

See `phase2-2.3-pwa-outline.md` for manifest fields and SW caching strategy.

**Summary:**

- `manifest.json`: name "SQT Living Grove", theme_color `#2E5A44`, icons 192/512 acorn motif
- SW caches: `circuit-current.json`, `calendar_matrix.json`, shell HTML, fonts
- Update strategy: stale-while-revalidate on JSON; `generated_at` compared client-side

---

## 9. Phase 2.3 Validation Gate

| Criterion | Status |
|-----------|--------|
| Discord command contracts with embed field mapping | ✅ §3 |
| Web component attributes, modal flow, a11y | ✅ §4 |
| VS Code contributions, status bar, insert templates | ✅ §5 |
| Shared JSON validated against live engine | ✅ §2 (lun6 day7 tested) |
| Static export + PWA outline | ✅ §7–8 |
| Architecture diagram updated | ✅ `phase2-architecture-diagram.md` |

**Handoff:** Phase 3 Chunk E — widget skeletons implement these contracts verbatim.

---

*Lightweight Reference: See Post_Project_Summary.md*