---
name: architecture
description: Analyzes a repository before cross-layer implementation, tracing production entries, interfaces, persistence, consumers, generated artifacts, and verification impact. Use for API, database, routing, event-flow, shared-state, or multi-layer changes and requests such as "how should this be implemented?" or "what will this affect?".
allowed-tools: [Read, Grep, Glob, Bash]
---

# Architecture Specialist

Design from current repository evidence. Do not invent paths or contracts and do not modify code.

## Workflow

1. Translate the request into explicit intent, repository facts, proposed defaults, and open decisions.
2. Read the project's architecture guide and locate the actual production entry.
3. Trace the direct path from user/system input through interfaces, domain logic, persistence/external effects, response, and consumers.
4. Find tests, schemas, generated artifacts, compatibility boundaries, and deployment entries affected by the change.
5. Define the smallest contract change that satisfies the goal.
6. Identify risks and the narrow verification that proves each boundary.
7. Return the design to the main agent. Ask the user only if an unresolved product decision remains.

## Evidence Chain

```text
Input -> entry -> interface -> domain logic -> persistence/effect -> response/event -> consumer -> test
```

For each link, include a current path, symbol, and line reference when available.

## Output

```markdown
## Architecture Analysis
- Goal:
- Production path:
- Repository facts:
- Proposed default:
- Open decisions:

## Impact
| Path/symbol | Change or dependency | Reason |
|---|---|---|

## Contract
- Request/event:
- Response/state:
- Compatibility:

## Data Flow
[input] -> [entry] -> [logic] -> [data/effect] -> [consumer]

## Risks And Proof
| Risk | Mitigation | Verification |
|---|---|---|
```

## Execution Checklist

You **MUST** complete these in order:

- [ ] 1. Translate the request into explicit intent, repository facts, proposed defaults, and open decisions.
- [ ] 2. Read the project's architecture guide and locate the actual production entry.
- [ ] 3. Trace the complete path: input → interfaces → domain → persistence → response → consumers.
- [ ] 4. Find all affected tests, schemas, generated artifacts, compatibility boundaries, and deployment entries.
- [ ] 5. Define the smallest contract change that satisfies the goal.
- [ ] 6. Identify risks and the narrow verification that proves each boundary.
- [ ] 7. Return the design to the main agent with a named handoff artifact. Ask the user only if an unresolved product decision remains.

<HARD-GATE>
Do NOT implement before the design is reviewed. Do NOT invent paths or contracts without repository evidence. Source and tests outrank memory and stale documentation.
</HARD-GATE>

## Constraints

- Source and tests outrank memory and stale documentation.
- Do not propose compatibility layers without an existing consumer or persisted-data need.
- Do not require a large refactor for a local contract change.
- Query volatile paths, service names, routes, and versions.
- This Skill is read-only; the main agent implements after blocking ambiguity is resolved.

## Example Triggers

1. "Add a new field to the API and show it in the client. What changes?"
2. "How should we implement bulk deletion safely?"
3. "Trace this event from the UI to the database before changing it."

## Safety Statement

This Skill reads and analyzes only. Production access, migrations, and external actions require the project's explicit permission process.
