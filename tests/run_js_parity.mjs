import {
  SQT_LUNATIONS_PER_YEAR,
  SQT_DAYS_PER_LUNATION,
  sqtStateForLunationDay,
} from '../lib/sqt-core.js';

const rows = [];
for (let lunation = 1; lunation <= SQT_LUNATIONS_PER_YEAR; lunation++) {
  for (let day = 1; day <= SQT_DAYS_PER_LUNATION; day++) {
    const s = sqtStateForLunationDay(lunation, day);
    rows.push({
      lunation,
      day,
      lunation_name_display: s.lunation_name_display,
      day_name_display: s.day_name_display,
      week_label: s.week_label,
      moon_phase: s.moon_phase,
      moon_phase_key: s.moon_phase_key,
    });
  }
}
process.stdout.write(JSON.stringify(rows));