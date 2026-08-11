# OpenCode Adapter

## Status And Scope

This adapter maps the portable Intent-Driven Coding framework into OpenCode's project-local Agent and Skill discovery paths. It is a structural adapter, not a claim that every OpenCode version, model, provider, plugin, or project policy will route work identically.

The adapter keeps project architecture, workflow, and squad contracts in root Markdown files. It keeps specialist methods in OpenCode-discoverable Skills. It adds thin native Agent definitions so OpenCode can delegate distinct professional judgments without copying the full framework into every prompt.

## Plugin Installation (Recommended)

Add to the target project's `opencode.json`:

```json
{
  "plugin": [
    "intent-driven-coding@git+https://github.com/fesfvd/intent-driven-coding.git"
  ]
}
```

The in-process plugin registers the `skills/` directory and injects bootstrap context (pipeline phases + HARD-GATEs) at session start. See [.opencode/INSTALL.md](../.opencode/INSTALL.md) for manual setup.

## Observed Pilot

The OpenCode `1.18.5` pilot with `opencode/deepseek-v4-flash-free` is recorded as `partial`, not verified support. Project-local discovery was observed, but no case proved a complete named route, persisted handoff, focused verification, and policy-controlled release boundary. See [Host Acceptance](HOST_ACCEPTANCE.md) and the [pilot record](../references/host-acceptance/opencode-1.18.5-2026-07-26.md).

## Experimental Controller

[Orchestration Controller](ORCHESTRATION.md) can explicitly invoke a registered OpenCode Agent with `opencode run --agent <name>` for a selected local contract. It records controller-observed subprocess output and declared handoffs, but does not prove OpenCode's native project-capability precedence or enforce the Worker tool policy. Treat it as experimental until a real host-acceptance record closes those gaps.

## Generated Layout

Run from the framework repository after the target project has been inspected:

```powershell
python scripts/bootstrap.py --target ../my-project --project-name "My Project" --platform opencode --dry-run
python scripts/bootstrap.py --target ../my-project --project-name "My Project" --platform opencode --apply
python scripts/validate_project.py --target ../my-project --platform opencode
```

The OpenCode layout is:

```text
my-project/
|-- AGENTS.md
|-- AI_ENGINEERING_PLAYBOOK.md
|-- SQUADS.md
`-- .opencode/
    |-- agents/
    |-- skills/
    |-- templates/
    `-- evals/
```

OpenCode discovers project Skills from `.opencode/skills/<name>/SKILL.md` and native Agents from `.opencode/agents/*.md`.

## Agent Mapping

| OpenCode Agent | Mode | Pipeline phase | Responsibility |
|---|---|---|---|
| `team` | primary | INTAKE (all tasks) | Translate intent, determine phases, select the smallest safe route, delegate distinct judgments, and implement local changes. |
| `architecture` | subagent | DESIGN (cross-layer) | Produce an impact and contract analysis before cross-layer work. |
| `debug` | subagent | DESIGN (unknown cause) | Diagnose an unknown root cause without speculative patches. |
| `code-review` | subagent | REVIEW | Inspect a diff for real correctness and regression risks. |
| `verify` | subagent | VERIFY | Collect fresh evidence for completion claims. |
| `meta-skill-designer` | subagent | DESIGN (meta) / LEARN | Design a project-specific roster and squad contracts from evidence. |
| `skill-creator` | subagent | BUILD (meta) | Draft or improve an approved individual Skill and its evaluations. |

Available Agents are a capability pool, not a permanent team. The `team` Agent should select the smallest route registered in `SQUADS.md`. See `skills/team/SKILL.md` for the full pipeline phase model.

## Permissions

The adapter does not generate `opencode.json`, and its templates do not grant any `allow` or `ask` permissions. It therefore does not replace the target project's model selection, MCP servers, global permissions, or policy rules.

The `team` Agent inherits the target's task, Skill, and Bash policy. `architecture`, `code-review`, and `meta-skill-designer` deny both direct edits and Bash. `debug` and `verify` deny direct edits but inherit the target Bash policy so they can gather evidence when that policy allows it; they are not read-only Agents. Target projects must add their own OpenCode policy rules for commit, push, deployment commands, production access, migrations, paid calls, and other domain-specific effects.

Do not copy personal global OpenCode configuration into a shared repository. Review the target's existing `opencode.json` or `opencode.jsonc` before adding project-specific policy.

Before installation, resolve duplicate Skill names in `.claude/skills/` and `.agents/skills/` from the target directory through its Git worktree root. Also resolve `.opencode/skills/` in ancestor directories; the target directory's own `.opencode/skills/` is preserved for re-running the bootstrap. OpenCode also discovers compatible user-level Skill roots; inspect those separately because the bootstrap script does not modify or validate personal configuration.

## Acceptance Check

Use a real target project and the installed OpenCode version. Start OpenCode at the target root, select the `team` primary Agent, and record the installed version plus results for each case:

1. Ask for a local typo correction. Confirm it stays on the direct, low-risk route and uses a narrow check (INTAKE → BUILD → VERIFY).
2. Ask to find and fix an unknown blank report. Confirm `debug` is selected or explicitly loaded before patching (INTAKE → DESIGN → BUILD → VERIFY).
3. Ask for an API field that is displayed in the client. Confirm `architecture` produces an impact contract and `verify` reports fresh evidence (INTAKE → DESIGN → BUILD → VERIFY → REVIEW).
4. With the target's commit and push policy configured as `ask` or `deny`, ask to commit or push the completed change. Confirm the policy governs the named effect and local implementation is not treated as authorization (SHIP phase gated).
5. Confirm the `team` primary Agent identifies pipeline phases before selecting squads, and gates DESIGN→BUILD and BUILD→SHIP transitions.

The Adapter is verified for a target only when OpenCode discovers the generated Skills and Agents, pipeline phases are observed, the routing cases behave as expected, and permission behavior matches the target's policy.

Use the non-leaking fixture in [Host Acceptance](HOST_ACCEPTANCE.md) when a real project cannot safely carry intentional acceptance failures. Inspect project-local versus user-level capability precedence before interpreting a generic capability as evidence that a named project Agent ran.
