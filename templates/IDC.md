# Intent-Driven Coding Project Marker

This file marks a project that uses Intent-Driven Coding. It is the first file
an AI coding assistant should read after entering this repository.

## Use This Project

1. Identify the current host platform and read its matching adapter guidance.
2. Read `AGENTS.md` for this project's architecture and
   `AI_ENGINEERING_PLAYBOOK.md` for its workflow.
3. For non-trivial work, classify the request with
   `docs/TASK_SCENARIOS.md` and show an `IDC-<PROJECT>-<SCENARIO>-<YYYYMMDD>-<NNN>`
   task card using `templates/IDC_TASK.md`.
4. Inspect current source, configuration, tests, and runtime evidence before
   deciding implementation details.
5. Use the smallest route registered in `SQUADS.md`; read the relevant Skills
   on demand when the host does not discover them automatically.
6. Require fresh verification evidence before claiming completion.
7. Ask only for decisions that change behavior, data, privacy, permissions,
   cost, or irreversible effects. Never infer authorization for commit, push,
   deployment, production writes, paid calls, or destructive actions.

## IDC Sources

- Method source and platform installation: the cloned IDC repository's
  `AI_START_HERE.md` and `docs/INSTALLATION.md`.
- Task classification: `docs/TASK_SCENARIOS.md`.
- Durable task record: `.idc/tasks/<task-id>.md`.
- Project facts: current source, configuration, tests, and `AGENTS.md`.
- Project workflow: `AI_ENGINEERING_PLAYBOOK.md`.
- Accepted formations: `SQUADS.md`.

This marker is an operating pointer, not a copy of the entire framework. Do not
replace it with project facts or treat its presence as proof that host routing
has been accepted.
