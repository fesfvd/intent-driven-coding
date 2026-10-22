/**
 * Write-path parity: the same workflow must produce the same events, card and
 * index under the Python reference implementation and this port.
 */

import assert from 'node:assert/strict';
import { execFileSync } from 'node:child_process';
import fs from 'node:fs';
import os from 'node:os';
import path from 'node:path';
import test from 'node:test';
import { fileURLToPath } from 'node:url';

import { Workflow } from '../src/core/workflow.js';
import { renderCard } from '../src/core/render.js';

const here = path.dirname(fileURLToPath(import.meta.url));
const repoRoot = path.resolve(here, '..', '..');
const pluginRoot = path.resolve(here, '..');
const python = process.env.IDC_PYTHON ?? 'D:\\LAS 5.2.3\\.venv\\Scripts\\python.exe';
const FIXED = new Date('2026-10-18T06:00:00+00:00');

function runJavaScript(project) {
  const workflow = new Workflow(project, { clock: () => new Date(FIXED) });
  const recordId = workflow.start('Port the IDC protocol', { scenes: ['META'] });
  const taskId = workflow.promote(recordId, 'IDC');
  workflow.shape(recordId, {
    goal: 'Port the IDC protocol to a DSH plugin',
    explicit: ['No Python runtime dependency'],
    scope: ['dsh-plugin/'],
    acceptance: [{ id: 'a1', statement: 'JS and Python produce the same card' }],
    classifications: ['META'],
    uncertainty: ['cross-boundary'],
    impacts: { external_effect: 'none', reversibility: 'low' },
    openDecisions: ['d1', 'd2'],
  });
  workflow.resolveDecision(recordId, { decision: 'd1', resolution: 'Native port' });
  workflow.resolveDecision(recordId, { decision: 'd2', resolution: 'Single writer' });
  workflow.recordActivity(recordId, 'design');
  workflow.transition(recordId, 'active');
  workflow.recordActivity(recordId, 'build');
  workflow.addEvidence(recordId, {
    kind: 'command-evidence',
    summary: 'node --test test/parity.test.mjs',
    result: 'pass',
    acceptanceIds: ['a1'],
    reference: 'test/parity.test.mjs',
  });
  workflow.recordActivity(recordId, 'verify');
  workflow.transition(recordId, 'validating');
  workflow.close(recordId, { outcome: 'completed', summary: 'Parity recorded' });
  workflow.reviewLearning(recordId, { outcome: 'none', reason: 'No reusable lesson' });
  const state = workflow.state(recordId);
  return {
    record_id: recordId,
    task_id: taskId,
    events: fs
      .readFileSync(path.join(project, '.idc', 'work-items', recordId, 'events.jsonl'), 'utf8')
      .split('\n')
      .filter((line) => line.trim() !== '')
      .map((line) => JSON.parse(line)),
    card: renderCard(state),
    index: JSON.parse(fs.readFileSync(path.join(project, '.idc', 'index', 'tasks.json'), 'utf8')),
  };
}

function normalize(value, recordId) {
  return JSON.parse(
    JSON.stringify(value).split(recordId).join('<record>'),
  );
}

test('JS and Python write paths agree', { timeout: 120_000 }, () => {
  assert.ok(fs.existsSync(python), `Python interpreter not found: ${python}`);
  const root = fs.mkdtempSync(path.join(os.tmpdir(), 'idc-write-'));
  const jsProject = path.join(root, 'js');
  const pyProject = path.join(root, 'py');
  fs.mkdirSync(jsProject);
  fs.mkdirSync(pyProject);
  try {
    const js = runJavaScript(jsProject);
    const reference = JSON.parse(
      execFileSync(python, [path.join(pluginRoot, 'test', 'scenario.py'), pyProject], {
        env: { ...process.env, PYTHONPATH: repoRoot, PYTHONDONTWRITEBYTECODE: '1' },
        encoding: 'utf8',
        maxBuffer: 16 * 1024 * 1024,
      }),
    );
    assert.equal(js.task_id, reference.task_id);
    assert.deepEqual(normalize(js.events, js.record_id), normalize(reference.events, reference.record_id));
    assert.equal(js.card, reference.card);
    assert.deepEqual(normalize(js.index, js.record_id), normalize(reference.index, reference.record_id));

    // Interoperability: the reference core must fold and render the JS-written log.
    const reread = JSON.parse(
      execFileSync(python, [path.join(pluginRoot, 'test', 'render.py'), jsProject, js.record_id], {
        env: { ...process.env, PYTHONPATH: repoRoot, PYTHONDONTWRITEBYTECODE: '1' },
        encoding: 'utf8',
        maxBuffer: 16 * 1024 * 1024,
      }),
    );
    assert.equal(reread.card, js.card);
    assert.equal(reread.lifecycle, 'closed');

    const provisional = path.join(jsProject, '.idc', 'tasks', `${js.task_id}.md`);
    assert.equal(fs.readFileSync(provisional, 'utf8'), reference.card);
    assert.equal(fs.existsSync(path.join(jsProject, '.idc', 'work-items', js.record_id, 'CARD.md')), false);
  } finally {
    fs.rmSync(root, { recursive: true, force: true });
  }
});
