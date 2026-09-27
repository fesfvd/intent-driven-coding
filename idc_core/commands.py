"""Handlers for record-oriented progressive CLI commands."""

from __future__ import annotations

from argparse import Namespace
from dataclasses import asdict
from typing import Any, Callable

from .render import render_card
from .workflow import Workflow


def run_record_command(
    args: Namespace,
    workflow: Workflow,
    load_config: Callable[[Any], dict[str, Any]],
    acceptance_pairs: Callable[[list[str], list[dict[str, str]]], list[dict[str, str]]],
    pair_values: Callable[[list[str], str], list[tuple[str, str]]],
) -> dict[str, Any]:
    command = args.command
    if command == "start":
        ttl_hours = args.ttl_hours
        if args.temporary and ttl_hours is None:
            ttl_hours = load_config(workflow.project)["capture_ttl_hours"]
        if args.temporary and (ttl_hours is None or ttl_hours <= 0):
            raise ValueError("ttl-hours must be a positive integer")
        record_id = workflow.start(args.summary, actor=args.actor, temporary=args.temporary,
                                   ttl_hours=ttl_hours if ttl_hours is not None else 72,
                                   scenes=args.scenes)
        report = {"record_id": record_id, "lifecycle": "captured", "scenario": args.scenes or [],
                  "outstanding_obligations": ["promote", "shape", "acceptance"],
                  "next_allowed_activity": "investigate, promote, or shape",
                  "current_blockers": ["task is captured; implementation is not allowed"],
                  "card": render_card(workflow.state(record_id))}
        if args.scenes:
            report["scenes"] = args.scenes
        return report
    if command == "promote":
        return {"record_id": args.record,
                "task_id": workflow.promote(args.record, project_key=load_config(workflow.project)["project_key"])}
    if command == "discard":
        return _state(workflow.discard(args.record, reason=args.reason))
    if command == "shape":
        previous = workflow.state(args.record)
        return _state(workflow.shape(args.record, goal=args.goal, explicit=args.explicit,
            repository_facts=args.fact, proposed_defaults=args.default, open_decisions=args.decision,
            scope=args.scope,
            acceptance=acceptance_pairs(args.acceptance, previous.acceptance) if args.acceptance is not None else None,
            classifications=args.classifications, uncertainty=args.uncertainty,
            impacts=dict(pair_values(args.impact, "impact")) if args.impact is not None else None))
    if command == "classify":
        return _state(workflow.classify(args.record, args.classifications, reason=args.reason))
    if command == "change":
        return _state(workflow.change_requirement(args.record, before=args.before, after=args.after, reason=args.reason, actor=args.actor))
    if command == "resolve-decision":
        return _state(workflow.resolve_decision(args.record, decision=args.decision, resolution=args.resolution, actor=args.actor))
    if command == "condition":
        return _state(workflow.set_condition(args.record, args.name, args.state == "active", reason=args.reason))
    if command == "transition":
        result = workflow.transition(args.record, args.to)
        report = _state(result.state)
        report["warnings"] = result.warnings
        return report
    if command == "activity":
        return _state(workflow.record_activity(args.record, args.name))
    if command == "add-evidence":
        return _state(workflow.add_evidence(args.record, kind=args.kind, summary=args.summary,
            result=args.result, acceptance_ids=args.acceptance, reference=args.reference,
            actor=args.actor, confirmation_ref=args.confirmation_ref,
            failure_attribution=args.failure_attribution))
    if command == "permission":
        return _state(workflow.permission(args.record, effect=args.effect, state=args.state, actor=args.actor))
    if command == "recovery":
        return _state(workflow.record_recovery(args.record, args.summary))
    if command == "close":
        result = workflow.close(args.record, outcome=args.outcome, summary=args.summary)
        report = _state(result.state)
        report["warnings"] = result.warnings
        return report
    if command == "learn-review":
        return _state(workflow.review_learning(args.record, outcome=args.outcome, candidate=args.candidate,
            evidence_refs=args.evidence_ref, destination=args.destination, reason=args.reason, actor=args.actor))
    if command == "learn-dispose":
        return _state(workflow.dispose_learning(args.record, disposition=args.disposition,
                                                 reason=args.reason, actor=args.actor))
    if command in {"show", "render"}:
        if command == "render":
            workflow._render(args.record)
        return _state(workflow.state(args.record))
    raise ValueError(f"unsupported command: {command}")


def _state(value: Any) -> dict[str, Any]:
    result = asdict(value)
    result["conditions"] = sorted(value.conditions)
    return result
