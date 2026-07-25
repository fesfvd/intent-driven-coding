#!/usr/bin/env python3
"""Evaluate agent-produced records against Intent-Driven Coding contracts offline."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from validate_contracts import DEFAULT_SCHEMA, json_files, validate


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_CONTRACTS = ROOT / "contracts" / "examples"
DEFAULT_RECORDS = ROOT / "evals" / "fixtures"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Evaluate Intent-Driven Coding records offline.")
    parser.add_argument("--contracts", type=Path, default=DEFAULT_CONTRACTS, help="Contract directory or file")
    parser.add_argument("--records", type=Path, default=DEFAULT_RECORDS, help="Evaluation record directory or file")
    return parser.parse_args()


def load_documents(path: Path) -> list[tuple[Path, dict[object, object]]]:
    documents: list[tuple[Path, dict[object, object]]] = []
    for file_path in json_files(path):
        payload = json.loads(file_path.read_text(encoding="utf-8"))
        if isinstance(payload, dict):
            documents.append((file_path, payload))
    return documents


def evaluate(contracts_path: Path, records_path: Path) -> list[str]:
    errors = validate(DEFAULT_SCHEMA, contracts_path)
    errors.extend(validate(DEFAULT_SCHEMA, records_path))
    if errors:
        return errors

    documents = load_documents(contracts_path)
    squads = {payload["id"]: payload for _, payload in documents if payload.get("kind") == "squad-contract"}
    cases = {payload["id"]: payload for _, payload in documents if payload.get("kind") == "evaluation-case"}

    for path, record in load_documents(records_path):
        if record.get("kind") != "evaluation-record":
            errors.append(f"{path}: expected kind 'evaluation-record'")
            continue
        case = cases.get(record["case_id"])
        if case is None:
            errors.append(f"{path}: unknown evaluation case '{record['case_id']}'")
            continue
        squad = squads.get(record["contract_id"])
        if squad is None:
            errors.append(f"{path}: unknown contract '{record['contract_id']}'")
            continue
        if record["contract_id"] != case["contract_id"]:
            errors.append(f"{path}: contract does not match evaluation case")
        if record["selected_route"] != case["expected_route"]:
            errors.append(f"{path}: selected route does not match evaluation case")
        for artifact in case["required_artifacts"]:
            if artifact not in record["artifacts"]:
                errors.append(f"{path}: missing required artifact '{artifact}'")
        for claim in case["required_verification_claims"]:
            if claim not in record["verification_claims"]:
                errors.append(f"{path}: missing verification claim '{claim}'")
        forbidden = set(record["observed_forbidden_behavior"]) & set(case["forbidden_behavior"])
        for behavior in sorted(forbidden):
            errors.append(f"{path}: observed forbidden behavior '{behavior}'")
        if record["authorization"]["required"] != case["authorization"]["required"]:
            errors.append(f"{path}: authorization requirement does not match evaluation case")
        if record["authorization"]["state"] != case["authorization"]["state"]:
            errors.append(f"{path}: authorization state does not match evaluation case")
        if record["authorization"]["effects"] != case["authorization"]["effects"]:
            errors.append(f"{path}: authorization effects do not match evaluation case")
    return errors


def main() -> int:
    args = parse_args()
    contracts_path = args.contracts.expanduser().resolve()
    records_path = args.records.expanduser().resolve()
    errors = evaluate(contracts_path, records_path)
    if errors:
        print("Offline evaluation failed:")
        for error in errors:
            print(f"- {error}")
        return 1
    print(f"Offline evaluation passed ({len(json_files(records_path))} evaluation records).")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
