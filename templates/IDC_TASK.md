# IDC Task Card

Use this template for a non-trivial task. Keep the card in the target project
under `.idc/tasks/<task-id>.md` when the project has adopted the `.idc/` layout.
The task ID identifies work; it does not prove that the work succeeded.

## Identity

- Task ID: `IDC-{{PROJECT_KEY}}-{{SCENARIO}}-{{YYYYMMDD}}-{{NNN}}`
- Title: {{TASK_TITLE}}
- Status: `INTAKE`
- Created: {{UTC_TIMESTAMP}}
- Owner: {{HUMAN_OR_AGENT}}

## Intent And Classification

- Requested outcome: {{OBSERVABLE_OUTCOME}}
- Scenario: `{{SCENARIO}}`
- Uncertainty modifiers: {{KNOWN_TARGET_OR_UNKNOWN_CAUSE_OR_OTHER}}
- Why this classification: {{CLASSIFICATION_REASON}}

## Scope

- Included: {{INCLUDED_PATHS_BOUNDARIES_BEHAVIORS}}
- Excluded: {{EXPLICIT_EXCLUSIONS}}
- Preserve: {{BEHAVIOR_DATA_CONTRACTS_TO_KEEP}}
- Baseline evidence: {{CURRENT_BEHAVIOR_REPRODUCTION_DIFF_OR_SOURCE_FACT}}

## Impact

| Dimension | Level | Rationale |
|---|---|---|
| Behavior | {{none/low/medium/high/unknown}} | {{RATIONALE}} |
| Data | {{none/low/medium/high/unknown}} | {{RATIONALE}} |
| Security | {{none/low/medium/high/unknown}} | {{RATIONALE}} |
| Privacy | {{none/low/medium/high/unknown}} | {{RATIONALE}} |
| Permission | {{none/low/medium/high/unknown}} | {{RATIONALE}} |
| Cost | {{none/low/medium/high/unknown}} | {{RATIONALE}} |
| Availability | {{none/low/medium/high/unknown}} | {{RATIONALE}} |
| External effect | {{none/low/medium/high/unknown}} | {{RATIONALE}} |
| Reversibility | {{none/low/medium/high/unknown}} | {{RATIONALE}} |

## Route And Gates

- Phase path: {{INTAKE_DESIGN_BUILD_VERIFY_REVIEW_SHIP}}
- Squad/Skills: {{ROUTE}}
- Handoff artifacts: {{ARTIFACTS_AND_CONSUMERS}}
- Current phase: `INTAKE`
- Blocking open decisions: {{NONE_OR_DECISIONS}}

## Acceptance And Verification

- Acceptance criteria:
  - [ ] {{OBSERVABLE_SUCCESS_CONDITION}}
- Regression invariants:
  - [ ] {{BEHAVIOR_THAT_MUST_REMAIN_TRUE}}
- Verification commands: {{EXACT_COMMANDS}}
- Evidence expected: {{COMMAND_ARTIFACT_HOST_OR_HUMAN_EVIDENCE}}
- Omitted checks and reason: {{NONE_OR_EXPLANATION}}

## Permission Boundary

- Permission-gated effects: {{NONE_OR_EXACT_EFFECTS}}
- Required approval: {{NONE_OR_NAMED_APPROVER_AND_SCOPE}}
- Target revision/environment: {{NONE_OR_EXACT_TARGET}}
- Recovery or rollback condition: {{NONE_OR_CONDITION}}

## Decision And Progress Log

| Time (UTC) | Phase | Decision or evidence | Result |
|---|---|---|---|
| {{UTC_TIMESTAMP}} | INTAKE | {{INITIAL_CLASSIFICATION_OR_DECISION}} | {{STATUS}} |
