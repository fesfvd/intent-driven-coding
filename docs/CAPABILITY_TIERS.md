# Capability Tiers

This guide helps a project decide which professional judgments deserve Skills. It is a design reference for `meta-skill-designer`, not a universal installation list.

## Default To Evaluation, Not Installation

Some capabilities are useful in almost every maintained software project. That means they should be evaluated first, not copied automatically and not invoked for every request.

Use this sequence:

```text
candidate capability
  -> repository evidence
  -> creation gate
  -> project-local contract
  -> routing and handoff evaluation
  -> accepted Skill or rejected hypothesis
```

The host agent may already perform a capability reliably. Create a Skill only when a project needs a more explicit method, trigger, handoff, or safety boundary.

## Tier 1: Universal Candidates

Evaluate these for almost every real software repository:

| Capability | Why it is broadly useful | Typical route | Do not over-route when |
|---|---|---|---|
| Intent routing | Separates user intent, repository facts, defaults, and open decisions | Every non-trivial intake | The host already has an equivalent thin control plane |
| Debugging | Prevents guessed fixes when the cause is unknown | `debug -> verify` | The cause and exact edit are already proven |
| Code review | Finds correctness, regression, data, security, and maintainability risks in changed behavior | `code-review -> verify` | The edit is mechanical, local, and fully covered by a narrow check |
| Verification | Requires fresh evidence before completion claims | Final proof stage | Never omit when claiming fixed, passing, ready, or complete |
| Architecture impact | Traces contracts, consumers, persistence, and cross-layer effects | `architecture -> code-review -> verify` | The change is isolated and has no meaningful boundary impact |

Code review and verification are different. Review asks whether the change contains risks not captured by the implementation story. Verification asks which fresh evidence proves each acceptance claim. Neither replaces the other.

Tier 1 capabilities belong in the project's capability pool when warranted. They do not form a permanent squad and do not all run on every task.

## Tier 2: Conditional Specialists

Add these only when repeated work or repository risk makes the judgment materially distinct:

| Risk trait | Candidate capability | Evidence that justifies it |
|---|---|---|
| Authentication or authorization | Security or authorization review | Repeated allow/deny logic, role matrices, incidents, sensitive endpoints |
| Persisted schema evolution | Migration and data-integrity review | Production migrations, compatibility windows, backfills, rollback constraints |
| User-facing interaction | UX, accessibility, or visual verification | Repeated usability failures, design-system constraints, browser/device matrices |
| Public API or SDK | API contract and backward-compatibility review | External consumers, versioning, deprecation obligations |
| Billing or quota | Billing, idempotency, or reconciliation review | Monetary effects, retries, duplicate prevention, ledger reconciliation |
| Async or distributed work | Reliability, concurrency, or recovery review | Queues, retries, ordering, eventual consistency, duplicate delivery |
| External integrations | Integration failure and cost review | Paid calls, rate limits, partial failure, provider fallback |
| Deployment complexity | Release readiness and rollback review | Multiple environments, migrations, irreversible rollout steps |
| Performance constraints | Profiling and capacity review | Measured latency, throughput, memory, or cost targets |
| LLM behavior | Prompt contract, evaluation, safety, or cost review | Non-deterministic outputs, structured parsing, model changes, safety boundaries |

Technology presence alone is insufficient. A project using a database does not automatically need a database Skill; repeated high-cost migration judgment may justify one.

## Tier 3: Exceptional Specialists

Create only for repeated domain expertise or high-consequence boundaries that general engineering review cannot cover reliably:

- financial ledger integrity;
- medical or clinical safety;
- tenant isolation and regulated data separation;
- regulatory traceability and retention;
- embedded real-time or resource limits;
- cryptographic protocol review;
- search or recommendation quality evaluation;
- model training, data lineage, and release governance.

These Skills require stronger evidence, domain-specific evaluation cases, and an explicit statement of what general review cannot judge.

## Creation Gate

Create a Skill only when all are true:

1. The outcome recurs or the failure boundary is materially expensive.
2. The judgment is not already covered by another Skill or deterministic control.
3. The method is stable across current implementation details.
4. Positive triggers and near misses can be separated.
5. The output is a concrete downstream artifact.
6. The expected benefit exceeds added routing, maintenance, and context cost.

Otherwise prefer direct agent instructions, project documentation, scripts, tests, schemas, linters, or more observation.

## Lifecycle

Review accepted Skills after meaningful architecture changes or repeated routing failures:

- retain when real work still selects it and its handoff saves investigation;
- narrow when false positives are common;
- merge when another Skill owns the same judgment;
- move volatile facts back to repository queries;
- replace deterministic sections with scripts or tests;
- retire when removing it loses no necessary judgment.
