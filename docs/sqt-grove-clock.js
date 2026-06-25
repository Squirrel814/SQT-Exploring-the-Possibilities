/**
 * <sqt-grove-clock> — embeddable SQT time + holiday + Circuit modal
 * Contract: phase2-2.3-widget-specs.md
 */
import { SQT_UNIQUE_DAYS_DISPLAY, sqtStateNow } from './sqt-core.js';
import {
  buildFullGridModel,
  buildMoonStripModel,
  buildSnapshot,
  calendarViewMode,
  formatHolidayAnnouncement,
  getFocusableElements,
  holidaysDiffer,
  showCalendarEnabled,
  trapFocus,
  upcomingHolidayCells,
} from './sqt-grove-helpers.js';

const BADGE_COLORS = {
  recurring: 'var(--sqt-badge-recurring, #4CAF50)',
  major: 'var(--sqt-badge-major, #FFD54F)',
  rare: 'var(--sqt-badge-rare, #78909C)',
  none: 'var(--sqt-badge-none, #8C6239)',
};

const THEME_STORAGE_KEY = 'sqt-grove-clock-theme';

const DAY_NAMES = Object.fromEntries(
  Object.entries(SQT_UNIQUE_DAYS_DISPLAY).map(([day, info]) => [Number(day), info[0]]),
);

function phaseLabel(live) {
  if (live.day === 10) return 'Lunation';
  return live.moon_phase;
}

function formatStamp(live) {
  const moon = live.lunation_name_display || `Moon ${live.lunation}`;
  const day = live.day_name_display || `Day ${live.day}`;
  return `Year ${live.year} · ${moon} · ${day} · ${phaseLabel(live)} · ${live.time}`;
}

function holidayFromMatrix(matrix, lunation, day) {
  if (!matrix?.cells) return null;
  const cell = matrix.cells.find((c) => c.lunation === lunation && c.day === day);
  if (!cell?.holiday_id) return null;
  return { id: cell.holiday_id, name: cell.holiday_name, type: cell.type };
}

function escapeHtml(text) {
  return String(text)
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;');
}

function isCeremonialMajor(holiday) {
  return holiday?.type === 'major';
}

function ceremonialKeywords(bundle, themes) {
  if (bundle?.ceremonial_header) return bundle.ceremonial_header;
  const kw = themes?.tone_keywords || [];
  return kw.filter(Boolean).join(' · ');
}

function ceremonialBannerHtml(bundle, themes) {
  const line = ceremonialKeywords(bundle, themes);
  if (!line) return '';
  return `<div class="ceremonial-banner" role="note" aria-label="Major lunation ceremonial themes">
    <span class="ceremonial-star" aria-hidden="true">✦</span>
    <span class="ceremonial-text">${escapeHtml(line)}</span>
  </div>`;
}

class SQTGroveClock extends HTMLElement {
  static get observedAttributes() {
    return ['src', 'refresh', 'theme', 'bundle-mode', 'calendar-src', 'lunation-labels', 'show-calendar', 'calendar-view'];
  }

  constructor() {
    super();
    this.attachShadow({ mode: 'open' });
    this._data = null;
    this._matrix = null;
    this._pollTimer = null;
    this._clockTimer = null;
    this._live = null;
    this._lastPosition = '';
    this._snapshot = null;
    this._releaseFocusTrap = null;
    this._focusReturn = null;
    this._announceTimer = null;
  }

  connectedCallback() {
    this.applyTheme(this.resolveTheme());
    this.renderShell();
    this.loadCalendarMatrix();
    this.fetchData();
    this.tickClock();
    this._clockTimer = setInterval(() => this.tickClock(), 1000);
    const sec = parseInt(this.getAttribute('refresh') || '60', 10);
    if (sec > 0) {
      this._pollTimer = setInterval(() => this.fetchData(), sec * 1000);
    }
  }

  disconnectedCallback() {
    if (this._pollTimer) clearInterval(this._pollTimer);
    if (this._clockTimer) clearInterval(this._clockTimer);
    if (this._announceTimer) clearTimeout(this._announceTimer);
    this.teardownFocusTrap();
  }

  attributeChangedCallback(name) {
    if (!this.isConnected) return;
    if (name === 'theme') this.applyTheme(this.resolveTheme());
    if (name === 'calendar-src') this.loadCalendarMatrix();
    if (name === 'show-calendar' || name === 'calendar-view') this.renderCalendar();
    if (name === 'src' || name === 'refresh') this.fetchData();
  }

  resolveTheme() {
    const attr = this.getAttribute('theme');
    if (attr === 'grove' || attr === 'minimal' || attr === 'high-contrast') return attr;
    try {
      const stored = localStorage.getItem(THEME_STORAGE_KEY);
      if (stored === 'grove' || stored === 'minimal' || stored === 'high-contrast') return stored;
    } catch {
      /* private mode */
    }
    return 'grove';
  }

  applyTheme(theme) {
    this.dataset.theme = theme;
    const toggle = this.shadowRoot?.querySelector('.theme-toggle');
    if (toggle) {
      const high = theme === 'high-contrast';
      toggle.setAttribute('aria-pressed', String(high));
      toggle.textContent = high ? 'Grove theme' : 'High contrast';
    }
  }

  toggleTheme() {
    const next = this.dataset.theme === 'high-contrast' ? 'grove' : 'high-contrast';
    this.setAttribute('theme', next);
    try {
      localStorage.setItem(THEME_STORAGE_KEY, next);
    } catch {
      /* private mode */
    }
    this.applyTheme(next);
  }

  async loadCalendarMatrix() {
    const src = this.getAttribute('calendar-src');
    if (!src) return;
    try {
      const res = await fetch(src);
      if (res.ok) {
        this._matrix = await res.json();
        this.renderCalendar();
      }
    } catch {
      this._matrix = null;
      this.renderCalendar();
    }
  }

  async fetchData() {
    const src = this.getAttribute('src') || './circuit-current.json';
    const url = `${src}${src.includes('?') ? '&' : '?'}t=${Date.now()}`;
    try {
      const res = await fetch(url, { cache: 'no-store' });
      if (!res.ok) throw new Error(`HTTP ${res.status}`);
      const data = await res.json();
      this._data = data;
      this.renderData(data);
      this.checkHolidayChange('poll');
      this.dispatchEvent(new CustomEvent('sqt-loaded', { detail: data, bubbles: true }));
    } catch (err) {
      if (!this._live) this.renderError(err.message);
      this.dispatchEvent(new CustomEvent('sqt-error', { detail: { message: err.message, src }, bubbles: true }));
    }
  }

  tickClock() {
    this._live = sqtStateNow();
    const timeEl = this.shadowRoot?.querySelector('.time');
    if (!timeEl) return;

    if (this._live.error) {
      timeEl.textContent = this._live.error;
      return;
    }

    timeEl.textContent = formatStamp(this._live);

    const pos = `${this._live.year}-${this._live.lunation}-${this._live.day}`;
    if (pos !== this._lastPosition) {
      this._lastPosition = pos;
      if (this._data) this.renderData(this._data);
      else this.renderCalendar();
      this.fetchData();
      this.checkHolidayChange('tick');
    }
  }

  activeHoliday() {
    if (this._live && this._matrix) {
      const fromMatrix = holidayFromMatrix(this._matrix, this._live.lunation, this._live.day);
      if (fromMatrix) return fromMatrix;
    }
    return this._data?.holiday || null;
  }

  currentSnapshot() {
    return buildSnapshot(this._live, this.activeHoliday());
  }

  checkHolidayChange(_source) {
    const current = this.currentSnapshot();
    if (!this._snapshot) {
      this._snapshot = current;
      return;
    }
    if (!holidaysDiffer(this._snapshot, current)) return;

    const previous = this._snapshot;
    this._snapshot = current;
    this.dispatchEvent(new CustomEvent('sqt-holiday-change', {
      detail: { previous, current },
      bubbles: true,
    }));
    this.announceHolidayChange(previous, current);
    this.renderData(this._data || {});
  }

  announceHolidayChange(previous, current) {
    const message = formatHolidayAnnouncement(previous, current);
    if (!message) return;

    const announcer = this.shadowRoot?.querySelector('.holiday-announce');
    if (!announcer) return;

    announcer.textContent = message;
    const badge = this.shadowRoot?.querySelector('.badge');
    badge?.classList.add('badge-changed');
    if (this._announceTimer) clearTimeout(this._announceTimer);
    this._announceTimer = setTimeout(() => {
      badge?.classList.remove('badge-changed');
      announcer.textContent = '';
    }, 4000);
  }

  renderShell() {
    this.shadowRoot.innerHTML = `
      <link rel="stylesheet" href="${this.getAttribute('css-href') || './sqt-grove-clock.css'}">
      <div class="root" role="region" aria-label="Squirrel Quantum Time">
        <div class="toolbar">
          <button type="button" class="theme-toggle" aria-pressed="false">High contrast</button>
        </div>
        <div class="time" aria-live="polite"></div>
        <div class="holiday-announce" aria-live="assertive"></div>
        <div class="badge-wrap"></div>
        <section class="calendar-strip" hidden aria-label="SQT calendar">
          <h3 class="calendar-title"></h3>
          <div class="moon-strip" role="list" aria-label="Days in current Moon"></div>
          <div class="upcoming-strip">
            <span class="upcoming-label">Upcoming</span>
            <ul class="upcoming-list"></ul>
          </div>
          <div class="calendar-grid-wrap" hidden>
            <h3 class="grid-title">Full year — 12 Moons × 19 days</h3>
            <div class="calendar-grid" role="grid" aria-label="SQT year calendar"></div>
          </div>
        </section>
        <button type="button" class="open-circuit" hidden>Open today's Circuit</button>
      </div>
      <dialog class="modal" aria-labelledby="circuit-title" aria-modal="true">
        <div class="modal-inner"></div>
        <button type="button" class="close">Close</button>
      </dialog>
    `;
    this.shadowRoot.querySelector('.open-circuit').addEventListener('click', (e) => this.openModal(e.currentTarget));
    this.shadowRoot.querySelector('.close').addEventListener('click', () => this.closeModal());
    this.shadowRoot.querySelector('.theme-toggle').addEventListener('click', () => this.toggleTheme());
    this.shadowRoot.querySelector('.modal').addEventListener('close', () => this.teardownFocusTrap());
    this.applyTheme(this.resolveTheme());
  }

  renderCalendarCellMarkup(cell, { interactive = false, role = 'listitem' } = {}) {
    const classes = ['cal-cell'];
    if (cell.isToday) classes.push('is-today');
    if (cell.isCurrentMoon) classes.push('is-current-moon');
    if (cell.holiday_id) classes.push('has-holiday', `holiday-${cell.type || 'recurring'}`);
    const title = `${cell.dayName || `Day ${cell.day}`}${cell.holiday_name ? ` · ${cell.holiday_name}` : ''}`;
    const attrs = [
      `class="${classes.join(' ')}"`,
      `role="${role}"`,
      `data-lunation="${cell.lunation}"`,
      `data-day="${cell.day}"`,
      `aria-label="${escapeHtml(cell.ariaLabel)}"`,
      `title="${escapeHtml(title)}"`,
    ];
    if (interactive) {
      attrs.push('tabindex="0"');
      attrs.push('aria-haspopup="dialog"');
    }
    return `<span ${attrs.join(' ')}>${cell.day}</span>`;
  }

  bindCalendarCellInteractions(root) {
    root.querySelectorAll('.cal-cell[data-lunation]').forEach((el) => {
      const open = () => {
        const lunation = Number(el.dataset.lunation);
        const day = Number(el.dataset.day);
        this.openCellTeaser(lunation, day, el);
      };
      el.addEventListener('click', open);
      el.addEventListener('keydown', (event) => {
        if (event.key === 'Enter' || event.key === ' ') {
          event.preventDefault();
          open();
        }
      });
    });
  }

  renderCalendar() {
    const strip = this.shadowRoot?.querySelector('.calendar-strip');
    if (!strip) return;

    const enabled = showCalendarEnabled(this.getAttribute('show-calendar'));
    if (!enabled || !this._matrix || !this._live || this._live.error) {
      strip.hidden = true;
      return;
    }

    const view = calendarViewMode(this.getAttribute('calendar-view'));
    const moonTitle = this.shadowRoot.querySelector('.calendar-title');
    const moonStrip = this.shadowRoot.querySelector('.moon-strip');
    const upcomingStrip = this.shadowRoot.querySelector('.upcoming-strip');
    const upcomingList = this.shadowRoot.querySelector('.upcoming-list');
    const gridWrap = this.shadowRoot.querySelector('.calendar-grid-wrap');
    const gridEl = this.shadowRoot.querySelector('.calendar-grid');
    const moonName = this._live.lunation_name_display || `Moon ${this._live.lunation}`;

    const showStrip = view === 'strip' || view === 'both';
    const showGrid = view === 'grid' || view === 'both';

    moonTitle.hidden = !showStrip;
    moonStrip.hidden = !showStrip;
    upcomingStrip.hidden = !showStrip;

    if (showStrip) {
      moonTitle.textContent = `${moonName} — days`;
      const stripModel = buildMoonStripModel(this._matrix, this._live, DAY_NAMES, moonName);
      moonStrip.innerHTML = stripModel.map((cell) => this.renderCalendarCellMarkup(cell, { interactive: true })).join('');
      this.bindCalendarCellInteractions(moonStrip);

      const upcoming = upcomingHolidayCells(this._matrix, this._live.lunation, this._live.day, 4);
      upcomingList.innerHTML = upcoming.length
        ? upcoming.map((cell) => {
            const moon = this._matrix.lunation_names?.[String(cell.lunation)] || `Moon ${cell.lunation}`;
            const dayName = DAY_NAMES[cell.day] || `Day ${cell.day}`;
            const label = `${cell.holiday_name} (${moon} Moon · ${dayName})`;
            return `<li class="upcoming-item holiday-${cell.type || 'recurring'}">${escapeHtml(label)}</li>`;
          }).join('')
        : '<li class="upcoming-item upcoming-none">No more holidays this cycle</li>';
    }

    if (showGrid && gridWrap && gridEl) {
      const { rows, daysPerLunation } = buildFullGridModel(this._matrix, this._live, DAY_NAMES);
      const headerCells = Array.from({ length: daysPerLunation }, (_, i) => {
        const day = i + 1;
        const dayName = DAY_NAMES[day] || '';
        return `<span class="grid-corner" role="columnheader" aria-label="Day ${day}">${day}</span>`;
      }).join('');

      const rowMarkup = rows.map((row) => {
        const rowCells = row.cells.map((cell) => this.renderCalendarCellMarkup(cell, { interactive: true, role: 'gridcell' })).join('');
        return `
          <div class="grid-row" role="row">
            <span class="moon-label" role="rowheader" title="${escapeHtml(row.moonName)} Moon">${escapeHtml(row.moonName)}</span>
            ${rowCells}
          </div>
        `;
      }).join('');

      gridEl.innerHTML = `
        <div class="grid-header" role="row">
          <span class="grid-corner moon-corner" role="columnheader" aria-label="Moon"></span>
          ${headerCells}
        </div>
        ${rowMarkup}
      `;
      this.bindCalendarCellInteractions(gridEl);
      gridWrap.hidden = false;
    } else if (gridWrap) {
      gridWrap.hidden = true;
    }

    strip.hidden = false;
  }

  renderError(msg) {
    const timeEl = this.shadowRoot.querySelector('.time');
    if (timeEl) timeEl.textContent = `SQT Grove offline: ${msg}`;
    this.renderCalendar();
  }

  renderData(data) {
    if (this._live && !this._live.error) {
      const timeEl = this.shadowRoot.querySelector('.time');
      if (timeEl) timeEl.textContent = formatStamp(this._live);
    }

    const h = this.activeHoliday();
    const ceremonial = isCeremonialMajor(h);
    if (ceremonial) {
      this.dataset.ceremonial = 'major';
    } else {
      delete this.dataset.ceremonial;
    }

    const rootEl = this.shadowRoot.querySelector('.root');
    if (rootEl) rootEl.classList.toggle('ceremonial-major', ceremonial);

    const badgeWrap = this.shadowRoot.querySelector('.badge-wrap');
    badgeWrap.innerHTML = '';
    if (h) {
      const badge = document.createElement('span');
      badge.className = `badge badge-${h.type}${ceremonial ? ' badge-major-ceremonial' : ''}`;
      badge.setAttribute('aria-label', `Active holiday: ${h.name}, ${h.type}`);
      badge.textContent = ceremonial ? `✦ ${h.name}` : h.name;
      badge.style.background = BADGE_COLORS[h.type] || BADGE_COLORS.none;
      badgeWrap.appendChild(badge);
      if (ceremonial) {
        const sub = document.createElement('p');
        sub.className = 'major-lunation-label';
        sub.textContent = 'Major Lunation Event';
        badgeWrap.appendChild(sub);
      }
    } else {
      const plain = document.createElement('span');
      plain.className = 'badge badge-none';
      plain.setAttribute('aria-label', 'No active holiday');
      plain.textContent = 'Plain Grove day';
      badgeWrap.appendChild(plain);
    }

    const openBtn = this.shadowRoot.querySelector('.open-circuit');
    const mode = this.getAttribute('bundle-mode') || 'teaser';
    openBtn.hidden = mode === 'none' || !data.bundle;
    openBtn.classList.toggle('ceremonial', ceremonial);
    openBtn.textContent = ceremonial
      ? `Open Ceremonial Circuit — ${h.name}`
      : (h ? `Open Circuit — ${h.name}` : "Open today's Circuit");

    this.renderCalendar();
  }

  teardownFocusTrap() {
    if (this._releaseFocusTrap) {
      this._releaseFocusTrap();
      this._releaseFocusTrap = null;
    }
    if (this._focusReturn?.focus) {
      this._focusReturn.focus();
      this._focusReturn = null;
    }
  }

  cellTeaserPayload(lunation, day) {
    const isToday = this._live
      && this._live.lunation === lunation
      && this._live.day === day;

    if (isToday && this._data?.bundle) {
      const h = this.activeHoliday();
      return {
        holiday: h,
        bundle: this._data.bundle,
        themes: this._data.themes || {},
        stamp: formatStamp(this._live),
        isToday: true,
      };
    }

    const cell = (this._matrix?.cells || []).find((c) => c.lunation === lunation && c.day === day);
    if (!cell) return null;

    const moon = this._matrix.lunation_names?.[String(lunation)] || `Moon ${lunation}`;
    const dayName = DAY_NAMES[day] || `Day ${day}`;
    const holiday = cell.holiday_id
      ? { id: cell.holiday_id, name: cell.holiday_name, type: cell.type }
      : null;

    return {
      holiday,
      bundle: cell.teaser || {
        journal_prompt: holiday
          ? `A preview of ${holiday.name} on ${moon} Moon, ${dayName}.`
          : `Plain Grove day on ${moon} Moon, ${dayName}.`,
        foraging_idea: holiday
          ? 'Return on this Grove day for the live Messenger\'s Circuit.'
          : 'No holiday active — a quiet day in the Grove.',
      },
      themes: {},
      stamp: `Year ${this._live?.year || 1} · ${moon} Moon · ${dayName}`,
      isToday: false,
    };
  }

  openCellTeaser(lunation, day, triggerEl) {
    const payload = this.cellTeaserPayload(lunation, day);
    if (!payload) return;
    this.openModal(triggerEl, payload);
  }

  openModal(triggerEl, payloadOverride = null) {
    const data = this._data;
    const modal = this.shadowRoot.querySelector('.modal');
    const inner = this.shadowRoot.querySelector('.modal-inner');

    const h = payloadOverride?.holiday ?? this.activeHoliday();
    const b = payloadOverride?.bundle ?? data?.bundle ?? {};
    const t = payloadOverride?.themes ?? data?.themes ?? {};
    const stamp = payloadOverride?.stamp ?? (this._live ? formatStamp(this._live) : '');
    const isToday = payloadOverride?.isToday ?? true;
    const mode = this.getAttribute('bundle-mode') || 'teaser';

    if (!payloadOverride && !data) return;
    const motifs = (t.motifs || [])
      .slice(0, 5)
      .map((m) => `<span class="motif-chip">${m}</span>`)
      .join('');
    const palettes = (b.mood_board?.palette || t.palettes || [])
      .map((c) => `<span class="swatch" style="background:${c}" title="${c}"></span>`)
      .join('');

    const majorCeremonial = isCeremonialMajor(h);
    inner.innerHTML = `
      <h2 id="circuit-title">${majorCeremonial ? '✦ ' : ''}${h ? escapeHtml(h.name) : 'Grove Day'}${majorCeremonial ? ' <span class="major-tag">Major Lunation</span>' : ''}</h2>
      <p class="circuit-stamp">${escapeHtml(stamp)}</p>
      ${majorCeremonial ? ceremonialBannerHtml(b, t) : ''}
      ${!isToday ? '<p class="preview-note">Calendar preview — open on this Grove day for the live Circuit.</p>' : ''}
      ${h ? `<p class="holiday-meta">Type: ${h.type}</p>` : ''}
      ${motifs ? `<div class="motifs" aria-label="Holiday motifs">${motifs}</div>` : ''}
      <p class="journal">${escapeHtml(b.journal_prompt || '')}</p>
      <p class="forage"><strong>Forage:</strong> ${escapeHtml(b.foraging_idea || '')}</p>
      ${mode === 'full' && b.story_seed ? `<details><summary>Story Seed</summary><p>${escapeHtml(b.story_seed)}</p></details>` : ''}
      ${mode === 'full' && b.art_prompt ? `<details><summary>Art Prompt</summary><p>${escapeHtml(b.art_prompt)}</p></details>` : ''}
      ${palettes ? `<div class="swatches" aria-label="Mood palette">${palettes}</div>` : ''}
      <div class="modal-actions">
        <button type="button" class="copy">Copy teaser</button>
        <button type="button" class="share" hidden>Share</button>
      </div>
    `;

    const teaserMarkdown = `## ${h?.name || 'SQT Grove'}\n${stamp}\n\n${b.journal_prompt || ''}\n\n**Forage:** ${b.foraging_idea || ''}`;
    inner.querySelector('.copy')?.addEventListener('click', () => {
      navigator.clipboard?.writeText(teaserMarkdown);
    });

    const shareBtn = inner.querySelector('.share');
    if (shareBtn && navigator.share) {
      shareBtn.hidden = false;
      shareBtn.addEventListener('click', async () => {
        try {
          await navigator.share({
            title: h?.name || 'SQT Grove',
            text: teaserMarkdown,
          });
        } catch {
          /* user cancelled */
        }
      });
    }

    this._focusReturn = triggerEl || this.shadowRoot.activeElement;
    modal.showModal();
    this.teardownFocusTrap();
    this._releaseFocusTrap = trapFocus(modal, () => this.closeModal());

    const focusable = getFocusableElements(modal);
    (focusable[0] || modal).focus();

    this.dispatchEvent(new CustomEvent('sqt-bundle-open', { detail: { mode }, bubbles: true }));
  }

  closeModal() {
    this.shadowRoot.querySelector('.modal')?.close();
  }
}

customElements.define('sqt-grove-clock', SQTGroveClock);