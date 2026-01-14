from __future__ import annotations
from pathlib import Path

MARKERS = {".git", "package.json", "pyproject.toml", "pnpm-workspace.yaml"}

def find_repo_root(start: Path) -> Path:
    cur = start.resolve()
    while True:
        if any((cur / m).exists() for m in MARKERS):
            return cur
        if cur.parent == cur:
            return cur
        cur = cur.parent
