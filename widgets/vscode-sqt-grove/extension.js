const vscode = require('vscode');
const { execFile } = require('child_process');
const fs = require('fs');
const path = require('path');
const { formatInsert, formatStatus, formatTooltipLines } = require('./vscode-format');

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

function formatTooltip(data) {
  const lines = formatTooltipLines(data);
  lines.push('', '[Insert Full Bundle](command:sqt-grove.insertBundle)');
  return new vscode.MarkdownString(lines.join('\n'));
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
        const fmt = getConfig().get('insertFormat') || 'markdown';
        ed.edit((eb) => eb.insert(ed.selection.active, formatInsert(data, fmt)));
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