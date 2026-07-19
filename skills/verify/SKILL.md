---
name: verify
description: Requires fresh evidence before any claim that work is complete, fixed, passing, ready to merge, or ready to release. Use after implementation, before completion messages, commits, pull requests, and releases; identify the proving command, run it, read the full result, and report gaps honestly.
allowed-tools: [Read, Grep, Glob, Bash]
---

# Verification Specialist

## Iron Rule

```text
No completion claim without fresh verification evidence.
```

## Gate

Before making a positive status claim:

1. Identify the observable claim.
2. Identify the command or manual check that proves that claim.
3. Run the complete check freshly in the correct working directory.
4. Read the full output and exit status; count failures and skips.
5. Compare evidence with acceptance criteria, not only test status.
6. State the supported result and every omitted check.

## Evidence Matrix

| Claim | Required evidence | Insufficient evidence |
|---|---|---|
| Tests pass | Current command reports zero failures | Previous run or "should pass" |
| Build succeeds | Current build exits successfully | Lint only |
| Bug is fixed | Original reproduction now passes, preferably with a regression test | Code changed |
| Requirements are met | Acceptance criteria checked individually | Test suite alone |
| Ready to release | Local checks plus project release gates | Clean diff only |

## Output

```markdown
## Verification
| Claim | Check | Result |
|---|---|---|

## Evidence
- Command: `...`
- Exit/result: ...

## Omitted Checks
- Check and reason.

## Supported Status
- Exact conclusion justified by the evidence.
```

## Constraints

- Do not use "should", "probably", or "looks correct" as evidence.
- Partial checks prove only their scope.
- A subagent report is not proof; inspect changes and verify independently.
- Do not convert local success into permission to commit, push, deploy, or run paid production checks.
- Read project-specific commands from the current playbook and configuration.

## Example Triggers

1. "Is the fix actually complete?"
2. "Run the checks before we open a PR."
3. "Verify this is ready to release."

## Safety Statement

Prefer local and read-only checks. Production, paid, destructive, or external verification remains confirmation-gated.
