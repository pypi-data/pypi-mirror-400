from __future__ import annotations

from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from ..utils.constants import BACKOFF_SCHEDULE_MS, PHASE_POLL_CAP_MS
from .storage import StorageLayout, find_repo_root, read_json, utc_now_iso


def _utc_now() -> datetime:
    return datetime.now(timezone.utc)


def _parse_iso(ts: str | None) -> datetime | None:
    if not ts:
        return None
    try:
        return datetime.fromisoformat(ts.replace("Z", "+00:00"))
    except Exception:
        return None


@dataclass(slots=True)
class BriefCache:
    generated_at: str
    recommended_poll_ms: int
    lines: list[str]

    def to_dict(self) -> dict[str, Any]:
        return {"generated_at": self.generated_at, "recommended_poll_ms": self.recommended_poll_ms, "lines": list(self.lines or [])}

    @classmethod
    def from_dict(cls, payload: dict[str, Any]) -> "BriefCache":
        return cls(
            generated_at=str(payload.get("generated_at") or utc_now_iso()),
            recommended_poll_ms=int(payload.get("recommended_poll_ms") or 15000),
            lines=[str(x) for x in (payload.get("lines") or []) if str(x).strip()],
        )


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
    supervisor_model: str = "gpt-5.2"
    supervisor_reasoning_effort: str = "medium"
    supervisor_extra_config: list[str] = field(default_factory=list)
    coder_model: str = "gpt-5.1-codex-max"
    coder_reasoning_effort: str = "medium"
    coder_extra_config: list[str] = field(default_factory=list)
    read_limits_max_files: int = 30
    read_limits_max_file_bytes: int = 65_536
    read_limits_max_total_bytes: int = 1_000_000
    kb_inbox_max_kb: int = 20
    kb_compact_max_kb: int = 10
    kb_archive_keep: int = 5
    kb_archive_max_kb: int = 200
    mode: str = "single"  # single|dual
    phase: str = "supervisor_run"  # supervisor_run|coder_run|integrate|cleanup|done|error
    next_action: str = "wait"  # wait|apply
    wait_reason: str = "idle"  # agent_running|cleanup_running|blocked|idle|ready_to_apply|error
    created_at: str = field(default_factory=utc_now_iso)
    updated_at: str = field(default_factory=utc_now_iso)
    retention_days: int = 10
    important_event: str = "initialized"
    important_event_at: str = field(default_factory=utc_now_iso)
    recommended_poll_ms: int = 15000
    brief_cache: BriefCache | None = None
    tasks: list[RunTask] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        payload = asdict(self)
        payload["tasks"] = [asdict(t) for t in self.tasks]
        payload["brief_cache"] = self.brief_cache.to_dict() if self.brief_cache else None
        return payload

    @classmethod
    def from_dict(cls, payload: dict[str, Any]) -> "RunState":
        tasks = [RunTask.from_dict(t) for t in (payload.get("tasks") or []) if isinstance(t, dict)]
        brief = payload.get("brief_cache")
        return cls(
            run_id=str(payload.get("run_id") or ""),
            repo_root=str(payload.get("repo_root") or ""),
            cwd=str(payload.get("cwd") or ""),
            query=str(payload.get("query") or ""),
            sandbox=str(payload.get("sandbox") or "workspace-write"),
            approval_policy=str(payload.get("approval_policy") or "never"),
            supervisor_model=str(payload.get("supervisor_model") or "gpt-5.1-codex-max"),
            supervisor_reasoning_effort=str(payload.get("supervisor_reasoning_effort") or "medium"),
            supervisor_extra_config=[str(x) for x in (payload.get("supervisor_extra_config") or []) if str(x).strip()],
            coder_model=str(payload.get("coder_model") or "gpt-5.1-codex-max"),
            coder_reasoning_effort=str(payload.get("coder_reasoning_effort") or "medium"),
            coder_extra_config=[str(x) for x in (payload.get("coder_extra_config") or []) if str(x).strip()],
            read_limits_max_files=int(payload.get("read_limits_max_files") or 30),
            read_limits_max_file_bytes=int(payload.get("read_limits_max_file_bytes") or 65_536),
            read_limits_max_total_bytes=int(payload.get("read_limits_max_total_bytes") or 1_000_000),
            kb_inbox_max_kb=int(payload.get("kb_inbox_max_kb") or 20),
            kb_compact_max_kb=int(payload.get("kb_compact_max_kb") or 10),
            kb_archive_keep=int(payload.get("kb_archive_keep") or 5),
            kb_archive_max_kb=int(payload.get("kb_archive_max_kb") or 200),
            mode=str(payload.get("mode") or "single"),
            phase=str(payload.get("phase") or "supervisor_run"),
            next_action=str(payload.get("next_action") or "wait"),
            wait_reason=str(payload.get("wait_reason") or "idle"),
            created_at=str(payload.get("created_at") or utc_now_iso()),
            updated_at=str(payload.get("updated_at") or utc_now_iso()),
            retention_days=int(payload.get("retention_days") or 10),
            important_event=str(payload.get("important_event") or "initialized"),
            important_event_at=str(payload.get("important_event_at") or utc_now_iso()),
            recommended_poll_ms=int(payload.get("recommended_poll_ms") or 15000),
            brief_cache=BriefCache.from_dict(brief) if isinstance(brief, dict) else None,
            tasks=tasks,
        )

    def _poll_cap_ms(self) -> int:
        return int(PHASE_POLL_CAP_MS.get(self.phase, BACKOFF_SCHEDULE_MS[-1]))

    def compute_recommended_poll_ms(self, *, now: datetime | None = None) -> int:
        now_dt = now or _utc_now()
        since = _parse_iso(self.important_event_at) or now_dt
        elapsed = max(0.0, (now_dt - since).total_seconds())
        # time-based step selection keeps behavior stable without mutating state on every status call.
        if elapsed < 2:
            ms = BACKOFF_SCHEDULE_MS[0]
        elif elapsed < 4:
            ms = BACKOFF_SCHEDULE_MS[1]
        elif elapsed < 8:
            ms = BACKOFF_SCHEDULE_MS[2]
        elif elapsed < 15:
            ms = BACKOFF_SCHEDULE_MS[3]
        elif elapsed < 30:
            ms = BACKOFF_SCHEDULE_MS[4]
        elif elapsed < 60:
            ms = BACKOFF_SCHEDULE_MS[5]
        else:
            ms = BACKOFF_SCHEDULE_MS[6]
        return min(int(ms), self._poll_cap_ms())

    def public_status(self, *, options: dict[str, Any] | None = None) -> dict[str, Any]:
        del options
        now = _utc_now()
        poll_ms = self.compute_recommended_poll_ms(now=now)
        cache = self.brief_cache
        if cache:
            cached_at = _parse_iso(cache.generated_at) or now
            if (now - cached_at).total_seconds() * 1000 < cache.recommended_poll_ms:
                return {
                    "run_id": self.run_id,
                    "next_action": self.next_action,
                    "recommended_poll_ms": cache.recommended_poll_ms,
                    "wait_reason": self.wait_reason,
                    "lines": list(cache.lines)[:3],
                }

        completed = sum(1 for t in self.tasks if t.status == "completed")
        failed = next((t.slug for t in self.tasks if t.status == "failed"), None)
        running = next((t.slug for t in self.tasks if t.status == "running"), None)
        total = max(1, len(self.tasks))
        task_summary = f"任务: {completed}/{total} 完成"
        if running:
            task_summary += f" | running: {running}"
        if failed:
            task_summary += f" | failed: {failed}"

        lines = [
            f"模式: {self.mode} | 阶段: {self.phase} | 动作: {self.next_action}",
            task_summary,
            f"最近: {self.important_event} | 建议等待: {poll_ms//1000}s",
        ]
        self.recommended_poll_ms = poll_ms
        self.brief_cache = BriefCache(generated_at=utc_now_iso(), recommended_poll_ms=poll_ms, lines=lines[:3])
        return {"run_id": self.run_id, "next_action": self.next_action, "recommended_poll_ms": poll_ms, "wait_reason": self.wait_reason, "lines": lines[:3]}


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
