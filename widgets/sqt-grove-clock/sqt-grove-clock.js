/**
 * <sqt-grove-clock> — embeddable SQT time + holiday + Circuit modal
 * Contract: phase2-2.3-widget-specs.md
 */
const BADGE_COLORS = {
  recurring: 'var(--sqt-badge-recurring, #4CAF50)',
  major: 'var(--sqt-badge-major, #FFD54F)',
  rare: 'var(--sqt-badge-rare, #78909C)',
  none: 'var(--sqt-badge-none, #8C6239)',
};

class SQTGroveClock extends HTMLElement {
  static get observedAttributes() {
    return ['src', 'refresh', 'theme', 'bundle-mode', 'calendar-src'];
  }

  constructor() {
    super();
    this.attachShadow({ mode: 'open' });
    this._data = null;
    this._timer = null;
  }

  connectedCallback() {
    this.renderShell();
    this.fetchData();
    const sec = parseInt(this.getAttribute('refresh') || '60', 10);
    if (sec > 0) {
      this._timer = setInterval(() => this.fetchData(), sec * 1000);
    }
  }

  disconnectedCallback() {
    if (this._timer) clearInterval(this._timer);
  }

  attributeChangedCallback() {
    if (this.isConnected) this.fetchData();
  }

  async fetchData() {
    const src = this.getAttribute('src') || './circuit-current.json';
    try {
      const res = await fetch(src);
      if (!res.ok) throw new Error(`HTTP ${res.status}`);
      const data = await res.json();
      this._data = data;
      this.renderData(data);
      this.dispatchEvent(new CustomEvent('sqt-loaded', { detail: data, bubbles: true }));
    } catch (err) {
      this.renderError(err.message);
      this.dispatchEvent(new CustomEvent('sqt-error', { detail: { message: err.message, src }, bubbles: true }));
    }
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
    const s = data.sqt || {};
    const h = data.holiday;
    const ext = data._extended?.sqt_full;
    const lunLabel = ext?.lunation_name || `Lunation ${s.lunation}`;
    const dayLabel = ext?.day_name || `Day ${s.day}`;

    const timeEl = this.shadowRoot.querySelector('.time');
    timeEl.textContent = `Year ${s.year} · ${lunLabel} · ${dayLabel} · ${s.time || '--:--:--'}`;

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
    const h = data.holiday;
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
      const text = `## ${h?.name || 'SQT Grove'}\n\n${b.journal_prompt || ''}\n\n**Forage:** ${b.foraging_idea || ''}`;
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