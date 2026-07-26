# Host Acceptance Records

Use one record per host version and target-project revision. A record describes observed behavior from a real run; it is not a claim that the framework works on every model, provider, project, or future host version.

## Before Running

1. Use a disposable local target project or a target revision that can safely receive the requested changes.
2. Bootstrap and structurally validate the target with the adapter under test.
3. Select prompts from `evals/squad-routing.json` without rewriting them to match the host response.
4. Configure any commit, push, deployment, migration, paid-call, or production-access policy to require confirmation or deny the effect.
5. Do not use a permission-bypass or auto-approve mode.

For the bundled non-leaking fixture, prepare an empty target with `python scripts/prepare_host_acceptance_fixture.py --target <empty-target> --platform opencode --apply` or replace `opencode` with `claude-code`. The script does not initialize Git, invoke a model, or authorize external actions.

## Required Record

Record the following for every run. Omit secrets, personal paths, private source, and unbounded host logs.

| Field | Record |
|---|---|
| Date and run ID | ISO date plus a local identifier |
| Host version | Exact CLI or application version |
| Model | Provider and model identifier when exposed |
| Target revision | Commit or immutable fixture revision |
| Entry and discovery | Entry file, Skill path, and Agent discovery observation |
| Case | Case ID and prompt from `evals/squad-routing.json` |
| Expected route | Route declared by the fixture |
| Actual route | Loaded Skills, selected Agents, and any direct work actually observed |
| Handoff evidence | Artifact name, location, and whether the downstream consumer used it |
| Verification evidence | Command, exit status, and bounded output reference when run |
| Host-observed evidence | Session export, host log, or other host-produced reference; otherwise write `not available` |
| Permission behavior | Requested effect, configured policy, prompt or block observed, and whether the effect ran |
| Evidence classification | Label each conclusion as `claimed`, `host-observed`, `command-evidence`, `artifact-evidence`, or `human-confirmed` rather than merging them into one result |
| Result | matched, mismatched, partial, blocked, or unobservable |
| Notes | Ambiguity, host limitation, model behavior, or framework issue |

## Interpretation

- `matched` requires host-observed evidence of the selected route and the expected safety boundary.
- `partial` means the result was useful but one required observation, handoff, or verification item is absent.
- `unobservable` means the host did not expose enough evidence to distinguish a claimed route from a real one.
- A structural bootstrap or validator pass alone is never an acceptance result.
- Record mismatches without adjusting the expected route after the fact. Classify them as a framework issue, host limitation, model behavior, or genuinely ambiguous case.

Publish a short summary only after all runs retain their raw or bounded host evidence. Do not calculate accuracy from unobservable runs.
