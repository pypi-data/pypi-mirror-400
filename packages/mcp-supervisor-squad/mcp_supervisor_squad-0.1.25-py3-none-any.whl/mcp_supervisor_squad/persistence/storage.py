from __future__ import annotations

import json
import os
import shutil
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any


def utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def parse_iso(ts: str | None) -> datetime | None:
    if not ts:
        return None
    try:
        return datetime.fromisoformat(ts.replace("Z", "+00:00"))
    except Exception:
        return None


def find_repo_root(start: Path) -> Path:
    """Walk upwards from start until a .git marker is found."""
    resolved = start.resolve()
    for path in (resolved, *resolved.parents):
        marker = path / ".git"
        if marker.is_dir() or marker.is_file():
            return path
    raise FileNotFoundError("Unable to locate repository root (.git not found).")


def atomic_write_json(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(path.suffix + ".tmp")
    with tmp.open("w", encoding="utf-8") as handle:
        json.dump(payload, handle, ensure_ascii=False, indent=2)
        handle.flush()
        os.fsync(handle.fileno())
    tmp.replace(path)


def read_json(path: Path) -> dict[str, Any] | None:
    try:
        data = path.read_text(encoding="utf-8")
    except FileNotFoundError:
        return None
    try:
        obj = json.loads(data)
    except json.JSONDecodeError:
        return None
    return obj if isinstance(obj, dict) else None


def safe_rmtree(path: Path) -> None:
    try:
        shutil.rmtree(path, ignore_errors=True)
    except Exception:
        return

@dataclass(frozen=True, slots=True)
class RunPaths:
    run_dir: Path
    state_path: Path
    artifacts_dir: Path
    patch_path: Path
    report_path: Path
    requirements_path: Path
    requirements_primary_path: Path
    requirements_secondary_path: Path
    contract_path: Path
    jobs_dir: Path


@dataclass(frozen=True, slots=True)
class StorageLayout:
    repo_root: Path
    base_dir: Path
    runs_dir: Path
    kb_dir: Path
    worktrees_dir: Path

    @classmethod
    def for_repo(cls, repo_root: Path) -> "StorageLayout":
        base = repo_root / ".codex" / "supervisor-squad"
        return cls(
            repo_root=repo_root,
            base_dir=base,
            runs_dir=base / "runs",
            kb_dir=base / "kb",
            worktrees_dir=base / "worktrees",
        )

    def run_paths(self, run_id: str) -> RunPaths:
        run_dir = self.runs_dir / run_id
        artifacts = run_dir / "artifacts"
        return RunPaths(
            run_dir=run_dir,
            state_path=run_dir / "state.json",
            artifacts_dir=artifacts,
            patch_path=artifacts / "patch.diff",
            report_path=artifacts / "report.md",
            requirements_path=artifacts / "requirements.md",
            requirements_primary_path=artifacts / "requirements-primary.md",
            requirements_secondary_path=artifacts / "requirements-secondary.md",
            contract_path=artifacts / "contract.json",
            jobs_dir=run_dir / "jobs",
        )


def prune_repo_storage(
    *,
    layout: StorageLayout,
    retention_days: int,
    rate_limit_seconds: int = 3600,
    max_runs: int = 20,
) -> None:
    """
    Best-effort prune for repo-local `.codex/supervisor-squad`.

    - Rate-limited via kb/prune_meta.json
    - Removes run/worktree dirs older than retention_days based on state.json timestamps
    - Also keeps at most `max_runs` most-recent runs (by created/updated time)
    """
    kb_dir = layout.kb_dir
    kb_dir.mkdir(parents=True, exist_ok=True)
    meta_path = kb_dir / "prune_meta.json"
    meta = read_json(meta_path) or {}
    last = parse_iso(str(meta.get("last_prune_at") or "")) if meta.get("last_prune_at") else None
    now = datetime.now(timezone.utc)
    if last and (now - last).total_seconds() < rate_limit_seconds:
        return

    cutoff = now - timedelta(days=max(1, int(retention_days)))
    runs_dir = layout.runs_dir
    worktrees_dir = layout.worktrees_dir
    survivors: list[tuple[datetime, Path]] = []
    if runs_dir.exists():
        for run_dir in runs_dir.iterdir():
            if not run_dir.is_dir():
                continue
            state_path = run_dir / "state.json"
            state = read_json(state_path) or {}
            created = parse_iso(str(state.get("created_at") or "")) or parse_iso(str(state.get("updated_at") or ""))
            if not created:
                continue
            if created >= cutoff:
                survivors.append((created, run_dir))
                continue
            run_id = run_dir.name
            safe_rmtree(run_dir)
            safe_rmtree(worktrees_dir / run_id)

    # Enforce max_runs by removing oldest beyond the limit.
    if max_runs > 0 and survivors:
        survivors.sort(key=lambda t: t[0], reverse=True)
        for _, run_dir in survivors[max_runs:]:
            run_id = run_dir.name
            safe_rmtree(run_dir)
            safe_rmtree(worktrees_dir / run_id)

    atomic_write_json(meta_path, {"last_prune_at": utc_now_iso(), "retention_days": retention_days, "max_runs": max_runs})
