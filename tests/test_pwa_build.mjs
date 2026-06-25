/**
 * PWA build verification — docs/ assets include Phase 3 features (offline CI check).
 * Live HTTP checks: scripts/smoke_widget_triad.py
 */
import assert from 'node:assert/strict';
import { readFileSync } from 'node:fs';
import { join, dirname } from 'node:path';
import { fileURLToPath } from 'node:url';

const ROOT = join(dirname(fileURLToPath(import.meta.url)), '..');
const js = readFileSync(join(ROOT, 'docs/sqt-grove-clock.js'), 'utf8');
const css = readFileSync(join(ROOT, 'docs/sqt-grove-clock.css'), 'utf8');
const html = readFileSync(join(ROOT, 'docs/index.html'), 'utf8');
const matrix = JSON.parse(readFileSync(join(ROOT, 'docs/calendar_matrix.json'), 'utf8'));

const requiredJs = [
  'buildFullGridModel',
  'calendar-grid',
  'openCellTeaser',
  'trapFocus',
  'sqt-holiday-change',
  'navigator.share',
  'high-contrast',
  'ceremonial-banner',
  'ceremonial-major',
  'Major Lunation',
];
for (const token of requiredJs) {
  assert.match(js, new RegExp(token.replace('.', '\\.')), `missing in sqt-grove-clock.js: ${token}`);
}

assert.match(css, /\.calendar-grid/);
assert.match(css, /\.ceremonial-banner/);
assert.match(css, /\.ceremonial-major/);
assert.match(html, /<sqt-grove-clock/);
assert.equal(matrix.cells?.length, 12 * 19);
assert.ok(matrix.cells.some((c) => c.teaser?.journal_prompt), 'matrix holiday teasers');

console.log('PWA build verification: ok');