/**
 * IDC event store (protocol v2), ported from idc_core/events.py.
 *
 * Single-writer note: the Python implementation takes an OS file lock on
 * `.events.lock`. Node has no portable advisory locking primitive, so this
 * port serialises writes inside one process and documents that the plugin
 * must not write concurrently with the Python CLI. Reads and appends are
 * still validated against the same invariants.
 */

import fs from 'node:fs';
import path from 'node:path';
import crypto from 'node:crypto';

import { isoformat, parseIsoformat, pyJsonDumps, splitLines } from './py.js';
import { updateIndex } from './task-index.js';

export const EVENT_SCHEMA_VERSION = 2;
export const TASK_ID_RE = /^IDC-([A-Z][A-Z0-9]*)-(\d{8})-(\d{3})$/;
export const RECORD_ID_RE = /^work-[a-z0-9-]+$/;
export const CORE_EVENT_TYPES = new Set([
  'request.captured',
  'task.promoted',
  'intent.translated',
  'scope.changed',
  'acceptance.changed',
  'classification.changed',
  'uncertainty.changed',
  'impact.assessed',
  'lifecycle.changed',
  'requirement.changed',
  'condition.changed',
  'activity.recorded',
  'decision.resolved',
  'evidence.recorded',
  'check.omitted',
  'permission.requested',
  'permission.granted',
  'permission.rejected',
  'permission.executed',
  'recovery.recorded',
  'task.closed',
  'learn.candidate',
  'learn.reviewed',
  'learn.disposed',
  'legacy.snapshot-imported',
  'capture.discarded',
  'capture.expired',
]);
export const PROVENANCE_TYPES = new Set([
  'claimed',
  'host-observed',
  'command-evidence',
  'artifact-evidence',
  'human-confirmed',
  'reconstructed',
]);

export const PROTOCOL_MISMATCH =
  'IDC protocol mismatch; writes are disabled. Run `idc migrate --check`, ' +
  'review the report, then confirm migration.';

export function configPath(project) {
  return path.join(path.resolve(project), '.idc', 'config.json');
}

/** Read `.idc/config.json`; returns null when absent. Throws on malformed JSON. */
export function loadConfig(project) {
  const file = configPath(project);
  let text;
  try {
    text = fs.readFileSync(file, 'utf8');
  } catch (error) {
    if (error && error.code === 'ENOENT') return null;
    throw new Error(`cannot validate IDC protocol config: ${file}`);
  }
  try {
    const value = JSON.parse(text);
    return value && typeof value === 'object' && !Array.isArray(value) ? value : {};
  } catch {
    throw new Error(`cannot validate IDC protocol config: ${file}`);
  }
}

export function isWriteCompatible(config) {
  return !config || (config.schema_version === 2 && config.idc_version === '1.2.0');
}

export function workItemsRoot(project) {
  return path.join(path.resolve(project), '.idc', 'work-items');
}

/** Count direct child directories of `.idc/work-items` (coverage lower bound). */
export function countWorkItems(project) {
  const root = workItemsRoot(project);
  let entries;
  try {
    entries = fs.readdirSync(root, { withFileTypes: true });
  } catch (error) {
    if (error && error.code === 'ENOENT') return 0;
    throw error;
  }
  return entries.filter((entry) => entry.isDirectory()).length;
}

function recordStamp(date) {
  const pad = (value) => String(value).padStart(2, '0');
  return (
    `${date.getUTCFullYear()}${pad(date.getUTCMonth() + 1)}${pad(date.getUTCDate())}` +
    `t${pad(date.getUTCHours())}${pad(date.getUTCMinutes())}${pad(date.getUTCSeconds())}z`
  ).toLowerCase();
}

function osErrorOnly(error) {
  return Boolean(error && typeof error.code === 'string');
}

export class EventStore {
  constructor(project, clock = () => new Date()) {
    this.project = path.resolve(project);
    this.clock = clock;
    this.recordsRoot = workItemsRoot(this.project);
  }

  capture(summary, actor = 'agent', options = {}) {
    const { temporary = false, ttlHours = 72 } = options;
    if (typeof summary !== 'string' || summary.trim() === '') {
      throw new Error('summary must not be empty');
    }
    if (temporary && (!Number.isInteger(ttlHours) || ttlHours <= 0)) {
      throw new Error('ttl_hours must be a positive integer');
    }
    const now = this.now();
    const recordId = `work-${recordStamp(now)}-${crypto.randomBytes(4).toString('hex')}`;
    const recordPath = path.join(this.recordsRoot, recordId);
    fs.mkdirSync(this.recordsRoot, { recursive: true });
    fs.mkdirSync(recordPath);
    this.append(
      recordId,
      'request.captured',
      {
        summary: summary.trim(),
        capture_mode: temporary ? 'temporary' : 'durable',
        expires_at: temporary ? isoformat(new Date(now.getTime() + ttlHours * 3600_000)) : null,
      },
      { actor, provenance: actor === 'human' ? 'human-confirmed' : 'claimed' },
    );
    return { record_id: recordId, path: recordPath };
  }

  createWithEvent(eventType, payload, options = {}) {
    const { actor = 'system', provenance = 'reconstructed' } = options;
    const now = this.now();
    const recordId = `work-${recordStamp(now)}-${crypto.randomBytes(4).toString('hex')}`;
    const recordPath = path.join(this.recordsRoot, recordId);
    fs.mkdirSync(this.recordsRoot, { recursive: true });
    fs.mkdirSync(recordPath);
    this.append(recordId, eventType, payload, { actor, provenance });
    return { record_id: recordId, path: recordPath };
  }

  promote(recordId, projectKey, actor = 'agent') {
    const key = String(projectKey || '').trim().toUpperCase();
    if (!/^[A-Z][A-Z0-9]*$/.test(key)) {
      throw new Error('project_key must contain only uppercase letters and digits');
    }
    this.read(recordId);
    const date = this.datePart(this.now());
    const taskId = this.reserveTaskId(recordId, key, date);
    this.append(recordId, 'task.promoted', { task_id: taskId }, { actor, provenance: 'artifact-evidence' });
    return taskId;
  }

  datePart(date) {
    const pad = (value) => String(value).padStart(2, '0');
    return `${date.getUTCFullYear()}${pad(date.getUTCMonth() + 1)}${pad(date.getUTCDate())}`;
  }

  reserveTaskId(recordId, projectKey, date) {
    const used = this.taskSequences(projectKey, date);
    const reservations = path.join(this.project, '.idc', 'task-ids');
    fs.mkdirSync(reservations, { recursive: true });
    for (let sequence = 1; sequence < 1000; sequence += 1) {
      if (used.has(sequence)) continue;
      const taskId = `IDC-${projectKey}-${date}-${String(sequence).padStart(3, '0')}`;
      try {
        const handle = fs.openSync(path.join(reservations, taskId), 'wx', 0o666);
        try {
          fs.writeFileSync(handle, recordId + '\n', 'utf8');
        } finally {
          fs.closeSync(handle);
        }
        return taskId;
      } catch (error) {
        if (error && error.code === 'EEXIST') continue;
        throw error;
      }
    }
    throw new Error(`no task IDs remain for ${projectKey} on ${date}`);
  }

  append(recordId, eventType, payload, options = {}) {
    const { actor = 'agent', provenance = 'claimed' } = options;
    this.assertWriteCompatible();
    if (!RECORD_ID_RE.test(recordId)) throw new Error('invalid record_id');
    if (!CORE_EVENT_TYPES.has(eventType) && !/^x\.[a-z0-9][a-z0-9.-]*$/.test(eventType)) {
      throw new Error(`unsupported event type: ${eventType}`);
    }
    if (!PROVENANCE_TYPES.has(provenance)) throw new Error(`unsupported provenance: ${provenance}`);
    const recordPath = path.join(this.recordsRoot, recordId);
    if (!this.isDirectory(recordPath)) throw new Error(`work record does not exist: ${recordId}`);

    const lock = path.join(recordPath, '.events.lock');
    this.ensureLockFile(lock);
    const events = this.readUnlocked(recordId);
    if (events.some((event) => event.schema_version !== EVENT_SCHEMA_VERSION)) {
      throw new Error(
        'cannot append schema 2 events to a schema 1 record; ' +
          'migrate the historical record explicitly first',
      );
    }
    const event = {
      schema_version: EVENT_SCHEMA_VERSION,
      record_id: recordId,
      seq: events.length,
      timestamp: isoformat(this.now()),
      actor: { kind: actor },
      type: eventType,
      provenance,
      payload,
    };
    const file = path.join(recordPath, 'events.jsonl');
    const handle = fs.openSync(file, 'a', 0o666);
    try {
      fs.writeFileSync(handle, pyJsonDumps(event) + '\n', 'utf8');
      fs.fsyncSync(handle);
    } finally {
      fs.closeSync(handle);
    }
    try {
      updateIndex(this.project, event);
    } catch (error) {
      if (!osErrorOnly(error)) throw error;
      // The event log stays authoritative when the optional cache cannot update.
    }
    return event;
  }

  assertWriteCompatible() {
    const config = loadConfig(this.project);
    if (!isWriteCompatible(config)) throw new Error(PROTOCOL_MISMATCH);
  }

  read(recordId) {
    const recordPath = path.join(this.recordsRoot, recordId);
    if (!this.isDirectory(recordPath)) throw new Error(`work record does not exist: ${recordId}`);
    return readEvents(this.project, recordId);
  }

  readUnlocked(recordId) {
    return readEvents(this.project, recordId);
  }

  taskSequences(projectKey, date) {
    const used = new Set();
    let entries = [];
    try {
      entries = fs.readdirSync(this.recordsRoot, { withFileTypes: true });
    } catch (error) {
      if (error && error.code === 'ENOENT') return used;
      throw error;
    }
    for (const entry of entries) {
      if (!entry.isDirectory()) continue;
      const file = path.join(this.recordsRoot, entry.name, 'events.jsonl');
      let text;
      try {
        text = fs.readFileSync(file, 'utf8');
      } catch {
        continue;
      }
      for (const line of splitLines(text)) {
        let event;
        try {
          event = JSON.parse(line);
        } catch {
          continue;
        }
        const taskId = event?.payload?.task_id;
        if (typeof taskId !== 'string') continue;
        const match = TASK_ID_RE.exec(taskId);
        if (match && match[1] === projectKey && match[2] === date) used.add(Number(match[3]));
      }
    }
    return used;
  }

  now() {
    const value = this.clock();
    if (!(value instanceof Date) || !Number.isFinite(value.getTime())) {
      throw new Error('clock must return a valid Date');
    }
    return new Date(value.getTime());
  }

  isDirectory(target) {
    try {
      return fs.statSync(target).isDirectory();
    } catch (error) {
      if (error && (error.code === 'ENOENT' || error.code === 'ENOTDIR')) return false;
      throw error;
    }
  }

  ensureLockFile(file) {
    let handle;
    try {
      handle = fs.openSync(file, 'a+');
      const stats = fs.fstatSync(handle);
      if (stats.size === 0) fs.writeFileSync(handle, Buffer.from([0]));
    } catch (error) {
      if (!osErrorOnly(error)) throw error;
    } finally {
      if (handle !== undefined) fs.closeSync(handle);
    }
  }
}

/**
 * Read one record without touching the filesystem (no lock file creation).
 * Used by read-only projections and parity tests over foreign repositories.
 */
export function readEvents(project, recordId) {
  const recordPath = path.join(workItemsRoot(project), recordId);
  if (!isDirectory(recordPath)) throw new Error(`work record does not exist: ${recordId}`);
  const file = path.join(recordPath, 'events.jsonl');
  let text;
  try {
    text = fs.readFileSync(file, 'utf8');
  } catch (error) {
    if (error && error.code === 'ENOENT') return [];
    throw error;
  }
  const events = [];
  splitLines(text).forEach((line, index) => {
    if (!line.trim()) return;
    let event;
    try {
      event = JSON.parse(line);
    } catch (error) {
      throw new Error(`invalid JSON in ${file}:${index + 1}: ${error.message}`);
    }
    if (event.record_id !== recordId || event.seq !== index) {
      throw new Error(`invalid event sequence in ${file}`);
    }
    events.push(event);
  });
  return events;
}

function isDirectory(target) {
  try {
    return fs.statSync(target).isDirectory();
  } catch (error) {
    if (error && (error.code === 'ENOENT' || error.code === 'ENOTDIR')) return false;
    throw error;
  }
}

/** Read and fold one record, honoring the store's read validation. */
export function readRecord(project, recordId) {
  return readEvents(project, recordId);
}

export { parseIsoformat };
