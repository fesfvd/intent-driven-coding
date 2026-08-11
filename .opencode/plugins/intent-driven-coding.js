// Intent-Driven Coding — OpenCode in-process plugin
// Registers the skills directory and injects team Skill bootstrap context at session start.
// Adapted from Superpowers .opencode/plugins/superpowers.js (MIT License)

const SKILLS_DIR = new URL("../../skills", import.meta.url).pathname;
const INJECTED_MARKER = "INTENT-DRIVEN-CODING-ACTIVE";
const VERSION = "1.0.0";

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
    `Intent-Driven Coding v${VERSION} active. Pipeline phase model + Skill execution checklists.`,
    ``,
    `The \`team\` Skill is your control plane. Core pipeline:`,
    `  INTAKE (classify intent) → DESIGN? (architecture/debug) → BUILD → VERIFY → REVIEW? → SHIP?`,
    ``,
    `Before any non-trivial task:`,
    `- Load the \`team\` Skill to classify intent and determine required pipeline phases.`,
    `- Select the smallest squad for the active phase — 2 members default, 3 max.`,
    `- Do NOT enter BUILD until DESIGN gate is satisfied (if DESIGN is required).`,
    `- Do NOT enter SHIP without explicit user authorization.`,
    ``,
    `Hard rules:`,
    `- No completion claim without fresh verification evidence.`,
    `- No commit/push/deploy/production write/paid call without explicit authorization.`,
    `- Query volatile repository facts; do not freeze them into Skills.`,
    ``,
    `Read \`skills/team/SKILL.md\` for the full pipeline phase model.`,
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
