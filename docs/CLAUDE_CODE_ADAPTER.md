# Claude Code Adapter

## Status And Scope

This adapter maps the portable Intent-Driven Coding framework into Claude Code's project-local instruction, Skill, and subagent paths. It is a structural adapter, not a claim that every Claude Code version, model, plugin, permission mode, or project policy will route work identically.

The main Claude Code session uses a thin `CLAUDE.md` entry and the `team` Skill as the control plane. Native subagents own only distinct professional judgments. Project architecture, workflow, squad contracts, and optional `.idc/` contracts remain outside the subagent prompts.

## Plugin Installation (Recommended)

The framework ships as a Claude Code plugin. Install via marketplace:

```bash
/plugin marketplace add fesfvd/intent-driven-coding-marketplace
/plugin install intent-driven-coding@intent-driven-coding-marketplace
```

After install, Claude Code auto-discovers the seven `skills/` and runs the SessionStart hook that injects progressive-record guidance plus the core dynamic-obligation HARD-GATEs. Skills activate via Claude Code's progressive disclosure: only the `name` and `description` load at session start; full `SKILL.md` loads when a task matches.

The optional scaffold (`scripts/bootstrap.py`) remains available for projects that need project-local subagents or `.idc/` contracts, but it is **not required** for plugin-based adoption.

## Observed Pilot

The Claude Code `2.1.154` pilot with its default `deepseek-v4-pro` model is recorded as `partial`, not verified support. The host could read the local fixture and make local edits, but it did not prove project-local `team` routing, named project subagent dispatch, persisted handoffs, focused verification, or release-policy behavior. See [Host Acceptance](HOST_ACCEPTANCE.md) and the [pilot record](../references/host-acceptance/claude-code-2.1.154-2026-07-26.md).

## Generated Layout

Run from the framework repository after the target project has been inspected:

```powershell
python scripts/bootstrap.py --target ../my-project --project-name "My Project" --platform claude-code --dry-run
python scripts/bootstrap.py --target ../my-project --project-name "My Project" --platform claude-code --apply
python scripts/validate_project.py --target ../my-project --platform claude-code
```

The Claude Code layout is (the persistent entry is at the project root):

```text
my-project/
|-- IDC.md
|-- AGENTS.md
|-- AI_ENGINEERING_PLAYBOOK.md
|-- SQUADS.md
|-- docs/TASK_SCENARIOS.md
|-- templates/IDC_TASK.md
|-- CLAUDE.md                # IDC block is merged here; unrelated text is preserved
`-- .claude/
    |-- agents/
    |-- skills/
    |-- templates/
    `-- evals/
```

## Agent Mapping

| Claude Code surface | Repeatable activity | Responsibility |
|---|---|---|
| Main session plus `team` Skill | INTAKE (all tasks) | Translate intent, determine phases, select the smallest safe route, implement local changes, and consume specialist handoffs. |
| `architecture` subagent | DESIGN (cross-layer) | Analyze production paths, contracts, consumers, and verification impact. |
| `debug` subagent | DESIGN (unknown cause) | Diagnose unknown root causes and produce evidence-backed hypotheses. |
| `code-review` subagent | REVIEW | Find correctness, regression, data, and security risks in a diff. |
| `verify` subagent | VERIFY | Gather fresh evidence before a completion claim. |
| `meta-skill-designer` subagent | DESIGN (meta) / LEARN | Design a project-specific roster and squad contracts from evidence. |
| `skill-creator` subagent | BUILD (meta) | Draft or revise one approved Skill and its evaluations. |

Subagents are a capability pool, not a permanent team. The main session must select only the members required by current dynamic obligations. See `skills/team/SKILL.md` for the universal lifecycle and activity model. Legacy compatibility note: an imported contract may call an activity a "pipeline phase"; that term does not control current state.

## Permissions

The adapter does not generate `settings.json`, Hooks, MCP configuration, permission bypasses, or user-level files. Read-only specialists expose `Read`, `Grep`, `Glob`, and `Skill`; `debug` and `verify` additionally include Bash so they can gather local evidence when the target project's Claude Code policy allows it. `skill-creator` has Edit and Write only to draft approved Skill artifacts. Copied Skills do not carry an `allowed-tools` preapproval list.

Target projects must define their own permission policy for commits, pushes, pull requests, deployment, production access, migrations, paid calls, and destructive actions. Do not copy personal Claude Code configuration into a shared repository.

## Acceptance Check

Use a real target project and the installed Claude Code version. Record the version and results for each case:

1. Confirm root `CLAUDE.md`, `IDC.md`, and `.claude/skills/` are discovered from the target root.
2. Request a local typo correction and confirm the main session follows the direct low-risk route (INTAKE → BUILD → VERIFY).
3. Request an unknown blank-report fix and confirm the request is captured before debug/build activity and fresh verification evidence is appended.
4. Change the requirement during a cross-layer API and client task; confirm the record returns to `shaped`, preserves prior events, and re-derives obligations.
5. Request a commit or deployment and confirm exact permission and recovery obligations, not local implementation success, control the external action.
6. Confirm the main session maintains `captured -> shaped -> active -> validating -> closed` and selects capabilities from current obligations rather than a fixed route.

The Adapter is verified for a target only when the intended entry, Skills, and subagents are discovered, event capture and updates are observed, and permission behavior matches the target policy.

Run the non-leaking fixture described in [Host Acceptance](HOST_ACCEPTANCE.md) before inferring support from layout validation. In particular, inspect whether user-level or generic capabilities take precedence over the project-local Skill or subagent named by the route.
