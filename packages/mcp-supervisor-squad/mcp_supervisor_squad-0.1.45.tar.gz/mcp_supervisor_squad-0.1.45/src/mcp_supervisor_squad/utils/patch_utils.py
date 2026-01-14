from __future__ import annotations

import json
import base64
from pathlib import Path
from typing import Any


def _extract_text(obj: Any) -> str | None:
    if obj is None:
        return None
    if isinstance(obj, str):
        return obj
    if isinstance(obj, list):
        for item in obj:
            text = _extract_text(item)
            if text:
                return text
        return None
    if isinstance(obj, dict):
        if "item" in obj and isinstance(obj.get("item"), dict):
            item = obj.get("item") or {}
            for key in ("text", "content", "message"):
                if isinstance(item.get(key), str):
                    return item.get(key)
            nested = _extract_text(item)
            if nested:
                return nested
        for key in ("text", "content", "message"):
            if isinstance(obj.get(key), str):
                return obj.get(key)
        return None
    return None


def extract_patch_from_stdout_jsonl(stdout_path: Path, *, max_bytes: int = 5_000_000) -> str | None:
    """
    Extract a git-style patch from Codex JSONL stdout.

    Heuristic: find the longest text segment that contains 'diff --git ' and return from the
    first occurrence onward.
    """
    try:
        raw = stdout_path.read_bytes()
    except FileNotFoundError:
        return None
    if max_bytes > 0 and len(raw) > max_bytes:
        raw = raw[-max_bytes:]
    best: str | None = None
    for line in raw.splitlines():
        line = line.strip()
        if not line:
            continue
        try:
            obj = json.loads(line.decode("utf-8", errors="replace"))
        except Exception:
            continue
        text = _extract_text(obj)
        if not text or "diff --git " not in text:
            continue
        start = text.find("diff --git ")
        candidate = text[start:].strip("\n") + "\n"
        if not best or len(candidate) > len(best):
            best = candidate
    return best


def extract_tagged_b64_json_from_stdout_jsonl(stdout_path: Path, *, tag: str, max_bytes: int = 5_000_000) -> dict[str, Any] | None:
    """
    Extract a base64-encoded JSON payload from Codex JSONL stdout.

    Expected format (in any text segment): `${tag}<base64>`
    Example: `PLANNER_JSON_B64: eyJrZXkiOiAidmFsIn0=`
    """
    try:
        raw = stdout_path.read_bytes()
    except FileNotFoundError:
        return None
    if max_bytes > 0 and len(raw) > max_bytes:
        raw = raw[-max_bytes:]

    best_text: str | None = None
    for line in raw.splitlines():
        line = line.strip()
        if not line:
            continue
        try:
            obj = json.loads(line.decode("utf-8", errors="replace"))
        except Exception:
            continue
        text = _extract_text(obj)
        if not text:
            continue
        if tag not in text:
            continue
        # Prefer the last occurrence (likely final output).
        best_text = text

    if not best_text:
        return None

    idx = best_text.rfind(tag)
    if idx < 0:
        return None
    tail = best_text[idx + len(tag) :]
    tail = tail.strip()
    # allow `TAG: <b64>` form
    if tail.startswith(":"):
        tail = tail[1:].strip()
    # keep only the first token as base64
    b64 = tail.split()[0].strip()
    if not b64:
        return None
    try:
        decoded = base64.b64decode(b64.encode("utf-8"), validate=False)
    except Exception:
        return None
    try:
        obj = json.loads(decoded.decode("utf-8", errors="replace"))
    except Exception:
        return None
    return obj if isinstance(obj, dict) else None


def touched_files_from_patch(patch_text: str) -> list[str]:
    files: list[str] = []
    for line in (patch_text or "").splitlines():
        if not line.startswith("diff --git "):
            continue
        parts = line.split()
        if len(parts) >= 4:
            a_path = parts[2]
            b_path = parts[3]
            files.append(f"{a_path}->{b_path}")
    return files


def touched_b_paths_from_patch(patch_text: str) -> list[str]:
    """
    Return a list of target paths from 'diff --git' headers.
    Paths are returned without the leading 'b/' prefix when present.
    """
    out: list[str] = []
    for line in (patch_text or "").splitlines():
        if not line.startswith("diff --git "):
            continue
        parts = line.split()
        if len(parts) < 4:
            continue
        b_path = parts[3]
        if b_path.startswith("b/"):
            b_path = b_path[2:]
        out.append(b_path)
    return out


def detect_patch_conflicts(patch_a: str, patch_b: str) -> list[str]:
    """
    Detect overlapping file targets between two patches via 'diff --git' headers.
    Returns a list of conflicting b/ paths (without the 'b/' prefix).
    """
    def b_paths(p: str) -> set[str]:
        out: set[str] = set()
        for line in (p or "").splitlines():
            if not line.startswith("diff --git "):
                continue
            parts = line.split()
            if len(parts) >= 4:
                b = parts[3]
                if b.startswith("b/"):
                    out.add(b[2:])
                else:
                    out.add(b)
        return out

    a = b_paths(patch_a)
    b = b_paths(patch_b)
    return sorted(a.intersection(b))
