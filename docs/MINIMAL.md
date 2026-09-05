# Minimal Path

This is the smallest useful adoption path. Stop after one safe task unless repeated work proves that more structure will help.

- **Skill**: one reusable professional judgment, such as debugging or verification.
- **Squad**: two or three complementary Skills used in a declared order.
- **Contract**: a human- or machine-readable statement of the route, handoffs, evidence, and permission boundary.
- **Evidence**: fresh source, test, command, artifact, host, or human facts that support a claim.

For the first task, inspect the target repository, classify the work with
[Task Scenarios](TASK_SCENARIOS.md), read only the relevant Skill on demand,
and make the smallest safe change. For non-trivial work, begin with an
`IDC-<PROJECT>-<SCENARIO>-<YYYYMMDD>-<NNN>` task card containing intent, scope,
impact, acceptance, verification, and permission gates. Record uncertainty
instead of inventing requirements. A `debug` -> `verify` sequence is enough for
an unknown-root-cause bug; use a third judgment only when it controls a
distinct risk.

Do not install every template, create a meta Skill, write a contract, or depend on host auto-routing before a repeated failure or coordination problem justifies it. Current host acceptance does not prove automatic project Skill selection. Treat project-local Skills as material an Agent can read explicitly, then perform host acceptance before relying on discovery or delegation behavior.
