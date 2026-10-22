"""Checkable skip preconditions for capability routing.

docs/CAPABILITY_TIERS.md states, for each Tier-1 capability, when routing that
capability would be over-routing. Those statements are prose. This module turns
them into predicates over a projected task state plus declared environment
facts, so the exclusion is checkable rather than asserted.

Evaluation is three-valued: a precondition is satisfied, unsatisfied, or
unknown. Unknown means neither the record nor the declared environment facts
answer the question. Only `satisfied` permits a skip; unknown never does. A
catalog that cannot be evaluated must fail closed, because an unanswerable
"do not over-route" rule is exactly the prose this module replaces.

Absence of a declaration is not evidence of absence. Predicates that assert a
negative finding (no assessed boundary impact) or a vacuous bound (scope of at
most one item) require the record to have answered the question first, so an
empty record cannot skip a capability by saying nothing. Predicates over a
declared set the obligation engine already treats as authoritative, such as
`uncertainty`, keep that engine's semantics: an empty set means the gate is not
triggered.
"""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Iterable

from .projector import TaskState


CATALOG_KIND = "capability-skip-catalog"

# Closed predicate vocabulary. Every kind must be answerable from TaskState or
# from declared environment facts. A kind that cannot be answered would make the
# catalog uncheckable, so it is rejected instead of guessed.
VALUE_PREDICATES = frozenset(
    {
        "uncertainty_absent",
        "activity_present",
        "impact_absent",
        "fact_declared",
    }
)
COUNT_PREDICATES = frozenset({"scope_at_most"})
COVERAGE_PREDICATES = frozenset({"acceptance_covered"})
PREDICATE_KINDS = VALUE_PREDICATES | COUNT_PREDICATES | COVERAGE_PREDICATES

SATISFIED = "satisfied"
UNSATISFIED = "unsatisfied"
UNKNOWN = "unknown"

SKIP = "skip"
KEEP = "keep"

#: Declared environment facts the catalog relies on. They describe the host, not
#: the task record, so a caller must declare them explicitly instead of having
#: this module assume them.
KNOWN_ENVIRONMENT_FACTS = frozenset({"host_thin_control_plane"})


@dataclass(frozen=True)
class ConditionOutcome:
    kind: str
    status: str
    explanation: str


@dataclass(frozen=True)
class PreconditionOutcome:
    id: str
    status: str
    rationale: str
    conditions: tuple[ConditionOutcome, ...]


@dataclass(frozen=True)
class CapabilityDecision:
    capability: str
    label: str
    tier: int
    skill: str | None
    skippable: bool
    status: str
    reason: str
    over_route_when_prose: str
    preconditions: tuple[PreconditionOutcome, ...] = field(default_factory=tuple)

    @property
    def skipped(self) -> bool:
        """Only a proven precondition permits skipping; unknown does not."""
        return self.status == SKIP


def load_catalog(path: Path) -> dict[str, Any]:
    """Load a capability skip catalog without validating it against the schema."""
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ValueError(f"{path}: catalog must be a JSON object")
    if payload.get("kind") != CATALOG_KIND:
        raise ValueError(f"{path}: kind must be '{CATALOG_KIND}'")
    capabilities = payload.get("capabilities")
    if not isinstance(capabilities, list) or not capabilities:
        raise ValueError(f"{path}: catalog needs a non-empty capabilities list")
    return payload


def evaluate_catalog(
    catalog: dict[str, Any],
    state: TaskState,
    *,
    facts: Iterable[str] | None = None,
) -> list[CapabilityDecision]:
    """Evaluate every catalog entry against one task state."""
    declared = None if facts is None else {str(fact) for fact in facts}
    return [
        evaluate_entry(entry, state, facts=declared)
        for entry in catalog.get("capabilities", [])
        if isinstance(entry, dict)
    ]


def evaluate_entry(
    entry: dict[str, Any],
    state: TaskState,
    *,
    facts: Iterable[str] | None = None,
) -> CapabilityDecision:
    declared = None if facts is None else {str(fact) for fact in facts}
    capability = str(entry.get("capability", ""))
    label = str(entry.get("label", capability))
    tier = int(entry.get("tier", 1))
    skill = entry.get("skill")
    skippable = bool(entry.get("skippable", False))
    prose = str(entry.get("over_route_when_prose", ""))

    if not skippable:
        return CapabilityDecision(
            capability=capability,
            label=label,
            tier=tier,
            skill=skill if isinstance(skill, str) else None,
            skippable=False,
            status=KEEP,
            reason="the catalog declares this capability is never skipped",
            over_route_when_prose=prose,
        )

    outcomes: list[PreconditionOutcome] = []
    for precondition in entry.get("skip_when", []):
        if not isinstance(precondition, dict):
            continue
        conditions = tuple(
            _condition_outcome(condition, state, declared)
            for condition in precondition.get("requires", [])
            if isinstance(condition, dict)
        )
        if not conditions:
            status = UNKNOWN
        elif all(condition.status == SATISFIED for condition in conditions):
            status = SATISFIED
        elif any(condition.status == UNSATISFIED for condition in conditions):
            status = UNSATISFIED
        else:
            status = UNKNOWN
        outcomes.append(
            PreconditionOutcome(
                id=str(precondition.get("id", "")),
                status=status,
                rationale=str(precondition.get("rationale", "")),
                conditions=conditions,
            )
        )

    satisfied = [outcome for outcome in outcomes if outcome.status == SATISFIED]
    unknown = [outcome for outcome in outcomes if outcome.status == UNKNOWN]
    if satisfied:
        status = SKIP
        reason = f"skip precondition '{satisfied[0].id}' is satisfied: {satisfied[0].rationale}"
    elif unknown:
        status = UNKNOWN
        reason = (
            f"skip precondition '{unknown[0].id}' cannot be decided from this record; "
            "supply the missing environment fact before skipping"
        )
    else:
        status = KEEP
        reason = "no skip precondition is satisfied by this record"

    return CapabilityDecision(
        capability=capability,
        label=label,
        tier=tier,
        skill=skill if isinstance(skill, str) else None,
        skippable=True,
        status=status,
        reason=reason,
        over_route_when_prose=prose,
        preconditions=tuple(outcomes),
    )


def _condition_outcome(
    condition: dict[str, Any], state: TaskState, facts: set[str] | None
) -> ConditionOutcome:
    kind = str(condition.get("kind", ""))
    values = [str(value) for value in condition.get("values", []) or []]

    if kind == "uncertainty_absent":
        present = [value for value in values if value in state.uncertainty]
        if present:
            return ConditionOutcome(kind, UNSATISFIED, f"uncertainty declares {', '.join(present)}")
        return ConditionOutcome(kind, SATISFIED, "no listed uncertainty is declared")

    if kind == "activity_present":
        recorded = [value for value in values if value in state.activities]
        if recorded:
            return ConditionOutcome(kind, SATISFIED, f"activity {', '.join(recorded)} is recorded")
        return ConditionOutcome(kind, UNSATISFIED, "no listed activity is recorded")

    if kind == "impact_absent":
        if not state.impacts:
            return ConditionOutcome(kind, UNSATISFIED, "no impact assessment is recorded")
        present = [value for value in values if state.impacts.get(value)]
        if present:
            return ConditionOutcome(kind, UNSATISFIED, f"impact {', '.join(present)} is assessed")
        return ConditionOutcome(kind, SATISFIED, "the recorded assessment has no listed dimension")

    if kind == "scope_at_most":
        limit = condition.get("value")
        if not isinstance(limit, int) or isinstance(limit, bool) or limit < 0:
            return ConditionOutcome(kind, UNKNOWN, "scope limit is not a non-negative integer")
        if not state.scope:
            return ConditionOutcome(kind, UNSATISFIED, "no scope is recorded")
        if len(state.scope) <= limit:
            return ConditionOutcome(kind, SATISFIED, f"scope has {len(state.scope)} item(s)")
        return ConditionOutcome(kind, UNSATISFIED, f"scope has {len(state.scope)} item(s)")

    if kind == "acceptance_covered":
        if not state.acceptance:
            return ConditionOutcome(kind, UNSATISFIED, "no acceptance item is recorded to cover")
        passing = {
            acceptance_id
            for evidence in state.evidence
            if evidence.get("result") == "pass"
            for acceptance_id in evidence.get("acceptance_ids", [])
        }
        uncovered = [
            str(item.get("id"))
            for item in state.acceptance
            if item.get("id") and item.get("id") not in passing
        ]
        if uncovered:
            return ConditionOutcome(kind, UNSATISFIED, f"uncovered acceptance: {', '.join(uncovered)}")
        return ConditionOutcome(kind, SATISFIED, "passing evidence covers every acceptance item")

    if kind == "fact_declared":
        if facts is None:
            return ConditionOutcome(kind, UNKNOWN, "no environment facts were declared")
        missing = [value for value in values if value not in facts]
        if missing:
            return ConditionOutcome(kind, UNSATISFIED, f"undeclared fact: {', '.join(missing)}")
        return ConditionOutcome(kind, SATISFIED, f"declared fact: {', '.join(values)}")

    return ConditionOutcome(kind, UNKNOWN, f"unsupported predicate kind '{kind}'")


def format_decisions(decisions: Iterable[CapabilityDecision]) -> str:
    """Render decisions as a stable, greppable text report."""
    lines: list[str] = []
    for decision in decisions:
        skill = decision.skill or "-"
        lines.append(f"{decision.status.upper():8} {decision.capability} (tier {decision.tier}, skill {skill})")
        lines.append(f"         over-route when: {decision.over_route_when_prose}")
        lines.append(f"         reason: {decision.reason}")
        for precondition in decision.preconditions:
            lines.append(f"         precondition {precondition.id}: {precondition.status}")
            for condition in precondition.conditions:
                lines.append(f"           - {condition.kind}: {condition.status} ({condition.explanation})")
    return "\n".join(lines)
