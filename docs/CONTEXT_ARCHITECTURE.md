# Context Architecture

## Goal

Optimize context capability density, not raw prompt length. Every loaded section should change a decision in the current task.

Reducing context must not increase the user's burden. The user describes intent; the agent derives the task contract, risk, specialist route, and verification plan.

## Three Layers

### 1. Persistent Entry

Keep only stable cross-task boundaries and pointers:

- Source and tests are the executable truth.
- Read before editing.
- Make the smallest correct change.
- Preserve unrelated work.
- Evidence is required before completion claims.
- External and production writes require confirmation.
- Where to find architecture, process, design, and specialist methods.

Do not put endpoint catalogs, service versions, current model lists, prices, or complete architecture manuals here.

### 2. On-Demand Methods

Load a Skill only when its professional method changes the result.

```text
Skills teach the agent how to judge.
The repository tells the agent what is currently true.
```

Skills should preserve stable methods such as root-cause diagnosis or diff review. They should query volatile facts such as routes, modes, container names, feature flags, thresholds, and deployment topology.

### 3. Task Evidence

Build current context from:

- Source and configuration.
- Tests and schemas.
- Generated architecture indexes.
- Runtime output and logs.
- Version-control diff.

Expand from production entry to direct call path, consumers, and tests. Stop when evidence is sufficient to make the next decision.

## Loading Budget

| Level | Typical task | Context strategy |
|---|---|---|
| L0 | Question or exact lookup | Target file or command only; no Skill |
| L1 | Local low-risk edit | Entry rules, target path, focused test |
| L2 | Cross-file feature, UI, prompt, or contract | Task contract, one specialist, direct call chain |
| L3 | API, database, authentication, permissions, billing | Architecture semantics, specialist, contract/security verification |
| L4 | Deployment, incident, migration, production data | Full evidence chain, operations specialist, explicit permission gate |

File count alone does not determine the level. Risk and cross-boundary behavior do.

## Authority Map

| Artifact | Responsibility |
|---|---|
| Agent entry | Stable boundaries and pointers |
| `AGENTS.md` | Human architecture semantics, critical flows, cross-file impact |
| Engineering playbook | Task contract, workflow, verification, completion standard |
| Design system | Production UI rules |
| Generated map | Machine-generated structural facts |
| Team router | Classification and minimum specialist composition |
| Specialist Skill | Stable professional method and output contract |
| Tests/scripts/lint | Deterministic constraints and mechanical rejection |

## Placement Test

Before adding a rule, ask:

1. Does it affect most tasks and remain stable? Put it in the entry or playbook.
2. Does it affect one type of professional judgment? Put it in a Skill.
3. Is it volatile and searchable? Keep it in source, configuration, or a generated map.
4. Can a machine reject violations? Implement a test, script, schema, or lint rule.
5. Is it a temporary plan or audit? Keep it outside permanent instructions.

## Evolution Path

```text
One observation -> session conclusion
Repeated architecture fact -> AGENTS.md
Operating discipline -> engineering playbook
Professional method -> Skill
Cross-specialist composition -> team router
Deterministic constraint -> test/script/lint
```

Avoid maintaining the same fact in multiple Skills. Duplication creates stale confidence.
