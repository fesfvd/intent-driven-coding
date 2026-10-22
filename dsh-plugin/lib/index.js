/** DSH host entry for the IDC plugin. */

import { registerAgentGuidance } from '../src/host/prompt.js';
import { registerSkills } from '../src/host/skills.js';
import { registerTools } from '../src/host/tools.js';

export const name = 'dsh-idc';

export const inject = ['tools', 'skills', 'systemPrompt'];

export function apply(ctx, config = {}) {
  const language = config.language === 'en' ? 'en' : 'zh';
  ctx.effect(() => registerTools(ctx), 'idc: tools');
  ctx.effect(() => registerSkills(ctx), 'idc: skills');
  registerAgentGuidance(ctx);
  void language;
}
