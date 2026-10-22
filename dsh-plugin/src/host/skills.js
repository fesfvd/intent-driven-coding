/** Register the bundled IDC method skills as runtime skills. */

import fs from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';

const here = path.dirname(fileURLToPath(import.meta.url));
const skillsRoot = path.resolve(here, '..', '..', 'assets', 'skills');

export function registerSkills(ctx) {
  let entries;
  try {
    entries = fs.readdirSync(skillsRoot, { withFileTypes: true });
  } catch {
    return;
  }
  for (const entry of entries) {
    if (!entry.isDirectory()) continue;
    let text;
    try {
      text = fs.readFileSync(path.join(skillsRoot, entry.name, 'SKILL.md'), 'utf8');
    } catch {
      continue;
    }
    const parsed = parseSkill(text);
    if (!parsed) continue;
    try {
      ctx.skills.register({
        name: parsed.name || entry.name,
        description: parsed.description,
        whenToUse: parsed.whenToUse,
        content: parsed.content,
      });
    } catch {
      // A malformed skill must not prevent the plugin from loading.
    }
  }
}

export function parseSkill(text) {
  const match = /^---\r?\n([\s\S]*?)\r?\n---\r?\n?([\s\S]*)$/.exec(text);
  if (!match) return null;
  const meta = {};
  for (const line of match[1].split(/\r?\n/)) {
    const colon = line.indexOf(':');
    if (colon <= 0) continue;
    const key = line.slice(0, colon).trim();
    let value = line.slice(colon + 1).trim();
    if (
      (value.startsWith('"') && value.endsWith('"')) ||
      (value.startsWith("'") && value.endsWith("'"))
    ) {
      value = value.slice(1, -1);
    }
    meta[key] = value;
  }
  if (!meta.name || !meta.description) return null;
  return {
    name: meta.name,
    description: meta.description,
    whenToUse: meta.whenToUse,
    content: match[2].trim() + '\n',
  };
}
