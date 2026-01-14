from __future__ import annotations
from pathlib import Path
from .constants import MARKER_FILES

def find_repo_root(start: Path) -> Path:
    cur = start.resolve()
    while True:
        if any((cur / m).exists() for m in MARKER_FILES):
            return cur
        if cur.parent == cur:
            return cur
        cur = cur.parent
