# AI Adoption Entry

You are reading a framework for designing a project-specific AI engineering system. Do not copy this repository unchanged into another project.

## Intended Outcome

Adapt the framework to a target repository so that users can express goals in ordinary language, the agent translates intent without inventing product requirements, current facts come from repository evidence, stable professional methods live in Skills, and repeated outcomes are handled by small squads of usually two or three complementary Skills.

Every handoff should have an artifact, every completion claim should have fresh evidence, and product meaning plus risky external actions should remain human decisions.

## Learn While Delivering

The human does not need to study this framework before benefiting from it. You, the coding agent, own framework learning, repository investigation, host-platform adaptation, and incremental system design.

Do not make full framework adaptation a prerequisite for the user's current task. Read only enough to act safely, deliver the current useful result, and collect evidence while working. Explain framework concepts briefly only when they affect a decision the user owns.

## Identify Your Host First

Before reading the full method, identify whether you are Claude Code, OpenCode, Codex, Cursor, GitHub Copilot, or another coding agent. Then read the matching section in `docs/PLATFORM_ADAPTERS.md` and use the host's real instruction, Skill, agent, permission, and task mechanisms. Do not ask the user to translate this framework into your platform conventions.

## Read In This Order

Read only as far as needed for the next adaptation decision:

1. `docs/PLATFORM_ADAPTERS.md` for your own host-specific path.
2. `docs/PROTOCOL.md` and the relevant base Skill for the current task.
3. `docs/CONTEXT_ARCHITECTURE.md` when deciding where durable knowledge belongs.
4. `docs/SQUAD_METHOD.md` when more than one professional judgment is needed.
5. `skills/meta-skill-designer/SKILL.md` only when repeated evidence justifies system design.
6. `skills/skill-creator/SKILL.md` only after a Skill contract is ready.
7. Capability, archetype, squad, template, and evaluation references only when the current adoption decision needs them.

Do not load every document and Skill by default. Follow the framework's progressive context model.

## Progressive Adoption Loop

Use this loop from the first real request:

```text
current user goal
  -> inspect only the relevant repository path
  -> use the smallest safe capability chain
  -> implement and verify the result
  -> record repeated friction, risk, and reusable handoffs
  -> add or revise project guidance only when evidence passes the creation gate
```

The first successful task may produce no new framework files. That is acceptable. Build project infrastructure only when it will reduce future work or control a real risk.

## Adaptation Workflow

### 1. Understand The Target

Inspect the target repository around the current task before writing framework files. Expand only when architecture or risk requires it:

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

Use `meta-skill-designer` after progressive evidence reveals recurring work, repeated correction, a material failure boundary, or missing handoffs. Do not hold the current task hostage while attempting to design a complete future roster.

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
