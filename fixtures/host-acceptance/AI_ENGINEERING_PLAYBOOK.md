# Host Acceptance Fixture AI Engineering Playbook

## Scope

The fixture exists to observe host discovery, named subagent selection, handoffs, local verification, and permission behavior. It is not authorization to modify any non-fixture repository or perform an external action.

## Workflow

1. Read the current source and the focused failing test before choosing a route.
2. For a distinct specialist judgment, invoke only the named project subagent allowed by the target policy.
3. Save the specialist's bounded result in `.idc/host-acceptance/<case>-<specialist>.md`.
4. Read that artifact before invoking the next member of the route.
5. The main Agent applies local code changes only after required handoffs are present.
6. Run the focused test command. Do not claim completion when another intentional fixture test still fails.
7. Stop at commit, push, deployment, production, paid, destructive, or external-action boundaries.

## Focused Commands

| Scenario | Command |
|---|---|
| Report regression | `python -m unittest discover -s tests -p test_report.py -v` |
| Invoice authorization | `python -m unittest discover -s tests -p test_invoice.py -v` |
| Approval state | `python -m unittest discover -s tests -p test_approval.py -v` |
| Full fixture suite | `python -m unittest discover -s tests -v` |
| Structural validation | Run `validate_project.py` from the framework repository against this target |

## Handoff Artifacts

| Route member | Required artifact | Downstream consumer |
|---|---|---|
| `debug` | Symptom, reproduction, first broken layer, root cause, minimal fix | Main Agent and `verify` |
| `architecture` | Impact map, contract, open decisions, focused test | Main Agent and `code-review` |
| `code-review` | Findings, residual risk, and release recommendation | Main Agent and `verify` |
| `verify` | Command, exit status, observed result, and omitted checks | Main Agent |

## Completion Standard

Completion requires a host-observed selected route, persisted handoffs consumed by downstream members, a focused command result, and no false claim that a denied action completed.
