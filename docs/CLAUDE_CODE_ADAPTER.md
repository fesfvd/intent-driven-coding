# Claude Code Adapter

## Status And Scope

This adapter maps the portable Intent-Driven Coding framework into Claude Code's project-local instruction, Skill, and subagent paths. It is a structural adapter, not a claim that every Claude Code version, model, plugin, permission mode, or project policy will route work identically.

The main Claude Code session uses a thin `CLAUDE.md` entry and the `team` Skill as the control plane. Native subagents own only distinct professional judgments. Project architecture, workflow, squad contracts, and optional `.idc/` contracts remain outside the subagent prompts.

## Generated Layout

Run from the framework repository after the target project has been inspected:

```powershell
python scripts/bootstrap.py --target ../my-project --project-name "My Project" --platform claude-code --dry-run
python scripts/bootstrap.py --target ../my-project --project-name "My Project" --platform claude-code --apply
python scripts/validate_project.py --target ../my-project --platform claude-code
```

The Claude Code layout is:

```text
my-project/
|-- AGENTS.md
|-- AI_ENGINEERING_PLAYBOOK.md
|-- SQUADS.md
`-- .claude/
    |-- CLAUDE.md
    |-- agents/
    |-- skills/
    |-- templates/
    `-- evals/
```

## Agent Mapping

| Claude Code surface | Responsibility |
|---|---|
| Main session plus `team` Skill | Translate intent, select the smallest safe route, implement local changes, and consume specialist handoffs. |
| `architecture` subagent | Analyze production paths, contracts, consumers, and verification impact. |
| `debug` subagent | Diagnose unknown root causes and produce evidence-backed hypotheses. |
| `code-review` subagent | Find correctness, regression, data, and security risks in a diff. |
| `verify` subagent | Gather fresh evidence before a completion claim. |
| `meta-skill-designer` subagent | Design a project-specific roster and squad contracts from evidence. |
| `skill-creator` subagent | Draft or revise one approved Skill and its evaluations. |

Subagents are a capability pool, not a permanent team. The main session must select only the members required by `SQUADS.md` or a project contract.

## Permissions

The adapter does not generate `settings.json`, Hooks, MCP configuration, permission bypasses, or user-level files. Read-only specialists expose `Read`, `Grep`, `Glob`, and `Skill`; `debug` and `verify` additionally include Bash so they can gather local evidence when the target project's Claude Code policy allows it. `skill-creator` has Edit and Write only to draft approved Skill artifacts. Copied Skills do not carry an `allowed-tools` preapproval list.

Target projects must define their own permission policy for commits, pushes, pull requests, deployment, production access, migrations, paid calls, and destructive actions. Do not copy personal Claude Code configuration into a shared repository.

## Acceptance Check

Use a real target project and the installed Claude Code version. Record the version and results for each case:

1. Confirm `CLAUDE.md` and `.claude/skills/` are discovered from the target root.
2. Request a local typo correction and confirm the main session follows the direct low-risk route.
3. Request an unknown blank-report fix and confirm `debug` is invoked or loaded before patching.
4. Request a cross-layer API and client change, then confirm `architecture` and `verify` produce usable handoffs and fresh evidence.
5. Request a commit or deployment and confirm the target's policy, not local implementation success, controls the external action.

The Adapter is verified for a target only when the intended entry, Skills, and subagents are discovered and its observed permission behavior matches the target policy.
