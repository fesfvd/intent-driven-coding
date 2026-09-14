# {{PROJECT_NAME}} Claude Code Entry

Read `AGENTS.md`, `AI_ENGINEERING_PLAYBOOK.md`, and `SQUADS.md` before non-trivial work. Load the `team` Skill to translate ordinary-language requests, classify risk, and select the smallest safe route.

Capture actionable requests before substantial work and promote durable work to `IDC-<PROJECT>-<YYYYMMDD>-<NNN>`. Append material changes to `events.jsonl`; `docs/TASK_SCENARIOS.md` supplies mutable labels and `templates/IDC_TASK.md` describes the generated projection.

Use project-local Skills for stable methods and the native subagents only for distinct professional judgments. Available subagents are a capability pool, not a permanent team.

**Repository investigation:** If a `.codegraph/` index exists, prefer `codegraph_explore` over Read/Grep/Glob for architecture tracing, call-path analysis, and impact assessment. One symbol-level query replaces multiple file searches.

Track `captured -> shaped -> active -> validating -> closed` and derive dynamic obligations from current risk and evidence. Discovery, design, build, verify, review, and ship are repeatable activities. For legacy compatibility, old guidance may call these activities a "pipeline phase"; that vocabulary never overrides lifecycle or gates.

Preserve unrelated work. Do not commit, push, open a pull request, deploy, write production data, call paid services, or perform destructive actions without explicit authorization for the named effect.
