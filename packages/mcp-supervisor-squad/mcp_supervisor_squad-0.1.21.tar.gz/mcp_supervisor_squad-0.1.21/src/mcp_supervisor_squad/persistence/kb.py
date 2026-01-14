from __future__ import annotations

import shutil
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from .storage import StorageLayout, atomic_write_json, read_json, utc_now_iso


@dataclass(frozen=True, slots=True)
class DirectorReport:
    kind: str  # json|md|none
    path: Path | None
    payload: dict[str, Any] | None
    text: str | None


def _max_bytes(kb: int) -> int:
    return int(max(1, kb)) * 1024


def inbox_paths(layout: StorageLayout) -> tuple[Path, Path]:
    inbox_dir = layout.kb_dir / "inbox"
    return inbox_dir / "director_report.md", inbox_dir / "director_report.json"


def read_director_report(*, layout: StorageLayout, max_kb: int) -> DirectorReport:
    md_path, json_path = inbox_paths(layout)
    max_b = _max_bytes(max_kb)

    if json_path.exists():
        try:
            if json_path.stat().st_size > max_b:
                return DirectorReport(kind="json", path=json_path, payload=None, text=None)
        except OSError:
            return DirectorReport(kind="json", path=json_path, payload=None, text=None)
        raw = read_json(json_path)
        if isinstance(raw, dict):
            return DirectorReport(kind="json", path=json_path, payload=raw, text=None)
        return DirectorReport(kind="json", path=json_path, payload=None, text=None)

    if md_path.exists():
        try:
            data = md_path.read_bytes()
        except OSError:
            return DirectorReport(kind="md", path=md_path, payload=None, text=None)
        if len(data) > max_b:
            data = data[:max_b]
            try:
                md_path.write_bytes(data)
            except OSError:
                pass
        return DirectorReport(kind="md", path=md_path, payload=None, text=data.decode("utf-8", errors="replace"))

    return DirectorReport(kind="none", path=None, payload=None, text=None)


def write_compact(*, layout: StorageLayout, compact_md: str, max_kb: int) -> Path:
    kb_dir = layout.kb_dir
    kb_dir.mkdir(parents=True, exist_ok=True)
    compact_path = kb_dir / "compact.md"
    sanitized = sanitize_compact_md(compact_md or "")
    raw = sanitized.encode("utf-8", errors="replace")
    if len(raw) > _max_bytes(max_kb):
        raw = raw[: _max_bytes(max_kb)]
    compact_path.write_bytes(raw)
    return compact_path


_FENCE_RE = re.compile(r"^```")


def sanitize_compact_md(text: str) -> str:
    """
    Keep shared KB high-signal and stable:
    - Remove fenced code blocks (they explode context and drift quickly).
    - Trim extremely long lines.
    - Collapse excessive blank lines.
    """
    lines = (text or "").splitlines()
    out: list[str] = []
    in_fence = False
    for line in lines:
        if _FENCE_RE.match(line.strip()):
            in_fence = not in_fence
            continue
        if in_fence:
            continue
        if len(line) > 400:
            line = line[:400] + "…"
        out.append(line.rstrip())

    collapsed: list[str] = []
    blank = 0
    for line in out:
        if not line.strip():
            blank += 1
            if blank > 2:
                continue
        else:
            blank = 0
        collapsed.append(line)
    return "\n".join(collapsed).strip() + "\n"


def _prune_archive(*, archive_dir: Path, keep: int, max_kb: int) -> None:
    if not archive_dir.exists():
        return
    items = [p for p in archive_dir.iterdir() if p.is_file()]
    items.sort(key=lambda p: p.stat().st_mtime, reverse=True)
    if keep >= 0 and len(items) > keep:
        for p in items[keep:]:
            try:
                p.unlink()
            except OSError:
                pass

    limit = _max_bytes(max_kb)
    items = [p for p in archive_dir.iterdir() if p.is_file()]
    items.sort(key=lambda p: p.stat().st_mtime, reverse=True)
    total = 0
    for p in items:
        try:
            size = p.stat().st_size
        except OSError:
            continue
        total += size
        if total <= limit:
            continue
        try:
            p.unlink()
        except OSError:
            pass


def archive_and_clear_inbox(*, layout: StorageLayout, keep: int, max_kb: int) -> None:
    md_path, json_path = inbox_paths(layout)
    inbox_dir = md_path.parent
    archive_dir = layout.kb_dir / "archive"
    archive_dir.mkdir(parents=True, exist_ok=True)

    ts = utc_now_iso().replace(":", "").replace("-", "").replace(".", "")
    for src in (json_path, md_path):
        if not src.exists():
            continue
        dst = archive_dir / f"{ts}-{src.name}"
        try:
            shutil.move(str(src), str(dst))
        except OSError:
            try:
                src.unlink()
            except OSError:
                pass

    # Keep inbox directory, but ensure it's not huge.
    try:
        inbox_dir.mkdir(parents=True, exist_ok=True)
    except OSError:
        pass

    _prune_archive(archive_dir=archive_dir, keep=keep, max_kb=max_kb)


def write_kb_index(*, layout: StorageLayout, note: str) -> None:
    """
    Best-effort small index for operators; not used by runtime logic.
    """
    path = layout.kb_dir / "kb_index.json"
    existing = read_json(path) or {}
    if not isinstance(existing, dict):
        existing = {}
    existing.update({"updated_at": utc_now_iso(), "note": str(note)[:500]})
    atomic_write_json(path, existing)
