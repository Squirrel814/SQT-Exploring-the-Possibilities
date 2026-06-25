/**
 * <sqt-grove-clock> — embeddable SQT time + holiday + Circuit modal
 * Contract: phase2-2.3-widget-specs.md
 */
import { sqtStateNow } from './sqt-core.js';

const BADGE_COLORS = {
  recurring: 'var(--sqt-badge-recurring, #4CAF50)',
  major: 'var(--sqt-badge-major, #FFD54F)',
  rare: 'var(--sqt-badge-rare, #78909C)',
  none: 'var(--sqt-badge-none, #8C6239)',
};

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

class SQTGroveClock extends HTMLElement {
  static get observedAttributes() {
    return ['src', 'refresh', 'theme', 'bundle-mode', 'calendar-src', 'lunation-labels'];
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
  }

  connectedCallback() {
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
  }

  attributeChangedCallback() {
    if (!this.isConnected) return;
    this.loadCalendarMatrix();
    this.fetchData();
  }

  async loadCalendarMatrix() {
    const src = this.getAttribute('calendar-src');
    if (!src) return;
    try {
      const res = await fetch(src);
      if (res.ok) this._matrix = await res.json();
    } catch {
      this._matrix = null;
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
      this.fetchData();
      this.dispatchEvent(new CustomEvent('sqt-holiday-change', {
        detail: { live: this._live, holiday: this.activeHoliday() },
        bubbles: true,
      }));
    }
  }

  activeHoliday() {
    if (this._live && this._matrix) {
      const fromMatrix = holidayFromMatrix(this._matrix, this._live.lunation, this._live.day);
      if (fromMatrix) return fromMatrix;
    }
    return this._data?.holiday || null;
  }

  renderShell() {
    this.shadowRoot.innerHTML = `
      <link rel="stylesheet" href="${this.getAttribute('css-href') || './sqt-grove-clock.css'}">
      <div class="root" role="region" aria-label="Squirrel Quantum Time">
        <div class="time" aria-live="polite"></div>
        <div class="badge-wrap"></div>
        <button type="button" class="open-circuit" hidden>Open today's Circuit</button>
      </div>
      <dialog class="modal" aria-label="Messenger's Circuit">
        <div class="modal-inner"></div>
        <button type="button" class="close">Close</button>
      </dialog>
    `;
    this.shadowRoot.querySelector('.open-circuit').addEventListener('click', () => this.openModal());
    this.shadowRoot.querySelector('.close').addEventListener('click', () => this.closeModal());
  }

  renderError(msg) {
    const timeEl = this.shadowRoot.querySelector('.time');
    if (timeEl) timeEl.textContent = `SQT Grove offline: ${msg}`;
  }

  renderData(data) {
    if (this._live && !this._live.error) {
      const timeEl = this.shadowRoot.querySelector('.time');
      if (timeEl) timeEl.textContent = formatStamp(this._live);
    }

    const h = this.activeHoliday();
    const badgeWrap = this.shadowRoot.querySelector('.badge-wrap');
    badgeWrap.innerHTML = '';
    if (h) {
      const badge = document.createElement('span');
      badge.className = `badge badge-${h.type}`;
      badge.setAttribute('aria-label', `Active holiday: ${h.name}, ${h.type}`);
      badge.textContent = h.name;
      badge.style.background = BADGE_COLORS[h.type] || BADGE_COLORS.none;
      badgeWrap.appendChild(badge);
    }

    const openBtn = this.shadowRoot.querySelector('.open-circuit');
    const mode = this.getAttribute('bundle-mode') || 'teaser';
    openBtn.hidden = mode === 'none' || !data.bundle;
    openBtn.textContent = h ? `Open Circuit — ${h.name}` : "Open today's Circuit";
  }

  openModal() {
    const data = this._data;
    if (!data) return;
    const modal = this.shadowRoot.querySelector('.modal');
    const inner = this.shadowRoot.querySelector('.modal-inner');
    const h = this.activeHoliday();
    const b = data.bundle || {};
    const mode = this.getAttribute('bundle-mode') || 'teaser';
    const palettes = (b.mood_board?.palette || data.themes?.palettes || [])
      .map((c) => `<span class="swatch" style="background:${c}" title="${c}"></span>`)
      .join('');

    inner.innerHTML = `
      <h2>${h ? h.name : 'Grove Day'}</h2>
      <p class="journal">${b.journal_prompt || ''}</p>
      <p class="forage"><strong>Forage:</strong> ${b.foraging_idea || ''}</p>
      ${mode === 'full' && b.story_seed ? `<details><summary>Story Seed</summary><p>${b.story_seed}</p></details>` : ''}
      ${mode === 'full' && b.art_prompt ? `<details><summary>Art Prompt</summary><p>${b.art_prompt}</p></details>` : ''}
      ${palettes ? `<div class="swatches">${palettes}</div>` : ''}
      <button type="button" class="copy">Copy teaser</button>
    `;
    inner.querySelector('.copy')?.addEventListener('click', () => {
      const stamp = this._live ? formatStamp(this._live) : '';
      const text = `## ${h?.name || 'SQT Grove'}\n${stamp}\n\n${b.journal_prompt || ''}\n\n**Forage:** ${b.foraging_idea || ''}`;
      navigator.clipboard?.writeText(text);
    });
    modal.showModal();
    this.dispatchEvent(new CustomEvent('sqt-bundle-open', { detail: { mode }, bubbles: true }));
  }

  closeModal() {
    this.shadowRoot.querySelector('.modal')?.close();
  }
}

customElements.define('sqt-grove-clock', SQTGroveClock);