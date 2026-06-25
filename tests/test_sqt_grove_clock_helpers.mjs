import assert from 'node:assert/strict';
import { formatHolidayAnnouncement } from '../widgets/sqt-grove-clock/sqt-grove-helpers.js';

const leybridge = { holiday: { id: 'leybridge_threading', name: 'Leybridge Threading', type: 'recurring' } };
const plain = { holiday: null };
const hoard = { holiday: { id: 'discerned_hoard', name: 'The Discerned Hoard', type: 'recurring' } };

assert.equal(
  formatHolidayAnnouncement(plain, leybridge),
  'Holiday began: Leybridge Threading',
);
assert.equal(
  formatHolidayAnnouncement(leybridge, plain),
  'Holiday ended: Leybridge Threading. Plain Grove day.',
);
assert.equal(
  formatHolidayAnnouncement(leybridge, hoard),
  'Holiday changed from Leybridge Threading to The Discerned Hoard',
);
assert.equal(formatHolidayAnnouncement(leybridge, leybridge), '');

console.log('sqt-grove-clock helper tests: ok');