/** Learning cadence, ported from idc_core/learning.py. */

import fs from 'node:fs';
import path from 'node:path';

import { getIndex } from './task-index.js';
import { pyJsonPretty } from './py.js';

export const DEFAULT_THRESHOLD = 5;
export const DEFAULT_MAX_DAYS = 14;

export function checkLearningCadence(project, options = {}) {
  const root = path.resolve(project);
  const current = ensureAware(options.now ?? new Date());
  const config = readJson(path.join(root, '.idc', 'config.json'));
  const learning = isPlainObject(config.learning) ? config.learning : {};
  const threshold = positiveInt(learning.completed_task_threshold, DEFAULT_THRESHOLD);
  const maxDays = positiveInt(learning.max_days, DEFAULT_MAX_DAYS);
  const state = readJson(path.join(root, '.idc', 'learning-state.json'));
  const lastReview = parseTime(state.last_review_at);
  const completed = completedTasks(root);
  const completedSince = completed.filter((item) => lastReview === null || item < lastReview);
  const ageDays = lastReview ? Math.trunc((current.getTime() - lastReview.getTime()) / 86_400_000) : null;
  let status;
  let reason;
  if (completedSince.length === 0) {
    status = 'quiet';
    reason = 'no completed work since the last review';
  } else if (completedSince.length >= threshold) {
    status = 'due';
    reason = `completed task threshold reached (${completedSince.length} >= ${threshold})`;
  } else if (ageDays !== null && ageDays >= maxDays) {
    status = 'due';
    reason = `review window elapsed (${ageDays} >= ${maxDays} days)`;
  } else {
    status = 'quiet';
    reason = 'review window has not opened';
  }
  return {
    status,
    reason,
    completed_since_review: completedSince.length,
    completed_total: completed.length,
    threshold,
    max_days: maxDays,
    last_review_at: state.last_review_at ?? null,
    suggested_squad: status === 'due' ? 'learning-curator' : null,
  };
}

export function recordLearningSession(project, options = {}) {
  const { summary } = options;
  if (typeof summary !== 'string' || summary.trim() === '') {
    throw new Error('learning session summary must not be empty');
  }
  const root = path.resolve(project);
  const current = ensureAware(options.now ?? new Date());
  const file = path.join(root, '.idc', 'learning-state.json');
  fs.mkdirSync(path.dirname(file), { recursive: true });
  const previous = readJson(file);
  const previousCount = previous.session_count;
  const count =
    Number.isInteger(previousCount) && previousCount >= 0 ? previousCount + 1 : 1;
  const state = {
    last_review_at: isoformat(current),
    summary: summary.trim(),
    session_count: count,
    previous_review_at: previous.last_review_at ?? null,
  };
  const temporary = path.join(
    path.dirname(file),
    `.learning-state-${process.pid}-${Math.random().toString(16).slice(2)}.tmp`,
  );
  try {
    const handle = fs.openSync(temporary, 'w', 0o666);
    try {
      fs.writeFileSync(handle, pyJsonPretty(state) + '\n', 'utf8');
      fs.fsyncSync(handle);
    } finally {
      fs.closeSync(handle);
    }
    fs.renameSync(temporary, file);
  } finally {
    try {
      fs.unlinkSync(temporary);
    } catch {
      // Already renamed.
    }
  }
  return { status: 'recorded', ...state };
}

function completedTasks(project) {
  const index = getIndex(project);
  if (index) {
    return Object.values(index.records ?? {})
      .filter((record) => record && record.outcome === 'completed')
      .map((record) => parseTime(record.closed_at))
      .filter((timestamp) => timestamp !== null)
      .sort((a, b) => a - b);
  }
  const result = [];
  const root = path.join(project, '.idc', 'work-items');
  let entries;
  try {
    entries = fs.readdirSync(root, { withFileTypes: true });
  } catch {
    return result;
  }
  for (const entry of entries) {
    if (!entry.isDirectory()) continue;
    let events;
    try {
      events = fs
        .readFileSync(path.join(root, entry.name, 'events.jsonl'), 'utf8')
        .split('\n')
        .filter((line) => line.trim())
        .map((line) => JSON.parse(line));
    } catch {
      continue;
    }
    for (const event of events) {
      if (event?.type === 'task.closed' && event?.payload?.outcome === 'completed') {
        const timestamp = parseTime(event.timestamp);
        if (timestamp) result.push(timestamp);
        break;
      }
    }
  }
  return result.sort((a, b) => a - b);
}

function readJson(file) {
  try {
    const value = JSON.parse(fs.readFileSync(file, 'utf8'));
    return isPlainObject(value) ? value : {};
  } catch {
    return {};
  }
}

function parseTime(value) {
  if (typeof value !== 'string') return null;
  const date = new Date(value);
  return Number.isFinite(date.getTime()) ? date : null;
}

function ensureAware(value) {
  const date = value instanceof Date ? value : new Date(value);
  if (!Number.isFinite(date.getTime())) throw new Error('invalid timestamp');
  return date;
}

function isoformat(date) {
  const pad = (number, width = 2) => String(number).padStart(width, '0');
  const base =
    `${pad(date.getUTCFullYear(), 4)}-${pad(date.getUTCMonth() + 1)}-${pad(date.getUTCDate())}` +
    `T${pad(date.getUTCHours())}:${pad(date.getUTCMinutes())}:${pad(date.getUTCSeconds())}`;
  const micros = date.getUTCMilliseconds() * 1000;
  return micros === 0 ? `${base}+00:00` : `${base}.${pad(micros, 6)}+00:00`;
}

function positiveInt(value, fallback) {
  return Number.isInteger(value) && value > 0 ? value : fallback;
}

function isPlainObject(value) {
  return Boolean(value) && typeof value === 'object' && !Array.isArray(value);
}
