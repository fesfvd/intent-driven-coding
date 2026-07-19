# AI Adoption Entry

You are reading a framework for designing a project-specific AI engineering system. Do not copy this repository unchanged into another project.

## Intended Outcome

Adapt the framework to a target repository so that users can express goals in ordinary language, the agent translates intent without inventing product requirements, current facts come from repository evidence, stable professional methods live in Skills, and repeated outcomes are handled by small squads of usually two or three complementary Skills.

Every handoff should have an artifact, every completion claim should have fresh evidence, and product meaning plus risky external actions should remain human decisions.

## Read In This Order

Read only as far as needed for the next adaptation decision:

1. `README.md` for purpose and the central model.
2. `docs/PROTOCOL.md` for requirement translation.
3. `docs/CONTEXT_ARCHITECTURE.md` for the three context layers.
4. `docs/SQUAD_METHOD.md` for Skill, squad, and router boundaries.
5. `docs/SQUAD_WORKSHOP.md` for deriving project-specific capabilities and squads.
6. `docs/CAPABILITY_TIERS.md` when deciding which capabilities are universal candidates, conditional, or exceptional.
7. `docs/PROJECT_ARCHETYPES.md` and `docs/SQUAD_CATALOG.md` only as reference hypotheses, never as install manifests.
8. `skills/meta-skill-designer/SKILL.md` for roster and squad design.
9. `skills/skill-creator/SKILL.md` for drafting and evaluating individual Skills.
10. `templates/` only when producing target-project artifacts.
11. `evals/` when creating routing, handoff, near-miss, and permission cases.
12. `docs/PLATFORM_ADAPTERS.md` when mapping the result to the user's coding-agent platform.

Do not load every document and Skill by default. Follow the framework's progressive context model.

## Adaptation Workflow

### 1. Understand The Target

Inspect the target repository before writing framework files:

- product purpose and current user-visible behavior;
- executable source, configuration, schemas, and tests;
- real production entries and critical data flows;
- persistence, authentication, privacy, billing, external calls, and destructive boundaries;
- source/generated/deployed artifact relationships;
- existing agent instructions, Skills, scripts, and verification commands;
- recurring work, repeated failures, and manual quality checks.

Repository evidence outranks examples in this framework.

### 2. Translate The Need

Separate explicit user intent, repository-proven facts, proposed defaults, and open decisions. Ask only when alternatives change behavior, data, permissions, privacy, cost, or irreversible effects. Discover engineering details independently.

### 3. Design Before Copying

Use `meta-skill-designer` to derive the minimum stable capability roster, decide which bundled Skills are relevant, identify repeated outcomes that deserve squads, define handoff artifacts and exit conditions, and move deterministic rules into tests or scripts instead of Skills.

Two members are the default closed loop. Add a third only for a distinct material judgment. Do not treat the bundled roster or example squads as mandatory architecture.

### 4. Produce Target Artifacts

Create only what the target needs. Typical artifacts are:

- a thin platform-recognized agent entry;
- `AGENTS.md` for architecture semantics and cross-file impact;
- `AI_ENGINEERING_PLAYBOOK.md` for workflow, risk, and verification;
- `SQUADS.md` for accepted project-specific formations;
- platform-recognized project-local Skills;
- a small routing and handoff evaluation set.

Templates are scaffolding. Replace placeholders with repository evidence and remove inapplicable sections.

### 5. Adapt To The Host Platform

Read `docs/PLATFORM_ADAPTERS.md`. Determine the installed tool and version, then map its project instruction entry, Skill location or on-demand reading mechanism, tool names, permissions, subagent support, and external-action confirmation behavior.

Do not claim automatic compatibility without testing actual discovery and triggering behavior.

### 6. Verify The Adaptation

At minimum:

- remove unresolved placeholders;
- confirm every registered squad references available Skills;
- keep normal squads to two or three members;
- test one direct low-risk request;
- test one squad request;
- test one product ambiguity;
- test one permission gate;
- run the target project's real checks;
- run `scripts/validate_project.py --target <target>` from this framework repository when available.

## Do Not

- Do not copy every Skill because it exists.
- Do not copy example squads as target-project facts.
- Do not freeze volatile routes, versions, service names, or feature lists into long-lived Skills.
- Do not replace repository investigation with template completion.
- Do not create a Skill for deterministic work better enforced mechanically.
- Do not count the router as a squad member.
- Do not add a third member without a distinct material judgment.
- Do not treat generated files as proof that adaptation is complete.
- Do not commit, push, publish, deploy, write production data, call paid services, or perform destructive actions without explicit authorization.

## Optional Scaffolding

`scripts/bootstrap.py` may create a neutral file skeleton after the framework and target project are understood. It is not the primary adoption process and does not perform project analysis or platform adaptation.

Prefer deliberate AI-assisted adaptation. Use scaffolding only when it saves mechanical file creation without replacing professional judgment.
