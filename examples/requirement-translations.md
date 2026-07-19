# Requirement Translation Examples

These examples show behavior, not exact wording. The agent should keep visible process proportional to the task.

## 1. Unknown Bug

User:

```text
The report is blank. Fix it.
```

Translation:

- Explicit intent: restore report rendering.
- Repository facts to discover: report producer, parser, persistence, API/event response, frontend consumer, production bundle/build path.
- Proposed default: reproduce and fix the first layer where valid data disappears.
- Open decision: none unless the repository does not define what report content should be visible.
- Route: `debug` -> implementation -> `verify`.

Do not ask whether the bug is frontend or backend; investigate it.

## 2. Privacy Ambiguity

User:

```text
Add a public switch to documents.
```

Translation:

- Explicit intent: users can control publication.
- Repository facts to discover: existing visibility fields, report/source separation, permissions, indexes, API and UI flow.
- Proposed default: least exposure consistent with existing behavior.
- Open decision: if "public" may mean metadata only, generated report, or full source content, ask because privacy behavior changes.
- Route: `architecture`, then ask one focused question if evidence cannot decide.

## 3. Responsive UI

User:

```text
This page is cramped on mobile.
```

Translation:

- Explicit intent: remove mobile crowding.
- Repository facts to discover: actual production component, breakpoints, overflow, spacing tokens, interaction states, desktop hierarchy.
- Proposed default: smallest responsive adjustment that preserves desktop behavior.
- Open decision: ask only if multiple information hierarchies are equally valid and visibly different.
- Route: project frontend specialist if available, otherwise direct implementation -> `verify`.

## 4. Broad Optimization

User:

```text
Optimize this endpoint.
```

Translation:

- Explicit intent: ambiguous performance/reliability goal.
- Repository facts to discover: current latency, query count, payload, error rate, hot path, tests.
- Proposed default: measure before changing.
- Open decision: ask what outcome matters only if repository evidence and context do not reveal it, such as latency versus memory versus external cost.
- Forbidden expansion: unrelated refactoring, caching, pagination, or infrastructure without measured need.

## 5. Continue

User:

```text
Continue.
```

Translation:

- Resume the latest unfinished safe stage using current task state.
- Do not repeat requirements already resolved.
- Do not cross a commit, deployment, production, paid-call, or destructive permission gate.

## 6. Delete

User:

```text
Let users delete their account.
```

Translation:

- Explicit intent: account deletion capability.
- Repository facts to discover: owned data, legal retention, soft-delete fields, external identities, billing, shared/public content, restoration behavior.
- Open decision: permanent deletion versus deactivation/anonymization materially changes data and irreversibility; ask if policy is not established.
- Route: `architecture` plus security/privacy specialist when available.

## 7. Review

User:

```text
Check the changes before release.
```

Translation:

- Explicit intent: identify release-blocking risks.
- Repository facts to discover: intended diff, release entry, verification matrix, migrations/config changes.
- Route: `verify` and `code-review`; project release specialist only if the user requests actual release work.
- Permission: review does not authorize commit, push, PR, or deployment.

## 8. Add Filtering

User:

```text
Add filtering to the list.
```

Translation:

- Explicit intent: users can narrow list results.
- Repository facts to discover: existing fields, server/client ownership, pagination, URL state, authorization, data size.
- Proposed default: use the current list architecture and expose only the requested filter.
- Open decision: ask which business field or semantics to filter if not established.
- Forbidden expansion: search, sorting, saved views, export, and advanced query builders unless requested or required.
