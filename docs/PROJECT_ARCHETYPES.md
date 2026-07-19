# Project Archetypes

Project archetypes seed investigation questions. They do not prove which Skills a repository needs.

## Risk Traits Outrank Project Labels

Risk traits outrank project labels when selecting capabilities.

Two projects called "SaaS" may have completely different boundaries. One may be a simple internal dashboard; another may handle payments, regulated data, multi-tenancy, queues, and public APIs. `meta-skill-designer` should inspect risk traits before using these reference patterns.

For each project, first ask:

- Who consumes its outputs and contracts?
- What data persists, and what is difficult to reverse?
- Where are authorization, privacy, money, quota, or paid-call boundaries?
- Which work repeatedly fails review or requires specialist judgment?
- What must remain compatible across versions, platforms, or deployments?
- Which claims need behavior evaluation beyond ordinary tests?

## Content Or Documentation Site

Common starting candidates:

- code review and verification;
- accessibility and visual verification when presentation matters;
- SEO or content validation when discoverability is a product requirement.

Usually unnecessary without contrary evidence:

- migration, billing, distributed reliability, and authorization specialists.

## SaaS Web Application

Common starting candidates:

- router, architecture, debug, code review, and verification;
- authorization, migration, UX, billing, integration, or release specialists only where those boundaries exist.

Avoid creating PM, frontend, backend, QA, and DevOps Skills merely to mirror a human organization. Create the judgment that is missing, such as product ambiguity handling, API contract review, migration safety, or release readiness.

## API Service Or Backend

Common starting candidates:

- architecture, debug, code review, verification;
- API contract, data integrity, integration recovery, observability, or performance when evidenced.

Public consumers increase compatibility needs. Internal-only services may not require a separate API specialist.

## CLI Or Developer Tool

Common starting candidates:

- debug, code review, verification;
- CLI usability, cross-platform behavior, configuration compatibility, packaging, and release readiness when repeated.

Pay special attention to filesystem effects, shell differences, safe defaults, dry-run behavior, and preservation of user-owned files.

## Library Or SDK

Common starting candidates:

- architecture, code review, verification;
- API design, backward compatibility, documentation examples, packaging, and release readiness.

Compatibility and consumer evidence usually matter more than product-management simulation.

## Mobile Or Desktop Application

Common starting candidates:

- architecture, debug, code review, verification;
- platform integration, UX, accessibility, offline state, privacy, performance, and release readiness when material.

## AI Or LLM Product

Common starting candidates:

- architecture, debug, code review, verification;
- prompt or output contract, behavior evaluation, safety, fallback, privacy, and cost-latency review.

Ordinary unit tests do not prove non-deterministic behavior quality. Model, prompt, parser, retrieval, and tool changes may require a project-specific evaluation Skill.

## High-Risk System

Examples include financial, medical, identity, infrastructure control, regulated data, or safety-critical systems.

Common starting candidates:

- architecture, domain-risk review, security review, code review, and verification;
- auditability, rollback, privacy, data integrity, compliance, and incident readiness when required.

High risk justifies stronger independent judgment, not unlimited squad size. Split work into multiple gated stages rather than creating a permanent mega-squad.

## How To Use These Patterns

1. Select one or more plausible archetypes.
2. Extract risk questions, not Skill names.
3. Confirm each risk against repository and workflow evidence.
4. Apply the creation gate in `CAPABILITY_TIERS.md`.
5. Register only the resulting project-local capabilities and squads.
