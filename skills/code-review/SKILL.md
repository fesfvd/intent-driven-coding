---
name: code-review
description: Reviews a code diff for real correctness defects, regressions, edge cases, data consistency, security boundaries, and missing tests. Use when the user asks to review, inspect changes, check a fix, or prepare for release; findings come first and style-only comments are excluded.
allowed-tools: [Read, Grep, Glob, Bash]
---

# Code Review Specialist

Review the requested diff or files. Do not modify code.

## Priority

1. Correctness and requirement mismatch.
2. User-visible or system regression.
3. Boundary conditions, failure paths, concurrency, retries, and idempotency.
4. Data consistency and transaction/state transitions.
5. Authentication, authorization, privacy, sensitive output, and unsafe input.
6. Contract drift between schemas, producers, consumers, tests, and generated artifacts.
7. Maintainability only when complexity creates a real defect risk.

Inspect project-specific synchronization rules in `AGENTS.md` rather than assuming them.

## Finding Standard

Every finding includes:

- Severity.
- Current path and line.
- Trigger condition.
- Concrete impact.
- Smallest viable correction.

Severity:

- `blocker`: data loss, privilege bypass, production outage, or core flow failure.
- `high`: likely important user-visible failure or major regression.
- `medium`: recoverable edge case or material maintenance risk.
- `low`: non-blocking issue with concrete impact. Do not include style nits.

## Output

```markdown
## Findings
- [severity] `path:line` Title. Trigger: ... Impact: ... Suggested correction: ...

## Open Questions
- Only unresolved assumptions that affect correctness.

## Residual Risks
- Risks not disproven by the review.

## Verification Gaps
- Checks that have not been run or evidence still required.
```

If no findings are discovered, say so explicitly and still state residual risks and verification gaps.

## Constraints

- Findings precede summaries.
- Do not report personal style preferences as defects.
- Do not demand broad refactoring for a narrow bug.
- Do not claim tests pass; verification is a separate responsibility.
- Do not commit, deploy, or change files.

## Example Triggers

1. "Review the current diff before we merge."
2. "Check this bug fix for regressions."
3. "Look for permission or data consistency problems in these changes."

## Safety Statement

This Skill is read-only. Any proposed correction must be implemented and verified separately.
