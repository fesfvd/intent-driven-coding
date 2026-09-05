# {{PROJECT_NAME}} Claude Code Entry

Read `AGENTS.md`, `AI_ENGINEERING_PLAYBOOK.md`, and `SQUADS.md` before non-trivial work. Load the `team` Skill to translate ordinary-language requests, classify risk, and select the smallest safe route.

Classify the task with `docs/TASK_SCENARIOS.md` and show an `IDC-<PROJECT>-<SCENARIO>-<YYYYMMDD>-<NNN>` start card from `templates/IDC_TASK.md` before implementation.

Use project-local Skills for stable methods and the native subagents only for distinct professional judgments. Available subagents are a capability pool, not a permanent team.

**Repository investigation:** If a `.codegraph/` index exists, prefer `codegraph_explore` over Read/Grep/Glob for architecture tracing, call-path analysis, and impact assessment. One symbol-level query replaces multiple file searches.

Track the current pipeline phase (INTAKE → DESIGN? → BUILD → VERIFY → REVIEW? → SHIP?) per the `team` Skill. "Continue" resumes the latest unfinished phase; it never bypasses the VERIFY or SHIP gate.

Preserve unrelated work. Do not commit, push, open a pull request, deploy, write production data, call paid services, or perform destructive actions without explicit authorization for the named effect.
