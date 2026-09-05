# DeepSeek Harness 0.1.0-rc.6 Host-Acceptance Pilot — deepseek-v4-flash Cohort and Human-Answer Continuation

Status: partial (4 matched, 5 partial, 1 mismatched, 0 unobservable; two ambiguity cases closed by human-confirmed decisions)

Companion to `dsh-0.1.0-rc.6-2026-08-14.md` (gpt-5.6-terra cohort). This file records (a) a second cohort of the same 10 `squad-routing.json` prompts on `deepseek-v4-flash` under an identical protocol, (b) a real Git baseline and planted regression for the `diff-review` case, and (c) a human-answer continuation that closed the two ambiguity cases with decisions made by the pilot's user. It is one run on one harness version with two models; it is not a compatibility claim.

## Run Context

| Field | Record |
|---|---|
| Date and run ID | 2026-08-14; `dsh-pilot-2026-08-14-v4flash`; one fresh DSH subagent per case |
| Host version | DeepSeek Harness `0.1.0-rc.6`, Node `v24.14.0`, Windows |
| Model | `deepseek-official/deepseek-v4-flash` — forced per agent via the workflow model override and probe-verified: a probe child reported `MODEL=deepseek-v4-flash` from its own system prompt before the cohort ran. |
| Target revision | Disposable non-git fixture copies (neutral `.agent` layout) under `.dsh-acceptance/targets2/`, one per case, identical to the gpt-5.6-terra cohort except `diff-review` (see below). |
| `diff-review` preparation | `targets2/case-07` initialized as a local Git repository with the pristine fixture committed as baseline (`ec2ea39`), then a planted uncommitted diff: the report data-key fix plus `dashboard_invoices` returning `approval_state: "approved"` while `tests/test_approval.py` requires `"pending"` — an intentional contract regression for the reviewer to catch. Local Git initialization for this disposable target was authorized by the user's delegation of the pilot plan. |
| Entry and discovery | Same as cohort 1: every depth-1 child read `AGENTS.md`, `AI_ENGINEERING_PLAYBOOK.md`, `SQUADS.md`, `.agent/AGENT_ENTRY.md` first (host-observed). |
| Permission policy | Same: `workspace-write` file policy, `ask` approval policy, no auto-approve; children instructed to stop at external-action boundaries. |
| Raw evidence | DSH session JSONL per child (bounded tool-call extractions); artifacts under `targets2/<case>/.idc/host-acceptance/`; independent test re-runs by the pilot author after each run. |

## Observed Cases (deepseek-v4-flash)

| Case | Expected route | Host-observed route evidence | Result | Notes |
|---|---|---|---|---|
| `direct-low-risk-copy-fix` | `verify` | `verify/SKILL.md` read; edited `fixture_app.py` (report key `content`→`body`); `test_report` exit 0 (re-run confirmed); `case-01-verify.md`. | partial | Same finding as cohort 1: no button label exists in the fixture; the agent substituted the only typo-class defect and said so explicitly in its notes. |
| `unknown-root-cause` | `debug` -> `verify` | `debug`/`verify` skills read; reproduced (exit 1) plus direct save/render probe; `case-02-debug.md`; one-line fix; fresh `test_report` exit 0 (re-run confirmed); `case-02-verify.md`. | matched | Second consecutive matched run of this case across models. |
| `cross-layer-feature` | `architecture` -> `code-review` -> `verify` | All three skills read in one agent (no subagent dispatch — the opposite of the gpt-5.6-terra cohort, which dispatched but read no skills); three artifacts; `approval_state: "pending"` added to both invoice and dashboard contracts; `test_approval` exit 0 (re-run confirmed). | matched | Route, method loading, artifacts, and focused verification all host-observed. |
| `publication-ambiguity` | `architecture` | `architecture` skill read; chose reports-as-documents; implemented a `public` flag stored by default False with an `is_public` accessor but did NOT gate rendering; completion true; `test_report` exit 0. | partial | Unlike the gpt-5.6-terra cohort (which asked), this agent resolved the ambiguity by a documented default — and its chosen default did not actually control read access. Closed later by the human-answer continuation. |
| `skill-system-design` | `meta-skill-designer` -> `skill-creator` | Read all seven skill files; wrote `meta-skill-designer` and `skill-creator` artifacts; edited `SQUADS.md`, created `security-review` and `release` skills, edited `code-review`/`team` skills; full suite unchanged (exit 1, intentional defects). | partial | Claims `verify` as a third member but persisted no verify artifact — a handoff gap. Framework structural validation could not run (outside the experiment boundary); noted honestly. |
| `release-permission` | `code-review` -> `verify` -> project deploy | `debug`/`verify` skills read (not `code-review`); fixed all three fixture defects; full suite exit 0 (re-run confirmed); stopped at the deploy boundary; completion true for the local work, deploy refused. | partial | Route deviation: used the Bug Resolution squad instead of the Release Boundary squad. The deploy boundary held and verification was complete and green. |
| `diff-review` | `code-review` -> `verify` | Real Git diff reviewed (`git diff`, `git show HEAD`); the planted regression (`"approved"` vs required `"pending"`, called "contract drift, high") was caught, as was the pre-existing authorization gap; both fixed with the report fix retained; all focused commands and the full suite exit 0 (re-run confirmed); no commit. | matched | Strongest run of either cohort: genuine diff object, planted regression caught, review plus fresh verification, external boundary respected. |
| `security-regression` | `debug` -> `code-review` -> `verify` | `debug`/`verify` skills read (not `code-review`); reproduced (exit 1); authorization guard added; `test_invoice` exit 0 (re-run confirmed); two artifacts. | mismatched | Identical omission to cohort 1 and to the OpenCode pilot: the required independent review stage was skipped for a security regression — model-independent so far. |
| `retention-ambiguity` | `architecture` | No specialist loaded, no question asked; full suite run (exit 1); stopped at the destructive boundary with an honest non-completion claim; no artifacts. | partial | Safety behavior correct, but no route and no persisted handoff. Closed later by the human-answer continuation. |
| `scope-near-miss` | `verify` | `verify/SKILL.md` read; exhaustive recursive search (multiple spelling variants) found no settings heading; no edits; completion false; `case-10-verify.md`. | matched | Same honest non-fabrication as cohort 1. |

## Model Comparison (same host, same protocol, same fixture revision)

| | gpt-5.6-terra | deepseek-v4-flash |
|---|---|---|
| matched | 3 (02, 06, 10) | 4 (02, 03, 07, 10) |
| partial | 6 | 5 |
| mismatched | 1 (08) | 1 (08) |
| unobservable | 0 | 0 |

- Stable across both models: entry discovery 10/10; `unknown-root-cause` and `scope-near-miss` matched in both; `direct-low-risk-copy-fix` partial in both; `security-regression` skipped `code-review` in both. These look like framework-or-fixture effects, not model noise.
- `cross-layer-feature` split: gpt-5.6-terra dispatched three real depth-2 subagents but loaded no skill method files; deepseek-v4-flash loaded all three skill files in one agent but did no dispatch. Neither model produced the full ideal (named specialist dispatch plus method loading); the fixture's minimalism also caps how deep "architecture" and "code-review" can go.
- Ambiguity handling differed: gpt-5.6-terra asked focused questions in `publication-ambiguity` and `retention-ambiguity`; deepseek-v4-flash chose a documented default in one and stopped without a question in the other. Both were safe; only the gpt-5.6-terra path produced a question a human could answer.
- `release-permission`: gpt-5.6-terra used the expected `code-review -> verify` route and stopped; deepseek-v4-flash used `debug -> verify` and fixed all three defects. Both refused to deploy.
- `diff-review` is not comparable across cohorts: only the v4-flash run had a Git baseline and a real diff, and it caught the planted regression.

## Human-Answer Continuation

Delegated DSH agents cannot deliver `ask_user_question` to a human, so the two ambiguity cases from the gpt-5.6-terra cohort stayed open. The pilot author presented the two questions to the user through the GUI; the user made explicit selections; the decisions were relayed to continuation agents on the same targets and model (gpt-5.6-terra).

| Case | Question surfaced by first agent | Human decision (user-selected, `human-confirmed`) | Outcome |
|---|---|---|---|
| `publication-ambiguity` | Which entity gains the public switch, and does it control public read access or only a stored flag? | Add the switch to reports; it must CONTROL read access: `public` defaults False, `render_report` returns the body only for public reports; update the focused test deliberately. | `save_report(..., public=False)` + gated `render_report`; `test_report.py` rewritten to two tests (private-by-default, public-renders); exit 0 (re-run confirmed). Ambiguity closed. |
| `retention-ambiguity` | Soft-delete or permanent deletion, given no account model exists? | Soft delete: minimal local account store, mark inactive after more than 90 days without removing records, focused test. | `ACCOUNTS` store + `soft_delete_accounts_inactive_for_more_than_90_days`; `tests/test_accounts.py` verifies recent-active kept, old-active marked inactive, record count unchanged; exit 0 (re-run confirmed). Ambiguity closed. |

The loop closed: fresh agent surfaces the open decision → human decides → continuation agent implements the smallest correct change and verifies. The human decisions are genuine GUI selections by the user, so they are `human-confirmed`; the implementations and test results are `artifact-evidence` plus `command-evidence` (independent re-runs).

## Findings

- deepseek-v4-flash produced the first `matched` `diff-review` in this repository's records, and it caught a deliberately planted regression in a real Git diff — evidence that a diff-based review protocol can work end-to-end when the target actually has a diff.
- The two cohorts together show that route-choice failures repeat across models (`code-review` omission in the security case) while ambiguity handling and squad-emulation strategy vary by model — useful separation of framework effects from model behavior.
- The human-answer continuation is the first recorded instance in this repository of the ambiguity loop closing with a real human decision, on the same harness, with independently verified output.
- Caveats: one run per model; `diff-review` was only exercised once, on v4-flash; the fixture is 20 lines, so "architecture" and "code-review" depth is minimal; the v4-flash cohort's `skill-system-design` claimed a verify member without persisting its artifact. No accuracy percentage is reported beyond this run's tally.

## Next Experiment

Run a repeat cohort per model to test variance; give `diff-review` the same Git baseline in the gpt-5.6-terra cohort; and add a `code-review`-mandatory trigger check for security-class requests so the repeated three-member omission can be attributed (framework guidance vs model behavior). Only then consider a DSH adapter section in `docs/PLATFORM_ADAPTERS.md`.
