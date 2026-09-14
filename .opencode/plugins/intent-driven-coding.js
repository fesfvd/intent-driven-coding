// Intent-Driven Coding — OpenCode in-process plugin
// Registers the skills directory and injects team Skill bootstrap context at session start.
// Adapted from Superpowers .opencode/plugins/superpowers.js (MIT License)

const SKILLS_DIR = new URL("../../skills", import.meta.url).pathname;
const INJECTED_MARKER = "INTENT-DRIVEN-CODING-ACTIVE";
const VERSION = "1.1.1";

export function config(config) {
  config.skills = config.skills || {};
  config.skills.paths = config.skills.paths || [];
  if (!config.skills.paths.includes(SKILLS_DIR)) {
    config.skills.paths.push(SKILLS_DIR);
  }
}

function buildBootstrap() {
  return [
    `<EXTREMELY_IMPORTANT>${INJECTED_MARKER}`,
    `Intent-Driven Coding v${VERSION} active. Progressive records + dynamic obligations.`,
    ``,
    `The \`team\` Skill is your control plane. Universal lifecycle:`,
    `  captured → shaped → active → validating → closed`,
    ``,
    `Before any non-trivial task:`,
    `- Load the \`team\` Skill and capture the request before investigation or mutation.`,
    `- Use \`docs/TASK_SCENARIOS.md\` for mutable labels; \`templates/IDC_TASK.md\` documents the generated projection.`,
    `- Promote only when investigation, a material decision, or a change begins.`,
    `- Derive dynamic obligations from impact, uncertainty, evidence, and requested effects.`,
    `- Select the smallest useful specialist chain; direct work is valid for low risk.`,
    ``,
    `Hard rules:`,
    `- No completion claim without fresh evidence mapped to acceptance.`,
    `- No commit/push/deploy/production write/paid call without explicit authorization for the exact effect.`,
    `- Requirement and classification changes append events; do not overwrite history.`,
    `- Query volatile repository facts; do not freeze them into Skills.`,
    ``,
    `Read \`skills/team/SKILL.md\` for the progressive lifecycle and dynamic obligations.`,
    `</EXTREMELY_IMPORTANT>`
  ].join("\n");
}

export const experimental = {
  chat: {
    messages: {
      transform(messages) {
        // Dedup: skip if already injected in this session
        const alreadyInjected = messages.some(
          (m) => m.content && typeof m.content === "string" && m.content.includes(INJECTED_MARKER)
        );
        if (alreadyInjected) return;

        const bootstrap = buildBootstrap();

        // Inject before the first user message
        for (let i = 0; i < messages.length; i++) {
          if (messages[i].role === "user") {
            messages[i].content = bootstrap + "\n\n" + (messages[i].content || "");
            break;
          }
        }
      }
    }
  }
};
