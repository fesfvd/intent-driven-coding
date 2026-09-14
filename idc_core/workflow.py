from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
import json
from pathlib import Path
from typing import Callable

from .events import EventStore
from .obligations import ObligationResult, evaluate_obligations
from .projector import TaskState, fold_events
from .render import render_card


class GateBlocked(RuntimeError):
    def __init__(self, blocks: list[str], explanations: dict[str, str] | None = None) -> None:
        self.blocks = blocks
        self.explanations = explanations or {}
        super().__init__("blocked by: " + ", ".join(blocks))


@dataclass
class WorkflowResult:
    state: TaskState
    warnings: list[str]


class Workflow:
    def __init__(self, project: Path, clock: Callable[[], datetime] | None = None) -> None:
        self.project = project.resolve()
        self.store = EventStore(self.project, clock=clock)

    def start(
        self,
        summary: str,
        actor: str = "agent",
        *,
        temporary: bool = False,
        ttl_hours: int | None = None,
        scenes: list[str] | None = None,
    ) -> str:
        if scenes and any(not scene.strip() for scene in scenes):
            raise ValueError("scene labels must not be empty")
        if ttl_hours is None:
            ttl_hours = 72
            config_path = self.project / ".idc" / "config.json"
            if config_path.is_file():
                try:
                    config = json.loads(config_path.read_text(encoding="utf-8"))
                    configured = config.get("capture_ttl_hours", 72)
                    if isinstance(configured, int) and not isinstance(configured, bool) and configured > 0:
                        ttl_hours = configured
                except (OSError, json.JSONDecodeError):
                    pass
        record_id = self.store.capture(
            summary, actor=actor, temporary=temporary, ttl_hours=ttl_hours
        ).record_id
        if scenes:
            self.classify(
                record_id,
                scenes,
                reason="Initial scene identification from the request",
                actor=actor,
            )
        else:
            self._render(record_id)
        return record_id

    def promote(self, record_id: str, project_key: str, actor: str = "agent") -> str:
        state = self.state(record_id)
        if state.capture_disposition in {"discarded", "expired"}:
            raise ValueError(f"capture is {state.capture_disposition}")
        task_id = self.store.promote(record_id, project_key=project_key, actor=actor)
        self._render(record_id)
        return task_id

    def discard(self, record_id: str, *, reason: str, actor: str = "agent") -> TaskState:
        state = self.state(record_id)
        if state.task_id:
            raise ValueError("promoted task cannot be discarded")
        self._append(record_id, "capture.discarded", {"reason": reason}, actor=actor)
        return self.state(record_id)

    def shape(
        self,
        record_id: str,
        *,
        goal: str,
        explicit: list[str] | None = None,
        repository_facts: list[str] | None = None,
        proposed_defaults: list[str] | None = None,
        open_decisions: list[str] | None = None,
        scope: list[str] | None = None,
        acceptance: list[dict[str, str]] | None = None,
        classifications: list[str] | None = None,
        uncertainty: list[str] | None = None,
        impacts: dict[str, str] | None = None,
        actor: str = "agent",
    ) -> TaskState:
        previous = self.state(record_id)
        self._append(
            record_id,
            "intent.translated",
            {
                "goal": goal,
                "explicit": previous.explicit if explicit is None else explicit,
                "repository_facts": previous.repository_facts if repository_facts is None else repository_facts,
                "proposed_defaults": previous.proposed_defaults if proposed_defaults is None else proposed_defaults,
                "open_decisions": previous.open_decisions if open_decisions is None else open_decisions,
            },
            actor=actor,
        )
        if scope is not None:
            self._append(record_id, "scope.changed", {"from": previous.scope, "to": scope}, actor=actor)
        if acceptance is not None:
            self._append(
                record_id,
                "acceptance.changed",
                {"from": previous.acceptance, "to": acceptance},
                actor=actor,
            )
        if classifications is not None:
            self._append(
                record_id,
                "classification.changed",
                {
                    "from": previous.classifications or None,
                    "to": classifications,
                    "reason": "Task shaping",
                },
                actor=actor,
            )
        if uncertainty is not None:
            self._append(
                record_id,
                "uncertainty.changed",
                {"from": previous.uncertainty, "to": uncertainty},
                actor=actor,
            )
        if impacts is not None:
            self._append(record_id, "impact.assessed", {"dimensions": impacts}, actor=actor)
        current = self.state(record_id)
        if current.lifecycle != "shaped":
            self._append(
                record_id,
                "lifecycle.changed",
                {"from": current.lifecycle, "to": "shaped"},
                actor=actor,
            )
        return self.state(record_id)

    def set_condition(
        self, record_id: str, name: str, active: bool, *, reason: str, actor: str = "agent"
    ) -> TaskState:
        self._append(
            record_id,
            "condition.changed",
            {"name": name, "active": active, "reason": reason},
            actor=actor,
        )
        return self.state(record_id)

    def change_requirement(
        self,
        record_id: str,
        *,
        before: str,
        after: str,
        reason: str,
        actor: str = "agent",
    ) -> TaskState:
        self._append(
            record_id,
            "requirement.changed",
            {"before": before, "after": after, "reason": reason},
            actor=actor,
            provenance="human-confirmed" if actor == "human" else "claimed",
        )
        return self.state(record_id)

    def classify(
        self,
        record_id: str,
        classifications: list[str],
        *,
        reason: str,
        actor: str = "agent",
    ) -> TaskState:
        previous = self.state(record_id)
        self._append(
            record_id,
            "classification.changed",
            {"from": previous.classifications or None, "to": classifications, "reason": reason},
            actor=actor,
        )
        return self.state(record_id)

    def resolve_decision(
        self,
        record_id: str,
        *,
        decision: str,
        resolution: str,
        actor: str = "human",
    ) -> TaskState:
        state = self.state(record_id)
        if decision not in state.open_decisions:
            raise ValueError(f"open decision does not exist: {decision}")
        self._append(
            record_id,
            "decision.resolved",
            {"decision": decision, "resolution": resolution},
            actor=actor,
            provenance="human-confirmed" if actor == "human" else "claimed",
        )
        return self.state(record_id)

    def permission(
        self,
        record_id: str,
        *,
        effect: str,
        state: str,
        actor: str = "human",
    ) -> TaskState:
        if state not in {"requested", "granted", "rejected", "executed"}:
            raise ValueError(f"invalid permission state: {state}")
        self._append(
            record_id,
            f"permission.{state}",
            {"effect": effect},
            actor=actor,
            provenance="human-confirmed" if actor == "human" else "host-observed",
        )
        return self.state(record_id)

    def record_recovery(self, record_id: str, summary: str, actor: str = "agent") -> TaskState:
        self._append(
            record_id,
            "recovery.recorded",
            {"summary": summary},
            actor=actor,
        )
        return self.state(record_id)

    def record_activity(self, record_id: str, name: str, actor: str = "agent") -> TaskState:
        state = self.state(record_id)
        evaluation = evaluate_obligations(state, target=name)
        self._raise_if_blocked(evaluation)
        self._append(record_id, "activity.recorded", {"name": name}, actor=actor)
        return self.state(record_id)

    def transition(self, record_id: str, target: str, actor: str = "agent") -> WorkflowResult:
        state = self.state(record_id)
        evaluation = evaluate_obligations(state, target=target)
        self._raise_if_blocked(evaluation)
        self._append(
            record_id,
            "lifecycle.changed",
            {"from": state.lifecycle, "to": target},
            actor=actor,
        )
        return WorkflowResult(state=self.state(record_id), warnings=evaluation.warnings)

    def add_evidence(
        self,
        record_id: str,
        *,
        kind: str,
        summary: str,
        result: str,
        acceptance_ids: list[str] | None = None,
        reference: str | None = None,
        actor: str = "agent",
        confirmation_ref: str | None = None,
    ) -> TaskState:
        if kind == "human-confirmed":
            if actor != "human":
                raise ValueError("human-confirmed evidence requires human actor")
            if not confirmation_ref or not confirmation_ref.strip():
                raise ValueError("human-confirmed evidence requires confirmation reference")
        self._append(
            record_id,
            "evidence.recorded",
            {
                "kind": kind,
                "summary": summary,
                "result": result,
                "acceptance_ids": acceptance_ids or [],
                "reference": reference,
                "confirmation_ref": confirmation_ref,
            },
            actor=actor,
            provenance=kind,
        )
        return self.state(record_id)

    def close(
        self, record_id: str, *, outcome: str, summary: str, actor: str = "agent"
    ) -> WorkflowResult:
        state = self.state(record_id)
        evaluation = evaluate_obligations(state, target=outcome)
        self._raise_if_blocked(evaluation)
        self._append(
            record_id,
            "task.closed",
            {"outcome": outcome, "summary": summary},
            actor=actor,
        )
        return WorkflowResult(state=self.state(record_id), warnings=evaluation.warnings)

    def state(self, record_id: str) -> TaskState:
        events = self.store.read(record_id)
        now = self.store._now()
        state = fold_events(events, now=now)
        if state.capture_disposition == "expired" and not any(
            event.get("type") == "capture.expired" for event in events
        ):
            self.store.append(
                record_id,
                "capture.expired",
                {"expired_at": state.expires_at},
                actor="system",
                provenance="artifact-evidence",
            )
            state = fold_events(self.store.read(record_id), now=now)
            self._render(record_id)
        return state

    def _append(
        self,
        record_id: str,
        event_type: str,
        payload: dict,
        *,
        actor: str,
        provenance: str = "claimed",
    ) -> None:
        self.store.append(
            record_id,
            event_type,
            payload,
            actor=actor,
            provenance=provenance,
        )
        self._render(record_id)

    def _render(self, record_id: str) -> None:
        state = self.state(record_id)
        provisional = self.store.records_root / record_id / "CARD.md"
        if state.task_id:
            path = self.project / ".idc" / "tasks" / f"{state.task_id}.md"
            if provisional.exists():
                provisional.unlink()
        elif state.capture_disposition == "open":
            path = provisional
        else:
            # Discarded or expired captures keep their event history but no
            # live card, matching the documented discard behavior.
            if provisional.exists():
                provisional.unlink()
            return
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(render_card(state), encoding="utf-8", newline="\n")

    @staticmethod
    def _raise_if_blocked(evaluation: ObligationResult) -> None:
        if evaluation.hard_blocks:
            raise GateBlocked(evaluation.hard_blocks, evaluation.explanations)
