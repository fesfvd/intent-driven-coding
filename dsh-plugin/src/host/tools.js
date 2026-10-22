/**
 * Model-facing tools. Every tool resolves the workspace from the owning
 * session, never from model-supplied paths, and reports gate refusal as data.
 */

import fs from 'node:fs';
import path from 'node:path';

import { GateBlocked, Workflow } from '../core/workflow.js';
import { loadConfig, PROTOCOL_MISMATCH } from '../core/events.js';
import {
  recordDetail,
  resolveRecordRef,
  requireWorkspace,
  resolveWorkspace,
  statusOverview,
  truncate,
} from './workspace.js';
import { checkLearningCadence } from '../core/learning.js';

let defineTool;
try {
  ({ defineTool } = await import('@deepseek-ai/dsh-tools'));
} catch {
  // Unit tests run without the host package; the host always provides it.
  defineTool = (definition) => definition;
}

const RECORD_REF_DESCRIPTION =
  'Task ID (IDC-…) or record ID (work-…). Use idc_status to list records.';
const HUMAN_CONFIRMATION_DESCRIPTION =
  'Set true only when the user explicitly confirmed this write in the conversation.';

const SCENES = ['FIX', 'SEC', 'FEAT', 'CHG', 'REF', 'REVIEW', 'OPS', 'EXP', 'META'];
const LEVELS = ['none', 'low', 'medium', 'high', 'unknown'];
const PROVENANCE = [
  'claimed',
  'host-observed',
  'command-evidence',
  'artifact-evidence',
  'human-confirmed',
  'reconstructed',
];
const FAILURE_ATTRIBUTIONS = [
  'code-regression',
  'pre-existing',
  'environment-tool',
  'encoding-presentation',
  'inconclusive',
];
const LEARNING_DESTINATIONS = ['architecture', 'playbook', 'skill', 'squad', 'test', 'script'];

function ok(code, text) {
  return { ok: true, code, text };
}

function fail(code, text) {
  return { ok: false, code, text };
}

function describeGate(blocked) {
  const blocks = (blocked.blocks ?? []).join(', ');
  const explanations = Object.entries(blocked.explanations ?? {})
    .map(([key, value]) => `- ${key}: ${value}`)
    .join('\n');
  return fail(
    'GATE_BLOCKED',
    `blocked: ${blocks}\n${explanations}\nNo event was written; resolve the blocks and retry.`,
  );
}

function describeError(error) {
  if (error instanceof GateBlocked) return describeGate(error);
  const message = error instanceof Error ? error.message : String(error);
  if (message === PROTOCOL_MISMATCH || message.startsWith('IDC protocol mismatch')) {
    return fail('PROTOCOL_MISMATCH', message);
  }
  if (error && error.code === 'NO_IDC_CONTEXT') {
    return fail('NO_IDC_CONTEXT', message);
  }
  if (message.includes('schema 1 record')) {
    return fail('SCHEMA_1_RECORD', message);
  }
  return fail('INVALID_REQUEST', message);
}

function requireRecord(project, ref) {
  const resolved = resolveRecordRef(project, ref);
  if (!resolved) {
    const error = new Error(`record not found: ${ref}`);
    error.code = 'RECORD_NOT_FOUND';
    throw error;
  }
  return resolved;
}

function workflowFor(project) {
  return new Workflow(project);
}

function recordLine(record) {
  const id = record.task_id ?? record.record_id;
  const blocks = record.hard_blocks?.length ? ` · blocked: ${record.hard_blocks.join(', ')}` : '';
  const next = record.next_target ? ` · next: ${record.next_target}` : '';
  return `- ${id} [${record.lifecycle}]${next}${blocks} · ${record.summary}`;
}

function statusText(status) {
  const header =
    `IDC ${status.project_key} · ${status.total_records} records on disk` +
    ` · index ${status.index_records ?? 'absent'} · coverage ${status.coverage}`;
  const learning = status.learning?.status
    ? `learning: ${status.learning.status} (${status.learning.reason ?? 'no reason'})`
    : 'learning: unknown';
  const lines = status.records.map((record) =>
    record.error ? `- ${record.record_id} [unreadable] ${record.error}` : recordLine(record),
  );
  return [header, learning, ...lines, status.truncated ? '… more records omitted' : '']
    .filter(Boolean)
    .join('\n');
}

function detailText(detail) {
  const record = detail.record;
  const blocks = record.obligations.hard_blocks.length
    ? record.obligations.hard_blocks.join(', ')
    : 'none';
  const target = record.obligations.target ?? 'none';
  const header = `${record.task_id ?? record.record_id} [${record.lifecycle}] · target ${target} · hard blocks: ${blocks}`;
  const card = record.card_truncated
    ? `${record.card}\n… card truncated; open ${record.card_path}`
    : record.card;
  return `${header}\n\n${card}`;
}

function buildImpacts(args) {
  const impacts = {};
  for (const dimension of ['external_effect', 'reversibility', 'security', 'privacy']) {
    if (args[dimension] !== undefined) impacts[dimension] = args[dimension];
  }
  if (typeof args.impacts_json === 'string' && args.impacts_json.trim() !== '') {
    const extra = JSON.parse(args.impacts_json);
    if (!extra || typeof extra !== 'object' || Array.isArray(extra)) {
      throw new Error('impacts_json must be a JSON object');
    }
    Object.assign(impacts, extra);
  }
  return Object.keys(impacts).length ? impacts : undefined;
}

export function registerTools(ctx) {
  ctx.tools.register(
    defineTool({
      name: 'idc_status',
      description:
        'Read-only view of the IDC task records in this workspace: lifecycle, next gate, outstanding obligations and index coverage. Call before editing code or claiming completion. Omit record_id for an overview.',
      parameters: {
        record_id: { type: 'string', description: RECORD_REF_DESCRIPTION },
      },
      output: {
        schema: {
          type: 'object',
          additionalProperties: false,
          properties: {
            ok: { type: 'boolean', required: true },
            code: { type: 'string', required: true },
            text: { type: 'string', required: true },
          },
        },
        render: (_args, value) => [{ type: 'text', text: value.text }],
      },
      async execute(args, exec) {
        try {
          const { project } = requireWorkspace(exec);
          if (args.record_id) {
            const recordId = requireRecord(project, args.record_id);
            return ok('OK', detailText(recordDetail(project, recordId)));
          }
          const status = statusOverview(project);
          status.code = status.coverage === 'incomplete' ? 'INCOMPLETE_READ' : 'OK';
          return ok(status.code, statusText(status));
        } catch (error) {
          return describeError(error);
        }
      },
      presentCall: (args) => ({ card: 'generic', title: 'IDC status', kind: 'other', rawInput: JSON.stringify(args) }),
    }),
  );

  ctx.tools.register(
    defineTool({
      name: 'idc_init',
      description:
        'Create .idc/config.json at the workspace root when missing. Safe to call repeatedly; an existing config is never rewritten.',
      parameters: {
        project_key: {
          type: 'string',
          description: 'Uppercase task-ID prefix. Defaults to the directory name.',
        },
        capture_ttl_hours: {
          type: 'number',
          description: 'Temporary-capture lifetime in hours. Default 72.',
        },
      },
      output: {
        schema: {
          type: 'object',
          additionalProperties: false,
          properties: {
            ok: { type: 'boolean', required: true },
            code: { type: 'string', required: true },
            text: { type: 'string', required: true },
          },
        },
        render: (_args, value) => [{ type: 'text', text: value.text }],
      },
      async execute(args, exec) {
        try {
          const { cwd } = resolveWorkspace(exec);
          const root = cwd;
          const configPath = path.join(root, '.idc', 'config.json');
          if (fs.existsSync(configPath)) {
            const config = loadConfig(root);
            return ok(
              'EXISTS',
              `unchanged: ${configPath} (schema ${config.schema_version}, idc ${config.idc_version})`,
            );
          }
          const key = String(args.project_key ?? path.basename(root))
            .trim()
            .toUpperCase()
            .replace(/[^A-Z0-9]/g, '');
          if (!/^[A-Z][A-Z0-9]*$/.test(key)) {
            throw new Error('project_key must start with a letter and contain only A-Z0-9');
          }
          const ttl = Number.isInteger(args.capture_ttl_hours) && args.capture_ttl_hours > 0 ? args.capture_ttl_hours : 72;
          fs.mkdirSync(path.join(root, '.idc'), { recursive: true });
          const config = {
            schema_version: 2,
            idc_version: '1.2.0',
            project_key: key,
            record_policy: 'local-private',
            adapter: 'dsh',
            capture_ttl_hours: ttl,
          };
          fs.writeFileSync(configPath, `${JSON.stringify(config, null, 2)}\n`, 'utf8');
          return ok('CREATED', `created ${configPath}\n\nNext: idc_start with the request summary.`);
        } catch (error) {
          return describeError(error);
        }
      },
      presentCall: (args) => ({ card: 'generic', title: 'IDC init', kind: 'other', rawInput: JSON.stringify(args) }),
    }),
  );

  ctx.tools.register(
    defineTool({
      name: 'idc_start',
      description:
        'Capture a request as a task record before investigation. Returns the record id and provisional card path. The record must be promoted and shaped before code changes.',
      parameters: {
        summary: { type: 'string', required: true, description: 'One-sentence request summary.' },
        scene: {
          type: 'string',
          description: `Initial scene label (${SCENES.join(', ')}).`,
        },
        temporary: {
          type: 'boolean',
          description: 'Expire the capture after the TTL instead of keeping it durable.',
        },
        ttl_hours: {
          type: 'number',
          description: 'Temporary-capture lifetime in hours; defaults to the project config.',
        },
      },
      output: {
        schema: {
          type: 'object',
          additionalProperties: false,
          properties: {
            ok: { type: 'boolean', required: true },
            code: { type: 'string', required: true },
            text: { type: 'string', required: true },
          },
        },
        render: (_args, value) => [{ type: 'text', text: value.text }],
      },
      async execute(args, exec) {
        try {
          const { project } = requireWorkspace(exec);
          if (args.scene !== undefined && !SCENES.includes(args.scene)) {
            throw new Error(`unknown scene: ${args.scene}`);
          }
          const recordId = workflowFor(project).start(args.summary, {
            temporary: args.temporary === true,
            ttlHours: args.ttl_hours,
            scenes: args.scene ? [args.scene] : [],
          });
          const cardPath = path.join(project, '.idc', 'work-items', recordId, 'CARD.md');
          return ok(
            'CAPTURED',
            `captured ${recordId}\ncard: ${cardPath}\n\nNext: idc_promote, then idc_shape with goal, scope and acceptance.`,
          );
        } catch (error) {
          return describeError(error);
        }
      },
      presentCall: (args) => ({ card: 'generic', title: 'IDC start', kind: 'other', rawInput: JSON.stringify(args) }),
    }),
  );

  ctx.tools.register(
    defineTool({
      name: 'idc_promote',
      description:
        'Promote a capture to a durable task and reserve its task ID. Shaping still required before edits.',
      parameters: {
        record_id: { type: 'string', required: true, description: RECORD_REF_DESCRIPTION },
        project_key: {
          type: 'string',
          description: 'Override the config project key for this task ID.',
        },
      },
      output: {
        schema: {
          type: 'object',
          additionalProperties: false,
          properties: {
            ok: { type: 'boolean', required: true },
            code: { type: 'string', required: true },
            text: { type: 'string', required: true },
          },
        },
        render: (_args, value) => [{ type: 'text', text: value.text }],
      },
      async execute(args, exec) {
        try {
          const { project } = requireWorkspace(exec);
          const recordId = requireRecord(project, args.record_id);
          const config = loadConfig(project);
          const key = args.project_key ?? config.project_key;
          if (typeof key !== 'string' || !/^[A-Z][A-Z0-9]*$/.test(key)) {
            throw new Error('project_key is missing or invalid; run idc_init first');
          }
          const taskId = workflowFor(project).promote(recordId, key);
          return ok('PROMOTED', `promoted ${recordId} to ${taskId}\n\nNext: idc_shape.`);
        } catch (error) {
          return describeError(error);
        }
      },
      presentCall: (args) => ({ card: 'generic', title: 'IDC promote', kind: 'other', rawInput: JSON.stringify(args) }),
    }),
  );

  ctx.tools.register(
    defineTool({
      name: 'idc_shape',
      description:
        'Translate intent into goal, scope, acceptance criteria, uncertainty and impact. Fills missing fields from the current state; a transition to shaped happens on the first call.',
      parameters: {
        record_id: { type: 'string', required: true, description: RECORD_REF_DESCRIPTION },
        goal: { type: 'string', description: 'Outcome to achieve, not an activity.' },
        explicit: { type: 'array', description: 'Explicit requests.', items: { type: 'string' } },
        repository_facts: { type: 'array', description: 'Verified repository facts.', items: { type: 'string' } },
        proposed_defaults: { type: 'array', description: 'Defaults the agent proposes.', items: { type: 'string' } },
        open_decisions: { type: 'array', description: 'Decision ids still open.', items: { type: 'string' } },
        scope: { type: 'array', description: 'Paths or areas in scope.', items: { type: 'string' } },
        acceptance: {
          type: 'array',
          description: 'Acceptance criteria; each needs a stable id.',
          items: {
            type: 'object',
            additionalProperties: false,
            properties: {
              id: { type: 'string', required: true, description: 'Stable short id, e.g. a1.' },
              statement: { type: 'string', required: true, description: 'Observable pass condition.' },
            },
          },
        },
        classifications: { type: 'array', description: 'Task types (FIX, FEAT, CHG, …).', items: { type: 'string' } },
        uncertainty: {
          type: 'array',
          description: 'unknown-cause requires discover; cross-boundary requires design.',
          items: { type: 'string' },
        },
        external_effect: { type: 'string', description: `Impact level (${LEVELS.join(', ')}).` },
        reversibility: { type: 'string', description: `Impact level (${LEVELS.join(', ')}).` },
        security: { type: 'string', description: `Impact level (${LEVELS.join(', ')}).` },
        privacy: { type: 'string', description: `Impact level (${LEVELS.join(', ')}).` },
        impacts_json: {
          type: 'string',
          description: 'Additional impact dimensions as a JSON object string.',
        },
      },
      output: {
        schema: {
          type: 'object',
          additionalProperties: false,
          properties: {
            ok: { type: 'boolean', required: true },
            code: { type: 'string', required: true },
            text: { type: 'string', required: true },
          },
        },
        render: (_args, value) => [{ type: 'text', text: value.text }],
      },
      async execute(args, exec) {
        try {
          const { project } = requireWorkspace(exec);
          const recordId = requireRecord(project, args.record_id);
          const workflow = workflowFor(project);
          workflow.shape(recordId, {
            goal: args.goal,
            explicit: args.explicit,
            repositoryFacts: args.repository_facts,
            proposedDefaults: args.proposed_defaults,
            openDecisions: args.open_decisions,
            scope: args.scope,
            acceptance: args.acceptance,
            classifications: args.classifications,
            uncertainty: args.uncertainty,
            impacts: buildImpacts(args),
          });
          const detail = recordDetail(project, recordId);
          const target = detail.record.obligations.target;
          const blocks = detail.record.obligations.hard_blocks;
          return ok(
            'SHAPED',
            `${detail.record.task_id ?? recordId} is ${detail.record.lifecycle}` +
              (target ? `\nnext target: ${target}` : '') +
              (blocks.length ? `\nstill blocked: ${blocks.join(', ')}` : '\nno hard blocks for the next transition'),
          );
        } catch (error) {
          return describeError(error);
        }
      },
      presentCall: (args) => ({ card: 'generic', title: 'IDC shape', kind: 'other', rawInput: JSON.stringify(args) }),
    }),
  );

  ctx.tools.register(
    defineTool({
      name: 'idc_record',
      description:
        'Record one or more domain events on a task: activity, condition, evidence, decision, permission, recovery, or requirement change. Events are evaluated against gates; a refused write leaves no trace.',
      parameters: {
        record_id: { type: 'string', required: true, description: RECORD_REF_DESCRIPTION },
        activity: {
          type: 'string',
          description: 'Activity name (discover, design, build, verify, ship, learn).',
        },
        condition: { type: 'string', description: 'Condition name, e.g. emergency.' },
        condition_active: { type: 'boolean', description: 'Set or clear the condition.' },
        evidence_kind: {
          type: 'string',
          description: `Provenance of the evidence (${PROVENANCE.join(', ')}).`,
        },
        evidence_result: {
          type: 'string',
          description: 'pass, fail, or inconclusive.',
        },
        evidence_summary: {
          type: 'string',
          description: 'What was observed. Avoid absolute user paths; use ~ or a workspace-relative path.',
        },
        evidence_acceptance_ids: {
          type: 'array',
          description: 'Acceptance ids this evidence maps to.',
          items: { type: 'string' },
        },
        evidence_reference: { type: 'string', description: 'Command, path, or URL.' },
        evidence_failure_attribution: {
          type: 'string',
          description: `Required for fail (${FAILURE_ATTRIBUTIONS.join(', ')}).`,
        },
        evidence_confirmation_ref: {
          type: 'string',
          description: 'Human confirmation reference; required for human-confirmed evidence.',
        },
        decision: { type: 'string', description: 'Open decision id to resolve.' },
        resolution: { type: 'string', description: 'Decision outcome.' },
        permission_effect: { type: 'string', description: 'External effect, e.g. commit.' },
        permission_status: {
          type: 'string',
          description: 'requested, granted, rejected, or executed.',
        },
        recovery_summary: { type: 'string', description: 'How the change can be undone.' },
        requirement_before: { type: 'string', description: 'Requirement before the change.' },
        requirement_after: { type: 'string', description: 'Requirement after the change.' },
        requirement_reason: { type: 'string', description: 'Why the requirement changed.' },
        human_confirmation: {
          type: 'boolean',
          description: HUMAN_CONFIRMATION_DESCRIPTION,
        },
      },
      output: {
        schema: {
          type: 'object',
          additionalProperties: false,
          properties: {
            ok: { type: 'boolean', required: true },
            code: { type: 'string', required: true },
            text: { type: 'string', required: true },
          },
        },
        render: (_args, value) => [{ type: 'text', text: value.text }],
      },
      async execute(args, exec) {
        try {
          const { project } = requireWorkspace(exec);
          const recordId = requireRecord(project, args.record_id);
          const workflow = workflowFor(project);
          const actor = args.human_confirmation === true ? 'human' : 'agent';
          const recorded = [];
          if (args.activity !== undefined) {
            workflow.recordActivity(recordId, args.activity, { actor });
            recorded.push(`activity ${args.activity}`);
          }
          if (args.condition !== undefined) {
            if (typeof args.condition_active !== 'boolean') {
              throw new Error('condition_active is required with condition');
            }
            workflow.setCondition(recordId, args.condition, args.condition_active, { actor });
            recorded.push(`condition ${args.condition}=${args.condition_active}`);
          }
          if (args.evidence_summary !== undefined) {
            if (!args.evidence_kind || !args.evidence_result) {
              throw new Error('evidence_kind and evidence_result are required with evidence_summary');
            }
            workflow.addEvidence(recordId, {
              kind: args.evidence_kind,
              summary: args.evidence_summary,
              result: args.evidence_result,
              acceptanceIds: args.evidence_acceptance_ids ?? [],
              reference: args.evidence_reference ?? null,
              actor,
              confirmationRef: args.evidence_confirmation_ref ?? null,
              failureAttribution: args.evidence_failure_attribution ?? null,
            });
            recorded.push(`evidence ${args.evidence_result}`);
          }
          if (args.decision !== undefined) {
            if (args.resolution === undefined) {
              throw new Error('resolution is required with decision');
            }
            workflow.resolveDecision(recordId, {
              decision: args.decision,
              resolution: args.resolution,
              actor,
            });
            recorded.push(`decision ${args.decision}`);
          }
          if (args.permission_effect !== undefined) {
            if (!args.permission_status) {
              throw new Error('permission_status is required with permission_effect');
            }
            workflow.permission(recordId, {
              effect: args.permission_effect,
              state: args.permission_status,
              actor,
            });
            recorded.push(`permission ${args.permission_effect}=${args.permission_status}`);
          }
          if (args.recovery_summary !== undefined) {
            workflow.recordRecovery(recordId, args.recovery_summary, { actor });
            recorded.push('recovery plan');
          }
          if (args.requirement_after !== undefined) {
            workflow.changeRequirement(recordId, {
              before: args.requirement_before ?? null,
              after: args.requirement_after,
              reason: args.requirement_reason ?? '',
              actor,
            });
            recorded.push('requirement change');
          }
          if (recorded.length === 0) {
            return fail('NOTHING_TO_RECORD', 'no recordable field was supplied');
          }
          const state = workflow.state(recordId);
          return ok(
            'RECORDED',
            `recorded: ${recorded.join(', ')}\n` +
              `${state.task_id ?? recordId} [${state.lifecycle}] · activities: ${state.activities.join(', ') || 'none'}`,
          );
        } catch (error) {
          return describeError(error);
        }
      },
      presentCall: (args) => ({ card: 'generic', title: 'IDC record', kind: 'other', rawInput: JSON.stringify(args) }),
    }),
  );

  ctx.tools.register(
    defineTool({
      name: 'idc_transition',
      description:
        'Move the task to shaped, active or validating. The gate is evaluated before writing; blocked calls return the missing obligations and change nothing.',
      parameters: {
        record_id: { type: 'string', required: true, description: RECORD_REF_DESCRIPTION },
        target: {
          type: 'string',
          required: true,
          description: 'shaped, active, or validating.',
        },
      },
      output: {
        schema: {
          type: 'object',
          additionalProperties: false,
          properties: {
            ok: { type: 'boolean', required: true },
            code: { type: 'string', required: true },
            text: { type: 'string', required: true },
          },
        },
        render: (_args, value) => [{ type: 'text', text: value.text }],
      },
      async execute(args, exec) {
        try {
          const { project } = requireWorkspace(exec);
          const recordId = requireRecord(project, args.record_id);
          const result = workflowFor(project).transition(recordId, args.target);
          const warnings = result.warnings.length ? `\nwarnings: ${result.warnings.join(', ')}` : '';
          return ok('TRANSITIONED', `now ${result.state.lifecycle}${warnings}`);
        } catch (error) {
          return describeError(error);
        }
      },
      presentCall: (args) => ({ card: 'generic', title: 'IDC transition', kind: 'other', rawInput: JSON.stringify(args) }),
    }),
  );

  ctx.tools.register(
    defineTool({
      name: 'idc_close',
      description:
        'Close the task with an outcome. Completion requires a goal, acceptance criteria, no open decisions and passing evidence for every acceptance id.',
      parameters: {
        record_id: { type: 'string', required: true, description: RECORD_REF_DESCRIPTION },
        outcome: {
          type: 'string',
          required: true,
          description: 'completed, superseded, unresolved, or cancelled.',
        },
        summary: { type: 'string', description: 'Closing summary.' },
      },
      output: {
        schema: {
          type: 'object',
          additionalProperties: false,
          properties: {
            ok: { type: 'boolean', required: true },
            code: { type: 'string', required: true },
            text: { type: 'string', required: true },
          },
        },
        render: (_args, value) => [{ type: 'text', text: value.text }],
      },
      async execute(args, exec) {
        try {
          const { project } = requireWorkspace(exec);
          const recordId = requireRecord(project, args.record_id);
          const result = workflowFor(project).close(recordId, {
            outcome: args.outcome,
            summary: args.summary ?? null,
          });
          const warnings = result.warnings.length ? `\nwarnings: ${result.warnings.join(', ')}` : '';
          return ok('CLOSED', `closed ${args.outcome}${warnings}`);
        } catch (error) {
          return describeError(error);
        }
      },
      presentCall: (args) => ({ card: 'generic', title: 'IDC close', kind: 'other', rawInput: JSON.stringify(args) }),
    }),
  );

  ctx.tools.register(
    defineTool({
      name: 'idc_learning',
      description:
        'Check the learning cadence, or review/dispose the learning candidate of a closed task. Review and disposal are human-only and need human_confirmation.',
      parameters: {
        action: {
          type: 'string',
          description: 'check (default), review, or dispose.',
        },
        record_id: { type: 'string', description: RECORD_REF_DESCRIPTION },
        outcome: { type: 'string', description: 'candidate or none (review).' },
        candidate: { type: 'string', description: 'Reusable lesson text (review).' },
        destination: {
          type: 'string',
          description: `Where the lesson belongs: ${LEARNING_DESTINATIONS.join(', ')}.`,
        },
        evidence_refs: {
          type: 'array',
          description: 'Evidence references backing the lesson.',
          items: { type: 'string' },
        },
        reason: { type: 'string', description: 'Why nothing is retained, or why disposing.' },
        disposition: {
          type: 'string',
          description: 'accepted, rejected, deferred, or merged (dispose).',
        },
        human_confirmation: {
          type: 'boolean',
          description: HUMAN_CONFIRMATION_DESCRIPTION,
        },
      },
      output: {
        schema: {
          type: 'object',
          additionalProperties: false,
          properties: {
            ok: { type: 'boolean', required: true },
            code: { type: 'string', required: true },
            text: { type: 'string', required: true },
          },
        },
        render: (_args, value) => [{ type: 'text', text: value.text }],
      },
      async execute(args, exec) {
        try {
          const { project } = requireWorkspace(exec);
          const action = args.action ?? 'check';
          if (action === 'check') {
            const cadence = checkLearningCadence(project);
            return ok(
              cadence.status === 'due' ? 'DUE' : 'QUIET',
              `learning: ${cadence.status} — ${cadence.reason}\n` +
                `completed since review: ${cadence.completed_since_review}/${cadence.threshold}` +
                (cadence.suggested_squad ? `\nsuggested: ${cadence.suggested_squad}` : ''),
            );
          }
          if (args.human_confirmation !== true) {
            return fail(
              'HUMAN_CONFIRMATION_REQUIRED',
              'learning review and disposal are human decisions; ask the user, then retry with human_confirmation=true',
            );
          }
          const recordId = requireRecord(project, args.record_id);
          const workflow = workflowFor(project);
          if (action === 'review') {
            workflow.reviewLearning(recordId, {
              outcome: args.outcome,
              candidate: args.candidate ?? null,
              evidenceRefs: args.evidence_refs ?? [],
              destination: args.destination ?? null,
              reason: args.reason ?? null,
              actor: 'human',
            });
            return ok('LEARNING_REVIEWED', `learning review recorded: ${args.outcome}`);
          }
          if (action === 'dispose') {
            workflow.disposeLearning(recordId, {
              disposition: args.disposition,
              reason: args.reason,
              actor: 'human',
            });
            return ok('LEARNING_DISPOSED', `learning disposition recorded: ${args.disposition}`);
          }
          return fail('INVALID_REQUEST', `unknown action: ${action}`);
        } catch (error) {
          return describeError(error);
        }
      },
      presentCall: (args) => ({ card: 'generic', title: 'IDC learning', kind: 'other', rawInput: JSON.stringify(args) }),
    }),
  );

  ctx.tools.register(
    defineTool({
      name: 'idc_discard',
      description: 'Discard a capture that was never promoted. Promoted tasks cannot be discarded.',
      parameters: {
        record_id: { type: 'string', required: true, description: RECORD_REF_DESCRIPTION },
        reason: { type: 'string', description: 'Why the capture is discarded.' },
      },
      output: {
        schema: {
          type: 'object',
          additionalProperties: false,
          properties: {
            ok: { type: 'boolean', required: true },
            code: { type: 'string', required: true },
            text: { type: 'string', required: true },
          },
        },
        render: (_args, value) => [{ type: 'text', text: value.text }],
      },
      async execute(args, exec) {
        try {
          const { project } = requireWorkspace(exec);
          const recordId = requireRecord(project, args.record_id);
          const state = workflowFor(project).discard(recordId, { reason: args.reason ?? null });
          return ok('DISCARDED', `discarded ${recordId} (${state.capture_disposition})`);
        } catch (error) {
          return describeError(error);
        }
      },
      presentCall: (args) => ({ card: 'generic', title: 'IDC discard', kind: 'other', rawInput: JSON.stringify(args) }),
    }),
  );
}
