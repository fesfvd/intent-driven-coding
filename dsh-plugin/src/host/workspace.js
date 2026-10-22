/** Workspace resolution and read-only projections shared by the host plugin. */

import fs from 'node:fs';
import path from 'node:path';

import { evaluateObligations } from '../core/gates.js';
import { foldEvents } from '../core/fold.js';
import { loadConfig, readRecord, countWorkItems } from '../core/events.js';
import { renderCard } from '../core/render.js';
import { getIndex } from '../core/task-index.js';
import { checkLearningCadence } from '../core/learning.js';

export const MAX_RECORDS = 25;
export const MAX_CARD_CHARS = 12_000;

export function sessionCwd(exec) {
  const cwd = exec?.agent?.session?.header?.cwd;
  return typeof cwd === 'string' && cwd !== '' ? cwd : null;
}

export function findIdcRoot(start) {
  if (typeof start !== 'string' || start === '') return null;
  let directory = path.resolve(start);
  for (;;) {
    try {
      if (fs.statSync(path.join(directory, '.idc')).isDirectory()) return directory;
    } catch {
      // Keep walking up.
    }
    const parent = path.dirname(directory);
    if (parent === directory) return null;
    directory = parent;
  }
}

export function resolveWorkspace(exec) {
  const cwd = sessionCwd(exec);
  if (!cwd) {
    throw new Error('IDC requires an owning agent session with a working directory');
  }
  const project = findIdcRoot(cwd);
  return { cwd, project };
}

export function requireWorkspace(exec) {
  const { cwd, project } = resolveWorkspace(exec);
  if (!project) {
    const error = new Error(
      `no .idc directory from ${cwd} upward; run idc_init in a project first`,
    );
    error.code = 'NO_IDC_CONTEXT';
    throw error;
  }
  return { cwd, project };
}

export function projectKeyOf(project) {
  const config = loadConfig(project);
  if (typeof config.project_key === 'string' && config.project_key !== '') {
    return config.project_key;
  }
  return path.basename(project).replace(/[^A-Za-z0-9]+/g, '').toUpperCase() || 'IDC';
}

export function listRecordIds(project) {
  const root = path.join(project, '.idc', 'work-items');
  let entries;
  try {
    entries = fs.readdirSync(root, { withFileTypes: true });
  } catch {
    return [];
  }
  return entries
    .filter((entry) => entry.isDirectory())
    .map((entry) => ({
      recordId: entry.name,
      eventsPath: path.join(root, entry.name, 'events.jsonl'),
    }))
    .filter((entry) => {
      try {
        return fs.statSync(entry.eventsPath).isFile();
      } catch {
        return false;
      }
    })
    .map((entry) => {
      let mtime = 0;
      try {
        mtime = fs.statSync(entry.eventsPath).mtimeMs;
      } catch {
        // Ignore an unreadable record.
      }
      return { record_id: entry.recordId, mtime };
    })
    .sort((a, b) => b.mtime - a.mtime);
}

export function resolveRecordRef(project, ref) {
  const value = String(ref ?? '').trim();
  if (value === '') return null;
  if (/^work-/.test(value)) {
    const eventsPath = path.join(project, '.idc', 'work-items', value, 'events.jsonl');
    return fs.existsSync(eventsPath) ? value : null;
  }
  for (const record of listRecordIds(project)) {
    try {
      const events = readRecord(project, record.record_id);
      const promoted = events.find((event) => event.type === 'task.promoted');
      if (promoted?.payload?.task_id === value) return record.record_id;
    } catch {
      // Keep looking.
    }
  }
  return null;
}

export function nextTarget(lifecycle) {
  switch (lifecycle) {
    case 'captured':
    case 'promoted':
      return 'shaped';
    case 'shaped':
      return 'active';
    case 'active':
    case 'validating':
      return 'completed';
    default:
      return null;
  }
}

export function acceptanceStatus(state) {
  const evidence = state.evidence ?? [];
  return (state.acceptance ?? []).map((item) => ({
    id: String(item.id),
    statement: String(item.statement),
    passing: evidence.some(
      (entry) =>
        entry.result === 'pass' && (entry.acceptance_ids ?? []).includes(String(item.id)),
    ),
  }));
}

export function coverage(project) {
  const onDisk = countWorkItems(project);
  const index = getIndex(project);
  if (!index) {
    return {
      records_on_disk: onDisk,
      index_records: null,
      coverage: 'unverified',
      note: 'no index cache; record count is a filesystem lower bound',
    };
  }
  const indexed = Object.keys(index.records ?? {}).length;
  return {
    records_on_disk: onDisk,
    index_records: indexed,
    coverage: indexed === onDisk ? 'complete' : 'incomplete',
    note:
      indexed === onDisk
        ? 'index and disk agree'
        : 'index is stale; rebuild with idc_status (read path never rewrites it)',
  };
}

export function recordSummary(project, recordId, now) {
  const events = readRecord(project, recordId);
  const state = foldEvents(events, { now });
  const target = nextTarget(state.lifecycle);
  const evaluation = target ? evaluateObligations(state, target) : null;
  return {
    record_id: recordId,
    task_id: state.task_id ?? null,
    lifecycle: state.lifecycle,
    outcome: state.outcome ?? null,
    summary: truncate(state.summary ?? '', 140),
    goal: truncate(state.goal ?? '', 200),
    capture_disposition: state.capture_disposition,
    open_decisions: state.open_decisions.length,
    acceptance: acceptanceStatus(state),
    next_target: target,
    hard_blocks: evaluation ? [...evaluation.hard_blocks] : [],
    warnings: evaluation ? [...evaluation.warnings] : [],
    updated_at: events.length ? events[events.length - 1].timestamp : null,
  };
}

export function statusOverview(project, options = {}) {
  const now = options.now ?? new Date();
  const learning = safeLearning(project, now);
  const records = [];
  for (const record of listRecordIds(project)) {
    if (records.length >= MAX_RECORDS) break;
    try {
      records.push(recordSummary(project, record.record_id, now));
    } catch (error) {
      records.push({
        record_id: record.record_id,
        error: error instanceof Error ? error.message : String(error),
      });
    }
  }
  const total = countWorkItems(project);
  return {
    code: 'OK',
    project,
    project_key: projectKeyOf(project),
    idc_version: loadConfig(project).idc_version ?? null,
    ...coverage(project),
    learning,
    records,
    truncated: total > records.length,
    total_records: total,
  };
}

export function recordDetail(project, recordId, options = {}) {
  const now = options.now ?? new Date();
  const events = readRecord(project, recordId);
  const state = foldEvents(events, { now });
  const target = nextTarget(state.lifecycle);
  const evaluation = target ? evaluateObligations(state, target) : null;
  const card = renderCard(state);
  return {
    code: 'OK',
    project,
    record: {
      record_id: recordId,
      task_id: state.task_id,
      lifecycle: state.lifecycle,
      outcome: state.outcome,
      summary: state.summary,
      goal: state.goal,
      explicit: state.explicit,
      scope: state.scope,
      acceptance: acceptanceStatus(state),
      open_decisions: state.open_decisions,
      uncertainty: state.uncertainty,
      classifications: state.classifications,
      impacts: state.impacts,
      activities: state.activities,
      evidence: state.evidence.map((entry) => ({
        kind: entry.kind,
        result: entry.result,
        acceptance_ids: entry.acceptance_ids,
        summary: truncate(entry.summary ?? '', 200),
        reference: entry.reference ?? null,
        failure_attribution: entry.failure_attribution ?? null,
      })),
      obligations: {
        target,
        hard_blocks: evaluation ? [...evaluation.hard_blocks] : [],
        warnings: evaluation ? [...evaluation.warnings] : [],
        explanations: evaluation ? { ...evaluation.explanations } : {},
      },
      card: truncate(card, MAX_CARD_CHARS),
      card_truncated: card.length > MAX_CARD_CHARS,
      card_path: state.task_id
        ? path.join(project, '.idc', 'tasks', `${state.task_id}.md`)
        : path.join(project, '.idc', 'work-items', recordId, 'CARD.md'),
      event_count: events.length,
    },
  };
}

export function latestRecordId(project) {
  const records = listRecordIds(project);
  return records.length ? records[0].record_id : null;
}

export function statusLine(project, now = new Date()) {
  const recordId = latestRecordId(project);
  if (!recordId) return 'IDC: no task records yet; use idc_start.';
  try {
    const summary = recordSummary(project, recordId, now);
    const task = summary.task_id ?? summary.record_id;
    const blocks = summary.hard_blocks.length ? ` · blocked: ${summary.hard_blocks.join(', ')}` : '';
    const next = summary.next_target ? ` · next: ${summary.next_target}` : '';
    return `IDC: ${task} ${summary.lifecycle}${next}${blocks}`;
  } catch {
    return 'IDC: latest record is unreadable; call idc_status.';
  }
}

export function safeLearning(project, now = new Date()) {
  try {
    return checkLearningCadence(project, { now });
  } catch (error) {
    return { status: 'unknown', reason: error instanceof Error ? error.message : String(error) };
  }
}

export function truncate(text, limit) {
  const value = String(text ?? '');
  return value.length > limit ? `${value.slice(0, limit - 1)}…` : value;
}
