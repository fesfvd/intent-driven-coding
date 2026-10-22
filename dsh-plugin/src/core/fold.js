/**
 * Event projection, ported from idc_core/projector.py.
 *
 * Field names stay snake_case so a folded state can be compared directly with
 * the Python reference output.
 */

import { parseIsoformat } from './py.js';

export function emptyState(recordId) {
  return {
    record_id: recordId,
    task_id: null,
    summary: '',
    lifecycle: 'captured',
    outcome: null,
    goal: '',
    explicit: [],
    repository_facts: [],
    proposed_defaults: [],
    open_decisions: [],
    decisions: [],
    scope: [],
    acceptance: [],
    uncertainty: [],
    classifications: [],
    classification_history: [],
    requirement_changes: [],
    impacts: {},
    permissions: {},
    recovery: null,
    conditions: new Set(),
    evidence: [],
    activities: [],
    events: [],
    legacy_snapshot: null,
    capture_mode: 'durable',
    expires_at: null,
    capture_disposition: 'open',
    learning_status: 'not-required',
    learning_candidates: [],
  };
}

function asList(value) {
  if (!value) return [];
  return Array.from(value);
}

export function foldEvents(events, options = {}) {
  const { now = new Date() } = options;
  if (!Array.isArray(events) || events.length === 0) {
    throw new Error('at least one event is required');
  }
  const recordId = events[0]?.record_id;
  if (typeof recordId !== 'string') throw new Error('event record_id is required');
  const state = emptyState(recordId);
  events.forEach((event, expectedSeq) => {
    if (event?.record_id !== recordId || event?.seq !== expectedSeq) {
      throw new Error('events must have one record_id and contiguous sequence numbers');
    }
    const payload = event.payload;
    if (!payload || typeof payload !== 'object' || Array.isArray(payload)) {
      throw new Error('event payload must be an object');
    }
    state.events.push(event);
    switch (event.type) {
      case 'request.captured':
        state.summary = String(payload.summary ?? '');
        state.capture_mode = String(payload.capture_mode ?? 'durable');
        state.expires_at = payload.expires_at ?? null;
        break;
      case 'task.promoted':
        state.task_id = String(payload.task_id);
        state.capture_disposition = 'promoted';
        state.lifecycle = 'promoted';
        break;
      case 'capture.discarded':
        state.capture_disposition = 'discarded';
        break;
      case 'capture.expired':
        state.capture_disposition = 'expired';
        break;
      case 'intent.translated':
        state.goal = String(payload.goal ?? '');
        state.explicit = asList(payload.explicit);
        state.repository_facts = asList(payload.repository_facts);
        state.proposed_defaults = asList(payload.proposed_defaults);
        state.open_decisions = asList(payload.open_decisions);
        break;
      case 'scope.changed':
        state.scope = asList(payload.to);
        break;
      case 'acceptance.changed':
        state.acceptance = asList(payload.to);
        break;
      case 'uncertainty.changed':
        state.uncertainty = asList(payload.to);
        break;
      case 'classification.changed':
        state.classifications = asList(payload.to);
        state.classification_history.push({ ...payload });
        break;
      case 'lifecycle.changed':
        state.lifecycle = String(payload.to);
        break;
      case 'requirement.changed':
        state.requirement_changes.push({ ...payload });
        if (state.lifecycle === 'active' || state.lifecycle === 'validating') state.lifecycle = 'shaped';
        break;
      case 'impact.assessed':
        Object.assign(state.impacts, payload.dimensions ?? {});
        break;
      case 'permission.requested':
        state.permissions[String(payload.effect)] = 'requested';
        break;
      case 'permission.granted':
        state.permissions[String(payload.effect)] = 'granted';
        break;
      case 'permission.rejected':
        state.permissions[String(payload.effect)] = 'rejected';
        break;
      case 'permission.executed':
        state.permissions[String(payload.effect)] = 'executed';
        break;
      case 'recovery.recorded':
        state.recovery = String(payload.summary);
        break;
      case 'condition.changed': {
        const name = String(payload.name);
        if (payload.active) state.conditions.add(name);
        else state.conditions.delete(name);
        break;
      }
      case 'evidence.recorded':
        state.evidence.push({ ...payload });
        break;
      case 'activity.recorded':
        state.activities.push(String(payload.name));
        break;
      case 'decision.resolved': {
        const decision = String(payload.decision);
        state.open_decisions = state.open_decisions.filter((item) => item !== decision);
        state.decisions.push({ ...payload });
        break;
      }
      case 'task.closed':
        state.lifecycle = 'closed';
        state.outcome = String(payload.outcome);
        break;
      case 'learn.reviewed':
        state.learning_status = String(payload.status);
        if (state.learning_status === 'candidate') {
          state.learning_candidates = [
            {
              candidate: String(payload.candidate),
              evidence_refs: asList(payload.evidence_refs),
              destination: String(payload.destination),
              reason: String(payload.reason ?? ''),
              status: 'pending',
            },
          ];
        } else {
          state.learning_candidates = [];
        }
        break;
      case 'learn.disposed':
        state.learning_status = String(payload.status);
        for (const candidate of state.learning_candidates) {
          candidate.status = state.learning_status;
          candidate.disposition_reason = String(payload.reason);
        }
        break;
      case 'legacy.snapshot-imported':
        state.legacy_snapshot = { ...payload };
        state.summary = String(payload.title ?? 'Legacy task snapshot');
        break;
      default:
        break;
    }
  });
  if (
    state.capture_mode === 'temporary' &&
    state.capture_disposition === 'open' &&
    state.expires_at
  ) {
    const expires = parseIsoformat(state.expires_at);
    if (expires.getTime() <= now.getTime()) state.capture_disposition = 'expired';
  }
  return state;
}
