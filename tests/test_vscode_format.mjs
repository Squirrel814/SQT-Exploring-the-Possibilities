import assert from 'node:assert/strict';
import { createRequire } from 'node:module';

const require = createRequire(import.meta.url);
const {
  ceremonialHeader,
  formatInsert,
  formatStatus,
  statusIcon,
} = require('../widgets/vscode-sqt-grove/vscode-format.js');

const recurring = {
  sqt: { year: 1, lunation: 6, day: 7, time: '04:22:02' },
  holiday: { id: 'leybridge_threading', name: 'Leybridge Threading', type: 'recurring' },
  bundle: { journal_prompt: 'Bridge?', foraging_idea: 'Connect.', story_seed: 'Pebbles.', art_prompt: 'Art.' },
  themes: { tone_keywords: ['steady'], motifs: ['pebbles'] },
  _extended: {
    sqt_full: {
      lunation_name_display: 'Canopy Moon',
      day_name_display: 'Stash-day',
    },
  },
};

const major = {
  sqt: { year: 1, lunation: 6, day: 19, time: '00:59:58' },
  holiday: { id: 'shadow_trial', name: 'The Shadow Trial', type: 'major' },
  bundle: {
    journal_prompt: 'Shadow path?',
    foraging_idea: 'Adapt.',
    story_seed: 'Fog.',
    art_prompt: 'Mist.',
    mood_board: { atmosphere: 'Misty', palette: ['#37474F'] },
  },
  themes: {
    tone_keywords: ['resilient', 'clever', 'shadow', 'adaptation'],
    palettes: ['#37474F'],
  },
  _extended: {
    sqt_full: {
      lunation_name_display: 'Canopy Moon',
      day_name_display: 'Nap-day',
    },
  },
};

assert.equal(statusIcon(recurring.holiday), '$(squirrel)');
assert.equal(statusIcon(major.holiday), '$(star-full)');

assert.match(formatStatus(recurring), /^\$\(squirrel\) Y1 Canopy Moon · Stash-day · Leybridge$/);
assert.match(formatStatus(major), /^\$\(star-full\) Y1 Canopy Moon · Nap-day · Shadow$/);

const md = formatInsert(major, 'markdown');
assert.match(md, /^> \*resilient · clever · shadow · adaptation\*/m);
assert.match(md, /## Messenger's Circuit — The Shadow Trial 🌕/);
assert.match(md, /Canopy Moon, Nap-day/);

const block = formatInsert(major, 'comment-block');
assert.match(block, /^\/\/ Ceremonial: resilient · clever · shadow · adaptation/m);

const plain = formatInsert({ ...recurring, holiday: null }, 'markdown');
assert.doesNotMatch(plain, /Ceremonial:/);
assert.match(plain, /Grove Day/);

console.log('vscode-format tests: ok');