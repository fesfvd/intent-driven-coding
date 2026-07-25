# Machine-Readable Contracts

## Purpose

Intent-Driven Coding uses JSON contracts only when a project needs a reusable squad, handoff, verification, authorization, or evaluation boundary that scripts must inspect. Markdown remains the human explanation; contracts make the operational boundary machine-checkable.

The v1 Schema is `schemas/intent-driven-coding-contract-v1.schema.json`. It defines three document kinds:

- `squad-contract`: routing, two or three members, handoffs, verification claims, and authorization state.
- `evaluation-case`: an ordinary-language request, expected route, required artifacts, verification claims, and authorization expectation.
- `evaluation-record`: an Agent-produced record evaluated offline against a case and squad contract.

## Validate Framework Examples

The validator uses `jsonschema` with draft 2020-12 support. Install the dependency once:

```powershell
python -m pip install -r requirements.txt
python scripts/validate_contracts.py
python scripts/evaluate_contracts.py
```

Validate the `.idc/` parent directory so evaluation cases can resolve their squad contracts, or validate an individual contract file:

```powershell
python scripts/validate_contracts.py --contracts ../my-project/.idc
python scripts/validate_contracts.py --contracts ../my-project/.idc/contracts/cross-layer-feature.squad.json
```

The validator is offline. It checks JSON structure against draft 2020-12, squad member and handoff consistency, and evaluation references to contracts, routes, artifacts, verification claims, and authorization requirements. It does not load a model, invoke an Agent, access a network service, or write files.

`scripts/evaluate_contracts.py` is also offline. It compares an Agent-produced `evaluation-record` with the corresponding contract and evaluation case. It checks route selection, declared artifacts, verification claims, authorization state, and forbidden behavior without executing the Agent that produced the record.

## Project Layout

When a project has enough evidence to formalize a reusable formation, keep its platform-neutral artifacts under `.idc/`:

```text
.idc/
|-- contracts/
|   `-- cross-layer-feature.squad.json
`-- evals/
    `-- cross-layer-feature.evaluation.json
```

Do not create these files merely because the framework is installed. A contract is justified only after repeated work or a material failure boundary passes the creation gate in `meta-skill-designer`.

## Contract Boundaries

- A contract names the expected route; it does not prove that a model selected it.
- An authorization contract records the scope required for an action; it does not grant permission.
- A verification contract names the evidence required for a claim; it does not substitute for fresh command output.
- The offline evaluator compares Agent-produced records with these contracts without calling a model.
