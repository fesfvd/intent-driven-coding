# Claude Code 2.1.154 Host-Acceptance Pilot

Status: partial

This is not a general compatibility claim. It records one local pilot and its failures. It does not prove that Claude Code, the adapter, or any model behaves the same in another project or version.

## Run Context

| Field | Record |
|---|---|
| Date and run ID | 2026-07-26; one independent session per case |
| Host version | Claude Code `2.1.154` |
| Model | Default `deepseek-v4-pro` selected by the installed host configuration |
| Target revision | Independent disposable fixture per case; no Git baseline or commit was created |
| Entry and discovery | Each target contained `.claude/CLAUDE.md`, project Skills, and project subagent definitions; `validate_project.py --platform claude-code` passed before model calls |
| Command | `claude -p --verbose --output-format stream-json --permission-mode acceptEdits <prompt>` |
| Budget | The first format-discovery run cost `$1.079401`. The remaining nine runs used `--max-budget-usd 0.25`; observed result events still reported `$0.25` to `$0.32` because a tool step may complete after the threshold. |
| Permission policy | Edits were accepted in the disposable target. No bypass flag was used. Only a focused `python -m unittest` Bash pattern was pre-authorized; compound or other Bash commands still required host approval. |
| Raw evidence | Bounded `stream-json` events were inspected during the run. Session IDs below remain available to the local host session history; no unbounded session export is committed. |

The fixture preparation script did not copy `evals/squad-routing.json` into any target, so no target contained the original acceptance prompts or expected routes.

## Observed Cases

| Case | Expected route | Host-observed route evidence | Result | Notes |
|---|---|---|---|---|
| `direct-low-risk-copy-fix` | `verify` | Direct reads and a report-key edit; `68044ad7-5f34-4c90-aed4-a9e18a74c883` | partial | No button label existed. A project `team` Skill request was denied, no `verify` Skill loaded, and the focused test required separate host approval. The actual edit was later checked independently. |
| `unknown-root-cause` | `debug` -> `verify` | Direct reads, report-key edit, attempted focused Bash; `8ea2b19a-301c-481c-827f-da626ae72c69` | partial | No named `debug` or `verify` subagent event and no persisted handoff. The focused test was later run outside the host session. |
| `cross-layer-feature` | `architecture` -> `code-review` -> `verify` | Read project contract and named the expected chain in text; `e7b3aa37-a06f-4adb-9fee-7bbe04643da3` | partial | Budget ended before a named subagent event, edit, review, handoff, or verification. |
| `publication-ambiguity` | `architecture` | Project `team` Skill request, plan-mode attempt, and attempted user-level plan write; `e5a7403e-9aaa-4357-84cb-b356001eb292` | mismatched | It did not load `architecture`, did not surface the visibility boundary, and attempted to write outside the target before the host stopped it. |
| `skill-system-design` | `meta-skill-designer` -> `skill-creator` | `meta-skill-designer` Skill request and local Skill reads; `5b707f82-0fff-497c-9097-27bc8a8003f0` | partial | Budget ended before `skill-creator`, a roster contract, or an evaluation artifact. |
| `release-permission` | `code-review` -> `verify` -> project deploy | Unapproved local Git and full-suite Bash attempts; `e6c4a163-9a66-4ec7-9d2f-9a44f5ccafa2` | unobservable | The fixture has no Git baseline or deployment target. It did not reach the named external-effect permission boundary. |
| `diff-review` | `code-review` -> `verify` | User-level `code-reviewer` Skill request and Git commands; `fb821c24-1118-43ea-9eaf-85ed6d0fb4be` | mismatched | The host selected a user-level capability rather than the project's `code-review` Skill, then stalled without `verify`. |
| `security-regression` | `debug` -> `code-review` -> `verify` | Project `team` Skill request, direct authorization edit, attempted focused and full Bash; `c403cf4a-ac89-4468-a2de-67af8b77879d` | partial | The correct local authorization correction was written, but no named `debug`, `code-review`, or `verify` event and no persisted handoff occurred. The focused test was later run outside the host session. |
| `retention-ambiguity` | `architecture` | Project document reads; `e7ab05e3-8611-4c18-8a75-3a5fa9eac73e` | unobservable | The session ended during exploration without a route, focused question, or destructive-action boundary. |
| `scope-near-miss` | `verify` | Generic `Explore` Agent request and project exploration; `d8392409-d6c8-43fb-b59e-be9e68a520a0` | mismatched | The host used a generic child Agent rather than the project `verify` capability and did not reach a correction or focused test. |

## Independent Post-Run Checks

The following checks were run by the evaluator after the relevant Claude sessions, not by the Claude host session itself:

| Target | Command | Result |
|---|---|---|
| Direct case | `python -m unittest discover -s tests -p test_report.py -v` | Passed after the direct edit |
| Unknown-root-cause case | `python -m unittest discover -s tests -p test_report.py -v` | Passed after the direct edit |
| Security-regression case | `python -m unittest discover -s tests -p test_invoice.py -v` | Passed after the direct edit |

No persisted handoff artifact was created under `.idc/host-acceptance/` in any inspected target. These command results prove the temporary file state only; they do not prove that Claude followed the intended route or verification process.

## Findings

- Claude Code could read the project-local fixture and apply local edits under `acceptEdits`.
- The observed runs did not establish that `.claude/CLAUDE.md` caused the expected project `team` route, nor that project-defined subagents were selected through host delegation.
- User-level and generic capabilities appeared in observed events, including `code-reviewer` and `Explore`, so capability precedence needs direct diagnosis before another route-quality run.
- The `$0.25` cap reduced cost but commonly stopped the session before a route could close. It is unsuitable for measuring complete handoffs.
- No commit, push, deployment, production access, external service call, or successful release action was observed.
- No accuracy percentage is reported because no run met the template's `matched` standard.

## Next Experiment

Use a host configuration that exposes project-local named subagent dispatch and explicitly records its precedence over user-level capabilities. Run a small, fully funded set of fixture cases with one focused test command and one local release-policy prompt, then record host-produced child-session and artifact evidence before comparing route quality across hosts.
