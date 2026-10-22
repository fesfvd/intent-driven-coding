/**
 * Byte-level parity against the Python reference implementation.
 *
 * Requires IDC_PYTHON (defaults to the LAS virtualenv interpreter) and a
 * checkout of idc_core (defaults to this repository root). LAS is optional:
 * set IDC_PARITY_PROJECTS as a `;`-separated list to override the projects.
 */

import assert from 'node:assert/strict';
import { execFileSync } from 'node:child_process';
import fs from 'node:fs';
import os from 'node:os';
import path from 'node:path';
import test from 'node:test';
import { fileURLToPath } from 'node:url';

import { readEvents } from '../src/core/events.js';
import { foldEvents } from '../src/core/fold.js';
import { renderCard } from '../src/core/render.js';
import { evaluateObligations } from '../src/core/gates.js';
import { rebuildIndex } from '../src/core/task-index.js';

const here = path.dirname(fileURLToPath(import.meta.url));
const repoRoot = path.resolve(here, '..', '..');
const pluginRoot = path.resolve(here, '..');
const python = process.env.IDC_PYTHON ?? 'D:\\LAS 5.2.3\\.venv\\Scripts\\python.exe';
const NOW = '2026-10-18T00:00:00+00:00';
const TARGETS = ['shaped', 'active', 'validating', 'build', 'completed', 'ship'];
const PROJECTS = (process.env.IDC_PARITY_PROJECTS
  ? process.env.IDC_PARITY_PROJECTS.split(';')
  : [repoRoot, 'D:\\LAS 5.2.3']
).filter((value) => value && fs.existsSync(path.join(value, '.idc')));

test('JS projections match the Python reference byte for byte', { timeout: 300_000 }, () => {
  assert.ok(PROJECTS.length > 0, 'no IDC project available for parity');
  assert.ok(fs.existsSync(python), `Python interpreter not found: ${python}`);
  const temporary = fs.mkdtempSync(path.join(os.tmpdir(), 'idc-parity-'));
  const output = path.join(temporary, 'oracle.json');
  try {
    execFileSync(
      python,
      [
        path.join(pluginRoot, 'test', 'oracle.py'),
        '--now',
        NOW,
        '--out',
        output,
        ...PROJECTS.flatMap((project) => ['--project', project]),
      ],
      { env: { ...process.env, PYTHONPATH: repoRoot, PYTHONDONTWRITEBYTECODE: '1' }, stdio: 'pipe' },
    );
    const oracle = JSON.parse(fs.readFileSync(output, 'utf8'));
    const now = new Date(NOW);
    for (const [index, project] of PROJECTS.entries()) {
      const data = oracle.projects[index].data;
      assert.equal(data.records.length > 0, true, `${project}: oracle returned no records`);
      assert.equal(data.index.records ? true : false, true, `${project}: oracle returned no index`);

      const diskRecords = fs
        .readdirSync(path.join(project, '.idc', 'work-items'), { withFileTypes: true })
        .filter((entry) => entry.isDirectory())
        .map((entry) => entry.name)
        .sort();
      assert.deepEqual(
        diskRecords,
        data.records.map((record) => record.record_id),
        `${project}: record set differs`,
      );

      for (const reference of data.records) {
        const events = readEvents(project, reference.record_id);
        if (reference.error) {
          // The Python reference rejects this record (for example a free-form
          // impact level). Parity means the port rejects it as well.
          assert.throws(() => {
            const state = foldEvents(events, { now });
            renderCard(state);
            for (const target of TARGETS) evaluateObligations(state, target);
          }, `${project}/${reference.record_id}: expected the reference rejection to be mirrored`);
          continue;
        }
        const state = foldEvents(events, { now });
        const normalizedState = { ...state, conditions: [...state.conditions].sort() };
        assert.deepEqual(normalizedState, reference.state, `${project}/${reference.record_id}: state`);
        assert.equal(renderCard(state), reference.card, `${project}/${reference.record_id}: card`);
        for (const target of TARGETS) {
          assert.deepEqual(
            evaluateObligations(state, target),
            reference.gates[target],
            `${project}/${reference.record_id}: gates ${target}`,
          );
        }
      }

      const copy = path.join(temporary, `index-${index}`);
      fs.mkdirSync(path.join(copy, '.idc'), { recursive: true });
      fs.cpSync(path.join(project, '.idc', 'work-items'), path.join(copy, '.idc', 'work-items'), {
        recursive: true,
      });
      const built = rebuildIndex(copy);
      assert.deepEqual(built, data.index, `${project}: rebuilt index`);
    }
  } finally {
    fs.rmSync(temporary, { recursive: true, force: true });
  }
});
