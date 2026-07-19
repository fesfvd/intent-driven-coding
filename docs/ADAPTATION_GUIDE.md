# Repository Adaptation Guide

## Objective

Turn the generic framework into a trustworthy local operating system for one repository. The target is not maximal documentation. The target is enough current context for an agent to make correct decisions and know what it must verify.

## Evidence Before Infrastructure

Adaptation is an AI responsibility performed alongside useful project work. Do not require the human to learn the framework, complete templates, enumerate Skills, or design squads before the first task can succeed.

Start with the user's current goal. Apply the smallest safe methods, inspect the relevant production path, and verify the result. While doing so, gather evidence about repeated investigation, corrections, failure boundaries, missing handoffs, and stable project rules. Create durable files and Skills only when that evidence shows they will reduce future work or control a material risk.

Teach through brief decisions at the moment they matter. Explain why you are asking a product question, loading a specialist, adding a permission gate, or proposing durable guidance; do not turn adoption into a reading assignment.

Use two concurrent tracks:

```text
Delivery track: current goal -> smallest safe route -> implementation -> fresh proof
Learning track: friction/risk evidence -> reusable rule or handoff -> creation gate -> incremental adaptation
```

## Step 1: Establish Truth Sources

Rank the repository's sources of truth. A common order is:

1. Executable source, configuration, schemas, and tests.
2. Generated architecture indexes.
3. Human-maintained architecture semantics.
4. Engineering workflow and verification policy.
5. Design and operations documents.
6. Skills as professional methods.

When documentation conflicts with executable evidence, fix drift within task scope rather than preserving a false description.

## Step 2: Map Production Reality

Document only facts that materially affect changes:

- Runtime entry points.
- Request/event/job flow across layers.
- Persistence and transaction boundaries.
- Authentication and authorization boundaries.
- External integrations and cost-bearing calls.
- Source versus generated/deployed artifact relationships.
- Hot reload versus restart/rebuild requirements.
- Shared functions and implicit module ordering.

Avoid a line-by-line directory catalog unless it changes impact analysis.

## Step 3: Build The Impact Matrix

For recurring changes, record what else must be checked:

| Change type | Primary location | Common consumers | Required verification |
|---|---|---|---|
| API field | Router/schema | Client, tests, docs | Contract and consumer tests |
| Database field | Model/migration | Services, serialization, jobs | Migration and compatibility tests |
| Frontend source module | Source component/page | Production bundle/build output | Build plus deployed-entry inspection |
| Permission rule | Auth/service | Every role and resource owner path | Allow/deny matrix |
| LLM output schema | Prompt/parser | Persistence, calculation, UI | Valid, missing, extra, truncated cases |

Replace this generic matrix with your repository's real coupling.

## Step 4: Make Verification Executable

Every command in the playbook should run from a defined working directory and have a clear proof target.

Include:

- Focused unit or contract tests.
- Full relevant suite.
- Lint and type checking when present.
- Build or package verification.
- Structural map regeneration rules.
- Manual UI or device checks that cannot yet be automated.
- Production smoke boundaries and side effects.

Delete fictional placeholders after setup. Do not let an agent treat a template command as real.

## Step 5: Derive Skills And Squads

Keep the base capabilities only when they serve your project. Do not treat the bundled roster as a mandatory permanent team.

Rename specialists only if your agent platform requires it. Prefer generic capabilities over project-branded roles in reusable Skills; keep product-specific expertise in project-local Skills.

When adding a specialist:

- Put real user phrases in the frontmatter description.
- State handoff boundaries.
- Query current repository facts.
- Add examples and safety constraints.
- Test it with positive and negative routing cases.

Then form two- or three-Skill squads around repeated outcomes:

- primary judgment plus independent proof by default;
- add a third domain/risk guard only when it owns a distinct material boundary;
- define handoff artifacts, exit conditions, and permission gates;
- register accepted formations in `SQUADS.md`.

Use `meta-skill-designer -> skill-creator` to design and evaluate the system itself.

## Step 6: Test Behavior, Not Just Files

Create a small evaluation set:

- Low-risk request that should execute directly.
- Cross-layer request that should load architecture.
- Unknown bug that should load debugging.
- Product ambiguity that should ask one question.
- High-risk request that should stop at permission.
- Completion claim that should trigger fresh verification.
- Skill/team design request that should invoke the meta-design squad.
- Near-miss request that should avoid an oversized squad.

Record expected routing and forbidden behavior. This becomes a regression suite for your agent framework.

## Step 7: Keep It Fresh

Audit periodically for:

- Paths that no longer exist.
- Commands that no longer run.
- Renamed services or endpoints frozen into Skills.
- Duplicate rules across entry, playbook, and Skills.
- New recurring tasks with no specialist.
- Long Skills loaded for simple work.
- Permission gates weakened by convenience language.

Promote deterministic rules into tests and scripts whenever possible.
