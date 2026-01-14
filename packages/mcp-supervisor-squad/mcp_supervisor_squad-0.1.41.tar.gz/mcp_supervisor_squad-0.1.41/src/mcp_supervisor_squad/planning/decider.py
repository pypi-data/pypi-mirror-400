"""Repo/project root selection and run pruning."""

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
    # stable-ish order
    return sorted({p.resolve() for p in roots}, key=lambda p: str(p))


def choose_secondary_root(*, primary: Path, candidates: list[Path], query: str) -> Path | None:
    q = (query or "").lower()
    distinct = [
        c
        for c in candidates
        if c != primary and (c not in primary.parents) and (primary not in c.parents)
    ]
    if not distinct:
        return None
    # Prefer explicit mentions of directory names in query.
    mentioned = [c for c in distinct if c.name.lower() in q]
    if len(mentioned) >= 1:
        return mentioned[0]
    # Common frontend/backend pattern: prefer web/api named roots if present.
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

    if opt_mode == "force_single":
        return StartDecision(repo_root=repo_root, primary_root=primary_root, secondary_root=None, mode="single")
    if opt_mode == "force_dual":
        secondary = choose_secondary_root(primary=primary_root, candidates=candidates, query=query)
        return StartDecision(repo_root=repo_root, primary_root=primary_root, secondary_root=secondary, mode="dual" if secondary else "single")

    # auto: only dual when query suggests it via two distinct root names.
    q = (query or "").lower()
    mentioned = [c for c in candidates if c.name.lower() in q]
    mentioned_distinct = [
        c
        for c in mentioned
        if c != primary_root and (c not in primary_root.parents) and (primary_root not in c.parents)
    ]
    secondary = mentioned_distinct[0] if mentioned_distinct else None
    if secondary:
        return StartDecision(repo_root=repo_root, primary_root=primary_root, secondary_root=secondary, mode="dual")
    return StartDecision(repo_root=repo_root, primary_root=primary_root, secondary_root=None, mode="single")


def _rel(repo_root: Path, path: Path) -> str:
    try:
        return str(path.resolve().relative_to(repo_root.resolve())).replace("\\", "/")
    except Exception:
        return str(path)


def write_requirements_single(*, layout: StorageLayout, run_id: str, query: str, primary_root: Path) -> Path:
    paths = layout.run_paths(run_id)
    paths.artifacts_dir.mkdir(parents=True, exist_ok=True)
    scope = _rel(layout.repo_root, primary_root) or "."
    text = "\n".join(
        [
            "# Requirements",
            "",
            "## Goal",
            query.strip() or "(empty query)",
            "",
            "## Scope",
            f"- Allowed: `{scope}/**`",
            "",
            "## Acceptance",
            "- Produces a single git-style patch affecting only allowed paths.",
            "- Keeps changes minimal and directly related to the goal.",
            "",
            "## Constraints",
            "- No compatibility layers; keep changes lean and direct.",
            "- Output patch only; no long logs or prose.",
            "- Do not touch unrelated directories.",
            "- Prefer existing toolchain (pnpm/pip/etc.) already used in repo.",
            "",
            "## Context Hints",
            f"- Project root: `{scope}`",
            "",
            "## Plan",
            "- Read repo-specific READMEs/manifests in scope for conventions.",
            "- Draft minimal implementation focused on the stated goal.",
            "- Keep logs small; surface only patch + brief risks/follow-ups.",
            "",
            "## Risks / Follow-ups",
            "- Over-scope edits will be rejected; stay within allowed paths.",
            "- Avoid introducing new package managers or config churn.",
            "",
        ]
    )
    paths.requirements_path.write_text(text, encoding="utf-8")
    return paths.requirements_path


def write_requirements_dual(
    *,
    layout: StorageLayout,
    run_id: str,
    query: str,
    primary_root: Path,
    secondary_root: Path,
) -> tuple[Path, Path]:
    paths = layout.run_paths(run_id)
    paths.artifacts_dir.mkdir(parents=True, exist_ok=True)
    primary_rel = _rel(layout.repo_root, primary_root) or "."
    secondary_rel = _rel(layout.repo_root, secondary_root) or "."

    primary_text = "\n".join(
        [
            "# Requirements (Primary)",
            "",
            "## Goal",
            query.strip() or "(empty query)",
            "",
            "## Scope",
            f"- Allowed: `{primary_rel}/**`",
            "",
            "## Acceptance",
            "- Produces a patch only for the primary project scope.",
            "",
            "## Constraints",
            "- Do not modify secondary project files.",
            "- Patch only.",
            "",
            "## Context Hints",
            f"- Project root: `{primary_rel}`",
            "",
        ]
    )
    secondary_text = "\n".join(
        [
            "# Requirements (Secondary)",
            "",
            "## Goal",
            query.strip() or "(empty query)",
            "",
            "## Scope",
            f"- Allowed: `{secondary_rel}/**`",
            "",
            "## Acceptance",
            "- Produces a patch only for the secondary project scope.",
            "",
            "## Constraints",
            "- Do not modify primary project files.",
            "- Patch only.",
            "",
            "## Context Hints",
            f"- Project root: `{secondary_rel}`",
            "",
        ]
    )
    paths.requirements_primary_path.write_text(primary_text, encoding="utf-8")
    paths.requirements_secondary_path.write_text(secondary_text, encoding="utf-8")

    return paths.requirements_primary_path, paths.requirements_secondary_path


def prune_on_start(*, repo_root: Path, retention_days: int) -> None:
    layout = StorageLayout.for_repo(repo_root)
    prune_repo_storage(layout=layout, retention_days=retention_days, max_runs=20)
