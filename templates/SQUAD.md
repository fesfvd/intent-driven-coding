# {{SQUAD_NAME}}

## Outcome

{{SQUAD_OUTCOME}}

## Presentation

- User-facing language: {{PRESENTATION_LANGUAGE}}
- Target audience: {{PRESENTATION_AUDIENCE}}
- Keep code, commands, identifiers, APIs, and maintainer-only documents in their established convention unless translation is explicitly requested.

## Selection

- Trigger language: {{SQUAD_TRIGGERS}}
- Repository context: {{SQUAD_CONTEXT}}
- Capability tier and evidence: {{SQUAD_CAPABILITY_TIER}}
- Exclusions and near misses: {{SQUAD_EXCLUSIONS}}
- Competing squads and precedence: {{SQUAD_PRECEDENCE}}
- Risk level: {{SQUAD_RISK}}

## Members

| Order | Skill | Unique judgment | Required output |
|---|---|---|---|
| 1 | {{MEMBER_1}} | {{MEMBER_1_JUDGMENT}} | {{MEMBER_1_OUTPUT}} |
| 2 | {{MEMBER_2}} | {{MEMBER_2_JUDGMENT}} | {{MEMBER_2_OUTPUT}} |
| 3, optional | {{MEMBER_3}} | {{MEMBER_3_JUDGMENT}} | {{MEMBER_3_OUTPUT}} |

Delete the third row unless it guards a distinct material boundary.

## Handoffs

```text
{{MEMBER_1}}
  -> artifact: {{HANDOFF_1}}
{{IMPLEMENTATION_OR_MEMBER_2}}
  -> artifact: {{HANDOFF_2}}
{{FINAL_MEMBER}}
```

State which work may run independently. Do not parallelize a consumer before its required handoff exists.
Carry the user-facing language into any artifact intended for the user or final presentation.

## Exit Conditions

- {{EXIT_CONDITION_1}}
- {{EXIT_CONDITION_2}}
- {{EXIT_CONDITION_3}}

## Permission Gate

{{SQUAD_PERMISSION_GATE}}

Use `none` only when the complete squad is local, reversible, and free of external side effects.

## Optional Controller Execution

- Machine-readable contract: {{SQUAD_CONTRACT_PATH}}
- Required verification commands: {{SQUAD_VERIFICATION_COMMANDS}}
- Required upstream artifact IDs: {{SQUAD_ARTIFACT_IDS}}
- Effects that remain separately authorized: {{SQUAD_EXTERNAL_EFFECTS}}

Only add an executable declaration after the squad and its local verification commands have repeated enough to justify a durable contract. The controller's `--execute` path does not grant external permissions.

## Evaluation Cases

| Case | Request | Expected route/behavior | Forbidden behavior |
|---|---|---|---|
| Positive | {{POSITIVE_CASE}} | {{POSITIVE_EXPECTED}} | {{POSITIVE_FORBIDDEN}} |
| Near miss | {{NEGATIVE_CASE}} | {{NEGATIVE_EXPECTED}} | {{NEGATIVE_FORBIDDEN}} |
| Routing conflict | {{CONFLICT_CASE}} | {{CONFLICT_EXPECTED}} | {{CONFLICT_FORBIDDEN}} |
| Over-routing | {{OVERROUTING_CASE}} | {{OVERROUTING_EXPECTED}} | {{OVERROUTING_FORBIDDEN}} |
| Handoff | {{HANDOFF_CASE}} | {{HANDOFF_EXPECTED}} | {{HANDOFF_FORBIDDEN}} |
| Permission | {{PERMISSION_CASE}} | {{PERMISSION_EXPECTED}} | {{PERMISSION_FORBIDDEN}} |

## Composition Check

- Removing member 1 loses: {{MEMBER_1_NECESSITY}}
- Removing member 2 loses: {{MEMBER_2_NECESSITY}}
- Removing optional member 3 loses: {{MEMBER_3_NECESSITY}}
- Overlap reviewed: {{OVERLAP_REVIEW}}
