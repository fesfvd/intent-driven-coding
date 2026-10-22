/**
 * Mirror the repository's method skills into the plugin bundle.
 *
 * The upstream files stay the source of truth. This script copies each
 * SKILL.md, rewrites CLI verbs to the matching idc_* tool names, adds a
 * whenToUse hint, and records upstream + content digests for drift checks.
 */

import crypto from 'node:crypto';
import { execFileSync } from 'node:child_process';
import fs from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';

const here = path.dirname(fileURLToPath(import.meta.url));
const pluginRoot = path.resolve(here, '..');
const repoRoot = path.resolve(pluginRoot, '..');
const sourceRoot = path.join(repoRoot, 'skills');
const targetRoot = path.join(pluginRoot, 'assets', 'skills');

const VERB_TO_TOOL = new Map([
  ['start', 'idc_start'],
  ['promote', 'idc_promote'],
  ['shape', 'idc_shape'],
  ['classify', 'idc_shape'],
  ['decide', 'idc_record'],
  ['activity', 'idc_record'],
  ['add-evidence', 'idc_record'],
  ['permission', 'idc_record'],
  ['recovery', 'idc_record'],
  ['change', 'idc_record'],
  ['transition', 'idc_transition'],
  ['close', 'idc_close'],
  ['show', 'idc_status'],
  ['status', 'idc_status'],
  ['learn-check', 'idc_learning'],
  ['learn-review', 'idc_learning'],
  ['learn-dispose', 'idc_learning'],
  ['discard', 'idc_discard'],
]);

function sha256(text) {
  return crypto.createHash('sha256').update(text, 'utf8').digest('hex');
}

function gitHead() {
  try {
    return execFileSync('git', ['rev-parse', 'HEAD'], {
      cwd: repoRoot,
      encoding: 'utf8',
    }).trim();
  } catch {
    return 'unknown';
  }
}

function parseSkill(text) {
  const match = /^---\r?\n([\s\S]*?)\r?\n---\r?\n?([\s\S]*)$/.exec(text);
  if (!match) throw new Error('SKILL.md is missing YAML frontmatter');
  const meta = {};
  for (const line of match[1].split(/\r?\n/)) {
    const colon = line.indexOf(':');
    if (colon <= 0) continue;
    meta[line.slice(0, colon).trim()] = line.slice(colon + 1).trim();
  }
  return { meta, body: match[2].trim() + '\n' };
}

function adaptBody(body) {
  const note =
    '> DSH edition: the `idc_*` names below are tools. Command flags in the examples map to tool parameters.\n\n';
  const rewritten = body.replace(/\bidc ([a-z][a-z-]*)\b/g, (whole, verb) => {
    const tool = VERB_TO_TOOL.get(verb);
    return tool ?? whole;
  });
  return note + rewritten;
}

function quoteYaml(value) {
  return `"${value.replace(/\\/g, '\\\\').replace(/"/g, '\\"')}"`;
}

function whenToUseOf(description) {
  const first = description.split(/(?<=[.!?。！？])\s+/)[0] ?? description;
  const trimmed = first.replace(/\s+/g, ' ').trim();
  return trimmed.length > 180 ? `${trimmed.slice(0, 179)}…` : trimmed;
}

function main() {
  const head = gitHead();
  const mirroredAt = new Date().toISOString();
  fs.rmSync(targetRoot, { recursive: true, force: true });
  let count = 0;
  for (const entry of fs.readdirSync(sourceRoot, { withFileTypes: true })) {
    if (!entry.isDirectory()) continue;
    const sourcePath = path.join(sourceRoot, entry.name, 'SKILL.md');
    if (!fs.existsSync(sourcePath)) continue;
    const upstream = fs.readFileSync(sourcePath, 'utf8');
    const { meta, body } = parseSkill(upstream);
    const name = meta.name || entry.name;
    if (!/^[a-z0-9]+(?:-[a-z0-9]+)*$/.test(name)) {
      throw new Error(`invalid skill name: ${name}`);
    }
    const description = meta.description || '';
    const content = adaptBody(body);
    const frontmatter = [
      '---',
      `name: ${name}`,
      `description: ${quoteYaml(description)}`,
      `whenToUse: ${quoteYaml(whenToUseOf(description))}`,
      '---',
      '',
    ].join('\n');
    const output = path.join(targetRoot, entry.name);
    fs.mkdirSync(output, { recursive: true });
    fs.writeFileSync(path.join(output, 'SKILL.md'), frontmatter + content, 'utf8');
    fs.writeFileSync(
      path.join(output, 'upstream.json'),
      JSON.stringify(
        {
          upstreamRef: head,
          upstreamPath: `skills/${entry.name}/SKILL.md`,
          upstreamSha256: sha256(upstream),
          contentSha256: sha256(frontmatter + content),
          mirroredAt,
        },
        null,
        2,
      ) + '\n',
      'utf8',
    );
    count += 1;
  }
  process.stdout.write(`mirrored ${count} skills into ${targetRoot}\n`);
}

main();
