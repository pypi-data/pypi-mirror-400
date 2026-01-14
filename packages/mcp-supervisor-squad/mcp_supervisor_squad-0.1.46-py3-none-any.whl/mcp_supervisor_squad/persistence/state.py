from __future__ import annotations

from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any
import hashlib
import math

from ..utils.constants import BACKOFF_SCHEDULE_MS, PHASE_POLL_CAP_MS
from ..utils.storage import read_json, atomic_write_json
from ..utils.time import utc_now_iso, parse_iso
from ..utils.path import find_repo_root
from .storage import StorageLayout

PHASE_FLOOR_MS: dict[str, int] = {
    "coder_run": 4000,
    "done": 0,
    "error": 0,
    "canceled": 0,
}


def _utc_now() -> datetime:
    return datetime.now(timezone.utc)


def _safe_mtime(path: Path) -> float | None:
    try:
        return path.stat().st_mtime
    except OSError:
        return None


def _last_activity_age_s(*, layout: StorageLayout, run_id: str, job_ids: list[str], now: datetime) -> int | None:
    paths = layout.run_paths(run_id)
    mtimes: list[float] = []
    for job_id in job_ids:
        if not job_id:
            continue
        job_dir = paths.jobs_dir / job_id
        for name in ("meta.json", "last_message.txt", "stdout.jsonl", "stderr.log"):
            m = _safe_mtime(job_dir / name)
            if m is not None:
                mtimes.append(m)
    if not mtimes:
        return None
    latest = max(mtimes)
    age = max(0, int(now.timestamp() - latest))
    return age


def _apply_jitter(ms: int, *, run_id: str, ratio: float) -> int:
    if ratio <= 0:
        return int(ms)
    r = min(0.5, float(ratio))
    base = int(ms)
    span = int(base * r)
    if span <= 0:
        return base
    h = hashlib.sha256(f"{run_id}:{base}".encode("utf-8")).digest()
    n = int.from_bytes(h[:2], "big")
    offset = int((n / 65535.0) * (2 * span) - span)
    return max(500, base + offset)


def _fmt_activity_precise(seconds: int) -> str:
    if seconds < 60:
        return f"{seconds}s"
    if seconds < 3600:
        return f"{seconds // 60}m{seconds % 60}s"
    return f"{seconds // 3600}h{(seconds % 3600) // 60}m"


@dataclass
class RunTask:
    slug: str
    project_root: str
    worktree: str
    job_id: str | None = None
    status: str = "pending"
    started_at: str | None = None
    finished_at: str | None = None
    error: str | None = None

    @classmethod
    def from_dict(cls, payload: dict[str, Any]) -> "RunTask":
        return cls(
            slug=str(payload.get("slug") or "single"),
            project_root=str(payload.get("project_root") or ""),
            worktree=str(payload.get("worktree") or ""),
            job_id=payload.get("job_id") if isinstance(payload.get("job_id"), str) else None,
            status=str(payload.get("status") or "pending"),
            started_at=payload.get("started_at") if isinstance(payload.get("started_at"), str) else None,
            finished_at=payload.get("finished_at") if isinstance(payload.get("finished_at"), str) else None,
            error=payload.get("error") if isinstance(payload.get("error"), str) else None,
        )


@dataclass
class RunState:
    run_id: str
    repo_root: str
    cwd: str
    query: str
    sandbox: str
    approval_policy: str
    planner_model: str
    planner_reasoning_effort: str
    planner_extra_config: list[str]
    coder_model: str
    coder_reasoning_effort: str
    coder_extra_config: list[str]
    planner_job_id: str | None
    read_limits_max_files: int
    read_limits_max_file_bytes: int
    read_limits_max_total_bytes: int
    polling_max_ms: int
    polling_jitter_ratio: float
    mode: str
    phase: str
    next_action: str
    wait_reason: str
    requirements_brief: str
    canceled: bool
    created_at: str
    updated_at: str
    phase_started_at: str
    retention_days: int
    important_event: str
    important_event_at: str
    forced_wait_ms: int
    event_seq: int
    events: list[dict[str, Any]]
    tasks: list[RunTask]

    def to_dict(self) -> dict[str, Any]:
        payload = asdict(self)
        payload["tasks"] = [asdict(t) for t in self.tasks]
        return payload

    @classmethod
    def from_dict(cls, payload: dict[str, Any]) -> "RunState":
        tasks = [RunTask.from_dict(t) for t in (payload.get("tasks") or []) if isinstance(t, dict)]
        return cls(
            run_id=str(payload.get("run_id") or ""),
            repo_root=str(payload.get("repo_root") or ""),
            cwd=str(payload.get("cwd") or ""),
            query=str(payload.get("query") or ""),
            sandbox=str(payload.get("sandbox") or "workspace-write"),
            approval_policy=str(payload.get("approval_policy") or "never"),
            planner_model=str(payload.get("planner_model") or "gpt-5.2"),
            planner_reasoning_effort=str(payload.get("planner_reasoning_effort") or "medium"),
            planner_extra_config=[str(x) for x in (payload.get("planner_extra_config") or []) if str(x).strip()],
            coder_model=str(payload.get("coder_model") or "gpt-5.1-codex-mini"),
            coder_reasoning_effort=str(payload.get("coder_reasoning_effort") or "medium"),
            coder_extra_config=[str(x) for x in (payload.get("coder_extra_config") or []) if str(x).strip()],
            planner_job_id=payload.get("planner_job_id") if isinstance(payload.get("planner_job_id"), str) else None,
            read_limits_max_files=int(payload.get("read_limits_max_files") or 30),
            read_limits_max_file_bytes=int(payload.get("read_limits_max_file_bytes") or 65_536),
            read_limits_max_total_bytes=int(payload.get("read_limits_max_total_bytes") or 1_000_000),
            polling_max_ms=int(payload.get("polling_max_ms") or 60_000),
            polling_jitter_ratio=float(payload.get("polling_jitter_ratio") or 0.1),
            mode=str(payload.get("mode") or "single"),
            phase=str(payload.get("phase") or "coder_run"),
            next_action=str(payload.get("next_action") or "wait"),
            wait_reason=str(payload.get("wait_reason") or "agent_running"),
            requirements_brief=str(payload.get("requirements_brief") or ""),
            canceled=bool(payload.get("canceled") or False),
            created_at=str(payload.get("created_at") or utc_now_iso()),
            updated_at=str(payload.get("updated_at") or utc_now_iso()),
            phase_started_at=str(payload.get("phase_started_at") or payload.get("important_event_at") or payload.get("created_at") or utc_now_iso()),
            retention_days=int(payload.get("retention_days") or 10),
            important_event=str(payload.get("important_event") or "initialized"),
            important_event_at=str(payload.get("important_event_at") or utc_now_iso()),
            forced_wait_ms=int(payload.get("forced_wait_ms") or 8000),
            event_seq=int(payload.get("event_seq") or 0),
            events=[e for e in (payload.get("events") or []) if isinstance(e, dict)],
            tasks=tasks,
        )

    def _poll_cap_ms(self) -> int:
        return int(min(PHASE_POLL_CAP_MS.get(self.phase, BACKOFF_SCHEDULE_MS[-1]), int(self.polling_max_ms or 60_000)))

    def compute_forced_wait_ms(self, *, now: datetime | None = None) -> int:
        now_dt = now or _utc_now()
        since = parse_iso(self.phase_started_at) or parse_iso(self.important_event_at) or now_dt
        elapsed = max(0.0, (now_dt - since).total_seconds())
        if self.phase in {"done", "error", "canceled"}:
            return 0
        phase_floor = PHASE_FLOOR_MS.get(self.phase, BACKOFF_SCHEDULE_MS[0])
        base = max(phase_floor, int(BACKOFF_SCHEDULE_MS[min(len(BACKOFF_SCHEDULE_MS) - 1, int(elapsed // 30))]))
        base = min(base, self._poll_cap_ms())
        jittered = _apply_jitter(base, run_id=self.run_id, ratio=self.polling_jitter_ratio)
        return int(jittered)

    def public_status(self, *, options: dict[str, Any] | None = None) -> dict[str, Any]:
        now = _utc_now()
        poll_ms = self.compute_forced_wait_ms(now=now)

        events_lines: list[str] = []
        for ev in list(self.events or []):
            if not isinstance(ev, dict):
                continue
            msg = str(ev.get("message") or "").strip()
            data_lines: list[str] = []
            if isinstance(ev.get("data"), str) and ev.get("data").strip():
                data_lines = [ln.strip() for ln in ev.get("data").splitlines() if ln.strip()]
            if msg:
                events_lines.append(msg)
            for ln in data_lines:
                events_lines.append(f"- {ln}")
        if self.phase in {"done", "canceled", "error"}:
            poll_ms = 0
            self.forced_wait_ms = 0
        else:
            self.forced_wait_ms = poll_ms
            if not events_lines:
                poll_ms = min(poll_ms, 4000)
        terminal = self.phase in {"done", "canceled", "error"}
        display_events = events_lines if terminal else events_lines[-20:]
        payload = {"run_id": self.run_id, "forced_wait_s": math.ceil(poll_ms / 100) / 10.0}
        if display_events:
            payload["event_lines"] = display_events
        if terminal:
            payload["next_step"] = "stop polling; print event_lines once"
            self.events = []
        return payload


class RunStore:
    def __init__(self) -> None:
        self._lock = None

    def _layout(self, *, cwd: str | None = None) -> StorageLayout:
        root = find_repo_root(Path(cwd).resolve()) if cwd else find_repo_root(Path.cwd())
        return StorageLayout.for_repo(root)

    def load(self, run_id: str, *, cwd: str | None = None) -> RunState:
        layout = self._layout(cwd=cwd)
        state_path = layout.run_paths(run_id).state_path
        raw = read_json(state_path)
        if not raw:
            if cwd is None:
                raise FileNotFoundError(
                    f"run_id not found in current repo: {run_id}. Pass options.cwd pointing inside the target repo that created this run."
                )
            raise FileNotFoundError(f"run_id not found: {run_id}")
        return RunState.from_dict(raw)

    def save(self, state: RunState) -> None:
        layout = StorageLayout.for_repo(Path(state.repo_root))
        paths = layout.run_paths(state.run_id)
        paths.run_dir.mkdir(parents=True, exist_ok=True)
        atomic_write_json(paths.state_path, state.to_dict())
