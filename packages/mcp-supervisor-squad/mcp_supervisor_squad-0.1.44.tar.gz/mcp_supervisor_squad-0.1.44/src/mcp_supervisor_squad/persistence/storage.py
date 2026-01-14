from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any

from .storage import parse_iso, read_json, safe_rmtree, utc_now_iso


@dataclass(frozen=True, slots=True)
class RunPaths:
    run_dir: Path
    state_path: Path
    artifacts_dir: Path
    report_path: Path
    jobs_dir: Path


@dataclass(frozen=True, slots=True)
class StorageLayout:
    repo_root: Path
    base_dir: Path
    runs_dir: Path
    worktrees_dir: Path

    @classmethod
    def for_repo(cls, repo_root: Path) -> "StorageLayout":
        base = repo_root / ".codex" / "supervisor-squad"
        return cls(
            repo_root=repo_root,
            base_dir=base,
            runs_dir=base / "runs",
            worktrees_dir=base / "worktrees",
        )

    def run_paths(self, run_id: str) -> RunPaths:
        run_dir = self.runs_dir / run_id
        artifacts = run_dir / "artifacts"
        return RunPaths(
            run_dir=run_dir,
            state_path=run_dir / "state.json",
            artifacts_dir=artifacts,
            report_path=artifacts / "report.md",
            jobs_dir=run_dir / "jobs",
        )


def prune_repo_storage(*, layout: StorageLayout, retention_days: int, max_runs: int = 20) -> None:
    """Remove stale runs/worktrees; store prune meta under base_dir."""
    now = datetime.now(timezone.utc)
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

    if max_runs > 0 and survivors:
        survivors.sort(key=lambda t: t[0], reverse=True)
        for _, run_dir in survivors[max_runs:]:
            run_id = run_dir.name
            safe_rmtree(run_dir)
            safe_rmtree(worktrees_dir / run_id)

    meta_path = layout.base_dir / "prune_meta.json"
    meta_path.parent.mkdir(parents=True, exist_ok=True)
    from .storage import atomic_write_json

    atomic_write_json(meta_path, {"last_prune_at": utc_now_iso(), "retention_days": retention_days, "max_runs": max_runs})
