# {{PROJECT_NAME}} AI Engineering Playbook

## Principles

- Think before coding and read current code before proposing implementation.
- Translate ordinary language into an executable task without inventing product behavior.
- Present user-facing conclusions, reports, and status in the user's resolved language preference; preserve code, commands, identifiers, APIs, and maintainer-only document conventions unless translation is requested.
- Make the smallest correct change; avoid speculative abstractions and adjacent cleanup.
- Preserve unrelated workspace changes.
- Use the narrowest check that proves the behavior, then expand verification according to risk.
- Require explicit authorization for external writes, production operations, destructive actions, and paid calls.
- Treat a Skill as one professional capability and a squad as two or three complementary Skills closing one outcome.

## Requirement Translation

Classify task information internally:

- **Explicit intent**: stated by the user.
- **Repository fact**: proven by source, configuration, tests, or runtime evidence.
- **Proposed default**: the simplest recommended approach, labeled as a proposal.
- **Open decision**: an ambiguity that changes behavior, data, permissions, privacy, cost, or irreversible effects.
- **Presentation preference**: explicit user language first, then current user language, then an explicitly established target-audience language for final user-facing output.

Ask only about open decisions. Discover files, tests, architecture, and implementation details independently.

## Task Contract

For non-trivial work, establish:

```markdown
- Goal:
- Scope:
- Preserve:
- Acceptance:
- Risks:
- Verification:
- Presentation language:
- Repository facts:
- Proposed defaults:
- Open decisions:
```

Skip a written contract for obvious, one-file, low-risk corrections.

## Workflow By Risk

| Risk | Boundary | Workflow |
|---|---|---|
| Low | Local module; no persisted data, API, permission, or production impact | Read -> edit -> focused check -> verify |
| Medium | Cross-module, UI flow, contract adaptation, generated artifact | Contract -> specialist if needed -> implement -> test -> review -> verify |
| High | Authentication, authorization, persisted schema, billing, privacy, destructive or production effect | Contract -> test/contract -> implement -> security/review -> verify -> permission gate |

## Squad Selection

Use `SQUADS.md` as the project registry.

- The router/control plane is not a squad member.
- Prefer a two-Skill closed loop: primary judgment plus independent proof.
- Add a third Skill only for a distinct material domain or risk boundary.
- Define a concrete handoff artifact between sequential members.
- Direct low-risk work does not need a ceremonial squad.
- Use `meta-skill-designer -> skill-creator` when designing or evolving the Skill system itself.

## Daily Loop

1. Translate the request and resolve blocking product ambiguity.
2. Locate the production entry, direct call path, consumers, and existing tests.
3. Define the smallest failing reproduction or acceptance condition.
4. Change the fewest necessary files.
5. Run focused checks after each logical unit.
6. Inspect the diff for unrelated changes and cross-file synchronization requirements.
7. Run final verification freshly.
8. Report evidence, omitted checks, residual risk, and gated external actions.

## Verification Commands

Replace every placeholder with a real command or `not applicable`.

| Proof | Command |
|---|---|
| Focused tests | `{{FOCUSED_TEST_COMMAND}}` |
| Full relevant suite | `{{FULL_TEST_COMMAND}}` |
| Lint | `{{LINT_COMMAND}}` |
| Type check | `{{TYPECHECK_COMMAND}}` |
| Build/package | `{{BUILD_COMMAND}}` |

Project-specific change matrix:

| Changed area | Minimum checks |
|---|---|
| {{AREA_1}} | {{AREA_1_CHECKS}} |
| {{AREA_2}} | {{AREA_2_CHECKS}} |
| {{AREA_3}} | {{AREA_3_CHECKS}} |

Tests are evidence for specific claims, not proof that every requirement is met. Re-read acceptance criteria before completion.

## Safety Boundaries

Explicit authorization is required before:

- commit, push, pull request, release, or deployment;
- production database or storage writes;
- paid or quota-consuming external calls;
- secret or credential changes;
- destructive cleanup or migration.

Never print secrets or private production data. Prefer dry-run and read-only modes. Protect unrelated worktree changes.

## Completion Standard

Before claiming completion, report:

- What changed and why.
- Files, contracts, or interfaces affected.
- Commands actually run and their results.
- Manual checks actually performed.
- Known limitations, skipped checks, and residual risks.
- Any next action that remains permission-gated.
