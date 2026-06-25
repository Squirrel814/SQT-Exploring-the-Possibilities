/**
 * VS Code extension smoke — uses real static feeds (no vscode API).
 * Simulates F5 path: load circuit JSON → formatStatus / formatInsert.
 */
import assert from 'node:assert/strict';
import { readFileSync } from 'node:fs';
import { createRequire } from 'node:module';
import { dirname, join } from 'node:path';
import { fileURLToPath } from 'node:url';
import { execFileSync } from 'node:child_process';

const __dirname = dirname(fileURLToPath(import.meta.url));
const ROOT = join(__dirname, '..');
const require = createRequire(import.meta.url);
const { formatInsert, formatStatus, statusIcon } = require(
  join(ROOT, 'widgets/vscode-sqt-grove/vscode-format.js'),
);

const circuitPath = join(ROOT, 'docs/circuit-current.json');
const circuit = JSON.parse(readFileSync(circuitPath, 'utf8'));

assert.ok(circuit.sqt, 'circuit-current.json must include sqt');
assert.ok(circuit.bundle?.journal_prompt, 'bundle journal_prompt required');

const status = formatStatus(circuit);
assert.match(status, /^\$\((squirrel|star-full)\) Y\d+/);
assert.match(formatInsert(circuit, 'markdown'), /Messenger's Circuit/);

const majorStdout = execFileSync(
  process.platform === 'win32' ? 'python' : 'python3',
  [
    join(ROOT, 'sqt_engine_unified.py'),
    '--json',
    '--compact',
    '--bundle',
    '--simulate-lunation',
    '6',
    '--simulate-day',
    '19',
    '--holidays',
    join(ROOT, 'sqt-holidays.sample.json'),
    '--themes',
    join(ROOT, 'sqt-themes.sample.json'),
  ],
  { cwd: ROOT, encoding: 'utf8', timeout: 8000 },
);
const major = JSON.parse(majorStdout);
assert.equal(statusIcon(major.holiday), '$(star-full)');
assert.match(formatStatus(major), /^\$\(star-full\)/);
assert.match(formatInsert(major, 'comment-block'), /^\/\/ Ceremonial:/m);

console.log('vscode extension smoke: ok');