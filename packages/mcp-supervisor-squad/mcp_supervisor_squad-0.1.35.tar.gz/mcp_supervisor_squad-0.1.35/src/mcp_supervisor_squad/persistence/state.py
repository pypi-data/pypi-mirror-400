from __future__ import annotations

from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any
import hashlib

from ..utils.constants import BACKOFF_SCHEDULE_MS, PHASE_POLL_CAP_MS
from .storage import StorageLayout, find_repo_root, read_json, utc_now_iso

PHASE_FLOOR_MS: dict[str, int] = {
    # Planner is split into light+heavy; both get higher floors to reduce early polling spam.
    "planner_light": 15_000,
    "planner_heavy": 20_000,
    "review": 10_000,
    "coder_run": 8_000,
    "integrate": 10_000,
    "cleanup": 10_000,
}


def _utc_now() -> datetime:
    return datetime.now(timezone.utc)


def _parse_iso(ts: str | None) -> datetime | None:
    if not ts:
        return None
    try:
        return datetime.fromisoformat(ts.replace("Z", "+00:00"))
    except Exception:
        return None


def _safe_mtime(path: Path) -> float | None:
    try:
        return path.stat().st_mtime
    except OSError:
        return None


def _last_activity_age_s(*, layout: StorageLayout, run_id: str, job_ids: list[str], now: datetime) -> int | None:
    """
    Best-effort "activity age" based on job artifact mtimes (no content reads).
    """
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
    n = int.from_bytes(h[:2], "big")  # 0..65535
    offset = int((n / 65535.0) * (2 * span) - span)
    return max(1000, base + offset)


def _fmt_elapsed_precise(seconds: int) -> str:
    if seconds < 60:
        return f"{seconds}s"
    minutes, secs = divmod(seconds, 60)
    if minutes < 60:
        return f"{minutes}m{secs}s"
    hours, mins = divmod(minutes, 60)
    return f"{hours}h{mins}m"


def _fmt_activity_precise(age_s: int) -> str:
    if age_s < 60:
        return f"{age_s}s"
    minutes, secs = divmod(age_s, 60)
    if minutes < 60:
        return f"{minutes}m{secs}s"
    hours, mins = divmod(minutes, 60)
    return f"{hours}h{mins}m"


def _round_wait_s(ms: int) -> int:
    s = max(1, int(ms // 1000))
    if s <= 15:
        return s
    return int(((s + 4) // 5) * 5)


@dataclass(slots=True)
class RunTask:
    slug: str
    project_root: str
    worktree: str
    job_id: str | None = None
    status: str = "pending"  # pending|running|completed|failed
    started_at: str | None = None
    finished_at: str | None = None
    error: str | None = None

    @classmethod
    def from_dict(cls, payload: dict[str, Any]) -> "RunTask":
        return cls(
            slug=str(payload.get("slug") or ""),
            project_root=str(payload.get("project_root") or ""),
            worktree=str(payload.get("worktree") or ""),
            job_id=payload.get("job_id"),
            status=str(payload.get("status") or "pending"),
            started_at=payload.get("started_at"),
            finished_at=payload.get("finished_at"),
            error=payload.get("error"),
        )


@dataclass(slots=True)
class RunState:
    run_id: str
    repo_root: str
    cwd: str
    query: str
    sandbox: str
    approval_policy: str
    planner_model: str = "gpt-5.2"
    planner_reasoning_effort: str = "medium"
    planner_extra_config: list[str] = field(default_factory=list)
    coder_model: str = "gpt-5.1-codex-max"
    coder_reasoning_effort: str = "medium"
    coder_extra_config: list[str] = field(default_factory=list)
    planner_job_id: str | None = None
    read_limits_max_files: int = 30
    read_limits_max_file_bytes: int = 65_536
    read_limits_max_total_bytes: int = 1_000_000
    kb_inbox_max_kb: int = 20
    kb_compact_max_kb: int = 10
    kb_archive_keep: int = 5
    kb_archive_max_kb: int = 200
    polling_max_ms: int = 60_000
    polling_jitter_ratio: float = 0.1
    mode: str = "single"  # single|dual
    phase: str = "planner_light"  # planner_light|planner_heavy|coder_run|integrate|cleanup|done|canceled|error
    next_action: str = "wait"  # wait|apply
    wait_reason: str = "idle"  # agent_running|cleanup_running|blocked|idle|ready_to_apply|canceled|error
    requirements_brief: str = ""
    canceled: bool = False
    created_at: str = field(default_factory=utc_now_iso)
    updated_at: str = field(default_factory=utc_now_iso)
    phase_started_at: str = field(default_factory=utc_now_iso)
    retention_days: int = 10
    important_event: str = "initialized"
    important_event_at: str = field(default_factory=utc_now_iso)
    forced_wait_ms: int = 15000
    event_seq: int = 0
    events: list[dict[str, Any]] = field(default_factory=list)
    tasks: list[RunTask] = field(default_factory=list)

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
            coder_model=str(payload.get("coder_model") or "gpt-5.1-codex-max"),
            coder_reasoning_effort=str(payload.get("coder_reasoning_effort") or "medium"),
            coder_extra_config=[str(x) for x in (payload.get("coder_extra_config") or []) if str(x).strip()],
            planner_job_id=payload.get("planner_job_id") if isinstance(payload.get("planner_job_id"), str) else None,
            read_limits_max_files=int(payload.get("read_limits_max_files") or 30),
            read_limits_max_file_bytes=int(payload.get("read_limits_max_file_bytes") or 65_536),
            read_limits_max_total_bytes=int(payload.get("read_limits_max_total_bytes") or 1_000_000),
            kb_inbox_max_kb=int(payload.get("kb_inbox_max_kb") or 20),
            kb_compact_max_kb=int(payload.get("kb_compact_max_kb") or 10),
            kb_archive_keep=int(payload.get("kb_archive_keep") or 5),
            kb_archive_max_kb=int(payload.get("kb_archive_max_kb") or 200),
            polling_max_ms=int(payload.get("polling_max_ms") or 60_000),
            polling_jitter_ratio=float(payload.get("polling_jitter_ratio") or 0.1),
            mode=str(payload.get("mode") or "single"),
            phase=str(payload.get("phase") or "planner_run"),
            next_action=str(payload.get("next_action") or "wait"),
            wait_reason=str(payload.get("wait_reason") or "idle"),
            requirements_brief=str(payload.get("requirements_brief") or ""),
            canceled=bool(payload.get("canceled") or False),
            created_at=str(payload.get("created_at") or utc_now_iso()),
            updated_at=str(payload.get("updated_at") or utc_now_iso()),
            phase_started_at=str(payload.get("phase_started_at") or payload.get("important_event_at") or payload.get("created_at") or utc_now_iso()),
            retention_days=int(payload.get("retention_days") or 10),
            important_event=str(payload.get("important_event") or "initialized"),
            important_event_at=str(payload.get("important_event_at") or utc_now_iso()),
            forced_wait_ms=int(payload.get("forced_wait_ms") or 15000),
            event_seq=int(payload.get("event_seq") or 0),
            events=[e for e in (payload.get("events") or []) if isinstance(e, dict)],
            tasks=tasks,
        )

    def _poll_cap_ms(self) -> int:
        return int(min(PHASE_POLL_CAP_MS.get(self.phase, BACKOFF_SCHEDULE_MS[-1]), int(self.polling_max_ms or 60_000)))

    def compute_forced_wait_ms(self, *, now: datetime | None = None) -> int:
        now_dt = now or _utc_now()
        since = _parse_iso(self.phase_started_at) or _parse_iso(self.important_event_at) or now_dt
        elapsed = max(0.0, (now_dt - since).total_seconds())
        phase_floor = PHASE_FLOOR_MS.get(self.phase, BACKOFF_SCHEDULE_MS[0])
        # Phase-aware backoff: long-running phases should reduce polling quickly and enforce a per-phase floor to avoid noisy short waits.
        if self.next_action == "apply" or self.wait_reason == "ready_to_apply":
            return min(60_000, self._poll_cap_ms())
        if self.phase == "canceled" or self.wait_reason == "canceled":
            return 60_000

        # Activity-based polling for long-running phases (no stdout reads).
        layout = StorageLayout.for_repo(Path(self.repo_root))
        job_ids: list[str] = []
        if self.planner_job_id:
            job_ids.append(self.planner_job_id)
        for t in self.tasks:
            if t.job_id and isinstance(t.job_id, str):
                job_ids.append(t.job_id)
        activity_age = _last_activity_age_s(layout=layout, run_id=self.run_id, job_ids=job_ids, now=now_dt)
        if activity_age is not None and self.phase in {"planner_run", "coder_run"}:
            if activity_age < 5:
                ms = BACKOFF_SCHEDULE_MS[0]
            elif activity_age < 20:
                ms = BACKOFF_SCHEDULE_MS[1]
            elif activity_age < 60:
                ms = BACKOFF_SCHEDULE_MS[2]
            elif activity_age < 300:
                ms = BACKOFF_SCHEDULE_MS[3]
            elif activity_age < 900:
                ms = BACKOFF_SCHEDULE_MS[4]
            else:
                ms = BACKOFF_SCHEDULE_MS[5]
            # As elapsed grows, reduce polling even if the run is "active" to avoid repetitive status spam.
            if self.phase == "planner_run":
                if elapsed > 180:
                    phase_floor = 60_000
                elif elapsed > 60:
                    phase_floor = 30_000
            ms = max(ms, phase_floor)
            return min(_apply_jitter(int(ms), run_id=self.run_id, ratio=self.polling_jitter_ratio), self._poll_cap_ms())

        if self.phase in {"planner_run", "coder_run"}:
            if elapsed < 10:
                ms = BACKOFF_SCHEDULE_MS[0]
            elif elapsed < 30:
                ms = BACKOFF_SCHEDULE_MS[1]
            elif elapsed < 90:
                ms = BACKOFF_SCHEDULE_MS[2]
            elif elapsed < 300:
                ms = BACKOFF_SCHEDULE_MS[3]
            else:
                ms = BACKOFF_SCHEDULE_MS[4]
        else:
            # Other phases are typically shorter; poll a bit more frequently but still back off.
            if elapsed < 10:
                ms = BACKOFF_SCHEDULE_MS[0]
            elif elapsed < 30:
                ms = BACKOFF_SCHEDULE_MS[1]
            elif elapsed < 90:
                ms = BACKOFF_SCHEDULE_MS[2]
            else:
                ms = BACKOFF_SCHEDULE_MS[3]
        ms = max(ms, phase_floor)
        # Long-running guard: if planner has been running >3m with no activity hint, back off to near-cap.
        if self.phase == "planner_run" and elapsed > 180 and activity_age is None:
            ms = max(ms, 60_000)
        return min(_apply_jitter(int(ms), run_id=self.run_id, ratio=self.polling_jitter_ratio), self._poll_cap_ms())

    def public_status(self, *, options: dict[str, Any] | None = None) -> dict[str, Any]:
        now = _utc_now()
        poll_ms = self.compute_forced_wait_ms(now=now)

        since = _parse_iso(self.phase_started_at) or _parse_iso(self.important_event_at) or now
        elapsed_s = max(0, int((now - since).total_seconds()))
        completed = sum(1 for t in self.tasks if t.status == "completed")
        failed = next((t.slug for t in self.tasks if t.status == "failed"), None)
        running = next((t.slug for t in self.tasks if t.status == "running"), None)
        total = max(1, len(self.tasks))
        task_summary = f"任务: {completed}/{total} 完成"
        if running:
            task_summary += f" | running: {running}"
        if failed:
            task_summary += f" | failed: {failed}"

        stage_hint = ""
        if self.phase == "planner_light":
            stage_hint = "planner: light"
        elif self.phase == "planner_heavy":
            stage_hint = "planner: deterministic" if not (self.planner_job_id or "").strip() else "planner: running"
        elif self.phase == "coder_run":
            stage_hint = "coder: running"
        elif self.phase == "integrate":
            stage_hint = "integrate: running"
        elif self.phase == "done":
            stage_hint = "ready: apply"
        elif self.phase == "cleanup":
            stage_hint = "cleanup: running"
        elif self.phase == "error":
            stage_hint = "status: error"

        artifact_hint = ""
        if self.phase in {"planner_light", "planner_heavy"}:
            artifact_hint = "out: requirements*.md" + ("+contract.json" if self.mode == "dual" else "")
        elif self.phase in {"coder_run", "integrate", "done"}:
            artifact_hint = "out: patch.diff"

        activity_hint = ""
        try:
            layout = StorageLayout.for_repo(Path(self.repo_root))
            job_ids: list[str] = []
            if self.planner_job_id:
                job_ids.append(self.planner_job_id)
            for t in self.tasks:
                if t.job_id and isinstance(t.job_id, str):
                    job_ids.append(t.job_id)
            activity_age = _last_activity_age_s(layout=layout, run_id=self.run_id, job_ids=job_ids, now=now)
            if activity_age is not None and self.phase in {"planner_run", "coder_run"}:
                activity_hint = f"活跃: {_fmt_activity_precise(int(activity_age))}"
        except Exception:
            activity_hint = ""

        # Event-driven: only emit summary when there is a new event.
        lines: list[str] = []
        lines.append(f"模式: {self.mode} | 阶段: {self.phase}" + (f" | {stage_hint}" if stage_hint else "") + f" | 动作: {self.next_action}")
        lines.append(task_summary + (f" | 活跃: {activity_hint}" if activity_hint else ""))
        lines.append(
            f"最近: {self.important_event} | 已等待: {_fmt_elapsed_precise(elapsed_s)}"
            + (f" | {artifact_hint}" if artifact_hint else "")
            + f" | 强制等待: {_round_wait_s(poll_ms)}s"
        )

        events_lines: list[str] = []
        for ev in list(self.events or []):
            if not isinstance(ev, dict):
                continue
            msg = ""
            if isinstance(ev.get("message"), str) and ev.get("message").strip():
                msg = ev.get("message").strip()
            data_lines: list[str] = []
            if isinstance(ev.get("data_lines"), list):
                data_lines = [str(x) for x in ev.get("data_lines") if str(x).strip()]
            elif isinstance(ev.get("data"), str) and ev.get("data").strip():
                data_lines = [ln.strip() for ln in ev.get("data").splitlines() if ln.strip()]
            if msg:
                events_lines.append(msg)
            for ln in data_lines:
                events_lines.append(f"- {ln}")
        # Clear events once delivered to avoid re-sending.
        self.events = []
        has_update = bool(events_lines)
        # When无事件时避免过长等待，压到5s内。
        if not has_update:
            poll_ms = min(poll_ms, 5000)
        terminal = self.phase in {"done", "canceled", "error"}
        if terminal:
            poll_ms = 0
        self.forced_wait_ms = poll_ms
        summary_payload = lines[:3] if (has_update or terminal) else [f"等待: {_round_wait_s(poll_ms)}s"]
        payload = {
            "run_id": self.run_id,
            "forced_wait_ms": poll_ms,
        }
        if summary_payload:
            payload["summary_lines"] = summary_payload
        if events_lines:
            payload["event_lines"] = events_lines
        return payload


class RunStore:
    """
    File-backed state store. By default, resolves repo_root from process cwd.

    `squad_status`/`squad_apply` may pass `options.cwd` to resolve a different repo.
    """

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
                    f"run_id not found in current repo: {run_id}. "
                    "Pass options.cwd pointing inside the target repo that created this run "
                    "and refer to <repo_root>/.codex/supervisor-squad/contract.json for usage."
                )
            raise FileNotFoundError(f"run_id not found: {run_id}")
        return RunState.from_dict(raw)

    def save(self, state: RunState) -> None:
        from .storage import atomic_write_json

        layout = StorageLayout.for_repo(Path(state.repo_root))
        paths = layout.run_paths(state.run_id)
        paths.run_dir.mkdir(parents=True, exist_ok=True)
        atomic_write_json(paths.state_path, state.to_dict())
