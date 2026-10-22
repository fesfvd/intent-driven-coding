/**
 * Obligation engine, ported from idc_core/obligations.py.
 *
 * Gates are preconditions: callers must evaluate before appending an event and
 * must not write when `hard_blocks` is non-empty.
 */

export function evaluateObligations(state, target) {
  const result = { hard_blocks: [], warnings: [], explanations: {} };
  const addBlock = (id, explanation) => {
    if (!result.hard_blocks.includes(id)) result.hard_blocks.push(id);
    if (explanation) result.explanations[id] = explanation;
  };

  lifecycle(state, target, result, addBlock);
  shaping(state, target, result, addBlock);
  uncertainty(state, target, result, addBlock);
  securityPrivacy(state, target, result, addBlock);
  permissionRecovery(state, target, result, addBlock);
  permissionRecovery(state, target, result, addBlock);
  acceptanceClosure(state, target, result, addBlock);
  return result;
}

function lifecycle(state, target, result, addBlock) {
  const allowed = {
    captured: new Set(['shaped']),
    promoted: new Set(['shaped']),
    shaped: new Set(['active', 'validating']),
    active: new Set(['shaped', 'validating']),
    validating: new Set(['shaped', 'active']),
    closed: new Set(),
  };
  if (['shaped', 'active', 'validating'].includes(target) && !(allowed[state.lifecycle] ?? new Set()).has(target)) {
    addBlock(
      `lifecycle:${state.lifecycle}->${target}`,
      'Move through a permitted lifecycle transition first.',
    );
  }
  if (['active', 'validating'].includes(target) && ['captured', 'promoted'].includes(state.lifecycle)) {
    addBlock('shape:required', 'Promote and shape the task before implementation or validation.');
  }
  if (
    state.lifecycle === 'closed' &&
    !['closed', 'completed', 'cancelled', 'superseded', 'unresolved'].includes(target)
  ) {
    addBlock('lifecycle:closed', 'A closed task cannot resume; create a new task or reopen explicitly.');
  }
}

function shaping(state, target, result, addBlock) {
  if (target !== 'active') return;
  for (const [missing, present] of [
    ['intent:goal', Boolean(state.goal)],
    ['scope', Boolean(state.scope?.length)],
    ['acceptance', Boolean(state.acceptance?.length)],
    ['impact', Object.keys(state.impacts ?? {}).length > 0],
  ]) {
    if (!present) result.warnings.push(missing);
  }
  if (state.open_decisions?.length) {
    if (state.conditions.has('emergency')) result.warnings.push('decision:open');
    else addBlock('decision:open', 'Resolve each open decision before activating the task.');
  }
}

function uncertainty(state, target, result, addBlock) {
  const required = [];
  if (target === 'build' || target === 'completed') {
    if (state.uncertainty.includes('unknown-cause') && !state.activities.includes('discover')) {
      required.push('activity:discover');
    }
    if (state.uncertainty.includes('cross-boundary') && !state.activities.includes('design')) {
      required.push('activity:design');
    }
  }
  if (target === 'build') {
    if (state.conditions.has('emergency')) result.warnings.push(...required);
    else {
      for (const item of required) {
        addBlock(item, `Record the required ${item.replace('activity:', '')} activity before building.`);
      }
    }
  } else if (target === 'completed') {
    for (const item of required) {
      addBlock(item, `Record the required ${item.replace('activity:', '')} activity before completion.`);
    }
  }
}

const LEVELS = ['none', 'low', 'medium', 'high', 'unknown'];

function levelIndex(level) {
  const index = LEVELS.indexOf(level);
  if (index < 0) throw new Error(`unknown impact level: ${level}`);
  return index;
}

function securityPrivacy(state, target, result, addBlock) {
  if (target !== 'completed') return;
  const level = [state.impacts?.security ?? 'none', state.impacts?.privacy ?? 'none'].reduce(
    (best, candidate) => (levelIndex(candidate) > levelIndex(best) ? candidate : best),
  );
  if ((level === 'high' || level === 'unknown') && !state.activities.includes('review')) {
    addBlock('activity:review', 'Record a security/privacy review before completion.');
  } else if (level === 'medium' && !state.activities.includes('review')) {
    result.warnings.push('activity:review');
  }
}

function permissionRecovery(state, target, result, addBlock) {
  if (
    target !== 'ship' ||
    !['medium', 'high', 'unknown'].includes(state.impacts?.external_effect)
  ) {
    return;
  }
  const permissions = state.permissions ?? {};
  const effects = Object.keys(permissions).sort();
  if (effects.length === 0) {
    addBlock('permission:external-effect', 'Record an effect-specific permission before shipping.');
  } else {
    for (const effect of effects) {
      if (!['granted', 'executed'].includes(permissions[effect])) {
        addBlock(`permission:${effect}`, `Obtain permission for ${effect} before shipping.`);
      }
    }
  }
  if (
    ['medium', 'high', 'unknown'].includes(state.impacts?.reversibility) &&
    !state.recovery
  ) {
    addBlock('recovery-plan', 'Record a rollback or recovery plan before shipping.');
  }
}

function acceptanceClosure(state, target, result, addBlock) {
  if (target !== 'completed') return;
  if (!state.goal) addBlock('intent:goal', 'Record the intended outcome before completing the task.');
  if (!state.acceptance?.length) {
    addBlock('acceptance', 'Record at least one acceptance criterion before completing the task.');
  }
  if (state.open_decisions?.length) addBlock('decision:open', 'Resolve each open decision before completion.');
  const passing = new Set();
  for (const evidence of state.evidence ?? []) {
    if (evidence.result === 'pass') {
      for (const acceptanceId of evidence.acceptance_ids ?? []) passing.add(acceptanceId);
    }
  }
  for (const item of state.acceptance ?? []) {
    const aid = item?.id;
    if (aid && !passing.has(aid)) {
      addBlock(`acceptance:${aid}`, `Attach passing evidence to acceptance item ${aid}.`);
    }
  }
}
