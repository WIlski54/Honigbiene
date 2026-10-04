import test from 'node:test';
import assert from 'node:assert/strict';
import { execFileSync, spawnSync } from 'node:child_process';
import { mkdtempSync, writeFileSync, openSync, ftruncateSync, closeSync, rmSync } from 'node:fs';
import { tmpdir } from 'node:os';
import { join } from 'node:path';
import { fileURLToPath } from 'node:url';

const script = fileURLToPath(new URL('../scripts/check-repository.mjs', import.meta.url));
function repository(t) {
  const cwd = mkdtempSync(join(tmpdir(), 'honigbiene-repo-test-'));
  t.after(() => rmSync(cwd, { recursive: true, force: true }));
  execFileSync('git', ['init', '--quiet'], { cwd });
  return cwd;
}
function check(cwd) {
  return spawnSync(process.execPath, [script], { cwd, encoding: 'utf8' });
}

test('repository check accepts a placeholder environment example', t => {
  const cwd = repository(t);
  writeFileSync(join(cwd, '.env.example'), 'SECRET_KEY=BITTE-ERSETZEN\n');
  const result = check(cwd);
  assert.equal(result.status, 0, result.stderr);
});

test('repository check rejects environment files and databases', t => {
  const cwd = repository(t);
  writeFileSync(join(cwd, '.env'), 'SECRET_KEY=private\n');
  writeFileSync(join(cwd, 'student.db'), 'database');
  const result = check(cwd);
  assert.equal(result.status, 1);
  assert.match(result.stderr, /\.env:/);
  assert.match(result.stderr, /student\.db:/);
});

test('repository check detects known tokens without printing them', t => {
  const cwd = repository(t);
  const token = 'ghp_' + 'a'.repeat(36);
  writeFileSync(join(cwd, 'config.js'), `const token = '${token}';`);
  const result = check(cwd);
  assert.equal(result.status, 1);
  assert.match(result.stderr, /config\.js:/);
  assert.ok(!`${result.stdout}${result.stderr}`.includes(token));
});

test('repository check rejects exports larger than 100 MiB', t => {
  const cwd = repository(t);
  const fd = openSync(join(cwd, 'export.bin'), 'w');
  try { ftruncateSync(fd, 100 * 1024 * 1024 + 1); } finally { closeSync(fd); }
  const result = check(cwd);
  assert.equal(result.status, 1);
  assert.match(result.stderr, /export\.bin:.*100 MiB/);
});
