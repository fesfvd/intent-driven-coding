# Platform Adapters

The method and Markdown files are tool-neutral. Automatic instruction loading, Skill discovery, allowed tool names, and permission configuration are platform-specific.

Before adapting, identify the installed product and version. Platform conventions evolve; inspect current documentation and existing repository configuration instead of relying only on this file.

## Generic Setup

1. Point the agent's project instruction entry at `.agent/AGENT_ENTRY.md`, or merge that thin entry into the platform's recognized project instruction file.
2. Install or reference `.agent/skills/*/SKILL.md` using the platform's project-local or user-level Skill mechanism.
3. Keep `AGENTS.md`, `AI_ENGINEERING_PLAYBOOK.md`, and `SQUADS.md` at the project root unless your platform requires another path.
4. Map `allowed-tools` names to the platform's actual tools.
5. Test one direct task, one squad task, one ambiguity, and one permission gate.

## Claude Code

Common project conventions include a root `CLAUDE.md` instruction entry and project-local Skills under `.claude/skills/<name>/SKILL.md`. Confirm these conventions against the installed version before writing.

Recommended adaptation:

1. Create a thin `CLAUDE.md` that points to `AGENTS.md`, `AI_ENGINEERING_PLAYBOOK.md`, and `SQUADS.md` instead of copying their complete content.
2. Install only the selected project Skills under the project-local Skill location recognized by that Claude Code version.
3. Preserve Skill frontmatter and map `allowed-tools` to tools actually available in the environment.
4. Verify that the project entry loads and realistic prompts trigger or explicitly read the expected Skills.
5. If subagents are available, they may execute distinct squad roles. Otherwise the main agent can apply Skills sequentially; the squad model does not require separate processes.

Do not assume the neutral `.agent/` directory is discovered automatically.

## OpenCode

OpenCode can use repository guidance such as `AGENTS.md` and supports configurable agents, commands, permissions, and Skills. Exact locations and schemas depend on the installed version and user/project configuration.

Recommended adaptation:

1. Keep architecture semantics in root `AGENTS.md`.
2. Connect a thin OpenCode-recognized entry or configuration to the playbook and `SQUADS.md`.
3. Install selected Skills in the project-local location recognized by the current OpenCode setup, or configure agents to read them on demand.
4. Translate `allowed-tools` and permission gates into the actual OpenCode tool and permission names.
5. Test automatic routing, direct Skill loading, and confirmation behavior rather than assuming compatibility from file shape alone.

Do not copy personal global OpenCode configuration into a shared project.

## Codex CLI And Codex-Based Agents

Codex commonly recognizes repository guidance through `AGENTS.md`. Skill and agent mechanisms may differ between Codex products and versions.

Recommended adaptation:

1. Use `AGENTS.md` as the architecture and repository-guidance anchor.
2. Reference `AI_ENGINEERING_PLAYBOOK.md` and `SQUADS.md` from the platform-recognized instruction entry.
3. If the installed Codex environment supports project Skills, place selected Skills in its documented location. Otherwise have the main agent read the relevant `SKILL.md` explicitly when a squad is selected.
4. Verify tool permissions and external-action confirmation behavior.
5. Do not claim automatic Skill triggering until it has been tested in that environment.

## Cursor, GitHub Copilot, Windsurf, Cline, Roo Code, And Others

For IDE assistants and other coding agents:

1. Find the tool's current project-instruction mechanism.
2. Keep that entry thin and point it to the framework artifacts.
3. Determine whether the tool supports reusable Skills, rules, agents, commands, or only explicit file reading.
4. Map selected Skill content into the closest supported mechanism.
5. Test discovery, context loading, tool permissions, and external-action confirmation.

When no reusable Skill mechanism exists, use `SQUADS.md` as the routing contract and read the required `SKILL.md` files explicitly.

## Compatibility Claim

The repository does not claim automatic compatibility with every coding agent. It provides portable content and a neutral generated layout. A platform is verified only after its entry loading, Skill triggering, tool mapping, and permission behavior have been tested there.

If a platform does not support automatic Skills, the main agent can still read the relevant `SKILL.md` on demand and follow the registered squad in `SQUADS.md`.
