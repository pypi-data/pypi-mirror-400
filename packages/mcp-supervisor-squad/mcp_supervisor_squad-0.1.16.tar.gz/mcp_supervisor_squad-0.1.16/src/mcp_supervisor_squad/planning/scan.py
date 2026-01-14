from __future__ import annotations

import subprocess
from pathlib import Path
from typing import Any

from ..utils.constants import MARKER_FILES
from ..persistence.storage import StorageLayout, atomic_write_json, read_json, utc_now_iso
from .decider import discover_project_roots


def _run_git(repo_root: Path, args: list[str]) -> tuple[int, str]:
    res = subprocess.run(["git", *args], cwd=repo_root, capture_output=True, text=True)
    out = (res.stdout or "") + (res.stderr or "")
    return res.returncode, out.strip()


def _repo_fingerprint(repo_root: Path) -> dict[str, Any]:
    code, head = _run_git(repo_root, ["rev-parse", "HEAD"])
    git_head = head.strip() if code == 0 else ""
    code, status = _run_git(repo_root, ["status", "--porcelain"])
    dirty = bool(status.strip()) if code == 0 else False
    return {"repo_root": str(repo_root), "git_head": git_head, "dirty": dirty}


def _markers_for_dir(dir_path: Path) -> list[str]:
    present: list[str] = []
    for marker in MARKER_FILES:
        if (dir_path / marker).is_file():
            present.append(marker)
    return present


def _key_files_for_root(root: Path) -> list[str]:
    candidates = ["README.md", "README", "package.json", "pyproject.toml", "go.mod", "Cargo.toml"]
    out: list[str] = []
    for name in candidates:
        if (root / name).exists():
            out.append(name)
    return out


def _top_level_dirs(repo_root: Path) -> list[str]:
    ignore = {".git", ".codex", "node_modules", "dist", "build", "__pycache__"}
    out: list[str] = []
    try:
        for p in repo_root.iterdir():
            if not p.is_dir():
                continue
            if p.name in ignore:
                continue
            out.append(p.name)
    except OSError:
        return []
    return sorted(out)[:200]


def ensure_repo_profile(*, layout: StorageLayout, primary_root: Path, secondary_root: Path | None) -> dict[str, Any]:
    """
    Best-effort shared KB entry that avoids repeated repo scanning.

    Writes `<repo_root>/.codex/supervisor-squad/kb/repo_profile.json` when missing or stale.
    """
    kb_path = layout.kb_dir / "repo_profile.json"
    fingerprint = _repo_fingerprint(layout.repo_root)

    existing = read_json(kb_path) or {}
    if isinstance(existing, dict) and isinstance(existing.get("fingerprint"), dict):
        if existing.get("fingerprint") == fingerprint:
            return existing

    roots = discover_project_roots(repo_root=layout.repo_root)
    rel_roots: list[dict[str, Any]] = []
    for r in roots:
        try:
            rel = str(r.resolve().relative_to(layout.repo_root.resolve())).replace("\\", "/") or "."
        except Exception:
            rel = str(r)
        rel_roots.append({"path": rel, "markers": _markers_for_dir(r), "key_files": _key_files_for_root(r)})

    def rel(path: Path | None) -> str | None:
        if not path:
            return None
        try:
            return str(path.resolve().relative_to(layout.repo_root.resolve())).replace("\\", "/") or "."
        except Exception:
            return str(path)

    profile: dict[str, Any] = {
        "version": 1,
        "generated_at": utc_now_iso(),
        "fingerprint": fingerprint,
        "primary_root": rel(primary_root),
        "secondary_root": rel(secondary_root),
        "project_roots": rel_roots[:200],
        "top_level_dirs": _top_level_dirs(layout.repo_root),
    }
    atomic_write_json(kb_path, profile)
    return profile
