"""Repo/project root selection and run pruning (minimal)."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any

from ..utils.constants import MARKER_FILES
from ..persistence.storage import StorageLayout, find_repo_root, prune_repo_storage


def _has_marker(dir_path: Path) -> bool:
    return any((dir_path / marker).is_file() for marker in MARKER_FILES)


def detect_primary_project_root(*, cwd: Path, repo_root: Path) -> Path:
    current = cwd
    while True:
        if _has_marker(current):
            return current
        if current == repo_root:
            return repo_root
        current = current.parent


def discover_project_roots(*, repo_root: Path, max_depth: int = 5) -> list[Path]:
    roots: list[Path] = []
    queue: list[tuple[Path, int]] = [(repo_root, 0)]
    while queue:
        path, depth = queue.pop(0)
        if depth > max_depth:
            continue
        if path != repo_root and _has_marker(path):
            roots.append(path)
            continue
        try:
            children = [p for p in path.iterdir() if p.is_dir()]
        except OSError:
            continue
        for child in children:
            if child.name in {".git", ".codex", "node_modules", "dist", "build", "__pycache__"}:
                continue
            queue.append((child, depth + 1))
    return sorted({p.resolve() for p in roots}, key=lambda p: str(p))


def choose_secondary_root(*, primary: Path, candidates: list[Path], query: str) -> Path | None:
    q = (query or "").lower()
    distinct = [c for c in candidates if c != primary and (c not in primary.parents) and (primary not in c.parents)]
    if not distinct:
        return None
    mentioned = [c for c in distinct if c.name.lower() in q]
    if mentioned:
        return mentioned[0]
    preferred = next((c for c in distinct if c.name.lower() in {"web-react", "api-fastapi"}), None)
    return preferred or distinct[0]


@dataclass(frozen=True, slots=True)
class StartDecision:
    repo_root: Path
    primary_root: Path
    secondary_root: Path | None
    mode: str  # single|dual


def decide_start(*, cwd: Path, query: str, options: dict[str, Any] | None) -> StartDecision:
    repo_root = find_repo_root(cwd)
    primary_root = detect_primary_project_root(cwd=cwd, repo_root=repo_root)
    opt_mode = str((options or {}).get("mode") or "auto").strip().lower()
    candidates = discover_project_roots(repo_root=repo_root)
    secondary = None
    if opt_mode == "dual":
        secondary = choose_secondary_root(primary=primary_root, candidates=candidates, query=query)
    return StartDecision(repo_root=repo_root, primary_root=primary_root, secondary_root=secondary, mode="single" if not secondary else "dual")


def prune_on_start(*, repo_root: Path, retention_days: int) -> None:
    layout = StorageLayout.for_repo(repo_root)
    prune_repo_storage(layout=layout, retention_days=retention_days, max_runs=20)
