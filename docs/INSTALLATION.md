# IDC Installation And Use

## What Gets Installed

Intent-Driven Coding is a repository of portable guidance, Skills, templates,
and validators. It is not installed by copying the entire IDC repository into
the target project's source tree.

There are two separate locations:

```text
workspace/
|-- my-project/              # The project the assistant changes
`-- intent-driven-coding/    # IDC source, templates, and validators
```

The target project receives only the selected adapter layout and the project
guidance it needs. The framework repository remains the source for updates and
validation.

## Recommended Clone And Install

1. Clone IDC beside the target project:

   ```powershell
   git clone https://github.com/fesfvd/intent-driven-coding.git intent-driven-coding
   ```

2. Identify the assistant and read this repository's
   [`AI_START_HERE.md`](../AI_START_HERE.md). The assistant, not the user,
   should determine which platform adapter applies.

3. Choose one installation path:

   | Assistant | Installation |
   |---|---|
   | Claude Code | Install the plugin through the marketplace, or generate the Claude Code project layout with `bootstrap.py --platform claude-code`. |
   | OpenCode | Add the IDC plugin to the target `opencode.json`, or generate `.opencode/agents/` and `.opencode/skills/` with `bootstrap.py --platform opencode`. |
   | Codex CLI | Generate `.agents/skills/` with `bootstrap.py --platform codex`; keep `AGENTS.md` as the project entry. |
   | Cursor, Copilot, and other assistants | Generate the neutral layout, then merge `IDC.md` and `AGENT_ENTRY.md` into the platform's project instruction mechanism. |

4. Preview the generated files before writing:

   ```powershell
   cd intent-driven-coding
   python scripts/bootstrap.py --target ../my-project --project-name "My Project" --dry-run
   ```

5. Apply only after reviewing the plan:

   ```powershell
   python scripts/bootstrap.py --target ../my-project --project-name "My Project" --apply
   ```

   Add `--platform codex`, `--platform opencode`, or `--platform claude-code` when a native layout
   is wanted. The script creates `IDC.md`, `docs/TASK_SCENARIOS.md`, and
   `templates/IDC_TASK.md` in the target project, plus the selected root and
   platform files. Existing files are preserved unless `--force` is explicitly
   used with `--apply`.

6. Start the assistant at the target project root and tell it:

   ```text
   Read IDC.md first. Identify your host platform, then read the matching
   adapter instructions. Do not copy the IDC repository wholesale. Inspect this
   project, capture my request before substantial work, and use only the
   smallest safe route. Promote durable work to IDC-<PROJECT>-<YYYYMMDD>-<NNN>,
   append material changes to events.jsonl, and derive dynamic obligations.
   Treat scenario codes as mutable labels and Markdown cards as generated views. Treat current
   source, tests, configuration, and command output as the facts. Ask me only
   about decisions that change behavior, data, privacy, permission, cost, or
   irreversible effects. Verify the result with fresh evidence before claiming
   completion.
   ```

7. Fill the generated `AGENTS.md`, `AI_ENGINEERING_PLAYBOOK.md`, and `SQUADS.md`
   with target-project facts. `IDC.md` explains how to use the framework;
   `AGENTS.md` explains how this project works. Do not mix those responsibilities.

8. Validate the installation from the IDC repository:

   ```powershell
   python scripts/validate_project.py --target ../my-project
   ```

   Use `--platform codex`, `--platform opencode`, or `--platform claude-code` when applicable.

9. Initialize the progressive record store with the installed CLI:

   ```powershell
   idc init --project ../my-project --project-key MYPROJECT --platform codex
   ```

   `bootstrap.py` owns guidance and host layout only. `idc init` exclusively
   owns initial `.idc/config.json` creation, so the two tools cannot silently
   overwrite each other's configuration.

   For the first real request, keep the record lightweight and append-only:

   ```powershell
   idc start --project ../my-project --summary "Describe the request" --scene <initial-scene> --actor human
   # If the idea is exploratory, use --temporary (default TTL: 72 hours).
   idc start --project ../my-project --summary "Investigate an idea" --temporary
   idc promote --project ../my-project --record <record-id>
   idc metrics --project ../my-project --json
   ```

   `start` prints the provisional card (header, scene, outstanding obligations)
   as the first work report and writes it to
   `.idc/work-items/<record-id>/CARD.md`; promotion moves it to
   `.idc/tasks/<task-id>.md`.

   Temporary captures can be discarded without deleting their event history:
   `idc discard --project ../my-project --record <record-id> --reason "Not needed"`.
   Configure the default temporary lifetime with `capture_ttl_hours` in
   `.idc/config.json`, or override it per capture with `--ttl-hours`. The CLI
   records facts; it does not prove that a host automatically captured requests
   or selected a named Agent. Validate those behaviors separately with
   [Host Acceptance](HOST_ACCEPTANCE.md).

## How The Assistant Understands IDC

The assistant should learn the repository through a bounded chain:

```text
IDC.md
  -> platform adapter
  -> PROGRESSIVE_TASKS.md and TASK_SCENARIOS.md
  -> AGENTS.md and AI_ENGINEERING_PLAYBOOK.md
  -> team Skill
  -> only the specialist Skill needed for this task
  -> current source, tests, configuration, and fresh command evidence
```

The files have different authority:

| File | Meaning | Authority |
|---|---|---|
| `IDC.md` | How the installed IDC method is used | Framework operating guidance |
| `AGENTS.md` | What the target project is and how its architecture behaves | Project architecture semantics; verify against source |
| `AI_ENGINEERING_PLAYBOOK.md` | How work is translated, executed, verified, and gated | Project workflow rules |
| `SQUADS.md` | Which project-specific formations have been accepted | Project route registry |
| `PROGRESSIVE_TASKS.md` | How work is captured, promoted, changed, proved, and closed | Lifecycle and dynamic obligations |
| `TASK_SCENARIOS.md` | Mutable search and routing labels | Classification guidance; not identity or a fixed route |
| `SKILL.md` | How one professional judgment is performed | Stable method; not a source of volatile project facts |
| `.idc/work-items/<record-id>/events.jsonl` | Append-only facts and provenance | Authoritative per-task record |
| `.idc/tasks/<task-id>.md` | Human-readable task view | Generated projection; do not edit |

When the assistant cannot automatically discover Skills or subagents, it must
read the needed `SKILL.md` explicitly and execute the route sequentially. That
fallback is valid; automatic routing is not required for IDC to be useful.

## What Installation Does Not Prove

Successful cloning, file generation, or project validation proves only that the
local layout is present and structurally consistent. It does not prove that the
assistant discovered the entry, selected the intended route, consumed a
handoff, obeyed host permissions, or ran the right verification command. Test
those behaviors with the host acceptance procedure before describing a platform
as verified.

## Updating IDC

Keep the cloned IDC repository outside the target project's source ownership.
When updating it, review the dry-run diff and re-run the target validator before
merging new framework guidance into existing project files. Do not overwrite
project-specific `AGENTS.md`, playbooks, squads, or Skills without a deliberate
human review.
