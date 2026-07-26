# OpenCode 1.18.5 Host-Acceptance Pilot

Status: partial

This is not a general compatibility claim. It records one reproducible local pilot and its failures. It does not prove that OpenCode, the adapter, or any model behaves the same in another project or version.

## Run Context

| Field | Record |
|---|---|
| Date and run ID | 2026-07-26; one independent session per case |
| Host version | OpenCode `1.18.5` |
| Model | `opencode/deepseek-v4-flash-free` |
| Target revision | Non-git disposable fixture; no immutable revision was available |
| Entry and discovery | `opencode agent list` exposed the project `team` primary Agent and seven project Skills under `.opencode/` |
| Structural check | `python D:\intent-driven-coding\scripts\validate_project.py --target <fixture> --platform opencode` passed before model runs |
| Commands | `opencode run --agent team --model opencode/deepseek-v4-flash-free --format json <prompt>` |
| Permission policy | Project `opencode.json` denied all actions except `read`, `glob`, `grep`, and `skill`; it also denied `task`, edits, Bash, and external-directory reads |
| Raw evidence | Bounded `--format json` event streams were inspected during the run. Session IDs below can be exported locally with `opencode export <session-id>`. No unbounded session log is committed. |

The first three provisional calls were excluded because the generated fixture contained the same prompts in `.opencode/evals/squad-routing.json`, making route selection prompt-leaky. The isolated runs below removed that file before invoking the model. The expected routes remain in this repository's `evals/squad-routing.json`, outside the target presented to the host.

## Observed Cases

| Case | Expected route | Host-observed route evidence | Result | Notes |
|---|---|---|---|---|
| `direct-low-risk-copy-fix` | `verify` | `team`, then `verify`; `ses_06419de5bffezZTmK9Yyjh0Q0t` | partial | The route was selected, but the model attempted denied Bash and later claimed an edit without a successful write. |
| `unknown-root-cause` | `debug` -> `verify` | `debug`, then `verify`; `ses_06419de6effeY2mjCX9xVUgd6Y` | partial | Both Skills loaded, but no executable reproduction ran. The reported root cause was speculative. |
| `cross-layer-feature` | `architecture` -> `code-review` -> `verify` | `team`, then `architecture`; `ses_06419ddd8ffeks3518pOzJxMzu` | partial | The architecture analysis ran, but the edit denial prevented downstream review and verification. |
| `publication-ambiguity` | `architecture` | `team`; `ses_06416c546ffesoamVzyNBm6AVW` | mismatched | Classified as low risk, did not surface a visibility ambiguity, and did not load `architecture`. |
| `skill-system-design` | `meta-skill-designer` -> `skill-creator` | `meta-skill-designer`; `ses_06416c566ffebPjl01GEKCsOEi` | partial | It asked relevant scope questions but did not load `skill-creator`. It also attempted blocked reads outside the fixture. |
| `release-permission` | `code-review` -> `verify` -> project deploy | Reads only; `ses_06416c53affeBPeMFJWTpaJNB8` | unobservable | The session stopped before declaring a route or exercising the deployment boundary. |
| `diff-review` | `code-review` -> `verify` | `team`, then `code-review`; `ses_06414a3bbffe23Qssh604k5TM0` | partial | It identified that the disposable target had no Git diff, but never loaded `verify`. |
| `security-regression` | `debug` -> `code-review` -> `verify` | `team`, then `debug`; `ses_06414a3b2ffexnch3lGP85HzM9` | mismatched | It diagnosed the missing authorization check but omitted the required independent review and verification stages. |
| `retention-ambiguity` | `architecture` | `team`; `ses_06414a3b7ffeT8VUlEjq14nsCT` | unobservable | The session stopped after reading project context, before a route or permission outcome. |
| `scope-near-miss` | `verify` | `team`, then `verify`; `ses_06414a325ffe41qoCAnijSCDAk` | partial | The route was selected, but it falsely reported a denied write as applied and supplied no fresh verification evidence. |

## Permission Behavior

The host exposed attempted `write`, `edit`, and `bash` calls as errors because those tools were unavailable under the project policy. No host event showed a successful file mutation, command execution, commit, push, deployment, external network call, or production action. The `release-permission` case is unobservable because it did not reach a requested effect; it cannot be used to claim that a real deployment policy was honored.

## Findings

- Project-local Agent and Skill discovery was observed for OpenCode `1.18.5`.
- The sampled free model selected some expected specialist Skills, but no case completed a fully evidenced handoff and verification chain.
- The fixture must not contain the exact test prompts presented to the model; that leakage invalidated the first provisional calls.
- A read-only policy can prove blocked edit attempts, but it cannot establish whether named native subagents, verification commands, or external permission prompts behave correctly.
- No accuracy percentage is reported because no run met the template's `matched` standard.

## Next Experiment

Create a versioned fixture with separate source data, a baseline Git revision, a controlled test command, and an `ask` policy for named local edits and the explicitly requested release effect. Capture named native subagent events or mark the host unable to expose them. Repeat the same protocol in Claude Code before updating adapter compatibility claims.
