/** Host-surface tests with a fake tool registry and session header. */

import assert from 'node:assert/strict';
import fs from 'node:fs';
import os from 'node:os';
import path from 'node:path';
import test from 'node:test';

import { registerTools } from '../src/host/tools.js';
import { parseSkill } from '../src/host/skills.js';

function fakeHost() {
  const tools = new Map();
  registerTools({ tools: { register: (definition) => tools.set(definition.name, definition) } });
  return tools;
}

function execAt(cwd) {
  return { agent: { session: { header: { cwd } } } };
}

async function call(tools, name, args, cwd) {
  const definition = tools.get(name);
  assert.ok(definition, `tool ${name} is registered`);
  return definition.execute(args, execAt(cwd));
}

test('the full task lifecycle is reachable through the tools', async () => {
  const root = fs.mkdtempSync(path.join(os.tmpdir(), 'idc-host-'));
  const project = path.join(root, 'project');
  fs.mkdirSync(path.join(project, 'src'), { recursive: true });
  const tools = fakeHost();
  try {
    const missing = await call(tools, 'idc_status', {}, project);
    assert.equal(missing.code, 'NO_IDC_CONTEXT');

    const initialized = await call(tools, 'idc_init', { project_key: 'TST' }, project);
    assert.equal(initialized.code, 'CREATED');
    assert.equal(
      JSON.parse(fs.readFileSync(path.join(project, '.idc', 'config.json'), 'utf8')).idc_version,
      '1.2.0',
    );

    const started = await call(
      tools,
      'idc_start',
      { summary: 'Add a widget', scene: 'FEAT' },
      path.join(project, 'src'),
    );
    assert.equal(started.code, 'CAPTURED');
    const recordId = /work-[a-z0-9-]+/.exec(started.text)?.[0];
    assert.ok(recordId);
    const eventsPath = path.join(project, '.idc', 'work-items', recordId, 'events.jsonl');
    const before = fs.readFileSync(eventsPath, 'utf8').trim().split('\n').length;

    const blocked = await call(tools, 'idc_transition', { record_id: recordId, target: 'active' }, project);
    assert.equal(blocked.code, 'GATE_BLOCKED');
    assert.match(blocked.text, /shape:required/);
    assert.equal(fs.readFileSync(eventsPath, 'utf8').trim().split('\n').length, before, 'no event written');

    const promoted = await call(tools, 'idc_promote', { record_id: recordId }, project);
    assert.equal(promoted.code, 'PROMOTED');
    const taskId = /IDC-[A-Z0-9]+-\d{8}-\d{3}/.exec(promoted.text)?.[0];
    assert.ok(taskId);

    const shaped = await call(
      tools,
      'idc_shape',
      {
        record_id: taskId,
        goal: 'Ship the widget',
        scope: ['src/'],
        acceptance: [{ id: 'a1', statement: 'widget renders' }],
        classifications: ['FEAT'],
        uncertainty: ['cross-boundary'],
        external_effect: 'none',
        reversibility: 'low',
      },
      project,
    );
    assert.equal(shaped.code, 'SHAPED');

    const design = await call(tools, 'idc_record', { record_id: taskId, activity: 'design' }, project);
    assert.equal(design.code, 'RECORDED');
    const active = await call(tools, 'idc_transition', { record_id: taskId, target: 'active' }, project);
    assert.equal(active.code, 'TRANSITIONED');

    const premature = await call(tools, 'idc_close', { record_id: taskId, outcome: 'completed' }, project);
    assert.equal(premature.code, 'GATE_BLOCKED');
    assert.match(premature.text, /acceptance|evidence/i);

    const evidence = await call(
      tools,
      'idc_record',
      {
        record_id: taskId,
        evidence_kind: 'command-evidence',
        evidence_result: 'pass',
        evidence_summary: 'node --test',
        evidence_acceptance_ids: ['a1'],
        evidence_reference: 'node --test',
      },
      project,
    );
    assert.equal(evidence.code, 'RECORDED');

    const closed = await call(
      tools,
      'idc_close',
      { record_id: taskId, outcome: 'completed', summary: 'Shipped' },
      project,
    );
    assert.equal(closed.code, 'CLOSED');

    const detail = await call(tools, 'idc_status', { record_id: taskId }, project);
    assert.equal(detail.code, 'OK');
    assert.match(detail.text, /closed/);

    // Coverage must be honest when the index no longer matches the disk.
    const ghost = path.join(project, '.idc', 'work-items', 'work-20260101t000000z-deadbeef');
    fs.mkdirSync(ghost, { recursive: true });
    fs.writeFileSync(path.join(ghost, 'events.jsonl'), '');
    const stale = await call(tools, 'idc_status', {}, project);
    assert.equal(stale.code, 'INCOMPLETE_READ');
  } finally {
    fs.rmSync(root, { recursive: true, force: true });
  }
});

test('protocol mismatch is refused before writing', async () => {
  const root = fs.mkdtempSync(path.join(os.tmpdir(), 'idc-proto-'));
  const tools = fakeHost();
  try {
    fs.mkdirSync(path.join(root, '.idc'), { recursive: true });
    fs.writeFileSync(
      path.join(root, '.idc', 'config.json'),
      JSON.stringify({ schema_version: 2, idc_version: '1.1.0', project_key: 'OLD' }),
    );
    const result = await call(tools, 'idc_start', { summary: 'should not write' }, root);
    assert.equal(result.code, 'PROTOCOL_MISMATCH');
  } finally {
    fs.rmSync(root, { recursive: true, force: true });
  }
});

test('human-confirmed evidence needs an explicit confirmation', async () => {
  const root = fs.mkdtempSync(path.join(os.tmpdir(), 'idc-human-'));
  const tools = fakeHost();
  try {
    await call(tools, 'idc_init', { project_key: 'HUM' }, root);
    const started = await call(tools, 'idc_start', { summary: 'human gate' }, root);
    const recordId = /work-[a-z0-9-]+/.exec(started.text)?.[0];
    await call(tools, 'idc_promote', { record_id: recordId }, root);
    await call(
      tools,
      'idc_shape',
      { record_id: recordId, goal: 'g', scope: ['x'], acceptance: [{ id: 'a1', statement: 's' }] },
      root,
    );
    const refused = await call(
      tools,
      'idc_record',
      {
        record_id: recordId,
        evidence_kind: 'human-confirmed',
        evidence_result: 'pass',
        evidence_summary: 'user checked it',
        evidence_acceptance_ids: ['a1'],
        evidence_confirmation_ref: 'message 42',
      },
      root,
    );
    assert.equal(refused.code, 'INVALID_REQUEST');
    assert.match(refused.text, /human actor/i);
  } finally {
    fs.rmSync(root, { recursive: true, force: true });
  }
});

test('bundled skills parse and are kebab-case', () => {
  const root = path.resolve(import.meta.dirname, '..', 'assets', 'skills');
  const names = fs.readdirSync(root).filter((entry) => fs.statSync(path.join(root, entry)).isDirectory());
  assert.equal(names.length, 8);
  for (const name of names) {
    const parsed = parseSkill(fs.readFileSync(path.join(root, name, 'SKILL.md'), 'utf8'));
    assert.ok(parsed, `${name} has frontmatter`);
    assert.match(parsed.name, /^[a-z0-9]+(?:-[a-z0-9]+)*$/);
    assert.ok(parsed.description.length > 20);
    assert.ok(parsed.content.includes('idc_'), `${name} refers to idc_* tools`);
  }
});
