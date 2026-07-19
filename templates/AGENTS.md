# {{PROJECT_NAME}} Architecture Guide

This document explains architecture meaning, critical data flow, and cross-file impact. Current source, configuration, schemas, and tests remain the executable truth.

## Product

{{PRODUCT_SUMMARY}}

## Technology

| Area | Current choice | Source of truth |
|---|---|---|
| Backend/runtime | {{BACKEND_STACK}} | {{BACKEND_CONFIG_PATH}} |
| Frontend/client | {{FRONTEND_STACK}} | {{FRONTEND_CONFIG_PATH}} |
| Persistence | {{PERSISTENCE_STACK}} | {{PERSISTENCE_CONFIG_PATH}} |
| Deployment | {{DEPLOYMENT_STACK}} | {{DEPLOYMENT_CONFIG_PATH}} |

## Production Entry Points

| Responsibility | Entry | Notes |
|---|---|---|
| Application | {{APPLICATION_ENTRY}} | {{APPLICATION_ENTRY_NOTES}} |
| Client | {{CLIENT_ENTRY}} | {{CLIENT_ENTRY_NOTES}} |
| Worker/jobs | {{WORKER_ENTRY}} | {{WORKER_ENTRY_NOTES}} |

Delete rows that do not apply. Distinguish real production entries from historical, development-only, or generated files.

## Critical Flow

Describe the most important end-to-end path:

```text
{{USER_ACTION}}
  -> {{CLIENT_HANDLER}}
  -> {{API_OR_EVENT_ENTRY}}
  -> {{DOMAIN_SERVICE}}
  -> {{PERSISTENCE_OR_EXTERNAL_EFFECT}}
  -> {{RESPONSE_OR_RENDER}}
```

State where validation, authorization, transactions, billing/quota, retries, and error recovery occur.

## Repository Map

| Path | Responsibility | Important boundary |
|---|---|---|
| {{PATH_1}} | {{PATH_1_ROLE}} | {{PATH_1_BOUNDARY}} |
| {{PATH_2}} | {{PATH_2_ROLE}} | {{PATH_2_BOUNDARY}} |
| {{PATH_3}} | {{PATH_3_ROLE}} | {{PATH_3_BOUNDARY}} |

Prefer responsibility and coupling over exhaustive file lists.

## Persistence And External Effects

| Data/effect | Owner | Write boundary | Recovery/rollback |
|---|---|---|---|
| {{DATA_1}} | {{DATA_1_OWNER}} | {{DATA_1_WRITE_BOUNDARY}} | {{DATA_1_RECOVERY}} |

Document privacy, payment, quota, email, storage, queues, and paid external calls where applicable.

## Cross-File Constraints

- {{SOURCE_GENERATED_ARTIFACT_RULE}}
- {{SHARED_INTERFACE_RULE}}
- {{CONFIG_RESTART_RULE}}
- {{DESIGN_SYSTEM_RULE}}
- {{MIGRATION_RULE}}

Delete unused placeholders. Add only constraints that repeatedly affect correctness.

## Impact Matrix

| Change | Must inspect | Why | Minimum proof |
|---|---|---|---|
| API/schema | {{API_CONSUMERS}} | Contract consumers must remain aligned | {{API_TEST_COMMAND}} |
| Persisted model | {{MODEL_CONSUMERS}} | Migration and compatibility boundary | {{MODEL_TEST_COMMAND}} |
| Client source | {{CLIENT_ARTIFACTS}} | Production output may differ from source | {{CLIENT_TEST_COMMAND}} |
| Auth/permission | {{ROLE_PATHS}} | Allow and deny paths must be covered | {{AUTH_TEST_COMMAND}} |

## Structural Change Rule

Regenerate or update architecture indexes only when these structures change:

- {{STRUCTURAL_CHANGE_1}}
- {{STRUCTURAL_CHANGE_2}}
- {{STRUCTURAL_CHANGE_3}}

Command: `{{ARCHITECTURE_MAP_COMMAND}}`

Do not create documentation churn for localized implementation changes that preserve architecture facts.
