# Permission And Risk Protocol

## Principle

Permission is scoped to the action the user authorized. A request to change local code does not imply permission to commit, push, open a pull request, deploy, modify production data, call a paid service, or delete resources.

## Action Classes

| Class | Examples | Default |
|---|---|---|
| Local and reversible | Read files, edit task-related files, run focused local tests | May proceed |
| External or collaborative write | Commit, push, PR, issue creation, external submission | Require explicit request or confirmation |
| High-risk or cost-bearing | Deployment, production write, migration, secret rotation, destructive cleanup, paid/limited E2E | Require explicit confirmation immediately before action |

Read-only production access may still expose sensitive data. Follow the project's operational policy and minimize output.

## Confirmation Must Name The Effect

Good confirmation:

```text
This production smoke test will create one record and consume one paid API call. Run it now?
```

Weak confirmation:

```text
Continue?
```

Authorization should not be widened. Approval to create a PR does not authorize deployment. Approval to deploy one revision does not authorize a database migration unless that effect was included.

## Workspace Safety

- Preserve unrelated changes, including untracked files.
- Never use destructive version-control commands unless the user explicitly requests the exact effect.
- Do not "clean up" adjacent code without task evidence.
- Do not print secrets, tokens, credentials, private user data, or sensitive production records.
- Prefer dry-run and read-only modes before scripts that write.
- Inspect generated scripts before first execution.

## Risk Classification

| Risk | Typical boundary | Minimum process |
|---|---|---|
| Low | One local module, no persisted data/API/permission/production impact | Read -> edit -> focused check -> verify |
| Medium | Cross-module, UI flow, API adaptation, generated artifact, LLM contract | Contract -> specialist if needed -> implement -> test -> review -> verify |
| High | Authentication, authorization, persisted schema, billing, privacy, destructive or production effect | Contract -> test/contract -> implement -> security/review -> verify -> explicit external-action confirmation |

Risk controls workflow length; file count does not.

## Completion Boundary

An agent may report local implementation and verification without performing external actions. State clearly:

- What is complete locally.
- Which checks actually ran.
- What remains gated.
- The exact side effect of the next action.
