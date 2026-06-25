import assert from 'node:assert/strict';
import {
  buildFullGridModel,
  buildMoonStripModel,
  calendarViewMode,
  formatCalendarCellLabel,
  formatHolidayAnnouncement,
  matrixCellAt,
  showCalendarEnabled,
  upcomingHolidayCells,
} from '../widgets/sqt-grove-clock/sqt-grove-helpers.js';

const leybridge = { holiday: { id: 'leybridge_threading', name: 'Leybridge Threading', type: 'recurring' } };
const plain = { holiday: null };
const hoard = { holiday: { id: 'discerned_hoard', name: 'The Discerned Hoard', type: 'recurring' } };

assert.equal(formatHolidayAnnouncement(plain, leybridge), 'Holiday began: Leybridge Threading');
assert.equal(
  formatHolidayAnnouncement(leybridge, plain),
  'Holiday ended: Leybridge Threading. Plain Grove day.',
);
assert.equal(
  formatHolidayAnnouncement(leybridge, hoard),
  'Holiday changed from Leybridge Threading to The Discerned Hoard',
);
assert.equal(formatHolidayAnnouncement(leybridge, leybridge), '');

assert.equal(showCalendarEnabled(null), true);
assert.equal(showCalendarEnabled('false'), false);
assert.equal(showCalendarEnabled('0'), false);

const matrix = {
  sqt_days_per_lunation: 19,
  cells: [
    { lunation: 6, day: 6, holiday_id: null, holiday_name: null, type: null },
    { lunation: 6, day: 7, holiday_id: 'leybridge_threading', holiday_name: 'Leybridge Threading', type: 'recurring' },
    { lunation: 6, day: 8, holiday_id: null, holiday_name: null, type: null },
    { lunation: 6, day: 13, holiday_id: 'burrowstill_knowing', holiday_name: 'Burrowstill Knowing', type: 'recurring' },
    { lunation: 6, day: 14, holiday_id: 'burrowstill_knowing', holiday_name: 'Burrowstill Knowing', type: 'recurring' },
    { lunation: 6, day: 17, holiday_id: 'chatterseed_scatter', holiday_name: 'Chatterseed Scatter', type: 'recurring' },
    { lunation: 6, day: 19, holiday_id: 'shadow_trial', holiday_name: 'The Shadow Trial', type: 'major' },
  ],
};

const upcoming = upcomingHolidayCells(matrix, 6, 7, 3);
assert.equal(upcoming.length, 3);
assert.equal(upcoming[0].holiday_id, 'burrowstill_knowing');
assert.equal(upcoming[1].holiday_id, 'chatterseed_scatter');
assert.equal(upcoming[2].holiday_id, 'shadow_trial');

const live = { lunation: 6, day: 7 };
const dayNames = { 7: 'Stash-day', 13: 'Timber-day' };
const strip = buildMoonStripModel(matrix, live, dayNames, 'Canopy Moon');
assert.equal(strip.length, 7);
assert.equal(strip.find((c) => c.day === 7)?.isToday, true);
assert.equal(
  formatCalendarCellLabel(strip[1], 'Canopy Moon', dayNames),
  'Canopy Moon, Stash-day, Leybridge Threading',
);

assert.equal(calendarViewMode(null), 'both');
assert.equal(calendarViewMode('strip'), 'strip');
assert.equal(calendarViewMode('grid'), 'grid');

assert.equal(matrixCellAt(matrix, 6, 7)?.holiday_id, 'leybridge_threading');
assert.equal(matrixCellAt(matrix, 6, 1), null);

const grid = buildFullGridModel(matrix, live, dayNames);
assert.equal(grid.rows.length, 12);
assert.equal(grid.rows[5].moonName, 'Moon 6');
assert.equal(grid.rows[5].cells.length, 19);
const todayCell = grid.rows[5].cells.find((c) => c.day === 7);
assert.equal(todayCell?.isToday, true);
assert.equal(todayCell?.isCurrentMoon, true);
assert.equal(grid.rows[0].cells[6]?.isCurrentMoon, false);

console.log('sqt-grove-clock helper tests: ok');