/**
 * Rebuildable task index, ported from idc_core/task_index.py.
 *
 * The index is a cache: it never overrides event history, and a stale index is
 * reported as incomplete rather than trusted silently.
 */

import fs from 'node:fs';
import path from 'node:path';
import crypto from 'node:crypto';

import { pyJsonPretty, pythonRound, splitLines } from './py.js';

export const INDEX_VERSION = 1;

export function indexPath(project) {
  return path.join(path.resolve(project), '.idc', 'index', 'tasks.json');
}

export function loadIndex(project) {
  const file = indexPath(project);
  let text;
  try {
    text = fs.readFileSync(file, 'utf8');
  } catch {
    return null;
  }
  let value;
  try {
    value = JSON.parse(text);
  } catch {
    return null;
  }
  if (!value || typeof value !== 'object' || value.version !== INDEX_VERSION) return null;
  if (!value.records || typeof value.records !== 'object' || Array.isArray(value.records)) return null;
  return value;
}

export function saveIndex(project, index) {
  const file = indexPath(project);
  fs.mkdirSync(path.dirname(file), { recursive: true });
  const temporary = path.join(
    path.dirname(file),
    `tasks-${crypto.randomBytes(8).toString('hex')}.json`,
  );
  try {
    const handle = fs.openSync(temporary, 'w', 0o666);
    try {
      fs.writeFileSync(handle, pyJsonPretty(index) + '\n', 'utf8');
      fs.fsyncSync(handle);
    } finally {
      fs.closeSync(handle);
    }
    fs.renameSync(temporary, file);
  } finally {
    if (fs.existsSync(temporary)) fs.unlinkSync(temporary);
  }
}

export function emptyIndex() {
  return { version: INDEX_VERSION, records: {} };
}

export function updateIndex(project, event) {
  const index = loadIndex(project) ?? emptyIndex();
  const recordId = event.record_id;
  if (!index.records[recordId]) index.records[recordId] = emptyRecord(recordId);
  applyEvent(index.records[recordId], event);
  saveIndex(project, index);
}

export function rebuildIndex(project) {
  const index = emptyIndex();
  const root = path.join(path.resolve(project), '.idc', 'work-items');
  let entries = [];
  try {
    entries = fs.readdirSync(root, { withFileTypes: true });
  } catch {
    entries = [];
  }
  const files = entries
    .filter((entry) => entry.isDirectory())
    .map((entry) => path.join(root, entry.name, 'events.jsonl'))
    .filter((file) => fs.existsSync(file))
    .sort();
  for (const file of files) {
    let text;
    try {
      text = fs.readFileSync(file, 'utf8');
    } catch {
      continue;
    }
    for (const line of splitLines(text)) {
      if (!line.trim()) continue;
      let event;
      try {
        event = JSON.parse(line);
      } catch {
        continue;
      }
      if (!event || typeof event !== 'object') continue;
      const recordId = event.record_id;
      if (typeof recordId !== 'string') continue;
      if (!index.records[recordId]) index.records[recordId] = emptyRecord(recordId);
      applyEvent(index.records[recordId], event);
    }
  }
  saveIndex(project, index);
  return index;
}

export function getIndex(project) {
  return loadIndex(project) ?? rebuildIndex(project);
}

export function emptyRecord(recordId) {
  return {
    record_id: recordId,
    task_id: null,
    summary: '',
    lifecycle: 'captured',
    outcome: null,
    capture_mode: 'durable',
    capture_disposition: 'open',
    event_count: 0,
    event_types: {},
    first_event_at: null,
    last_event_at: null,
    promoted_at: null,
    closed_at: null,
    requirement_changes: 0,
    gate_blocks: 0,
    acceptance: [],
    passing_acceptance: [],
    manual_backfills: 0,
  };
}

export function applyEvent(record, event) {
  const eventType = event.type;
  const payload = event.payload && typeof event.payload === 'object' ? event.payload : {};
  const timestamp = event.timestamp;
  record.event_count += 1;
  record.event_types[String(eventType)] = (record.event_types[String(eventType)] ?? 0) + 1;
  if (record.first_event_at === null && typeof timestamp === 'string') record.first_event_at = timestamp;
  if (typeof timestamp === 'string') record.last_event_at = timestamp;
  if (eventType === 'request.captured') {
    record.summary = String(payload.summary ?? '');
    record.capture_mode = String(payload.capture_mode ?? 'durable');
  } else if (eventType === 'task.promoted') {
    record.task_id = payload.task_id ?? null;
    record.promoted_at = timestamp;
    record.capture_disposition = 'promoted';
    record.lifecycle = 'promoted';
  } else if (eventType === 'capture.discarded') {
    record.capture_disposition = 'discarded';
  } else if (eventType === 'capture.expired') {
    record.capture_disposition = 'expired';
  } else if (eventType === 'lifecycle.changed') {
    record.lifecycle = payload.to ?? record.lifecycle;
  } else if (eventType === 'task.closed') {
    record.lifecycle = 'closed';
    record.outcome = payload.outcome ?? null;
    record.closed_at = timestamp;
  } else if (eventType === 'requirement.changed') {
    record.requirement_changes += 1;
  } else if (eventType === 'acceptance.changed') {
    record.acceptance = Array.isArray(payload.to) ? [...payload.to] : [];
  } else if (eventType === 'evidence.recorded' && payload.result === 'pass') {
    record.passing_acceptance = [
      ...new Set([...(record.passing_acceptance ?? []), ...(payload.acceptance_ids ?? [])]),
    ].sort();
  } else if (eventType === 'legacy.snapshot-imported') {
    record.manual_backfills += 1;
  }
  if (['gate.blocked', 'obligation.blocked', 'check.blocked'].includes(eventType)) {
    record.gate_blocks += 1;
  } else if (Array.isArray(payload.hard_blocks)) {
    record.gate_blocks += payload.hard_blocks.length;
  }
}

export function recordMetrics(record) {
  const acceptance = record.acceptance ?? [];
  const passing = new Set(record.passing_acceptance ?? []);
  return {
    record_id: record.record_id,
    task_id: record.task_id,
    summary: record.summary,
    lifecycle: record.lifecycle,
    outcome: record.outcome,
    capture_mode: record.capture_mode,
    capture_disposition: record.capture_disposition,
    event_count: record.event_count,
    event_types: Object.fromEntries(
      Object.entries(record.event_types ?? {}).sort(([a], [b]) => (a < b ? -1 : a > b ? 1 : 0)),
    ),
    requirement_changes: record.requirement_changes,
    gate_blocks: record.gate_blocks,
    first_event_at: record.first_event_at,
    last_event_at: record.last_event_at,
    promoted_at: record.promoted_at,
    closed_at: record.closed_at,
    acceptance_count: acceptance.length,
    uncompleted_acceptance: acceptance.filter((item) => !passing.has(item?.id)).length,
    capture_to_promote_hours: elapsedHours(record.first_event_at, record.promoted_at),
    manual_backfills: record.manual_backfills,
  };
}

function elapsedHours(start, end) {
  if (!start || !end) return null;
  const startTime = Date.parse(start);
  const endTime = Date.parse(end);
  if (!Number.isFinite(startTime) || !Number.isFinite(endTime)) return null;
  return pythonRound((endTime - startTime) / 3600_000, 3);
}
