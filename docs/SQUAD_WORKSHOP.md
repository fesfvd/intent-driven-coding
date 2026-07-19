# Build Your Project's Professional Squads

This workshop converts recurring project work into a small roster of professional Skills and two- or three-Skill squads.

## Step 1: Collect Outcomes

List 10 to 20 recent or expected requests in the language people actually use:

```text
The checkout total is wrong.
Add an approval state to invoices.
Review this before release.
The mobile form is hard to use.
Deploy the verified revision.
```

Do not start by naming Skills. Start with outcomes and failures.

## Step 2: Cluster By Required Judgment

For each request, ask what professional judgment changes the result:

| Repeated need | Candidate capability |
|---|---|
| Unknown cause across layers | Root-cause diagnosis |
| Contract and persistence change | Architecture impact analysis |
| Permission-sensitive behavior | Security/privacy review |
| Production interaction flow | UX audit |
| Claim needs proof | Verification |
| Repeated Skill/team maintenance | Meta Skill design |

One cluster may become a Skill when it has a stable method, clear trigger, and reusable output.

Classify it as a universal candidate, conditional specialist, or exceptional specialist using `CAPABILITY_TIERS.md`. Project archetypes in `PROJECT_ARCHETYPES.md` provide questions, not answers.

## Step 3: Draft Each Skill Boundary

For every candidate, complete:

```markdown
- Capability:
- Triggers in ordinary language:
- Inputs/evidence:
- Judgment owned:
- Output artifact:
- Explicit exclusions:
- Handoff target:
- Safety boundary:
```

If two candidates own the same judgment or output, combine them or make the boundary sharper.

Apply the creation gate before continuing. A human job title, technology choice, or hypothetical future need is not enough.

## Step 4: Form Squads Around Outcomes

Use `templates/SQUAD.md` for each recurring outcome.

`SQUAD_CATALOG.md` contains candidate formations. Treat them as hypotheses to prove against the repository, not squads to register unchanged.

Prefer:

- two members for primary judgment plus proof;
- three members only when a distinct risk/domain guard is necessary;
- no squad for obvious low-risk work that the main agent and focused verification can close.

Example:

```text
Outcome: safely implement a cross-layer API feature
Members: architecture + code-review + verify
Handoff 1: interface/data-flow contract
Handoff 2: implementation diff and known risks
Exit: acceptance checks pass; no blocking review findings
```

## Step 5: Write Routing Cases

For each Skill and squad, create:

- three to five positive requests;
- three to five near-miss requests that should not select it;
- one ambiguous request that requires repository context;
- one handoff case;
- one permission-boundary case where relevant.
- one competing-Skill conflict case;
- one over-routing case proving low-risk direct work stays small.

Store machine-readable cases using `evals/squad-routing.json` as a starting schema.

## Step 6: Evaluate Handoffs

Do not evaluate only whether a Skill produces a polished answer. Check whether the next member can use its output without redoing the work.

Good handoff assertions include:

- The architecture output names the actual producer and consumers.
- The debug output distinguishes evidence from inference.
- The review output references the implemented contract.
- Verification maps commands to explicit acceptance claims.
- Permission-gated effects remain unexecuted.

## Step 7: Run The Meta Squad

Use:

```text
meta-skill-designer -> skill-creator
```

The first member derives roles, boundaries, and squad contracts. The second writes or improves each Skill, creates positive and near-miss evaluations, compares outputs, and iterates.

When files are ready for publication, run repository verification separately.

## Step 8: Keep The Roster Small

Review every few months or after major architecture changes:

- Remove unused Skills.
- Merge overlapping roles.
- Replace stale facts with repository queries.
- Promote deterministic rules into tests or scripts.
- Add a specialist only after repeated evidence of a missing judgment.
- Re-run routing and handoff cases after description changes.

## Workshop Exit Criteria

- Every Skill owns one distinct professional judgment.
- Every registered squad closes one observable outcome.
- Every squad has two or three necessary members.
- Every handoff names a concrete artifact.
- Positive and near-miss routing cases exist.
- High-risk side effects remain human-gated.
- The router selects squads but does not impersonate their specialists.
