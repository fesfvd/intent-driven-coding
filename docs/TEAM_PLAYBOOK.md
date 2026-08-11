# Team Playbook

## The Small-Squad Model

An agent system should be organized around distinct professional judgments, not personalities or a large catalog of prompts. A Skill is one capability; a squad is usually two or three Skills assembled around one outcome.

The router receives ordinary language and selects the smallest registered squad that can safely complete the work. The router is the control plane and is not counted as a squad member. Specialists remain narrow: they provide a method and a handoff artifact, then return control to the main agent or next specialist.

Requirement translation is part of this control plane, not a separate specialist by default. It classifies intent, repository facts, proposed defaults, and open decisions so the router can select the next smallest safe route. Create a project-specific product or requirements Skill only when repeated work requires an independent professional judgment, a concrete downstream artifact, and a boundary that the router must not decide.

```text
Intent -> translate -> classify risk -> determine phases -> select squad -> gate transitions -> specialist handoffs -> build -> proof -> external action if authorized
```

See `SQUAD_METHOD.md` for composition rules, `SQUAD_WORKSHOP.md` for deriving project-specific formations, `CAPABILITY_TIERS.md` for capability selection, and `SQUAD_CATALOG.md` for reference formations.

## Capability Roster

### Team Router

Owns:

- Requirement translation.
- User-facing presentation preference.
- Risk classification.
- Minimum Skill selection.
- Workflow state and permission gates.

Does not own:

- Architecture conclusions.
- Root-cause conclusions.
- Review findings.
- Verification evidence.

### Architecture Specialist

Use when interfaces, persistence, routing, generated artifacts, or multiple layers are affected.

Output:

- Actual production path.
- Impact chain.
- Contract changes.
- Files and consumers affected.
- Risks and narrow verification.

### Debug Specialist

Use when the root cause is unknown.

Output:

- Symptom and environment.
- First broken layer.
- Evidence.
- Falsifiable hypothesis.
- Minimal reproduction or failing test.
- Root cause and narrow fix.

### Code Review Specialist

Use for requested reviews, medium/high-risk changes, and release preparation.

Output findings first, ordered by severity, with file/line evidence, trigger conditions, and impact. It does not replace verification and should not fill the response with style preferences.

### Verification Specialist

Use before any claim that work is complete, fixed, passing, ready to merge, or ready to release.

It identifies the command that proves each claim, runs it freshly, reads the complete result, and reports omissions honestly.

### Meta Skill Designer

Use when the professional system itself needs design: repeated work, overlapping Skills, missing handoffs, or weak routing.

Output:

- Workflow evidence.
- Distinct role boundaries.
- Two- or three-Skill squad contracts.
- Trigger and handoff evaluation plan.

### Skill Creator

Use after a role and squad boundary are understood.

Output:

- Lean `SKILL.md` and optional resources.
- Positive and near-miss trigger cases.
- Handoff and safety evaluations.
- Evidence-based iterations.

## Standard Squads

| Outcome | Squad | Phase path |
|---|---|---|
| Exact low-risk edit | Main agent -> verify | INTAKE → BUILD → VERIFY |
| Cross-layer feature | architecture -> code-review -> verify when material risk warrants all three | INTAKE → DESIGN → BUILD → VERIFY → REVIEW |
| Unknown-root-cause bug | debug -> verify; add code-review only for a distinct material regression boundary | INTAKE → DESIGN(debug) → BUILD → VERIFY (+ REVIEW) |
| Explicit code review | code-review -> verification gap report | INTAKE → REVIEW → VERIFY |
| Release preparation | verify -> code-review -> project-specific deployment process | INTAKE → VERIFY → REVIEW → SHIP |
| Production incident | project-specific read-only operations -> debug -> local fix -> release process | INTAKE → DESIGN(debug) → BUILD → VERIFY → SHIP |
| Skill/team design | meta-skill-designer -> skill-creator | INTAKE → DESIGN(meta) → BUILD(meta) |

The full pipeline phase model, including phase→squad mapping and phase gates, is defined in `skills/team/SKILL.md`. The router determines which phases apply per task type, then gates each transition.

Do not summon a design, planning, security, testing, review, and deployment specialist for every request. A large team is not evidence of rigor. If one specialist plus proof closes the result, use two. A third member must guard a distinct boundary.

## Adding Specialists

Add a Skill when all are true:

1. The work recurs.
2. It requires judgment that the existing roster does not represent.
3. A narrow trigger can be described in natural user language.
4. Its method is stable enough to outlive current paths and versions.
5. Its output can hand control back cleanly.

After defining a specialist, decide which outcome squads need it. An unused capability is not automatically a squad.

Classify candidates before drafting:

- universal candidates are evaluated for most projects but are not installed or invoked automatically;
- conditional specialists require a repeated material repository boundary;
- exceptional specialists require domain-specific judgment or high failure cost.

Project labels and technology choices seed investigation only. Risk traits and repeated outcomes decide the roster. See `CAPABILITY_TIERS.md` and `PROJECT_ARCHETYPES.md`.

Potential Phase 2 specialists:

- Security and privacy review.
- UX flow audit.
- Production frontend design.
- Prompt/LLM contract design.
- Performance profiling.
- Deployment and operations.
- External research.
- Skill freshness auditor.

## Skill Quality Rules

- Frontmatter description states what the Skill does and when ordinary language should trigger it.
- The body contains method, constraints, exit criteria, and output format.
- Stable method stays in the Skill; volatile facts are queried.
- Read-only Skills do not claim to modify code.
- High-risk side effects contain an explicit confirmation boundary.
- Overlapping Skills have a documented handoff.
- Three realistic trigger examples are included.

## Squad Quality Rules

- One observable outcome defines the formation.
- Two members are the default; three is the maximum normal formation.
- Each member owns a distinct judgment.
- Every sequential handoff names a concrete artifact.
- Exit conditions are observable.
- The proof role is independent from the primary judgment.
- Permission gates name the external effect.
- Positive, near-miss, handoff, and safety cases exist.

## State Machine (Pipeline Phases)

The full pipeline phase model lives in `skills/team/SKILL.md`. This section summarizes the canonical state machine:

```text
Intake -> Design? -> Plan? -> Build -> Verify -> Review? -> Ship? -> Learn?
```

Each phase maps to a specific squad activation. Not all tasks go through all phases — the router selects the subset appropriate to the task type and risk.

**Phase entry conditions:**
- Enter **Design** when cross-boundary judgment or root-cause investigation is required.
- Enter **Plan** only when the user requests a plan or safe execution requires one.
- Enter **Build** only after DESIGN gate is satisfied and open decisions are resolved.
- Enter **Verify** after every Build (not skippable).
- Enter **Review** for material regression risk or an explicit review request.
- Enter **Ship** only on explicit authorization naming the exact side effect.
- Enter **Learn** after repeated failures or recurring workflow friction.

The word "continue" resumes the latest unfinished safe stage. It never bypasses a permission gate.

## Presentation Preference

The router carries the user's resolved language preference through user-facing artifacts and final reports. Explicit preference wins; otherwise use the current user language, then an explicitly established audience language. This localizes presentation, not code, commands, identifiers, APIs, or maintainer-only documentation. A specialist must preserve the preference when its artifact is intended for the user.
