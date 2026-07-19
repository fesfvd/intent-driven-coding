---
name: debug
description: Performs evidence-first root-cause diagnosis for bugs, crashes, blank screens, missing data, failed jobs, broken scripts, and behavior that does not work. Use when the cause is unknown; reproduce the symptom, locate the first broken layer, test a falsifiable hypothesis, and avoid speculative patches.
allowed-tools: [Read, Grep, Glob, Bash]
---

# Debug Specialist

## Core Rule

```text
Do not patch before locating the root cause.
```

Translate the report into observed facts, unproven inferences, and evidence to collect. Ask the user only when different product expectations change what "correct" means.

## Four Phases

| Phase | Activity | Exit condition |
|---|---|---|
| Root-cause investigation | Read the full error, reproduce, locate the real entry, inspect recent relevant changes | The failing layer is identified |
| Pattern analysis | Find a working reference and compare input, state, environment, and path | A falsifiable hypothesis exists |
| Hypothesis test | Change one variable or create the smallest failing regression test | Hypothesis is confirmed or rejected |
| Root-cause fix | Hand the minimal fix to the main agent and verify symptom plus regressions | Fresh evidence supports the result |

After three failed speculative attempts or repeatedly shifting symptoms, stop patching and revisit the architecture assumption.

## Layer Checklist

Use only layers relevant to the repository:

1. Input and validation.
2. UI/client state and network/event handling.
3. Interface/API/queue boundary.
4. Domain/service logic.
5. Persistence and transaction state.
6. External dependency.
7. Serialization/parsing/rendering.
8. Build, generated artifact, deployment, or environment configuration.

Locate the first layer where actual behavior diverges from expected behavior.

## Output

```markdown
## Diagnosis
- Symptom:
- Environment:
- Reproduction:
- First broken layer:
- Evidence:
- Root cause:
- Minimal fix:
- Regression proof:
- Unverified risk:
```

## Constraints

- Do not treat a guess as a root cause.
- Do not rely on error-code, route, service, timeout, or version snapshots stored in this Skill.
- Do not modify production data to diagnose a local bug.
- Do not confuse a passive health check with proof of a complete user flow.
- Prefer a failing regression test before implementation when feasible.

## Example Triggers

1. "This page is blank after login. Fix it."
2. "The job succeeds but the database record is missing."
3. "This script started failing with a KeyError."

## Safety Statement

Default to local, read-only diagnosis. Production logs, sensitive records, paid calls, and write operations require project-specific authorization.
