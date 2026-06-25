# Phase 2 Segment 2.3 — PWA & Service Worker Outline

**Project:** SQT-Exploring-the-Possibilities  
**Segment:** 2.3 (companion to `phase2-2.3-widget-specs.md`)  
**Status:** Design outline — implementation Phase 3 Chunk D  
**Date:** 2026-06-24

---

## 1. Purpose

Outline for making the SQT Grove demo surface installable and offline-capable on GitHub Pages. The PWA wraps the `<sqt-grove-clock>` embed and static JSON feeds — not a replacement for the full upstream Tkinter dashboard.

---

## 2. `manifest.json` (draft)

```json
{
  "name": "SQT Living Grove",
  "short_name": "SQT Grove",
  "description": "Squirrel Quantum Time — holidays, Messenger's Circuit, and the Living Grove",
  "start_url": "/SQT-Exploring-the-Possibilities/",
  "display": "standalone",
  "background_color": "#2E5A44",
  "theme_color": "#2E5A44",
  "orientation": "any",
  "icons": [
    { "src": "icons/acorn-192.png", "sizes": "192x192", "type": "image/png", "purpose": "any maskable" },
    { "src": "icons/acorn-512.png", "sizes": "512x512", "type": "image/png", "purpose": "any maskable" }
  ],
  "categories": ["lifestyle", "education"],
  "lang": "en"
}
```

**Icon brief (Crystal):** Acorn with subtle leyline curl, `#2E5A44` background, `#4AF626` acorn cap highlight. Match `sqt-grove-style-guide.md` motifs.

---

## 3. Service Worker Strategy

**File:** `sw.js` (root of Pages deploy)

### 3.1 Cache Names

| Cache | Contents | Version bump |
|-------|----------|--------------|
| `sqt-shell-v1` | `index.html`, `sqt-grove-clock.js`, `sqt-grove-clock.css` | On JS/CSS change |
| `sqt-data-v1` | `circuit-current.json`, `calendar_matrix.json` | On deploy |

### 3.2 Fetch Handlers

```
install  → precache shell assets
activate → delete old sqt-shell-* / sqt-data-* caches

fetch:
  circuit-current.json | calendar_matrix.json
    → stale-while-revalidate (return cache, background fetch, update cache if generated_at newer)

  sqt-grove-clock.js | .css | index.html
    → cache-first

  other
    → network-only
```

### 3.3 Update Notification

When `generated_at` in fresh JSON > cached copy:

- Dispatch `sqt-data-updated` to any mounted `<sqt-grove-clock>` on page
- Optional toast: "A new Grove message has arrived."

### 3.4 Offline Behavior

| Asset | Offline |
|-------|---------|
| Shell UI | ✅ from cache |
| Last JSON snapshot | ✅ from cache |
| Live engine subprocess | ❌ not in PWA scope |

---

## 4. HTML Shell (minimal)

```html
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <meta name="theme-color" content="#2E5A44" />
  <link rel="manifest" href="manifest.json" />
  <link rel="stylesheet" href="sqt-grove-clock.css" />
  <title>SQT Living Grove</title>
</head>
<body>
  <main>
    <h1>Squirrel Quantum Time</h1>
    <sqt-grove-clock
      src="./circuit-current.json"
      calendar-src="./calendar_matrix.json"
      refresh="60"
      bundle-mode="full"
    ></sqt-grove-clock>
  </main>
  <script src="sqt-grove-clock.js" type="module"></script>
  <script>
    if ('serviceWorker' in navigator) {
      navigator.serviceWorker.register('./sw.js');
    }
  </script>
</body>
</html>
```

---

## 5. Phase 3 Dependencies

- `scripts/export_static_feed.py` generates JSON before each deploy
- GitHub Actions workflow: export → commit to `/docs` → Pages deploy
- Icon assets from Crystal (192 + 512 PNG)

---

*Lightweight Reference: See Post_Project_Summary.md*