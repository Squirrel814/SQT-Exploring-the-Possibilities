export function holidayKey(holiday) {
  return holiday?.id || null;
}

export function buildSnapshot(live, holiday) {
  return {
    position: live ? `${live.year}-${live.lunation}-${live.day}` : '',
    holiday: holiday ? { ...holiday } : null,
    live: live ? { ...live } : null,
  };
}

export function holidaysDiffer(previous, current) {
  return holidayKey(previous?.holiday) !== holidayKey(current?.holiday);
}

export function formatHolidayAnnouncement(previous, current) {
  const prevName = previous?.holiday?.name;
  const currName = current?.holiday?.name;
  if (!prevName && currName) return `Holiday began: ${currName}`;
  if (prevName && !currName) return `Holiday ended: ${prevName}. Plain Grove day.`;
  if (prevName && currName && prevName !== currName) {
    return `Holiday changed from ${prevName} to ${currName}`;
  }
  return '';
}

export function getFocusableElements(root) {
  return Array.from(
    root.querySelectorAll(
      'button:not([disabled]), [href], input:not([disabled]), select:not([disabled]), textarea:not([disabled]), summary, [tabindex]:not([tabindex="-1"])',
    ),
  ).filter((el) => el.offsetParent !== null || el === root.activeElement);
}

export function sqtLinearIndex(lunation, day, daysPerLunation = 19) {
  return (lunation - 1) * daysPerLunation + (day - 1);
}

export function moonDayCells(matrix, lunation) {
  return (matrix?.cells || []).filter((cell) => cell.lunation === lunation);
}

export function upcomingHolidayCells(matrix, lunation, day, limit = 4) {
  const cells = matrix?.cells || [];
  if (!cells.length || limit <= 0) return [];

  let start = cells.findIndex((c) => c.lunation === lunation && c.day === day);
  if (start < 0) {
    start = sqtLinearIndex(lunation, day, matrix.sqt_days_per_lunation || 19);
    if (start >= cells.length) return [];
  }

  const result = [];
  for (let offset = 1; offset <= cells.length && result.length < limit; offset += 1) {
    const cell = cells[(start + offset) % cells.length];
    if (!cell?.holiday_id) continue;
    const prev = result[result.length - 1];
    if (prev?.holiday_id === cell.holiday_id) continue;
    result.push(cell);
  }
  return result;
}

export function formatCalendarCellLabel(cell, moonName, dayNames = {}) {
  const moon = moonName || `Moon ${cell.lunation}`;
  const dayName = dayNames[cell.day] || `Day ${cell.day}`;
  if (cell.holiday_name) return `${moon}, ${dayName}, ${cell.holiday_name}`;
  return `${moon}, ${dayName}, no holiday`;
}

export function buildMoonStripModel(matrix, live, dayNames = {}, moonDisplayName = '') {
  if (!matrix || !live) return [];
  const moon = moonDisplayName || `Moon ${live.lunation}`;
  return moonDayCells(matrix, live.lunation).map((cell) => ({
    ...cell,
    isToday: cell.day === live.day,
    dayName: dayNames[cell.day] || `Day ${cell.day}`,
    ariaLabel: formatCalendarCellLabel(cell, moon, dayNames),
  }));
}

export function matrixCellAt(matrix, lunation, day) {
  return (matrix?.cells || []).find((c) => c.lunation === lunation && c.day === day) || null;
}

export function calendarViewMode(attr) {
  if (attr === 'strip' || attr === 'grid') return attr;
  return 'both';
}

export function buildFullGridModel(matrix, live, dayNames = {}) {
  if (!matrix?.cells?.length) return { rows: [], daysPerLunation: 19, lunationsPerYear: 12 };

  const daysPerLunation = matrix.sqt_days_per_lunation || 19;
  const lunationsPerYear = matrix.sqt_lunations_per_year || 12;
  const moonNames = matrix.lunation_names || {};
  const rows = [];

  for (let lunation = 1; lunation <= lunationsPerYear; lunation += 1) {
    const moon = moonNames[String(lunation)] || `Moon ${lunation}`;
    const cells = [];
    for (let day = 1; day <= daysPerLunation; day += 1) {
      const cell = matrixCellAt(matrix, lunation, day) || { lunation, day };
      const isToday = live && cell.lunation === live.lunation && cell.day === live.day;
      const isCurrentMoon = live && cell.lunation === live.lunation;
      cells.push({
        ...cell,
        isToday,
        isCurrentMoon,
        dayName: dayNames[day] || `Day ${day}`,
        moonName: moon,
        ariaLabel: formatCalendarCellLabel(cell, `${moon} Moon`, dayNames),
      });
    }
    rows.push({ lunation, moonName: moon, cells });
  }

  return { rows, daysPerLunation, lunationsPerYear };
}

export function showCalendarEnabled(attr) {
  return attr !== 'false' && attr !== '0';
}

export function trapFocus(container, onEscape) {
  const handleKeyDown = (event) => {
    if (event.key === 'Escape') {
      event.preventDefault();
      onEscape();
      return;
    }
    if (event.key !== 'Tab') return;

    const focusable = getFocusableElements(container);
    if (!focusable.length) return;

    const first = focusable[0];
    const last = focusable[focusable.length - 1];
    const active = container.getRootNode().activeElement;

    if (event.shiftKey && active === first) {
      event.preventDefault();
      last.focus();
    } else if (!event.shiftKey && active === last) {
      event.preventDefault();
      first.focus();
    }
  };

  container.addEventListener('keydown', handleKeyDown);
  return () => container.removeEventListener('keydown', handleKeyDown);
}