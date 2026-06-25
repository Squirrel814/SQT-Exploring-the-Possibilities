/** Pure formatters for SQT Grove VS Code extension (testable without vscode API). */

const MOON_NAMES = {
  1: 'Sleepy Moon', 2: 'Pinecone Moon', 3: 'Scamper Moon', 4: 'Asher Moon',
  5: 'Bark Stripper Moon', 6: 'Canopy Moon', 7: 'Hollow Tree Moon', 8: 'Golden Leaf Moon',
  9: 'Cache Moon', 10: 'Shadow Moon', 11: 'Forage Moon', 12: 'Chattering Moon',
};

const DAY_NAMES = {
  1: 'Truffle-day', 2: 'Sprout-day', 3: 'Sap-day', 4: 'Twig-day', 5: 'Fern-day',
  6: 'Chitter-day', 7: 'Stash-day', 8: 'Thicket-day', 9: 'Moss-day', 10: 'Cache-Day',
  11: 'Forage-day', 12: 'Oak-day', 13: 'Timber-day', 14: 'Swindle-day', 15: 'Scurry-day',
  16: 'Bark-day', 17: 'Willow-day', 18: 'Drey-day', 19: 'Nap-day',
};

const HASH_COMMENT_LANGS = new Set([
  'python', 'shellscript', 'powershell', 'dockerfile', 'makefile', 'ruby', 'perl', 'r',
  'yaml', 'toml', 'properties', 'cmake', 'julia', 'coffeescript',
]);

const DASH_COMMENT_LANGS = new Set(['sql', 'lua', 'haskell', 'graphql']);

function resolveSqtLabels(data) {
  const s = data.sqt || {};
  const ext = data._extended?.sqt_full || {};
  const moon = ext.lunation_name_display || MOON_NAMES[s.lunation] || `Moon ${s.lunation}`;
  const day = ext.day_name_display || DAY_NAMES[s.day] || `Day ${s.day}`;
  return { s, moon, day };
}

function commentStyleForLanguage(languageId = '') {
  const id = String(languageId).toLowerCase();
  if (HASH_COMMENT_LANGS.has(id)) return { prefix: '# ', decorate: (line) => `# ${line}` };
  if (DASH_COMMENT_LANGS.has(id)) return { prefix: '-- ', decorate: (line) => `-- ${line}` };
  if (id === 'bat') return { prefix: 'REM ', decorate: (line) => `REM ${line}` };
  if (id === 'latex') return { prefix: '% ', decorate: (line) => `% ${line}` };
  return { prefix: '// ', decorate: (line) => `// ${line}` };
}

function statusIcon(holiday) {
  return holiday?.type === 'major' ? '$(star-full)' : '$(squirrel)';
}

function shortHolidayName(name) {
  if (!name) return '';
  const trimmed = name.replace(/^The\s+/i, '');
  return trimmed.split(' ')[0];
}

function formatStatus(data) {
  const { s, moon, day } = resolveSqtLabels(data);
  const h = data.holiday;
  const icon = statusIcon(h);
  const hol = h ? ` · ${shortHolidayName(h.name)}` : '';
  return `${icon} Y${s.year} ${moon} · ${day}${hol}`;
}

function ceremonialHeader(themes, fmt, languageId = 'javascript') {
  const keywords = themes?.tone_keywords || [];
  if (!keywords.length) return '';
  const line = keywords.join(' · ');
  if (fmt === 'comment-block') {
    return `${commentStyleForLanguage(languageId).decorate(`Ceremonial: ${line}`)}\n`;
  }
  return `> *${line}*\n\n`;
}

function formatTooltipLines(data) {
  const { s, moon, day } = resolveSqtLabels(data);
  const h = data.holiday;
  const b = data.bundle || {};
  const t = data.themes || {};
  const lines = [
    `**SQT** Year ${s.year}, ${moon}, ${day}`,
    `**Time** ${s.time || '—'}`,
  ];
  if (h) {
    const majorNote = h.type === 'major' ? ' 🌕 Major Lunation Event' : '';
    lines.push(`**Holiday** ${h.name} (${h.type})${majorNote}`);
  }
  if (b.squirrel_ops_lab?.title) lines.push(`_Squirrel Ops:_ ${b.squirrel_ops_lab.title}`);
  if (b.foraging_idea) lines.push(`_Forage:_ ${b.foraging_idea}`);
  if (t.motifs?.length) lines.push(`_Motifs:_ ${t.motifs.slice(0, 5).join(', ')}`);
  return lines;
}

function formatInsert(data, insertFormat = 'markdown', languageId = 'javascript') {
  const { s, moon, day } = resolveSqtLabels(data);
  const h = data.holiday;
  const b = data.bundle || {};
  const t = data.themes || {};
  const ceremonial = h?.type === 'major' ? ceremonialHeader(t, insertFormat, languageId) : '';
  const hid = h?.id || 'grove_day';
  const comment = commentStyleForLanguage(languageId);

  if (insertFormat === 'comment-block') {
    const j = (b.journal_prompt || '').replace(/\n/g, ' ').slice(0, 120);
    const story = (b.story_seed || '').replace(/\n/g, ' ').slice(0, 120);
    const forage = (b.foraging_idea || '').replace(/\n/g, ' ').slice(0, 200);
    return [
      ceremonial,
      comment.decorate(`═══ SQT Grove · ${h?.name || 'Grove Day'} · Y${s.year} ${moon} · ${day} ═══`),
      comment.decorate(`Journal: ${j}`),
      comment.decorate(`Forage: ${forage}`),
      story ? comment.decorate(`Story: ${story}`) : null,
      comment.decorate('═══'),
      '',
    ].filter(Boolean).join('\n');
  }

  const mood = b.mood_board || {};
  const palette = (mood.palette || t.palettes || []).map((c) => `\`${c}\``).join(' ');

  return [
    `<!-- sqt-grove: Y${s.year}-M${s.lunation}-D${s.day} ${hid} -->`,
    ceremonial,
    `## Messenger's Circuit — ${h?.name || 'Grove Day'}${h?.type === 'major' ? ' 🌕' : ''}`,
    `*Year ${s.year}, ${moon}, ${day} · ${s.time || '—'}*`,
    '',
    '### Journal',
    b.journal_prompt || '',
    '',
    '### Story Seed',
    b.story_seed || '',
    '',
    '### Foraging',
    b.foraging_idea || '',
    '',
    mood.atmosphere ? '### Mood\n' + mood.atmosphere + '\n' : '',
    palette ? `*Palette:* ${palette}\n` : '',
    '### Art Prompt',
    b.art_prompt || '',
    '',
  ].filter((line) => line !== '').join('\n');
}

module.exports = {
  MOON_NAMES,
  DAY_NAMES,
  resolveSqtLabels,
  commentStyleForLanguage,
  statusIcon,
  formatStatus,
  formatTooltipLines,
  formatInsert,
  ceremonialHeader,
};