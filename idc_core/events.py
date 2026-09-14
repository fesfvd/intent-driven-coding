from __future__ import annotations

import json
import os
import re
import threading
import time
import uuid
from contextlib import contextmanager
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Callable


TASK_ID_RE = re.compile(r"^IDC-([A-Z][A-Z0-9]*)-(\d{8})-(\d{3})$")
CORE_EVENT_TYPES = {
    "request.captured",
    "task.promoted",
    "intent.translated",
    "scope.changed",
    "acceptance.changed",
    "classification.changed",
    "uncertainty.changed",
    "impact.assessed",
    "lifecycle.changed",
    "requirement.changed",
    "condition.changed",
    "activity.recorded",
    "decision.resolved",
    "evidence.recorded",
    "check.omitted",
    "permission.requested",
    "permission.granted",
    "permission.rejected",
    "permission.executed",
    "recovery.recorded",
    "task.closed",
    "learn.candidate",
    "legacy.snapshot-imported",
    "capture.discarded",
    "capture.expired",
}
PROVENANCE_TYPES = {
    "claimed",
    "host-observed",
    "command-evidence",
    "artifact-evidence",
    "human-confirmed",
    "reconstructed",
}
_THREAD_LOCKS: dict[str, threading.Lock] = {}
_THREAD_LOCKS_GUARD = threading.Lock()


@dataclass(frozen=True)
class WorkRecord:
    record_id: str
    path: Path


class EventStore:
    def __init__(
        self,
        project: Path,
        clock: Callable[[], datetime] | None = None,
    ) -> None:
        self.project = project.resolve()
        self.clock = clock or (lambda: datetime.now(timezone.utc))
        self.records_root = self.project / ".idc" / "work-items"

    def capture(self, summary: str, actor: str = "agent", *, temporary: bool = False, ttl_hours: int = 72) -> WorkRecord:
        if not summary.strip():
            raise ValueError("summary must not be empty")
        if temporary and (not isinstance(ttl_hours, int) or isinstance(ttl_hours, bool) or ttl_hours <= 0):
            raise ValueError("ttl_hours must be a positive integer")
        now = self._now()
        record_id = f"work-{now.strftime('%Y%m%dt%H%M%Sz').lower()}-{uuid.uuid4().hex[:8]}"
        record_path = self.records_root / record_id
        record_path.mkdir(parents=True, exist_ok=False)
        self.append(
            record_id,
            "request.captured",
            {
                "summary": summary.strip(),
                "capture_mode": "temporary" if temporary else "durable",
                "expires_at": (now + timedelta(hours=ttl_hours)).isoformat() if temporary else None,
            },
            actor=actor,
            provenance="human-confirmed" if actor == "human" else "claimed",
        )
        return WorkRecord(record_id=record_id, path=record_path)

    def create_with_event(
        self,
        event_type: str,
        payload: dict,
        *,
        actor: str = "system",
        provenance: str = "reconstructed",
    ) -> WorkRecord:
        now = self._now()
        record_id = f"work-{now.strftime('%Y%m%dt%H%M%Sz').lower()}-{uuid.uuid4().hex[:8]}"
        record_path = self.records_root / record_id
        record_path.mkdir(parents=True, exist_ok=False)
        self.append(
            record_id,
            event_type,
            payload,
            actor=actor,
            provenance=provenance,
        )
        return WorkRecord(record_id=record_id, path=record_path)

    def promote(self, record_id: str, project_key: str, actor: str = "agent") -> str:
        key = project_key.strip().upper()
        if not re.fullmatch(r"[A-Z][A-Z0-9]*", key):
            raise ValueError("project_key must contain only uppercase letters and digits")
        self.read(record_id)
        date = self._now().strftime("%Y%m%d")
        task_id = self._reserve_task_id(record_id, key, date)
        self.append(
            record_id,
            "task.promoted",
            {"task_id": task_id},
            actor=actor,
            provenance="artifact-evidence",
        )
        return task_id

    def _reserve_task_id(self, record_id: str, project_key: str, date: str) -> str:
        used = self._task_sequences(project_key, date)
        reservations = self.project / ".idc" / "task-ids"
        reservations.mkdir(parents=True, exist_ok=True)
        for sequence in range(1, 1000):
            if sequence in used:
                continue
            task_id = f"IDC-{project_key}-{date}-{sequence:03d}"
            try:
                with (reservations / task_id).open("x", encoding="utf-8") as stream:
                    stream.write(record_id + "\n")
                return task_id
            except FileExistsError:
                continue
        raise RuntimeError(f"no task IDs remain for {project_key} on {date}")

    def append(
        self,
        record_id: str,
        event_type: str,
        payload: dict,
        *,
        actor: str = "agent",
        provenance: str = "claimed",
    ) -> dict:
        if not re.fullmatch(r"work-[a-z0-9-]+", record_id):
            raise ValueError("invalid record_id")
        if event_type not in CORE_EVENT_TYPES and not re.fullmatch(r"x\.[a-z0-9][a-z0-9.-]*", event_type):
            raise ValueError(f"unsupported event type: {event_type}")
        if provenance not in PROVENANCE_TYPES:
            raise ValueError(f"unsupported provenance: {provenance}")
        record_path = self.records_root / record_id
        if not record_path.is_dir():
            raise FileNotFoundError(f"work record does not exist: {record_id}")
        with _record_lock(record_path):
            events = self._read_unlocked(record_id)
            event = {
                "schema_version": 1,
                "record_id": record_id,
                "seq": len(events),
                "timestamp": self._now().isoformat(),
                "actor": {"kind": actor},
                "type": event_type,
                "provenance": provenance,
                "payload": payload,
            }
            with (record_path / "events.jsonl").open("a", encoding="utf-8", newline="\n") as stream:
                stream.write(json.dumps(event, ensure_ascii=False, sort_keys=True) + "\n")
                stream.flush()
                os.fsync(stream.fileno())
        return event

    def read(self, record_id: str) -> list[dict]:
        record_path = self.records_root / record_id
        if not record_path.is_dir():
            raise FileNotFoundError(f"work record does not exist: {record_id}")
        with _record_lock(record_path):
            return self._read_unlocked(record_id)

    def _read_unlocked(self, record_id: str) -> list[dict]:
        record_path = self.records_root / record_id
        path = record_path / "events.jsonl"
        if not record_path.is_dir():
            raise FileNotFoundError(f"work record does not exist: {record_id}")
        if not path.exists():
            return []
        events: list[dict] = []
        for expected_seq, line in enumerate(path.read_text(encoding="utf-8").splitlines()):
            if not line.strip():
                continue
            try:
                event = json.loads(line)
            except json.JSONDecodeError as exc:
                raise ValueError(f"invalid JSON in {path}:{expected_seq + 1}: {exc.msg}") from exc
            if event.get("record_id") != record_id or event.get("seq") != expected_seq:
                raise ValueError(f"invalid event sequence in {path}")
            events.append(event)
        return events

    def _task_sequences(self, project_key: str, date: str) -> set[int]:
        used: set[int] = set()
        if not self.records_root.is_dir():
            return used
        for events_path in self.records_root.glob("*/events.jsonl"):
            for line in events_path.read_text(encoding="utf-8").splitlines():
                try:
                    event = json.loads(line)
                except json.JSONDecodeError:
                    continue
                task_id = event.get("payload", {}).get("task_id")
                if not isinstance(task_id, str):
                    continue
                match = TASK_ID_RE.fullmatch(task_id)
                if match and match.group(1) == project_key and match.group(2) == date:
                    used.add(int(match.group(3)))
        return used

    def _now(self) -> datetime:
        value = self.clock()
        if value.tzinfo is None:
            raise ValueError("clock must return a timezone-aware datetime")
        return value.astimezone(timezone.utc)


@contextmanager
def _record_lock(record_path: Path, timeout_seconds: float = 5.0):
    lock_path = record_path / ".events.lock"
    key = str(lock_path.resolve())
    with _THREAD_LOCKS_GUARD:
        thread_lock = _THREAD_LOCKS.setdefault(key, threading.Lock())
    if not thread_lock.acquire(timeout=timeout_seconds):
        raise TimeoutError(f"timed out waiting for event lock: {lock_path}")
    lock_stream = None
    try:
        lock_stream = lock_path.open("a+b")
        lock_stream.seek(0, os.SEEK_END)
        if lock_stream.tell() == 0:
            lock_stream.write(b"\0")
            lock_stream.flush()
        deadline = time.monotonic() + timeout_seconds
        while True:
            try:
                _lock_file(lock_stream)
                break
            except OSError:
                if time.monotonic() >= deadline:
                    raise TimeoutError(f"timed out waiting for event lock: {lock_path}")
                time.sleep(0.01)
        yield
    finally:
        if lock_stream is not None:
            _unlock_file(lock_stream)
            lock_stream.close()
        thread_lock.release()


def _lock_file(stream) -> None:
    stream.seek(0)
    if os.name == "nt":
        import msvcrt

        msvcrt.locking(stream.fileno(), msvcrt.LK_NBLCK, 1)
    else:
        import fcntl

        fcntl.flock(stream.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)


def _unlock_file(stream) -> None:
    try:
        stream.seek(0)
        if os.name == "nt":
            import msvcrt

            msvcrt.locking(stream.fileno(), msvcrt.LK_UNLCK, 1)
        else:
            import fcntl

            fcntl.flock(stream.fileno(), fcntl.LOCK_UN)
    except OSError:
        pass
