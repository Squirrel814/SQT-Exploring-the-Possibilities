const vscode = require('vscode');
const { execFile } = require('child_process');
const fs = require('fs');
const path = require('path');

let statusItem;
let cache = { data: null, at: 0 };
const CACHE_MS = 60_000;

function getConfig() {
  return vscode.workspace.getConfiguration('sqtGrove');
}

function findEnginePath() {
  const cfg = getConfig().get('enginePath');
  if (cfg && fs.existsSync(cfg)) return cfg;
  const folders = vscode.workspace.workspaceFolders || [];
  for (const f of folders) {
    const p = path.join(f.uri.fsPath, 'sqt_engine_unified.py');
    if (fs.existsSync(p)) return p;
  }
  return null;
}

function fetchCircuit(callback) {
  const now = Date.now();
  if (cache.data && now - cache.at < CACHE_MS) {
    return callback(null, cache.data);
  }
  const staticPath = getConfig().get('staticJsonPath');
  if (staticPath && fs.existsSync(staticPath)) {
    try {
      const data = JSON.parse(fs.readFileSync(staticPath, 'utf8'));
      cache = { data, at: now };
      return callback(null, data);
    } catch (e) {
      return callback(e);
    }
  }
  const engine = findEnginePath();
  if (!engine) return callback(new Error('sqt_engine_unified.py not found'));
  const python = getConfig().get('pythonPath') || 'python';
  const cwd = path.dirname(engine);
  execFile(python, [engine, '--json', '--bundle', '--compact'], { cwd, timeout: 5000 }, (err, stdout) => {
    if (err) return callback(err);
    try {
      const data = JSON.parse(stdout);
      cache = { data, at: now };
      callback(null, data);
    } catch (e) {
      callback(e);
    }
  });
}

function formatStatus(data) {
  const s = data.sqt || {};
  const h = data.holiday;
  const ext = data._extended?.sqt_full;
  const lun = ext?.lunation_name || `L${s.lunation}`;
  const day = ext?.day_name || `D${s.day}`;
  const hol = h ? ` · ${h.name.split(' ')[0]}` : '';
  return `$(squirrel) Y${s.year} ${lun} · ${day}${hol}`;
}

function formatTooltip(data) {
  const s = data.sqt || {};
  const h = data.holiday;
  const b = data.bundle || {};
  const lines = [
    `**SQT** Year ${s.year}, Lunation ${s.lunation}, Day ${s.day}`,
    `**Time** ${s.time || '—'}`,
  ];
  if (h) lines.push(`**Holiday** ${h.name} (${h.type})`);
  if (b.foraging_idea) lines.push(`_Forage:_ ${b.foraging_idea}`);
  return new vscode.MarkdownString(lines.join('\n'));
}

function formatInsert(data) {
  const s = data.sqt || {};
  const h = data.holiday;
  const b = data.bundle || {};
  const fmt = getConfig().get('insertFormat') || 'markdown';
  if (fmt === 'comment-block') {
    const j = (b.journal_prompt || '').replace(/\n/g, ' ').slice(0, 120);
    return [
      `// ═══ SQT Grove · ${h?.name || 'Grove Day'} · Y${s.year} L${s.lunation} D${s.day} ═══`,
      `// Journal: ${j}`,
      `// Forage: ${b.foraging_idea || ''}`,
      `// ═══`,
      '',
    ].join('\n');
  }
  return [
    `<!-- sqt-grove: Y${s.year}-L${s.lunation}-D${s.day} -->`,
    `## Messenger's Circuit — ${h?.name || 'Grove Day'}`,
    `*Year ${s.year}, Lunation ${s.lunation}, Day ${s.day} · ${s.time}*`,
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
    '### Art Prompt',
    b.art_prompt || '',
    '',
  ].join('\n');
}

function refreshStatusBar() {
  fetchCircuit((err, data) => {
    if (err || !statusItem) {
      if (statusItem) {
        statusItem.text = '$(error) SQT offline';
        statusItem.tooltip = String(err);
      }
      return;
    }
    statusItem.text = formatStatus(data);
    statusItem.tooltip = formatTooltip(data);
  });
}

function activate(context) {
  statusItem = vscode.window.createStatusBarItem(vscode.StatusBarAlignment.Right, 50);
  statusItem.command = 'sqt-grove.insertBundle';
  statusItem.show();
  refreshStatusBar();
  const interval = setInterval(refreshStatusBar, CACHE_MS);

  context.subscriptions.push(
    statusItem,
    { dispose: () => clearInterval(interval) },
    vscode.commands.registerCommand('sqt-grove.refresh', refreshStatusBar),
    vscode.commands.registerCommand('sqt-grove.insertBundle', () => {
      fetchCircuit((err, data) => {
        if (err) return vscode.window.showErrorMessage(String(err));
        const ed = vscode.window.activeTextEditor;
        if (!ed) return;
        ed.edit((eb) => eb.insert(ed.selection.active, formatInsert(data)));
      });
    }),
    vscode.commands.registerCommand('sqt-grove.insertForage', () => {
      fetchCircuit((err, data) => {
        if (err) return vscode.window.showErrorMessage(String(err));
        const ed = vscode.window.activeTextEditor;
        if (!ed) return;
        const line = (data.bundle?.foraging_idea || '') + '\n';
        ed.edit((eb) => eb.insert(ed.selection.active, line));
      });
    }),
  );
}

function deactivate() {}

module.exports = { activate, deactivate };