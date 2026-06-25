/**
 * SQT core math — parity with sqt_engine_unified.py / reference/sqt_engine_2.py
 * SQT year = 12 lunations; each lunation = 19 unique days.
 */
export const SQT_EPOCH_MS = Date.parse('2026-01-18T20:52:00Z');
export const EARTH_HOURS_PER_SQT_DAY = 37.301826;
export const SEC_PER_SQT_DAY = EARTH_HOURS_PER_SQT_DAY * 3600;
export const LUNAR_CYCLE_SECONDS = 29.53059 * 24 * 3600;
export const SQT_LUNATIONS_PER_YEAR = 12;
export const SQT_DAYS_PER_LUNATION = 19;

export const SQT_LUNATIONS_DISPLAY = {
  1: 'Sleepy Moon', 2: 'Pinecone Moon', 3: 'Scamper Moon',
  4: 'Asher Moon', 5: 'Bark Stripper Moon', 6: 'Canopy Moon',
  7: 'Hollow Tree Moon', 8: 'Golden Leaf Moon', 9: 'Cache Moon',
  10: 'Shadow Moon', 11: 'Forage Moon', 12: 'Chattering Moon',
};

export const SQT_UNIQUE_DAYS_DISPLAY = {
  1: ['Truffle-day', 'Week 1: The First Nibble'],
  2: ['Sprout-day', 'Week 1: The First Nibble'],
  3: ['Sap-day', 'Week 1: The First Nibble'],
  4: ['Twig-day', 'Week 1: The First Nibble'],
  5: ['Fern-day', 'Week 2: The High Canopy'],
  6: ['Chitter-day', 'Week 2: The High Canopy'],
  7: ['Stash-day', 'Week 2: The High Canopy'],
  8: ['Thicket-day', 'Week 2: The High Canopy'],
  9: ['Moss-day', 'Week 2: The High Canopy'],
  10: ['Cache-Day', 'Week 3: The Great Acorn'],
  11: ['Forage-day', 'Week 3: The Great Acorn'],
  12: ['Oak-day', 'Week 3: The Great Acorn'],
  13: ['Timber-day', 'Week 3: The Great Acorn'],
  14: ['Swindle-day', 'Week 3: The Great Acorn'],
  15: ['Scurry-day', 'Week 4: The Deep Burrow'],
  16: ['Bark-day', 'Week 4: The Deep Burrow'],
  17: ['Willow-day', 'Week 4: The Deep Burrow'],
  18: ['Drey-day', 'Week 4: The Deep Burrow'],
  19: ['Nap-day', 'Week 4: The Deep Burrow'],
};

export function computeMoonPhase(day) {
  if (day === 1 || day === 19) return 'New Moon';
  if (day >= 2 && day <= 4) return 'Waxing Crescent';
  if (day === 5) return 'First Quarter';
  if (day >= 6 && day <= 9) return 'Waxing Gibbous';
  if (day === 10) return 'Full Moon';
  if (day >= 11 && day <= 14) return 'Waning Gibbous';
  if (day === 15) return 'Last Quarter';
  return 'Waning Crescent';
}

export function computeMoonPhaseKey(day) {
  const phase = computeMoonPhase(day);
  if (phase.startsWith('New Moon')) return 'new_moon';
  if (phase.startsWith('Full Moon')) return 'full';
  if (phase.startsWith('Waxing')) return 'waxing';
  if (phase.startsWith('Waning')) return 'waning';
  return 'any';
}

export function elapsedSecondsForLunationDay(lunation, day) {
  const position = (day - 1) / SQT_DAYS_PER_LUNATION;
  const totalLunations = (lunation - 1) + position;
  return totalLunations * LUNAR_CYCLE_SECONDS + 3600;
}

export function sqtStateFromElapsed(elapsedSeconds) {
  if (elapsedSeconds < 0) {
    return { error: 'Before SQT Epoch', year: 1, lunation: 1, day: 1 };
  }
  const totalLunations = elapsedSeconds / LUNAR_CYCLE_SECONDS;
  const currentLunationRaw = Math.floor(totalLunations);
  const positionInLunation = totalLunations - currentLunationRaw;

  const year = Math.floor(currentLunationRaw / SQT_LUNATIONS_PER_YEAR) + 1;
  let lunation = (currentLunationRaw % SQT_LUNATIONS_PER_YEAR) + 1;
  let sqtDay = Math.max(1, Math.min(SQT_DAYS_PER_LUNATION, Math.floor(positionInLunation * SQT_DAYS_PER_LUNATION) + 1));

  const lunationDisplay = SQT_LUNATIONS_DISPLAY[lunation] || 'Unknown Lunation';
  const dayInfo = SQT_UNIQUE_DAYS_DISPLAY[sqtDay] || ['Unknown-day', 'Unknown Week'];
  const secondsIntoLunation = positionInLunation * LUNAR_CYCLE_SECONDS;
  const secondsIntoDay = secondsIntoLunation % SEC_PER_SQT_DAY;
  const h = Math.floor(secondsIntoDay / 3600);
  const m = Math.floor((secondsIntoDay % 3600) / 60);
  const s = Math.floor(secondsIntoDay % 60);
  const time = `${String(h).padStart(2, '0')}:${String(m).padStart(2, '0')}:${String(s).padStart(2, '0')}`;

  return {
    year,
    lunation,
    lunation_name_display: lunationDisplay,
    day: sqtDay,
    day_name_display: dayInfo[0],
    week_label: dayInfo[1],
    time,
    moon_phase: computeMoonPhase(sqtDay),
    moon_phase_key: computeMoonPhaseKey(sqtDay),
    position_in_lunation: Math.round(positionInLunation * 1e6) / 1e6,
  };
}

export function sqtStateForLunationDay(lunation, day) {
  return sqtStateFromElapsed(elapsedSecondsForLunationDay(lunation, day));
}

export function sqtStateNow(nowMs = Date.now()) {
  const elapsed = (nowMs - SQT_EPOCH_MS) / 1000;
  return sqtStateFromElapsed(elapsed);
}