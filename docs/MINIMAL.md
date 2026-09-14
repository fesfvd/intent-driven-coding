# Minimal Path

This is the smallest useful adoption path. Stop after one safe task unless repeated work proves that more structure will help.

- **Skill**: one reusable professional judgment, such as debugging or verification.
- **Squad**: two or three complementary Skills used in a declared order.
- **Contract**: a human- or machine-readable statement of the route, handoffs, evidence, and permission boundary.
- **Evidence**: fresh source, test, command, artifact, host, or human facts that support a claim.

For the first task, capture the request, inspect the target repository, apply
mutable labels from [Task Scenarios](TASK_SCENARIOS.md), read only the relevant
Skill on demand, and make the smallest safe change. Promote durable work to
`IDC-<PROJECT>-<YYYYMMDD>-<NNN>` and append facts to `events.jsonl`; derive
dynamic obligations from impact, acceptance, verification, and permission.
Record uncertainty
instead of inventing requirements. A `debug` -> `verify` sequence is enough for
an unknown-root-cause bug; use a third judgment only when it controls a
distinct risk.

Do not install every template, create a meta Skill, write a contract, or depend on host auto-routing before a repeated failure or coordination problem justifies it. Current host acceptance does not prove automatic project Skill selection. Treat project-local Skills as material an Agent can read explicitly, then perform host acceptance before relying on discovery or delegation behavior.
