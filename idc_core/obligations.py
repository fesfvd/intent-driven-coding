from __future__ import annotations

from dataclasses import dataclass, field
from typing import Callable

from .projector import TaskState


@dataclass
class ObligationResult:
    hard_blocks: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)
    explanations: dict[str, str] = field(default_factory=dict)

    def add_block(self, obligation_id: str, explanation: str | None = None) -> None:
        if obligation_id not in self.hard_blocks:
            self.hard_blocks.append(obligation_id)
        if explanation:
            self.explanations[obligation_id] = explanation


@dataclass(frozen=True)
class Obligation:
    id: str
    evaluate: Callable[[TaskState, str, ObligationResult], None]


def _lifecycle(state: TaskState, target: str, result: ObligationResult) -> None:
    allowed = {"captured": {"shaped", "active"}, "shaped": {"active", "validating"}, "active": {"shaped", "validating"}, "validating": {"shaped", "active"}, "closed": set()}
    if target in {"shaped", "active", "validating"} and target not in allowed.get(state.lifecycle, set()):
        result.add_block(f"lifecycle:{state.lifecycle}->{target}", "Move through a permitted lifecycle transition first.")
    if state.lifecycle == "closed" and target not in {"closed", "completed", "cancelled", "superseded", "unresolved"}:
        result.add_block("lifecycle:closed", "A closed task cannot resume; create a new task or reopen explicitly.")


def _shaping(state: TaskState, target: str, result: ObligationResult) -> None:
    if target != "active":
        return
    for missing, present in (("intent:goal", bool(state.goal)), ("scope", bool(state.scope)), ("acceptance", bool(state.acceptance)), ("impact", bool(state.impacts))):
        if not present:
            result.warnings.append(missing)
    if state.open_decisions:
        if "emergency" in state.conditions:
            result.warnings.append("decision:open")
        else:
            result.add_block("decision:open", "Resolve each open decision before activating the task.")


def _uncertainty(state: TaskState, target: str, result: ObligationResult) -> None:
    required: list[str] = []
    if target in {"build", "completed"}:
        if "unknown-cause" in state.uncertainty and "discover" not in state.activities:
            required.append("activity:discover")
        if "cross-boundary" in state.uncertainty and "design" not in state.activities:
            required.append("activity:design")
    if target == "build":
        if "emergency" in state.conditions:
            result.warnings.extend(required)
        else:
            for item in required:
                result.add_block(item, f"Record the required {item.removeprefix('activity:')} activity before building.")
    elif target == "completed":
        for item in required:
            result.add_block(item, f"Record the required {item.removeprefix('activity:')} activity before completion.")


def _security_privacy(state: TaskState, target: str, result: ObligationResult) -> None:
    if target != "completed":
        return
    level = max((state.impacts.get("security", "none"), state.impacts.get("privacy", "none")), key=("none", "low", "medium", "high", "unknown").index)
    if level in {"high", "unknown"} and "review" not in state.activities:
        result.add_block("activity:review", "Record a security/privacy review before completion.")
    elif level == "medium" and "review" not in state.activities:
        result.warnings.append("activity:review")


def _permission_recovery(state: TaskState, target: str, result: ObligationResult) -> None:
    if target != "ship" or state.impacts.get("external_effect") not in {"medium", "high", "unknown"}:
        return
    if not state.permissions:
        result.add_block("permission:external-effect", "Record an effect-specific permission before shipping.")
    else:
        for effect in sorted(state.permissions):
            if state.permissions[effect] not in {"granted", "executed"}:
                result.add_block(f"permission:{effect}", f"Obtain permission for {effect} before shipping.")
    if state.impacts.get("reversibility") in {"medium", "high", "unknown"} and not state.recovery:
        result.add_block("recovery-plan", "Record a rollback or recovery plan before shipping.")


def _acceptance_closure(state: TaskState, target: str, result: ObligationResult) -> None:
    if target != "completed":
        return
    if not state.goal:
        result.add_block("intent:goal", "Record the intended outcome before completing the task.")
    if not state.acceptance:
        result.add_block("acceptance", "Record at least one acceptance criterion before completing the task.")
    if state.open_decisions:
        result.add_block("decision:open", "Resolve each open decision before completion.")
    passing = {aid for evidence in state.evidence if evidence.get("result") == "pass" for aid in evidence.get("acceptance_ids", [])}
    for item in state.acceptance:
        aid = item.get("id")
        if aid and aid not in passing:
            result.add_block(f"acceptance:{aid}", f"Attach passing evidence to acceptance item {aid}.")


OBLIGATIONS: tuple[Obligation, ...] = (
    Obligation("lifecycle", _lifecycle), Obligation("shaping", _shaping),
    Obligation("uncertainty", _uncertainty), Obligation("security-privacy", _security_privacy),
    Obligation("permission", _permission_recovery), Obligation("recovery", _permission_recovery),
    Obligation("closure", _acceptance_closure),
)


def evaluate_obligations(state: TaskState, target: str) -> ObligationResult:
    result = ObligationResult()
    for obligation in OBLIGATIONS:
        obligation.evaluate(state, target, result)
    return result
