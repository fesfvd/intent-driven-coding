#!/usr/bin/env python3
"""Validate Intent-Driven Coding JSON contracts without modifying them."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

try:
    from jsonschema import Draft202012Validator, SchemaError
except ImportError:
    Draft202012Validator = None
    SchemaError = Exception


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_SCHEMA = ROOT / "schemas" / "intent-driven-coding-contract-v1.schema.json"
DEFAULT_CONTRACTS = ROOT / "contracts" / "examples"
REFERENCE_KEYWORDS = ("$ref", "$dynamicRef", "$recursiveRef")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Validate Intent-Driven Coding JSON contracts.")
    parser.add_argument("--schema", type=Path, default=DEFAULT_SCHEMA, help="Contract JSON Schema path")
    parser.add_argument("--contracts", type=Path, default=DEFAULT_CONTRACTS, help="Contract file or directory")
    return parser.parse_args()


def json_files(path: Path) -> list[Path]:
    if path.is_file():
        return [path] if path.suffix == ".json" else []
    if path.is_dir():
        return sorted(path.rglob("*.json"))
    return []


def external_schema_references(value: object, location: str = "root") -> list[str]:
    errors: list[str] = []
    if isinstance(value, dict):
        for key, item in value.items():
            child_location = f"{location}.{key}"
            if key in REFERENCE_KEYWORDS and isinstance(item, str) and not item.startswith("#"):
                errors.append(f"external schema reference at {child_location}: {item}")
            errors.extend(external_schema_references(item, child_location))
    elif isinstance(value, list):
        for index, item in enumerate(value):
            errors.extend(external_schema_references(item, f"{location}[{index}]"))
    return errors


def semantic_errors(payload: dict[object, object]) -> list[str]:
    if payload.get("kind") != "squad-contract":
        return []

    member_skills = [
        member["skill"]
        for member in payload["members"]
        if isinstance(member, dict) and isinstance(member.get("skill"), str)
    ]
    members = set(member_skills)
    outputs = {
        member["skill"]: member["required_output"]
        for member in payload["members"]
        if isinstance(member, dict)
    }
    errors: list[str] = []
    for skill in sorted({skill for skill in member_skills if member_skills.count(skill) > 1}):
        errors.append(f"duplicate squad member '{skill}'")
    claim_ids = [claim["id"] for claim in payload["verification"]["claims"]]
    for claim_id in sorted({claim_id for claim_id in claim_ids if claim_ids.count(claim_id) > 1}):
        errors.append(f"duplicate verification claim '{claim_id}'")
    command_ids = [
        command["id"]
        for command in payload["verification"].get("commands", [])
        if isinstance(command, dict) and isinstance(command.get("id"), str)
    ]
    for command_id in sorted(
        {command_id for command_id in command_ids if command_ids.count(command_id) > 1}
    ):
        errors.append(f"duplicate verification command '{command_id}'")
    for handoff in payload["handoffs"]:
        if not isinstance(handoff, dict):
            continue
        for role in ("from", "to"):
            member = handoff.get(role)
            if member not in members:
                errors.append(f"handoff {role} '{member}' is not a squad member")
        if handoff.get("from") == handoff.get("to"):
            errors.append("handoff must transfer between distinct members")
        producer = handoff.get("from")
        artifact_id = handoff.get("artifact_id")
        if producer in outputs and artifact_id != outputs[producer]:
            errors.append(
                f"handoff artifact '{artifact_id}' is not produced by '{producer}'"
            )
    expected_handoffs = list(zip(member_skills, member_skills[1:]))
    actual_handoffs = [
        (handoff.get("from"), handoff.get("to"))
        for handoff in payload["handoffs"]
        if isinstance(handoff, dict)
    ]
    if set(actual_handoffs) != set(expected_handoffs) or len(actual_handoffs) != len(expected_handoffs):
        errors.append("handoffs must connect each adjacent squad member in declared order")
    return errors


def cross_document_errors(documents: list[tuple[Path, dict[object, object]]]) -> list[str]:
    errors: list[str] = []
    squads: dict[object, dict[object, object]] = {}
    cases: dict[object, dict[object, object]] = {}
    for path, payload in documents:
        if payload.get("kind") == "squad-contract":
            contract_id = payload["id"]
            if contract_id in squads:
                errors.append(f"{path}: duplicate squad contract id '{contract_id}'")
                continue
            squads[contract_id] = payload
        elif payload.get("kind") == "evaluation-case":
            case_id = payload["id"]
            if case_id in cases:
                errors.append(f"{path}: duplicate evaluation case id '{case_id}'")
                continue
            cases[case_id] = payload

    for path, payload in ((path, payload) for path, payload in documents if payload.get("kind") == "evaluation-case"):
        contract_id = payload["contract_id"]
        squad = squads.get(contract_id)
        if squad is None:
            errors.append(f"{path}: unknown contract '{contract_id}'")
            continue

        member_skills = [member["skill"] for member in squad["members"]]
        if payload["expected_route"] != member_skills:
            errors.append(f"{path}: expected route does not match contract '{contract_id}'")
        produced_artifacts = {member["required_output"] for member in squad["members"]}
        for artifact in payload["required_artifacts"]:
            if artifact not in produced_artifacts:
                errors.append(f"{path}: required artifact '{artifact}' is not produced by '{contract_id}'")
        claim_ids = {claim["id"] for claim in squad["verification"]["claims"]}
        for claim in payload["required_verification_claims"]:
            if claim not in claim_ids:
                errors.append(f"{path}: unknown verification claim '{claim}' in '{contract_id}'")
        if payload["authorization"]["required"] != squad["authorization"]["required"]:
            errors.append(f"{path}: authorization requirement does not match contract '{contract_id}'")
        if payload["authorization"]["effects"] != squad["authorization"]["effects"]:
            errors.append(f"{path}: authorization effects do not match contract '{contract_id}'")
    return errors


def validate(schema_path: Path, contracts_path: Path) -> list[str]:
    errors: list[str] = []
    if Draft202012Validator is None:
        return ["Missing dependency: install requirements.txt to use jsonschema."]
    if not schema_path.is_file():
        return [f"Missing schema: {schema_path}"]

    try:
        schema = json.loads(schema_path.read_text(encoding="utf-8"))
        references = external_schema_references(schema)
        if references:
            return [f"Invalid schema {schema_path}: {reference}" for reference in references]
        Draft202012Validator.check_schema(schema)
    except (OSError, UnicodeError, json.JSONDecodeError, SchemaError) as exc:
        return [f"Invalid schema {schema_path}: {exc}"]

    paths = json_files(contracts_path)
    if not paths:
        return [f"No JSON contracts found: {contracts_path}"]

    validator = Draft202012Validator(schema)
    documents: list[tuple[Path, dict[object, object]]] = []
    for path in paths:
        try:
            payload = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, UnicodeError, json.JSONDecodeError) as exc:
            errors.append(f"{path}: cannot read JSON ({exc})")
            continue
        try:
            schema_errors = sorted(validator.iter_errors(payload), key=lambda item: list(item.absolute_path))
        except Exception as exc:
            errors.append(f"{path}: schema validation failed ({exc})")
            continue
        for error in schema_errors:
            location = ".".join(str(part) for part in error.absolute_path) or "root"
            errors.append(f"{path}: {location}: {error.message}")
        if not schema_errors and isinstance(payload, dict):
            for error in semantic_errors(payload):
                errors.append(f"{path}: {error}")
            documents.append((path, payload))
    errors.extend(cross_document_errors(documents))
    return errors


def main() -> int:
    args = parse_args()
    schema_path = args.schema.expanduser().resolve()
    contracts_path = args.contracts.expanduser().resolve()
    errors = validate(schema_path, contracts_path)
    if errors:
        print("Contract validation failed:")
        for error in errors:
            print(f"- {error}")
        return 1
    print(f"Contract validation passed ({len(json_files(contracts_path))} JSON contract files).")
    print("Note: JSON consistency does not prove host routing or Agent execution.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
