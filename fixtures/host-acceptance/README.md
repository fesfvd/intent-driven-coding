# Host Acceptance Fixture

This source fixture prepares a disposable target for manual routing, handoff, verification, and permission experiments. It is not an application template and must not be deployed or connected to external services.

The expected routes and original natural-language prompts remain in the framework's `evals/squad-routing.json`; the preparation script deliberately does not copy them into the target.

## Preparation

Create an empty disposable directory, then run:

```powershell
python scripts/prepare_host_acceptance_fixture.py --target <empty-target> --platform opencode --apply
python scripts/validate_project.py --target <empty-target> --platform opencode
```

For a diff-based run, initialize and commit the baseline only after explicitly authorizing that local Git action. The fixture begins with three intentional failures. Use the focused commands in `AI_ENGINEERING_PLAYBOOK.md`; do not run all tests and treat unrelated intentional failures as regressions.

## Scope

- `tests/test_report.py` exercises an unknown-root-cause report defect.
- `tests/test_invoice.py` exercises a cross-account authorization regression.
- `tests/test_approval.py` exercises a cross-layer approval-state feature.
- `opencode.json` allows only named project subagents through the Task tool and asks before edits or unlisted shell commands.

The primary Agent must persist each specialist result under `.idc/host-acceptance/` before asking the next specialist to consume it. A host record may call a handoff usable only when the bounded host event stream and the persisted artifact agree.
