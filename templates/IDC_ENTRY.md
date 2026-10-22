<!-- IDC:BEGIN -->
## IDC: Mandatory Agent Workflow

This project uses Intent-Driven Coding (IDC). You MUST apply these rules to every actionable request within the user's authorized scope.

1. **Capture before work.** Before investigating or editing, read the project-root `IDC.md` and run `idc start --project . --summary "<request>"` from the project root. Retain the returned `record_id`; include its state, scenario labels, and outstanding obligations in your first work report. If capture is unavailable or fails, report the setup gap; you MUST NOT claim the request was recorded.
2. **Promote and shape.** Before substantive investigation, a material decision, or implementation, run `idc promote --project . --record <record-id>`. Before implementation, record the goal, scope, acceptance criteria, and impact through `idc shape`; separate explicit intent, repository facts, defaults, and open decisions. Use the same record for follow-ups to the same task.
3. **Ground and route.** Inspect current source, configuration, and tests before deciding changes. Use `AGENTS.md` for architecture, `AI_ENGINEERING_PLAYBOOK.md` for detailed workflow, and the smallest sufficient route in `SQUADS.md`. Load relevant Skills on demand; the user need not name them. Preserve unrelated workspace changes.
4. **Maintain the record.** Use IDC commands/tools to record material changes and evidence. `.idc/work-items/<record-id>/events.jsonl` is authoritative; cards and indexes are generated views. You MUST satisfy current dynamic obligations before gated actions or closure; never bypass a hard block or hand-edit generated state to imply success.
5. **Prove completion.** Run fresh verification appropriate to the change, record evidence against acceptance criteria, and close the record with an explicit outcome. You MUST NOT claim completion, correctness, or readiness without evidence; report failed or skipped checks and remaining limitations.
6. **Respect authorization.** Ask only for material unresolved decisions. Commit, push, PR creation, deployment, production writes, paid calls, external submissions, and destructive actions require explicit authorization for that effect. An IDC record or permission entry does not grant authorization.
7. **Learn at checkpoints.** Run `idc learn-check --project . --json`. Keep `quiet` quiet; route `learning-curator` only when `due`. Apply learned changes to durable guidance only after explicit human disposition.

Use the project root as `--project` when working elsewhere. Read `IDC.md` and its references for details needed by the current task; these entry rules apply before those details are loaded.
<!-- IDC:END -->
