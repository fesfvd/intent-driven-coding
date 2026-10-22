/**
 * IDC workflow mutations, ported from idc_core/workflow.py.
 *
 * Every mutation appends one protocol event and refreshes the derived card.
 * Gates are evaluated before the append, so a blocked transition leaves no
 * trace in the event log.
 */

import fs from 'node:fs';
import path from 'node:path';

import { EventStore } from './events.js';
import { foldEvents } from './fold.js';
import { evaluateObligations } from './gates.js';
import { renderCard } from './render.js';

export class GateBlocked extends Error {
  constructor(blocks, explanations = {}) {
    super(`blocked by: ${blocks.join(', ')}`);
    this.name = 'GateBlocked';
    this.blocks = [...blocks];
    this.explanations = { ...explanations };
  }
}

const FAILURE_ATTRIBUTIONS = new Set([
  'code-regression',
  'pre-existing',
  'environment-tool',
  'encoding-presentation',
  'inconclusive',
]);
const LEARNING_DESTINATIONS = new Set(['architecture', 'playbook', 'skill', 'squad', 'test', 'script']);
const LEARNING_DISPOSITIONS = new Set(['accepted', 'rejected', 'deferred', 'merged']);
const PERMISSION_STATES = new Set(['requested', 'granted', 'rejected', 'executed']);

export class Workflow {
  constructor(project, options = {}) {
    this.project = path.resolve(project);
    this.store = new EventStore(this.project, options.clock ?? (() => new Date()));
  }

  start(summary, options = {}) {
    const { actor = 'agent', temporary = false, scenes = [] } = options;
    let { ttlHours } = options;
    if (scenes.some((scene) => typeof scene !== 'string' || scene.trim() === '')) {
      throw new Error('scene labels must not be empty');
    }
    if (ttlHours === undefined || ttlHours === null) {
      ttlHours = 72;
      const configPath = path.join(this.project, '.idc', 'config.json');
      try {
        const parsed = JSON.parse(fs.readFileSync(configPath, 'utf8'));
        const configured = parsed?.capture_ttl_hours;
        if (Number.isInteger(configured) && configured > 0) ttlHours = configured;
      } catch {
        // Absent or malformed config falls back to the default TTL.
      }
    }
    const record = this.store.capture(summary, actor, { temporary, ttlHours });
    if (scenes.length > 0) {
      this.classify(record.record_id, scenes, {
        reason: 'Initial scene identification from the request',
        actor,
      });
    } else {
      this.render(record.record_id);
    }
    return record.record_id;
  }

  promote(recordId, projectKey, options = {}) {
    const { actor = 'agent' } = options;
    const state = this.state(recordId);
    if (state.capture_disposition === 'discarded' || state.capture_disposition === 'expired') {
      throw new Error(`capture is ${state.capture_disposition}`);
    }
    const taskId = this.store.promote(recordId, projectKey, actor);
    this.render(recordId);
    return taskId;
  }

  discard(recordId, options = {}) {
    const { reason, actor = 'agent' } = options;
    const state = this.state(recordId);
    if (state.task_id) throw new Error('promoted task cannot be discarded');
    this.append(recordId, 'capture.discarded', { reason }, { actor });
    return this.state(recordId);
  }

  shape(recordId, options = {}) {
    const {
      goal,
      explicit,
      repositoryFacts,
      proposedDefaults,
      openDecisions,
      scope,
      acceptance,
      classifications,
      uncertainty,
      impacts,
      actor = 'agent',
    } = options;
    const previous = this.state(recordId);
    this.append(
      recordId,
      'intent.translated',
      {
        goal,
        explicit: explicit === undefined ? previous.explicit : explicit,
        repository_facts:
          repositoryFacts === undefined ? previous.repository_facts : repositoryFacts,
        proposed_defaults:
          proposedDefaults === undefined ? previous.proposed_defaults : proposedDefaults,
        open_decisions:
          openDecisions === undefined ? previous.open_decisions : openDecisions,
      },
      { actor },
    );
    if (previous.lifecycle === 'captured' || previous.lifecycle === 'promoted') {
      this.append(
        recordId,
        'lifecycle.changed',
        { from: previous.lifecycle, to: 'shaped' },
        { actor },
      );
    }
    if (scope !== undefined) {
      this.append(recordId, 'scope.changed', { from: previous.scope, to: scope }, { actor });
    }
    if (acceptance !== undefined) {
      this.append(
        recordId,
        'acceptance.changed',
        { from: previous.acceptance, to: acceptance },
        { actor },
      );
    }
    if (classifications !== undefined) {
      this.append(
        recordId,
        'classification.changed',
        {
          from: previous.classifications.length ? previous.classifications : null,
          to: classifications,
          reason: 'Task shaping',
        },
        { actor },
      );
    }
    if (uncertainty !== undefined) {
      this.append(
        recordId,
        'uncertainty.changed',
        { from: previous.uncertainty, to: uncertainty },
        { actor },
      );
    }
    if (impacts !== undefined) {
      this.append(recordId, 'impact.assessed', { dimensions: impacts }, { actor });
    }
    const current = this.state(recordId);
    if (current.lifecycle !== 'shaped') {
      this.append(
        recordId,
        'lifecycle.changed',
        { from: current.lifecycle, to: 'shaped' },
        { actor },
      );
    }
    return this.state(recordId);
  }

  setCondition(recordId, name, active, options = {}) {
    const { reason, actor = 'agent' } = options;
    this.append(
      recordId,
      'condition.changed',
      { name, active, reason },
      { actor },
    );
    return this.state(recordId);
  }

  changeRequirement(recordId, options = {}) {
    const { before, after, reason, actor = 'agent' } = options;
    this.append(
      recordId,
      'requirement.changed',
      { before, after, reason },
      { actor, provenance: actor === 'human' ? 'human-confirmed' : 'claimed' },
    );
    return this.state(recordId);
  }

  classify(recordId, classifications, options = {}) {
    const { reason, actor = 'agent' } = options;
    const previous = this.state(recordId);
    this.append(
      recordId,
      'classification.changed',
      {
        from: previous.classifications.length ? previous.classifications : null,
        to: classifications,
        reason,
      },
      { actor },
    );
    return this.state(recordId);
  }

  resolveDecision(recordId, options = {}) {
    const { decision, resolution, actor = 'human' } = options;
    const state = this.state(recordId);
    if (!state.open_decisions.includes(decision)) {
      throw new Error(`open decision does not exist: ${decision}`);
    }
    this.append(
      recordId,
      'decision.resolved',
      { decision, resolution },
      { actor, provenance: actor === 'human' ? 'human-confirmed' : 'claimed' },
    );
    return this.state(recordId);
  }

  permission(recordId, options = {}) {
    const { effect, state: permissionState, actor = 'human' } = options;
    if (!PERMISSION_STATES.has(permissionState)) {
      throw new Error(`invalid permission state: ${permissionState}`);
    }
    this.append(
      recordId,
      `permission.${permissionState}`,
      { effect },
      { actor, provenance: actor === 'human' ? 'human-confirmed' : 'host-observed' },
    );
    return this.state(recordId);
  }

  recordRecovery(recordId, summary, options = {}) {
    const { actor = 'agent' } = options;
    this.append(recordId, 'recovery.recorded', { summary }, { actor });
    return this.state(recordId);
  }

  recordActivity(recordId, name, options = {}) {
    const { actor = 'agent' } = options;
    const state = this.state(recordId);
    const evaluation = evaluateObligations(state, name);
    raiseIfBlocked(evaluation);
    this.append(recordId, 'activity.recorded', { name }, { actor });
    return this.state(recordId);
  }

  transition(recordId, target, options = {}) {
    const { actor = 'agent' } = options;
    const state = this.state(recordId);
    const evaluation = evaluateObligations(state, target);
    raiseIfBlocked(evaluation);
    this.append(
      recordId,
      'lifecycle.changed',
      { from: state.lifecycle, to: target },
      { actor },
    );
    return { state: this.state(recordId), warnings: [...evaluation.warnings] };
  }

  addEvidence(recordId, options = {}) {
    const {
      kind,
      summary,
      result,
      acceptanceIds = [],
      reference = null,
      actor = 'agent',
      confirmationRef = null,
      failureAttribution = null,
    } = options;
    if (result === 'fail' && !FAILURE_ATTRIBUTIONS.has(failureAttribution)) {
      throw new Error('failed evidence requires a failure attribution');
    }
    if (result !== 'fail' && failureAttribution !== null && failureAttribution !== undefined) {
      throw new Error('failure attribution is only valid for failed evidence');
    }
    if (kind === 'human-confirmed') {
      if (actor !== 'human') throw new Error('human-confirmed evidence requires human actor');
      if (typeof confirmationRef !== 'string' || confirmationRef.trim() === '') {
        throw new Error('human-confirmed evidence requires confirmation reference');
      }
    }
    this.append(
      recordId,
      'evidence.recorded',
      {
        kind,
        summary,
        result,
        acceptance_ids: acceptanceIds ?? [],
        reference: reference ?? null,
        confirmation_ref: confirmationRef ?? null,
        failure_attribution: failureAttribution ?? null,
      },
      { actor, provenance: kind },
    );
    return this.state(recordId);
  }

  close(recordId, options = {}) {
    const { outcome, summary, actor = 'agent' } = options;
    const state = this.state(recordId);
    const unattributed = state.evidence.some(
      (evidence) => evidence.result === 'fail' && !evidence.failure_attribution,
    );
    if (outcome === 'completed' && unattributed) {
      throw new GateBlocked(['evidence:failure-attribution'], {
        'evidence:failure-attribution': 'Classify every failed verification before completion.',
      });
    }
    const evaluation = evaluateObligations(state, outcome);
    raiseIfBlocked(evaluation);
    this.append(recordId, 'task.closed', { outcome, summary }, { actor });
    return { state: this.state(recordId), warnings: [...evaluation.warnings] };
  }

  reviewLearning(recordId, options = {}) {
    const {
      outcome,
      candidate = null,
      evidenceRefs = [],
      destination = null,
      reason = null,
      actor = 'human',
    } = options;
    if (actor !== 'human') throw new Error('learning review requires human actor');
    if (this.state(recordId).lifecycle !== 'closed') {
      throw new GateBlocked(['lifecycle:closed'], {
        'lifecycle:closed': 'Review learning after task closure.',
      });
    }
    if (outcome !== 'candidate' && outcome !== 'none') {
      throw new Error('learning review outcome must be candidate or none');
    }
    if (outcome === 'candidate') {
      if (typeof candidate !== 'string' || candidate.trim() === '') {
        throw new Error('candidate learning requires a non-empty candidate');
      }
      if (!evidenceRefs || evidenceRefs.length === 0) {
        throw new Error('candidate learning requires evidence references');
      }
      if (!LEARNING_DESTINATIONS.has(destination)) {
        throw new Error('candidate learning requires a valid destination');
      }
    } else if (typeof reason !== 'string' || reason.trim() === '') {
      throw new Error('a no-retention learning decision requires a reason');
    }
    this.append(
      recordId,
      'learn.reviewed',
      {
        status: outcome,
        candidate,
        evidence_refs: evidenceRefs ?? [],
        destination,
        reason: reason ?? '',
      },
      { actor, provenance: 'human-confirmed' },
    );
    return this.state(recordId);
  }

  disposeLearning(recordId, options = {}) {
    const { disposition, reason, actor = 'human' } = options;
    if (actor !== 'human') throw new Error('learning disposition requires human actor');
    const state = this.state(recordId);
    if (state.learning_status !== 'candidate') {
      throw new GateBlocked(['learning:candidate'], {
        'learning:candidate': 'Review a learning candidate before disposition.',
      });
    }
    if (!LEARNING_DISPOSITIONS.has(disposition)) {
      throw new Error('invalid learning disposition');
    }
    if (typeof reason !== 'string' || reason.trim() === '') {
      throw new Error('learning disposition requires a reason');
    }
    this.append(
      recordId,
      'learn.disposed',
      { status: disposition, reason },
      { actor, provenance: 'human-confirmed' },
    );
    return this.state(recordId);
  }

  state(recordId) {
    let events = this.store.read(recordId);
    const now = this.store.now();
    let state = foldEvents(events, { now });
    if (
      state.capture_disposition === 'expired' &&
      !events.some((event) => event.type === 'capture.expired')
    ) {
      this.store.append(
        recordId,
        'capture.expired',
        { expired_at: state.expires_at },
        { actor: 'system', provenance: 'artifact-evidence' },
      );
      events = this.store.read(recordId);
      state = foldEvents(events, { now });
      this.render(recordId);
    }
    return state;
  }

  append(recordId, eventType, payload, options = {}) {
    this.store.append(recordId, eventType, payload, options);
    this.render(recordId);
  }

  render(recordId) {
    const state = this.state(recordId);
    const provisional = path.join(this.store.recordsRoot, recordId, 'CARD.md');
    let target;
    if (state.task_id) {
      target = path.join(this.project, '.idc', 'tasks', `${state.task_id}.md`);
      removeIfPresent(provisional);
    } else if (state.capture_disposition === 'open') {
      target = provisional;
    } else {
      removeIfPresent(provisional);
      return;
    }
    fs.mkdirSync(path.dirname(target), { recursive: true });
    fs.writeFileSync(target, renderCard(state), 'utf8');
  }
}

function removeIfPresent(file) {
  try {
    fs.unlinkSync(file);
  } catch (error) {
    if (!error || error.code !== 'ENOENT') throw error;
  }
}

function raiseIfBlocked(evaluation) {
  if (evaluation.hard_blocks.length > 0) {
    throw new GateBlocked(evaluation.hard_blocks, evaluation.explanations);
  }
}
