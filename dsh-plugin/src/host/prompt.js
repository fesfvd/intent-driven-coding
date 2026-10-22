/** Resident method guidance, injected only for agents whose workspace has .idc/. */

import { findIdcRoot, statusLine } from './workspace.js';

const METHOD_TEXT = `IDC (Intent-Driven Coding) is active: this workspace contains .idc/ task records.
Before changing code, call idc_status. If the request is not captured yet: idc_start -> idc_promote -> idc_shape (goal, scope, acceptance ids, uncertainty, impact), then idc_transition active.
Record work with idc_record: activities, evidence, decisions, permissions, recovery plans. Every acceptance id needs passing evidence before idc_close completed.
Gates run before writing. A GATE_BLOCKED result means nothing was written; resolve the named blocks, never bypass them.
.idc/events.jsonl is the source of truth; cards and the index are projections. Never hand-edit .idc files.
Keep provenance truthful: command-evidence only from real command results, human-confirmed only after the user explicitly confirms (human_confirmation=true).`;

const SECTION_ORDER = 40;
const CONTEXT_ORDER = 41;

export function registerAgentGuidance(ctx) {
  const registered = new WeakSet();
  ctx.on('agent/created', (payload) => {
    const agent = payload?.agent;
    if (!agent || registered.has(agent)) return;
    const cwd = agent.session?.header?.cwd;
    if (typeof cwd !== 'string' || !findIdcRoot(cwd)) return;
    registered.add(agent);
    const agentCtx = agent.ctx;
    if (!agentCtx?.systemPrompt) return;
    let cached = { at: 0, project: null, text: '' };
    try {
      agentCtx.effect(
        () =>
          agentCtx.systemPrompt.section({
            name: 'idc-method',
            order: SECTION_ORDER,
            text: METHOD_TEXT,
          }),
        'idc: method section',
      );
      agentCtx.effect(
        () =>
          agentCtx.systemPrompt.context({
            name: 'idc-state',
            order: CONTEXT_ORDER,
            text: () => {
              const now = Date.now();
              if (cached.project && now - cached.at < 2000) return cached.text;
              const project = findIdcRoot(agent.session?.header?.cwd ?? '');
              if (!project) return '';
              const text = statusLine(project);
              cached = { at: now, project, text };
              return text;
            },
          }),
        'idc: state context',
      );
    } catch {
      // Guidance must never break agent creation.
    }
  });
}
