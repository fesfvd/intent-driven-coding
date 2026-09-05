# AI-First, Human-Guided Quick Start

The human does not need to study the whole framework first. The recommended path is for the coding agent to learn what the current task requires, deliver useful work, and explain the relevant concepts back to the user. Human and AI then use real evidence, experience, and correction to grow project-specific guidance over time.

## Install (Plugin — Recommended)

**Claude Code**:
```bash
/plugin marketplace add fesfvd/intent-driven-coding-marketplace
/plugin install intent-driven-coding@intent-driven-coding-marketplace
```

**OpenCode**: add to target project `opencode.json`:
```json
{ "plugin": ["intent-driven-coding@git+https://github.com/fesfvd/intent-driven-coding.git"] }
```

After plugin install, the agent auto-receives pipeline phase guidance at session start. The manual paths below remain available.

## Manual Setup

### First Useful Task

Place this repository beside the target project:

```text
workspace/
|-- my-project/
`-- intent-driven-coding/
```

Start the coding agent in `my-project` and give it this instruction:

```text
Read ../intent-driven-coding/AI_START_HERE.md, identify your host-platform section, and then handle my next real task. Do not stop to install the full framework. Investigate the relevant repository path, use the smallest safe method, implement, and verify. Briefly teach me the core concept, evidence, uncertainty, or tradeoff when it affects how we should work. Learn the project with me and propose durable Skills or squads only after repeated evidence and my judgment justify them.
```

Then give it a real bug, feature, review, or refactor request. The agent should
classify it with [`docs/TASK_SCENARIOS.md`](docs/TASK_SCENARIOS.md) and show a
compact `IDC-<PROJECT>-<SCENARIO>-<YYYYMMDD>-<NNN>` task card before starting
non-trivial work. The first useful result is a verified project outcome, not a
generated framework directory.

## What The Agent Does Incrementally

During ordinary work the agent should:

1. Learn the host platform's real entry, Skill, agent, and permission mechanisms.
2. Investigate only the repository paths needed for the current goal.
3. Apply requirement translation, the relevant specialist method, and fresh verification.
4. Explain the core concept, evidence, uncertainty, or tradeoff when it affects a shared decision.
5. Combine observed friction and risks with the user's experience, corrections, and priorities.
6. Add a thin entry, architecture note, Skill, squad, or evaluation only when shared evidence and judgment show it will help future work.
7. Keep a durable task card under `.idc/tasks/` when the work has meaningful scope, impact, handoffs, or decisions.

## Human And AI Learn Together

The agent takes the first pass at framework learning, repository investigation, implementation, and verification. It also explains relevant concepts at decision time instead of requiring an upfront course.

The human contributes more than approval. The user brings goals, domain knowledge, development experience, observed pain, preferences, skepticism, and the final judgment about whether an abstraction will improve future work. Less experienced users can begin with smaller, better-explained decisions; experienced users can challenge assumptions and identify deeper patterns sooner.

The agent should propose, explain, and execute. The human should question, correct, and choose. Neither model capability nor user experience alone is sufficient for a strong project-specific system.

## Optional: Deliberate System Build-Out

Use the remaining steps when repeated work and human judgment now justify durable project artifacts. They are not prerequisites for the first task.

Use the ready-to-paste Chinese prompt in `README.md`, or express the same goal in your own language.

## Optional: Scaffold Files

The following steps create a neutral skeleton only. Use them after the agent understands the target, or when manual file creation is the only thing you want to automate.

Install the framework validation dependency once:

```powershell
python -m pip install -r requirements.txt
```

## 1. Preview The Installation

From this repository:

```powershell
python scripts/bootstrap.py --target ../my-project --project-name "My Project" --dry-run
```

Review every destination path. The script performs no writes in dry-run mode.

## 2. Install The Starter Files

```powershell
python scripts/bootstrap.py --target ../my-project --project-name "My Project" --apply
```

The installer refuses to replace existing files. If your project already has `AGENTS.md` or an engineering playbook, merge the templates manually rather than immediately using `--force`.

### OpenCode Native Layout

When the target uses OpenCode and you want the optional native Agent and Skill layout, use the OpenCode platform flag instead of the neutral default:

```powershell
python scripts/bootstrap.py --target ../my-project --project-name "My Project" --platform opencode --dry-run
python scripts/bootstrap.py --target ../my-project --project-name "My Project" --platform opencode --apply
python scripts/validate_project.py --target ../my-project --platform opencode
```

This generates `.opencode/agents/` and `.opencode/skills/` without creating or replacing `opencode.json`. Read [OpenCode Adapter](docs/OPENCODE_ADAPTER.md) before relying on automatic routing or permission behavior.

### Claude Code Native Layout

When the target uses Claude Code and you want the optional native instruction, Skill, and subagent layout, use the Claude Code platform flag:

```powershell
python scripts/bootstrap.py --target ../my-project --project-name "My Project" --platform claude-code --dry-run
python scripts/bootstrap.py --target ../my-project --project-name "My Project" --platform claude-code --apply
python scripts/validate_project.py --target ../my-project --platform claude-code
```

This generates `.claude/CLAUDE.md`, `.claude/agents/`, and `.claude/skills/` without creating or replacing `settings.json`. Read [Claude Code Adapter](docs/CLAUDE_CODE_ADAPTER.md) before relying on discovery or permission behavior.

## 3. Fill The Architecture Map First

Open `AGENTS.md` in the target project and replace every double-brace template token.

At minimum, document:

1. The product in one paragraph.
2. The real production entry points.
3. One end-to-end critical data flow.
4. Persisted data and external side effects.
5. Cross-file or source/generated-artifact synchronization rules.
6. The commands that prove common changes work.

Do not list every file. Explain the boundaries that source search alone cannot reveal.

## 4. Configure The Playbook

Open `AI_ENGINEERING_PLAYBOOK.md` and replace:

- the focused test command placeholder;
- the full relevant test-suite placeholder;
- the lint command placeholder;
- the type-check command placeholder;
- the build command placeholder.

Delete checks your project does not use. A fake command is worse than an explicit `not applicable`.

## 5. Register Your First Squads

Open `SQUADS.md`. Keep the generic formations that match your project and replace the custom placeholder with one real recurring outcome.

Use `.agent/templates/SQUAD.md` for the neutral layout, `.opencode/templates/SQUAD.md` for the OpenCode layout, or `.claude/templates/SQUAD.md` for the Claude Code layout, then check:

- the formation has two members by default and at most three;
- each member owns a distinct judgment;
- every handoff names an artifact;
- the final member proves the outcome;
- external side effects remain human-gated.

For a deeper workshop, follow `docs/SQUAD_WORKSHOP.md` in this source repository.

Then adapt `.agent/evals/squad-routing.json` and `.agent/evals/skill-design.json` for the neutral layout, `.opencode/evals/squad-routing.json` and `.opencode/evals/skill-design.json` for the OpenCode layout, or `.claude/evals/squad-routing.json` and `.claude/evals/skill-design.json` for the Claude Code layout, to your real user language and project boundaries.

## 6. Connect Your Agent

`.agent/AGENT_ENTRY.md` is tool-neutral. Point your coding agent at it using the mechanism supported by that product. For the OpenCode layout, start from the generated `team` primary Agent instead. For the Claude Code layout, start from `.claude/CLAUDE.md`.

Common approaches:

- Rename or copy its short content into the instruction filename your agent automatically loads.
- Keep it as a canonical source and reference it from an existing agent entry.
- Install `.agent/skills/` into your agent's project-local or user-level Skill directory.

Do not duplicate project facts in both the entry and Skills. The entry should point to `AGENTS.md`; Skills should query the current repository.

## 7. Run Validation

Run from this framework repository:

```powershell
python scripts/validate_repository.py
python scripts/validate_contracts.py
python scripts/evaluate_contracts.py
python scripts/audit_skills.py
python scripts/validate_project.py --target ../my-project
python -m unittest discover -s tests -v
```

For the OpenCode layout, replace the project validation command with:

```powershell
python scripts/validate_project.py --target ../my-project --platform opencode
```

For the Claude Code layout, replace the project validation command with:

```powershell
python scripts/validate_project.py --target ../my-project --platform claude-code
```

Then search the generated target files for unresolved placeholders:

```powershell
python scripts/bootstrap.py --target ../my-project --project-name "My Project" --dry-run
```

The project validator reports unresolved placeholders, missing Skills, invalid squad sizes, and suspicious local/private facts. The second dry run should report existing files and make no changes.

## 8. Test With Four Requests

Use ordinary language, not Skill names:

```text
This page is cramped on mobile. Fix it without changing the desktop hierarchy.
```

Expected behavior: the agent locates the production UI, investigates responsive constraints, and asks only if different information hierarchies are genuinely valid.

```text
The report is blank. Find the cause and fix it.
```

Expected behavior: the agent reproduces the problem and traces the data path instead of asking whether it is a frontend or backend issue.

```text
Add a public switch to documents.
```

Expected behavior: the agent inspects existing privacy fields and asks if "public" could mean materially different content exposure.

```text
Our project keeps repeating the same API design, permission review, and release checks. Build a professional squad for it.
```

Expected behavior: `meta-skill-designer` derives distinct roles and a two- or three-Skill squad before `skill-creator` drafts or revises individual Skills.

## Exit Criteria

Your first setup is usable when:

- All template tokens are resolved.
- The agent can name the actual production entry and critical flow from `AGENTS.md`.
- The playbook contains executable verification commands.
- A low-risk request does not trigger a long Skill chain.
- A real product ambiguity is surfaced rather than silently decided.
- The agent does not infer permission to commit, push, deploy, or write production data.
- The project can explain why every registered squad needs each of its two or three members.
- Skill design requests route through the meta-design squad rather than immediately creating more prompts.
- The target platform actually discovers the intended entry and Skills, or the project documents an on-demand reading fallback.
- The result reflects the target repository rather than unchanged examples from this framework.
