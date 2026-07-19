# Requirement Translation Protocol

## Purpose

Users should be able to describe a goal or symptom in ordinary language. The agent owns the work of converting that input into a precise engineering task without inventing product requirements.

The protocol prevents two failures:

- **Responsibility dumping**: asking the user to select files, tests, implementation patterns, or internal tools that the repository can establish.
- **Silent invention**: choosing product semantics, privacy behavior, destructive scope, or cost-bearing actions without authorization.

## Four Information Classes

Every non-trivial request is interpreted through four classes:

| Class | Source | Agent behavior |
|---|---|---|
| Explicit intent | Directly stated by the user | Preserve its meaning and translate it into observable behavior |
| Repository fact | Proven by current source, configuration, tests, runtime evidence, or authoritative project docs | Discover it independently and add it to scope/preservation rules |
| Proposed default | The agent's simplest valid recommendation | Label it as a proposal; do not present it as user intent |
| Open decision | Alternatives materially change behavior, data, permissions, privacy, cost, or irreversible effects | Present concise alternatives and ask one focused question |

## Translation Sequence

1. State the requested outcome in concrete behavioral language.
2. Inspect the repository before proposing files or implementation.
3. Add behavior that current evidence shows must be preserved.
4. Select the smallest valid engineering approach and label assumptions.
5. Identify whether any unresolved choice changes product meaning or risk.
6. Ask only for blocking open decisions.
7. If none remain, execute without requesting approval for routine engineering details.

## Decision Test

Ask the user when the answer changes one or more of these:

- What users can see or do.
- What data is stored, deleted, migrated, or exposed.
- Who has permission.
- Whether an action consumes money, quota, or a scarce external resource.
- Whether an effect is destructive or difficult to reverse.
- Which product meaning is correct when the repository does not establish it.

Do not ask the user to choose:

- Source files or symbols.
- Which Skill or subagent to invoke.
- Unit versus integration tests.
- Internal abstractions or implementation patterns.
- Risk labels.
- Facts that source, configuration, tests, or logs can answer.

## Minimal External Format

Most low-risk requests should not produce a large visible specification. Use a short statement when useful:

```markdown
I understand the goal as: [observable outcome].
I will first locate [production path/current constraint], then make the smallest change and verify [key behavior].
```

For a blocking ambiguity:

```markdown
The repository supports two materially different meanings:
1. [Option A and consequence]
2. [Option B and consequence]

Recommended default: [option and reason]. Which behavior do you want?
```

Internally, the agent can use:

```markdown
- Goal:
- Scope:
- Preserve:
- Acceptance:
- Risks:
- Verification:
- Repository facts:
- Proposed defaults:
- Open decisions:
```

## Scope Discipline

Active translation does not authorize feature expansion. Every changed line must trace to:

- explicit intent;
- a repository-proven constraint;
- an accepted proposed default; or
- verification required to prove the behavior.

Adjacent cleanup, speculative configurability, compatibility layers, and unrelated refactors remain out of scope unless concrete evidence makes them necessary.
