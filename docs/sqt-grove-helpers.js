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