# {{PROJECT_NAME}} Agent Entry

This file is a thin entry point. It must not duplicate the architecture manual, API catalog, or changing runtime state.

## Sources Of Truth

Use this order:

1. Current source, configuration, schemas, and tests.
2. Generated architecture indexes, if present.
3. `AGENTS.md` for architecture semantics, critical flows, and impact boundaries.
4. `IDC.md` for the installed IDC operating model and source map.
5. `AI_ENGINEERING_PLAYBOOK.md` for task translation, risk, verification, and completion rules.
6. `SQUADS.md` for registered two- or three-Skill outcome formations.
7. Project design and operations documents when relevant.
8. Skills for stable professional methods; verify volatile facts in the repository.

When documentation conflicts with executable evidence, follow source/tests and correct documentation drift within task scope.

## Execution Rules

- On first adoption, learn while delivering: handle the current task with the smallest safe route and do not block useful work on full framework setup.
- Collect repeated friction, risk, and handoff evidence during normal work; combine it with the user's experience and judgment before creating durable Skills or squads.
- Teach the user through brief decision explanations rather than requiring prior framework study. Expose relevant concepts, evidence, uncertainty, and tradeoffs so the user can question and correct the system.
- Human judgment is not limited to permission gates. Ask for lived pain, priorities, objections, and decisions about which abstractions should become durable project practice.
- The user may describe a goal or symptom in ordinary language. Translate it into an executable task without inventing requirements.
- Capture actionable requests before substantial work, promote durable work to `IDC-<PROJECT>-<YYYYMMDD>-<NNN>`, and append every material change to `events.jsonl`. Use `docs/TASK_SCENARIOS.md` for mutable labels and `templates/IDC_TASK.md` for the generated projection contract; satisfy current dynamic obligations before gated effects or closure.
- Resolve the language of user-facing final presentation from explicit preference first, then the current user language. Preserve code, commands, identifiers, APIs, and maintainer-only document conventions unless translation is requested.
- Separate explicit intent, repository facts, proposed defaults, and open decisions.
- Ask only when alternatives materially change product behavior, data, permissions, privacy, cost, or irreversible effects.
- Investigate files, tests, architecture, and implementation details independently.
- Read `AGENTS.md`, then locate the real production entry and direct call path before non-trivial edits.
- Select the smallest sufficient registered squad. The router is not a squad member; prefer two specialists and add a third only for a distinct material boundary. Do not require the user to name a Skill.
- Make the smallest correct change and preserve unrelated workspace changes.
- Run fresh verification before claiming completion, correctness, or readiness.
- Commit, push, PR, deployment, production writes, paid calls, external submissions, and destructive actions require explicit authorization.

## Project-Specific Pointers

- Architecture: `AGENTS.md`
- Engineering workflow: `AI_ENGINEERING_PLAYBOOK.md`
- Professional squads: `SQUADS.md`
- Design system: {{DESIGN_SYSTEM_PATH}}
- Generated architecture map: {{ARCHITECTURE_MAP_PATH}}
- Operations policy: {{OPERATIONS_DOC_PATH}}

Remove unavailable pointers rather than leaving misleading paths.
