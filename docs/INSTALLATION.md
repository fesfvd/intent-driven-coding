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
   | Claude Code | Install the plugin through the marketplace, or use `bootstrap.py --platform claude-code` to add a root `CLAUDE.md` entry and project-local resources. |
   | OpenCode | Add the IDC plugin to the target `opencode.json`, or use `bootstrap.py --platform opencode` to add an IDC block to root `AGENTS.md` and generate native resources. |
   | Codex CLI | Use `bootstrap.py --platform codex` to add an IDC block to root `AGENTS.md` and generate project Skills. |
   | Cursor, Copilot, and other assistants | Their native persistent entry is not installer-verified here; use their documented project instruction file and add the short IDC entry block after reviewing that file. |

   The bootstrapper preserves text outside `<!-- IDC:BEGIN -->` and
   `<!-- IDC:END -->` in existing `AGENTS.md` or `CLAUDE.md`. Dry-run shows
   the actual merged diff. It does not merge an unmarked IDC block into an
   existing file, and it does not configure third-party hosts automatically.

4. Install the CLI in the environment that will run `idc`:

   ```powershell
   cd intent-driven-coding
   python -m pip install -e .
   idc --help
   ```

   This installs the `idc` command from this checkout. Keep the IDC checkout
   available for updates. If you only need the file scaffold and do not intend
   to use task capture yet, the CLI install can be deferred; the persistent
   entry will then report that capture is unavailable.

5. Preview the generated files before writing:

   ```powershell
   cd intent-driven-coding
   python scripts/bootstrap.py --target ../my-project --project-name "My Project" --dry-run
   ```

6. Apply only after reviewing the plan:

   ```powershell
   python scripts/bootstrap.py --target ../my-project --project-name "My Project" --apply
   ```

   Add `--platform codex`, `--platform opencode`, or `--platform claude-code`
   to install the matching persistent entry. Review the dry-run diff before
   apply, especially when the root instruction file already contains project
   rules. Outside the managed IDC block those rules remain unchanged. Other
   existing scaffold files are skipped by default; avoid `--force` unless you
   intend to replace those files.

7. Start the assistant at the target project root. Initialize the record store
   once before expecting `idc start` to capture tasks:

   ```powershell
   idc init --project ../my-project --project-key MYPROJECT --platform codex
   ```

   Use `--platform claude-code` or `--platform opencode` as appropriate.
   Then run `idc start --project ../my-project --summary "..."` to confirm the
   CLI can write a capture. The host entry instructs the agent to perform this
   capture; host acceptance is a separate check of whether the host actually
   loads and follows that entry.

8. Start the assistant at the target project root and tell it:

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

9. Fill the generated `AGENTS.md`, `AI_ENGINEERING_PLAYBOOK.md`, and `SQUADS.md`
   with target-project facts. `IDC.md` explains how to use the framework;
   `AGENTS.md` explains how this project works. Do not mix those responsibilities.

10. Validate the installation from the IDC repository:

   ```powershell
   python scripts/validate_project.py --target ../my-project
   ```

   Use `--platform codex`, `--platform opencode`, or `--platform claude-code` when applicable.

   `bootstrap.py` owns guidance and host layout only. `idc init` exclusively
   owns initial `.idc/config.json` creation, so the two tools cannot silently
   overwrite each other's configuration.

   For real requests, keep the record lightweight and append-only:

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
