# Host Acceptance Fixture Architecture Guide

## Product

This is a disposable local fixture for host-acceptance experiments. It contains no credentials, network integration, deployment path, production data, or external service.

## Technology

| Area | Current choice | Source of truth |
|---|---|---|
| Runtime | Python standard library | `fixture_app.py` |
| Tests | `unittest` | `tests/` |
| Persistence | Process-local dictionaries | `fixture_app.py` |
| Deployment | not applicable | not applicable |

## Repository Map

| Path | Responsibility | Important boundary |
|---|---|---|
| `fixture_app.py` | Report, invoice, and approval-state behavior | Contains intentional acceptance failures |
| `tests/test_report.py` | Report save/render regression | Fails until the data-key mismatch is corrected |
| `tests/test_invoice.py` | Cross-account invoice access regression | Fails until authorization is enforced |
| `tests/test_approval.py` | Approval-state feature | Fails until the model and dashboard contract exist |
| `.idc/host-acceptance/` | Main-Agent persisted handoffs | Contains no source code or credentials |

## Cross-File Constraints

- Never treat an intentional failing fixture test as a production failure.
- The main Agent owns edits and writes the returned specialist handoff before loading the next specialist.
- Keep every change local to the disposable target; do not commit, push, deploy, or call external services without explicit authorization.
- The target must not contain the natural-language routing prompts or expected routes.

## Impact Matrix

| Change | Must inspect | Why | Minimum proof |
|---|---|---|---|
| Report flow | `fixture_app.py`, `tests/test_report.py` | Save and render must use the same data key | `python -m unittest discover -s tests -p test_report.py -v` |
| Invoice access | `fixture_app.py`, `tests/test_invoice.py` | Caller identity must constrain returned data | `python -m unittest discover -s tests -p test_invoice.py -v` |
| Approval state | `fixture_app.py`, `tests/test_approval.py` | Model and dashboard contract change together | `python -m unittest discover -s tests -p test_approval.py -v` |

## Structural Change Rule

Update the fixture only when its host boundary, intentional defect, or focused proof command changes. Keep prompt expectations in the framework repository, not this target.
