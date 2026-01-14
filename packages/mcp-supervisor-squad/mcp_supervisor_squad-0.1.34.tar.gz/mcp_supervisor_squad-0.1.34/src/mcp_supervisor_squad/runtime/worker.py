from __future__ import annotations

from collections.abc import Callable
import os
import signal
import time
import subprocess
import threading
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any
from uuid import uuid4

from .dispatch import run_codex_exec
from ..persistence.contract import write_repo_contract
from ..persistence.kb import archive_and_clear_inbox, read_director_report, write_compact, write_kb_index
from ..persistence.storage import StorageLayout, atomic_write_json, read_json, safe_rmtree, utc_now_iso
from ..utils.patch_utils import (
    detect_patch_conflicts,
    extract_patch_from_stdout_jsonl,
    touched_b_paths_from_patch,
    touched_files_from_patch,
)
from ..persistence.state import RunState, RunStore, RunTask
from ..planning.config import effective_config
from ..planning.scan import ensure_repo_profile
from ..planning.decider import decide_start, prune_on_start, write_requirements_dual, write_requirements_single


def _run_git(repo_root: Path, args: list[str]) -> tuple[int, str]:
    res = subprocess.run(["git", *args], cwd=repo_root, capture_output=True, text=True)
    out = (res.stdout or "") + (res.stderr or "")
    return res.returncode, out.strip()


class Worker:
    def __init__(self, store: RunStore):
        self._store = store
        self._lock = threading.Lock()

    def _requirements_brief_lines(self, text: str, max_len: int = 1000) -> list[str]:
        if not isinstance(text, str) or not text.strip():
            return []
        trimmed = text.strip()
        if len(trimmed) > max_len:
            note = "(详见 artifacts/requirements.md)"
            trimmed = trimmed[: max(0, max_len - len(note))].rstrip() + "\n" + note
        lines = [ln.strip() for ln in trimmed.splitlines() if ln.strip()]
        return lines

    def _classify_difficulty(self, query: str, project_root: Path, repo_root: Path) -> str:
        """
        Roughly classify task difficulty to skip heavy planning for simple tasks.
        simple   -> jump to coder
        medium   -> planner_light only
        hard     -> light + heavy
        """
        q = (query or "").lower()
        simple_keywords = {"rename", "typo", "doc", "docs", "readme", "copy", "text", "style"}
        hard_keywords = {"feature", "refactor", "api", "schema", "workflow", "migration"}
        # Repo shape hints
        is_root = True
        try:
            is_root = project_root.resolve() == repo_root.resolve()
        except Exception:
            pass
        if any(k in q for k in simple_keywords) and not any(k in q for k in hard_keywords):
            return "simple"
        if not is_root:
            return "medium"
        if any(k in q for k in hard_keywords):
            return "hard"
        return "medium"

    def start(self, *, cwd: str, query: str, options: dict[str, Any]) -> RunState:
        resolved_cwd = Path(cwd).resolve()
        decision = decide_start(cwd=resolved_cwd, query=query, options=options)
        layout = StorageLayout.for_repo(decision.repo_root)
        retention_days = int(options.get("retention_days") or 10)
        prune_on_start(repo_root=decision.repo_root, retention_days=retention_days)
        # Kill any orphaned codex jobs from previous runs to avoid runaway processes.
        self._kill_orphan_jobs(layout=layout)

        cfg = effective_config(repo_root=decision.repo_root, options=options)
        _ = ensure_repo_profile(layout=layout, primary_root=decision.primary_root, secondary_root=decision.secondary_root)
        try:
            from .. import __version__

            _ = write_repo_contract(layout=layout, cfg=cfg, package_version=__version__)
        except Exception:
            pass

        run_id = f"ss-{uuid4().hex}"
        paths = layout.run_paths(run_id)
        paths.run_dir.mkdir(parents=True, exist_ok=True)
        paths.artifacts_dir.mkdir(parents=True, exist_ok=True)
        paths.jobs_dir.mkdir(parents=True, exist_ok=True)

        tasks: list[RunTask] = []
        if decision.secondary_root:
            primary_slug = "primary"
            secondary_slug = "secondary"
            tasks = [
                RunTask(slug=primary_slug, project_root=str(decision.primary_root), worktree=str(layout.worktrees_dir / run_id / primary_slug)),
                RunTask(slug=secondary_slug, project_root=str(decision.secondary_root), worktree=str(layout.worktrees_dir / run_id / secondary_slug)),
            ]
            important = "已创建 run"
        else:
            tasks = [RunTask(slug="single", project_root=str(decision.primary_root), worktree=str(layout.worktrees_dir / run_id / "single"))]
            important = "已创建 run"

        now = utc_now_iso()
        state = RunState(
            run_id=run_id,
            repo_root=str(decision.repo_root),
            cwd=str(resolved_cwd),
            query=query,
            sandbox=cfg.execution.sandbox,
            approval_policy=cfg.execution.approval_policy,
            planner_model=cfg.planner.model,
            planner_reasoning_effort=cfg.planner.reasoning_effort,
            planner_extra_config=list(cfg.planner.extra_config),
            coder_model=cfg.coder.model,
            coder_reasoning_effort=cfg.coder.reasoning_effort,
            coder_extra_config=list(cfg.coder.extra_config),
            read_limits_max_files=cfg.read_limits.max_files,
            read_limits_max_file_bytes=cfg.read_limits.max_file_bytes,
            read_limits_max_total_bytes=cfg.read_limits.max_total_bytes,
            kb_inbox_max_kb=cfg.kb.inbox_max_kb,
            kb_compact_max_kb=cfg.kb.compact_max_kb,
            kb_archive_keep=cfg.kb.archive_keep,
            kb_archive_max_kb=cfg.kb.archive_max_kb,
            polling_max_ms=cfg.polling.max_ms,
            polling_jitter_ratio=cfg.polling.jitter_ratio,
            mode=decision.mode,
            phase="planner_run",
            next_action="wait",
            wait_reason="agent_running",
            created_at=now,
            updated_at=now,
            phase_started_at=now,
            retention_days=retention_days,
            important_event=important,
            important_event_at=now,
            event_seq=1,
            tasks=tasks,
        )
        state.events = [{"tag": "", "phase": state.phase, "kind": "info", "message": "已创建 run"}]
        self._store.save(state)
        self._write_report(layout=layout, state=state)

        thread = threading.Thread(
            target=self._run, args=(state.run_id, state.repo_root), name=f"supervisor-squad-{run_id}", daemon=True
        )
        thread.start()
        return state

    def cancel(self, *, run_id: str, cwd: str, reason: str | None = None) -> bool:
        """
        Best-effort cancellation to reduce wasted time/context (kills running jobs).
        Returns True if cancellation was applied, otherwise False.
        """
        with self._lock:
            state = self._store.load(run_id, cwd=cwd)
            if state.phase in {"done", "cleanup", "canceled", "error"}:
                return False
            layout = StorageLayout.for_repo(Path(state.repo_root))
            jobs_dir = layout.run_paths(run_id).jobs_dir
            state.canceled = True
            state.phase = "canceled"
            state.next_action = "wait"
            state.wait_reason = "canceled"
            state.phase_started_at = utc_now_iso()
            state.important_event = "已取消" + (f": {str(reason)[:80]}" if reason else "")
            state.important_event_at = utc_now_iso()
            state.updated_at = utc_now_iso()
            state.event_seq += 1
            self._store.save(state)
            self._write_report(layout=layout, state=state)

        # Try to kill running planner/coder jobs to save time/resources.
        job_ids: list[str] = []
        try:
            state = self._store.load(run_id, cwd=cwd)
            if state.planner_job_id:
                job_ids.append(state.planner_job_id)
            for t in state.tasks:
                if t.job_id:
                    job_ids.append(t.job_id)
        except Exception:
            pass
        killed = self._kill_jobs(jobs_dir=jobs_dir, job_ids=job_ids)

        # Update event with kill count to surface whether cancel saved work.
        with self._lock:
            try:
                state = self._store.load(run_id, cwd=cwd)
                state.important_event = state.important_event + f" | kill={killed}"
                state.updated_at = utc_now_iso()
                state.event_seq += 1
                self._store.save(state)
                self._write_report(layout=layout, state=state)
            except Exception:
                pass
        return True

    def _kill_jobs(self, *, jobs_dir: Path, job_ids: list[str]) -> int:
        """Best-effort terminate running codex exec jobs to save time/context."""
        killed = 0
        for job_id in job_ids:
            meta_path = jobs_dir / job_id / "meta.json"
            meta = read_json(meta_path)
            if not isinstance(meta, dict):
                continue
            pid = meta.get("pid")
            if not pid:
                continue
            try:
                os.kill(int(pid), signal.SIGTERM)
                time.sleep(0.5)
                os.kill(int(pid), 0)
                os.kill(int(pid), signal.SIGKILL)
                killed += 1
            except ProcessLookupError:
                continue
            except Exception:
                continue
        return killed

    def _kill_orphan_jobs(self, *, layout: StorageLayout) -> None:
        """
        Best-effort kill any codex jobs whose parent run no longer exists or exceeded retention/max_runs.
        Prevents runaway processes consuming memory/CPU after forced exits.
        """
        jobs_dir = layout.base_dir / "runs"
        if not jobs_dir.exists():
            return
        for run_dir in jobs_dir.iterdir():
            if not run_dir.is_dir():
                continue
            # If state.json is missing, consider orphan.
            state_path = run_dir / "state.json"
            if not state_path.exists():
                meta_path = run_dir / "jobs"
                if not meta_path.exists():
                    continue
                for job_dir in meta_path.iterdir():
                    if not job_dir.is_dir():
                        continue
                    meta = read_json(job_dir / "meta.json")
                    if not isinstance(meta, dict):
                        continue
                    pid = meta.get("pid")
                    if not pid:
                        continue
                    try:
                        os.kill(int(pid), signal.SIGTERM)
                    except Exception:
                        continue

    def _run(self, run_id: str, repo_root_hint: str | None = None) -> None:
        try:
            state = self._store.load(run_id, cwd=repo_root_hint)
        except Exception:
            return
        repo_root = Path(state.repo_root or repo_root_hint or ".").resolve()
        layout = StorageLayout.for_repo(repo_root)
        paths = layout.run_paths(run_id)

        def update(*, mutator: Callable[[RunState], None] | None = None, event: dict[str, Any] | None = None, **fields: Any) -> None:
            with self._lock:
                current = self._store.load(run_id, cwd=str(repo_root))
                if current.canceled or current.phase == "canceled":
                    return
                if mutator is not None:
                    mutator(current)
                if current.canceled or current.phase == "canceled":
                    return
                event_msg = str(fields.get("important_event") or "").strip()
                if "phase" in fields:
                    new_phase = fields.get("phase")
                    if isinstance(new_phase, str) and new_phase and new_phase != current.phase:
                        current.phase_started_at = utc_now_iso()
                for k, v in fields.items():
                    setattr(current, k, v)
                # Push event when we have an important_event or explicit event payload.
                if event_msg or event:
                    kind = "info"
                    data = None
                    if isinstance(event, dict):
                        kind = str(event.get("kind") or "info")
                        data = event.get("data")
                        if isinstance(event.get("message"), str) and event.get("message").strip():
                            event_msg = event.get("message").strip()
                    evt = {
                        "id": current.event_seq + 1,
                        "ts": utc_now_iso(),
                        "kind": kind,
                        "phase": fields.get("phase") or current.phase,
                        "message": event_msg or current.important_event or "",
                    }
                    if data is not None:
                        evt["data"] = data
                    current.events.append(evt)
                    # Trim to avoid unbounded growth.
                    current.events = current.events[-50:]
                current.updated_at = utc_now_iso()
                current.event_seq += 1
                self._store.save(current)
                self._write_report(layout=layout, state=current)

        update(phase="planner_light", important_event="已开始执行 planner(轻量)", important_event_at=utc_now_iso())

        # Planner phase: read director report (if any) and produce requirements/contract/compact.
        report = read_director_report(layout=layout, max_kb=state.kb_inbox_max_kb)
        if getattr(report, "kind", "") == "json" and getattr(report, "payload", None) is None and getattr(report, "path", None):
            # Oversized or invalid JSON report; archive it to avoid repeated failures.
            archive_and_clear_inbox(layout=layout, keep=state.kb_archive_keep, max_kb=state.kb_archive_max_kb)
            report = read_director_report(layout=layout, max_kb=state.kb_inbox_max_kb)

        difficulty = self._classify_difficulty(state.query, Path(state.tasks[0].project_root) if state.tasks else repo_root, repo_root)

        if difficulty in {"medium", "hard"}:
            light_files = self._plan_scan(repo_root=repo_root, query=state.query, layout=layout, light=True)
            light_evidence = self._exec_scan(
                layout=layout,
                plan_files=light_files,
                artifacts_dir=paths.artifacts_dir,
                read_limits=(min(3, state.read_limits_max_files), state.read_limits_max_file_bytes, state.read_limits_max_total_bytes),
            )
            light_paths = [e.get("path", "") for e in light_evidence if isinstance(e, dict)]
            summary = f"轻扫: {', '.join(light_paths[:5])}" if light_paths else "轻扫: 无文件"
            light_summary_path = paths.artifacts_dir / "summary_light.md"
            light_summary_text = ""
            try:
                scope = "."
                if state.tasks:
                    try:
                        rel = Path(state.tasks[0].project_root).resolve().relative_to(repo_root.resolve())
                        scope = str(rel).replace("\\", "/") or "."
                    except Exception:
                        scope = "."

                lines = [
                    "# Planner Light 摘要（面向用户）",
                    "",
                    "## 需求概述",
                    (state.query.strip() or "(empty query)")[:2000],
                    "",
                    "## 目标范围",
                    f"- 允许路径: `{scope}/**`",
                    "- 保持改动最小，不触碰无关目录。",
                    "",
                    "## 预期交付",
                    "- 一页简明介绍（本次需求），突出使用方式与优势。",
                    "- 随后由 coder 产出详细 requirements.md 与最终补丁。",
                    "",
                    "## 提醒",
                    "- 避免兼容性代码；遵循既有工具链（pnpm/pip 等）。",
                    "- 控制上下文，基于实际文件，不编造内容；日志简短。",
                    "",
                    summary,
                    "",
                ]
                light_summary_text = "\n".join(lines)
                light_summary_path.write_text(light_summary_text, encoding="utf-8")
            except Exception:
                pass
            update(
                important_event=summary,
                important_event_at=utc_now_iso(),
                event={"kind": "light_summary", "data_lines": [ln for ln in light_summary_text.splitlines() if ln.strip()]},
            )
        else:
            update(
                important_event="跳过 planner，直接执行 coder（简单任务）",
                important_event_at=utc_now_iso(),
                event={"kind": "info", "data_lines": ["简单任务: 跳过 planner，直接执行 coder"]},
            )

        if difficulty == "hard":
            update(phase="planner_heavy", important_event="开始深度扫描", important_event_at=utc_now_iso())
        # Requirements & heavy scan
        requirements_payload = ""
        if difficulty == "hard":
            plan_files = self._plan_scan(repo_root=repo_root, query=state.query, layout=layout, light=False)
            evidence = self._exec_scan(
                layout=layout,
                plan_files=plan_files,
                artifacts_dir=paths.artifacts_dir,
                read_limits=(state.read_limits_max_files, state.read_limits_max_file_bytes, state.read_limits_max_total_bytes),
            )

            try:
                paths.artifacts_dir.mkdir(parents=True, exist_ok=True)
                if state.mode == "dual" and len(state.tasks) > 1:
                    _ = write_requirements_dual(
                        layout=layout,
                        run_id=run_id,
                        query=state.query,
                        primary_root=Path(state.tasks[0].project_root),
                        secondary_root=Path(state.tasks[1].project_root),
                    )
                else:
                    req_path = write_requirements_single(
                        layout=layout,
                        run_id=run_id,
                        query=state.query,
                        primary_root=Path(state.tasks[0].project_root) if state.tasks else repo_root,
                    )
                    try:
                        requirements_payload = req_path.read_text(encoding="utf-8")
                    except Exception:
                        requirements_payload = ""

                profile = read_json(layout.kb_dir / "repo_profile.json") or {}
                fp = profile.get("fingerprint") if isinstance(profile.get("fingerprint"), dict) else {}
                git_head = str(fp.get("git_head") or "")
                dirty = bool(fp.get("dirty") or False)
                top_dirs = profile.get("top_level_dirs") if isinstance(profile.get("top_level_dirs"), list) else []
                roots = profile.get("project_roots") if isinstance(profile.get("project_roots"), list) else []
                roots = [r for r in roots if isinstance(r, dict)]
                roots_hint = ", ".join(str(r.get("path") or "") for r in roots[:8] if str(r.get("path") or "").strip())
                evidence_paths = [e.get("path", "") for e in evidence if isinstance(e, dict)]
                compact_md = "\n".join(
                    [
                        "# Supervisor Squad KB (Compact)",
                        "",
                        f"- Mode: {state.mode}",
                        f"- Repo: {Path(state.repo_root).name} | git_head: {git_head[:12] or '(unknown)'} | dirty: {dirty}",
                        f"- Top-level dirs: {', '.join(str(x) for x in top_dirs[:12]) if top_dirs else '(unknown)'}",
                        f"- Project roots: {roots_hint or '(unknown)'}",
                        f"- Director report: {getattr(report, 'kind', 'none')}",
                        f"- Evidence files: {', '.join(evidence_paths[:10]) if evidence_paths else '(none)'}",
                        "",
                        "## Goal (raw)",
                        (state.query.strip() or "(empty query)")[:2000],
                        "",
                        "## Next",
                        "- Coder writes patch.diff according to requirements.md.",
                        "",
                    ]
                )
                _ = write_compact(layout=layout, compact_md=compact_md, max_kb=state.kb_compact_max_kb)
                write_kb_index(layout=layout, note="requirements generated")
                archive_and_clear_inbox(layout=layout, keep=state.kb_archive_keep, max_kb=state.kb_archive_max_kb)
            except Exception:
                update(
                    phase="error",
                    next_action="wait",
                    wait_reason="error",
                    important_event="写入 requirements/KB 失败",
                    important_event_at=utc_now_iso(),
                )
                return

            def set_requirements_brief(current: RunState) -> None:
                q = (current.query or "").strip().splitlines()
                current.requirements_brief = (q[0] if q else "requirements generated")[:160]

            update(
                mutator=set_requirements_brief,
                important_event="已生成需求文档",
                important_event_at=utc_now_iso(),
                event={"kind": "requirements", "data_lines": self._requirements_brief_lines(requirements_payload)},
            )
        else:
            try:
                req_path = write_requirements_single(
                    layout=layout,
                    run_id=run_id,
                    query=state.query,
                    primary_root=Path(state.tasks[0].project_root) if state.tasks else repo_root,
                )
                try:
                    requirements_payload = req_path.read_text(encoding="utf-8")
                except Exception:
                    requirements_payload = ""
                update(
                    important_event="已生成需求文档",
                    important_event_at=utc_now_iso(),
                    event={"kind": "requirements", "data_lines": self._requirements_brief_lines(requirements_payload)},
                )
            except Exception:
                update(
                    phase="error",
                    next_action="wait",
                    wait_reason="error",
                    important_event="写入 requirements 失败",
                    important_event_at=utc_now_iso(),
                )
                return

        # Coder phase (shared)
        update(phase="coder_run", wait_reason="agent_running", important_event="已开始执行 coder", important_event_at=utc_now_iso())
        patches: dict[str, str] = {}
        patches_lock = threading.Lock()
        task_threads: list[threading.Thread] = []

        contract_hint = paths.contract_path if state.mode == "dual" else None

        allow_prefix_by_slug: dict[str, str] = {}
        prepared: list[tuple[str, Path, str]] = []

        def run_task(*, task_slug: str, prompt_text: str, cwd_path: Path, allow_prefix: str, forbid: list[str]) -> None:
            job_id = f"{run_id}--{task_slug}"

            def set_running(current: RunState) -> None:
                for t in current.tasks:
                    if t.slug != task_slug:
                        continue
                    t.status = "running"
                    t.started_at = utc_now_iso()
                    t.job_id = job_id
                    t.error = None
                    return

            update(mutator=set_running)

            res = run_codex_exec(
                job_id=job_id,
                jobs_dir=paths.jobs_dir,
                prompt=prompt_text,
                cwd=cwd_path,
                model=state.coder_model,
                sandbox=state.sandbox,
                approval_policy=state.approval_policy,
                extra_config=[
                    f"model_reasoning_effort=\"{state.coder_reasoning_effort}\"",
                    *list(state.coder_extra_config or []),
                ],
            )

            def set_finished(current: RunState) -> None:
                for t in current.tasks:
                    if t.slug != task_slug:
                        continue
                    t.finished_at = utc_now_iso()
                    return

            update(mutator=set_finished)
            if res.status != "completed":
                def set_failed(current: RunState) -> None:
                    for t in current.tasks:
                        if t.slug != task_slug:
                            continue
                        t.status = "failed"
                        t.error = f"codex exit={res.exit_code}"
                        return

                update(
                    mutator=set_failed,
                    phase="error",
                    next_action="wait",
                    wait_reason="error",
                    important_event=f"coder 失败: {task_slug}",
                    important_event_at=utc_now_iso(),
                )
                return

            patch = extract_patch_from_stdout_jsonl(res.artifacts.stdout_jsonl)
            if not patch or "diff --git " not in patch:
                def set_failed_no_patch(current: RunState) -> None:
                    for t in current.tasks:
                        if t.slug != task_slug:
                            continue
                        t.status = "failed"
                        t.error = "patch not found in stdout"
                        return

                update(
                    mutator=set_failed_no_patch,
                    phase="error",
                    next_action="wait",
                    wait_reason="error",
                    important_event=f"未提取到 patch: {task_slug}",
                    important_event_at=utc_now_iso(),
                )
                return

            touched = touched_b_paths_from_patch(patch)
            scope_guard_enabled = bool(allow_prefix) and state.mode == "dual"
            if scope_guard_enabled:
                allowed_extras = {".codex"}
                disallowed: list[str] = []
                for p in touched:
                    if p == allow_prefix or p.startswith(f"{allow_prefix}/"):
                        continue
                    if any(p == extra or p.startswith(f"{extra}/") for extra in allowed_extras):
                        continue
                    disallowed.append(p)
                if disallowed:
                    warn = ", ".join(disallowed[:10]) + (" (+more)" if len(disallowed) > 10 else "")
                    update(event={"kind": "scope_warning", "data": f"越界路径: {warn}"})
            for prefix in (forbid or []):
                if not prefix:
                    continue
                crossed: list[str] = []
                for p in touched:
                    if p == prefix or p.startswith(f"{prefix}/"):
                        crossed.append(p)
                if crossed:
                    warn = ", ".join(crossed[:10]) + (" (+more)" if len(crossed) > 10 else "")
                    update(event={"kind": "scope_warning", "data": f"跨项目路径: {warn}"})

            with patches_lock:
                patches[task_slug] = patch

            def set_completed(current: RunState) -> None:
                for t in current.tasks:
                    if t.slug != task_slug:
                        continue
                    t.status = "completed"
                    return

            update(mutator=set_completed)

        task_specs = [(t.slug, t.project_root) for t in (state.tasks or [])]
        for slug, project_root_str in task_specs:
            # Run coder in-place (no worktree) to reduce overhead. Coder outputs patch only; apply happens separately.
            worktree_path = repo_root

            # Scope prefix used for cross-scope patch validation.
            project_root = Path(project_root_str)
            try:
                rel = project_root.resolve().relative_to(repo_root.resolve())
                allow_prefix = str(rel).replace("\\", "/").strip("/")
                if allow_prefix in {"", "."}:
                    allow_prefix = ""
            except Exception:
                allow_prefix = ""
            allow_prefix_by_slug[slug] = allow_prefix

            requirements_hint = (
                paths.requirements_path
                if slug == "single"
                else (paths.requirements_primary_path if slug == "primary" else paths.requirements_secondary_path)
            )
            prompt = self._build_coder_prompt(requirements_path=requirements_hint, contract_path=contract_hint)
            prepared.append((slug, worktree_path, prompt))

        forbid_by_slug: dict[str, list[str]] = {}
        if state.mode == "dual":
            forbid_by_slug["primary"] = [allow_prefix_by_slug.get("secondary", "")]
            forbid_by_slug["secondary"] = [allow_prefix_by_slug.get("primary", "")]

        for slug, worktree_path, prompt in prepared:
            t = threading.Thread(
                target=run_task,
                kwargs={
                    "task_slug": slug,
                    "prompt_text": prompt,
                    "cwd_path": worktree_path,
                    "allow_prefix": allow_prefix_by_slug.get(slug, ""),
                    "forbid": list(forbid_by_slug.get(slug, [])),
                },
                name=f"{run_id}--{slug}",
                daemon=True,
            )
            task_threads.append(t)
            t.start()

        for t in task_threads:
            t.join()

        # If any task set the run to error, stop here.
        try:
            current = self._store.load(run_id)
        except Exception:
            return
        if current.phase == "error":
            return

        # Integrate patches
        update(phase="integrate", important_event="正在整合 patch", important_event_at=utc_now_iso())
        if state.mode == "dual":
            patch_a = patches.get("primary", "")
            patch_b = patches.get("secondary", "")
            overlaps = detect_patch_conflicts(patch_a, patch_b)
            if overlaps:
                update(phase="error", next_action="wait", wait_reason="error", important_event=f"patch 冲突(同文件): {len(overlaps)}", important_event_at=utc_now_iso())
                return
            final_patch = (patch_a.rstrip() + "\n\n" + patch_b.lstrip()).strip("\n") + "\n"
        else:
            final_patch = patches.get("single", "").strip("\n") + "\n"

        paths.patch_path.write_text(final_patch, encoding="utf-8")

        update(
            phase="done",
            next_action="apply",
            wait_reason="ready_to_apply",
            important_event="可执行 squad_apply",
            important_event_at=utc_now_iso(),
        )
        return

        plan_files = self._plan_scan(repo_root=repo_root, query=state.query, layout=layout, light=False)
        evidence = self._exec_scan(
            layout=layout,
            plan_files=plan_files,
            artifacts_dir=paths.artifacts_dir,
            read_limits=(state.read_limits_max_files, state.read_limits_max_file_bytes, state.read_limits_max_total_bytes),
        )

        try:
            paths.artifacts_dir.mkdir(parents=True, exist_ok=True)
            requirements_payload = ""
            if state.mode == "dual" and len(state.tasks) > 1:
                _ = write_requirements_dual(
                    layout=layout,
                    run_id=run_id,
                    query=state.query,
                    primary_root=Path(state.tasks[0].project_root),
                    secondary_root=Path(state.tasks[1].project_root),
                )
            else:
                req_path = write_requirements_single(
                    layout=layout,
                    run_id=run_id,
                    query=state.query,
                    primary_root=Path(state.tasks[0].project_root) if state.tasks else repo_root,
                )
                try:
                    requirements_payload = req_path.read_text(encoding="utf-8")
                except Exception:
                    requirements_payload = ""

            profile = read_json(layout.kb_dir / "repo_profile.json") or {}
            fp = profile.get("fingerprint") if isinstance(profile.get("fingerprint"), dict) else {}
            git_head = str(fp.get("git_head") or "")
            dirty = bool(fp.get("dirty") or False)
            top_dirs = profile.get("top_level_dirs") if isinstance(profile.get("top_level_dirs"), list) else []
            roots = profile.get("project_roots") if isinstance(profile.get("project_roots"), list) else []
            roots = [r for r in roots if isinstance(r, dict)]
            roots_hint = ", ".join(str(r.get("path") or "") for r in roots[:8] if str(r.get("path") or "").strip())
            evidence_paths = [e.get("path", "") for e in evidence if isinstance(e, dict)]
            compact_md = "\n".join(
                [
                    "# Supervisor Squad KB (Compact)",
                    "",
                    f"- Mode: {state.mode}",
                    f"- Repo: {Path(state.repo_root).name} | git_head: {git_head[:12] or '(unknown)'} | dirty: {dirty}",
                    f"- Top-level dirs: {', '.join(str(x) for x in top_dirs[:12]) if top_dirs else '(unknown)'}",
                    f"- Project roots: {roots_hint or '(unknown)'}",
                    f"- Director report: {getattr(report, 'kind', 'none')}",
                    f"- Evidence files: {', '.join(evidence_paths[:10]) if evidence_paths else '(none)'}",
                    "",
                    "## Goal (raw)",
                    (state.query.strip() or "(empty query)")[:2000],
                    "",
                    "## Next",
                    "- Coder writes patch.diff according to requirements.md.",
                    "",
                ]
            )
            _ = write_compact(layout=layout, compact_md=compact_md, max_kb=state.kb_compact_max_kb)
            write_kb_index(layout=layout, note="requirements generated")
            archive_and_clear_inbox(layout=layout, keep=state.kb_archive_keep, max_kb=state.kb_archive_max_kb)
        except Exception:
            update(
                phase="error",
                next_action="wait",
                wait_reason="error",
                important_event="写入 requirements/KB 失败",
                important_event_at=utc_now_iso(),
            )
            return

        def set_requirements_brief(current: RunState) -> None:
            q = (current.query or "").strip().splitlines()
            current.requirements_brief = (q[0] if q else "requirements generated")[:160]

        update(
            mutator=set_requirements_brief,
            important_event="已生成需求文档",
            important_event_at=utc_now_iso(),
            event={"kind": "requirements", "data_lines": self._requirements_brief_lines(requirements_payload)},
        )
        update(phase="coder_run", wait_reason="agent_running", important_event="已开始执行 coder", important_event_at=utc_now_iso())

        # Prepare worktrees and sparse checkout, then run coder tasks concurrently.
        patches: dict[str, str] = {}
        patches_lock = threading.Lock()
        task_threads: list[threading.Thread] = []

        contract_hint = paths.contract_path if state.mode == "dual" else None

        allow_prefix_by_slug: dict[str, str] = {}
        prepared: list[tuple[str, Path, str]] = []

        def run_task(*, task_slug: str, prompt_text: str, cwd_path: Path, allow_prefix: str, forbid: list[str]) -> None:
            job_id = f"{run_id}--{task_slug}"

            def set_running(current: RunState) -> None:
                for t in current.tasks:
                    if t.slug != task_slug:
                        continue
                    t.status = "running"
                    t.started_at = utc_now_iso()
                    t.job_id = job_id
                    t.error = None
                    return

            update(mutator=set_running)

            res = run_codex_exec(
                job_id=job_id,
                jobs_dir=paths.jobs_dir,
                prompt=prompt_text,
                cwd=cwd_path,
                model=state.coder_model,
                sandbox=state.sandbox,
                approval_policy=state.approval_policy,
                extra_config=[
                    f"model_reasoning_effort=\"{state.coder_reasoning_effort}\"",
                    *list(state.coder_extra_config or []),
                ],
            )

            def set_finished(current: RunState) -> None:
                for t in current.tasks:
                    if t.slug != task_slug:
                        continue
                    t.finished_at = utc_now_iso()
                    return

            update(mutator=set_finished)
            if res.status != "completed":
                def set_failed(current: RunState) -> None:
                    for t in current.tasks:
                        if t.slug != task_slug:
                            continue
                        t.status = "failed"
                        t.error = f"codex exit={res.exit_code}"
                        return

                update(
                    mutator=set_failed,
                    phase="error",
                    next_action="wait",
                    wait_reason="error",
                    important_event=f"coder 失败: {task_slug}",
                    important_event_at=utc_now_iso(),
                )
                return

            patch = extract_patch_from_stdout_jsonl(res.artifacts.stdout_jsonl)
            if not patch or "diff --git " not in patch:
                def set_failed_no_patch(current: RunState) -> None:
                    for t in current.tasks:
                        if t.slug != task_slug:
                            continue
                        t.status = "failed"
                        t.error = "patch not found in stdout"
                        return

                update(
                    mutator=set_failed_no_patch,
                    phase="error",
                    next_action="wait",
                    wait_reason="error",
                    important_event=f"未提取到 patch: {task_slug}",
                    important_event_at=utc_now_iso(),
                )
                return

            touched = touched_b_paths_from_patch(patch)
            scope_guard_enabled = bool(allow_prefix) and state.mode == "dual"
            if scope_guard_enabled:
                allowed_extras = {".codex"}
                disallowed: list[str] = []
                for p in touched:
                    if p == allow_prefix or p.startswith(f"{allow_prefix}/"):
                        continue
                    if any(p == extra or p.startswith(f"{extra}/") for extra in allowed_extras):
                        continue
                    disallowed.append(p)
                if disallowed:
                    warn = ", ".join(disallowed[:10]) + (" (+more)" if len(disallowed) > 10 else "")
                    update(event={"kind": "scope_warning", "data": f"越界路径: {warn}"})
            for prefix in (forbid or []):
                if not prefix:
                    continue
                crossed: list[str] = []
                for p in touched:
                    if p == prefix or p.startswith(f"{prefix}/"):
                        crossed.append(p)
                if crossed:
                    warn = ", ".join(crossed[:10]) + (" (+more)" if len(crossed) > 10 else "")
                    update(event={"kind": "scope_warning", "data": f"跨项目路径: {warn}"})

            with patches_lock:
                patches[task_slug] = patch

            def set_completed(current: RunState) -> None:
                for t in current.tasks:
                    if t.slug != task_slug:
                        continue
                    t.status = "completed"
                    return

            update(mutator=set_completed)

        task_specs = [(t.slug, t.project_root) for t in (state.tasks or [])]
        for slug, project_root_str in task_specs:
            # Run coder in-place (no worktree) to reduce overhead. Coder outputs patch only; apply happens separately.
            worktree_path = repo_root

            # Scope prefix used for cross-scope patch validation.
            project_root = Path(project_root_str)
            try:
                rel = project_root.resolve().relative_to(repo_root.resolve())
                allow_prefix = str(rel).replace("\\", "/").strip("/")
                if allow_prefix in {"", "."}:
                    allow_prefix = ""
            except Exception:
                allow_prefix = ""
            allow_prefix_by_slug[slug] = allow_prefix

            requirements_hint = (
                paths.requirements_path
                if slug == "single"
                else (paths.requirements_primary_path if slug == "primary" else paths.requirements_secondary_path)
            )
            prompt = self._build_coder_prompt(requirements_path=requirements_hint, contract_path=contract_hint)
            prepared.append((slug, worktree_path, prompt))

        forbid_by_slug: dict[str, list[str]] = {}
        if state.mode == "dual":
            forbid_by_slug["primary"] = [allow_prefix_by_slug.get("secondary", "")]
            forbid_by_slug["secondary"] = [allow_prefix_by_slug.get("primary", "")]

        for slug, worktree_path, prompt in prepared:
            t = threading.Thread(
                target=run_task,
                kwargs={
                    "task_slug": slug,
                    "prompt_text": prompt,
                    "cwd_path": worktree_path,
                    "allow_prefix": allow_prefix_by_slug.get(slug, ""),
                    "forbid": list(forbid_by_slug.get(slug, [])),
                },
                name=f"{run_id}--{slug}",
                daemon=True,
            )
            task_threads.append(t)
            t.start()

        for t in task_threads:
            t.join()

        # If any task set the run to error, stop here.
        try:
            current = self._store.load(run_id)
        except Exception:
            return
        if current.phase == "error":
            return

        # Integrate patches
        update(phase="integrate", important_event="正在整合 patch", important_event_at=utc_now_iso())
        if state.mode == "dual":
            patch_a = patches.get("primary", "")
            patch_b = patches.get("secondary", "")
            overlaps = detect_patch_conflicts(patch_a, patch_b)
            if overlaps:
                update(phase="error", next_action="wait", wait_reason="error", important_event=f"patch 冲突(同文件): {len(overlaps)}", important_event_at=utc_now_iso())
                return
            final_patch = (patch_a.rstrip() + "\n\n" + patch_b.lstrip()).strip("\n") + "\n"
        else:
            final_patch = patches.get("single", "").strip("\n") + "\n"

        paths.patch_path.write_text(final_patch, encoding="utf-8")

        code, out = _run_git(repo_root, ["apply", "--check", str(paths.patch_path)])
        if code != 0:
            _ = out
            update(
                phase="error",
                next_action="wait",
                wait_reason="error",
                important_event="patch 预检失败(git apply --check)",
                important_event_at=utc_now_iso(),
            )
            return

        update(phase="done", next_action="apply", wait_reason="ready_to_apply", important_event="patch 已就绪", important_event_at=utc_now_iso())

    def _build_coder_prompt(self, *, requirements_path: Path, contract_path: Path | None) -> str:
        parts = [
            "You are a focused code-writing subagent.",
            "Rules:",
            "- Output MUST be a git-style patch (diff) only.",
            "- Keep changes minimal and directly related to the goal.",
            "- Self-check acceptance criteria before returning.",
            f"- Read requirements: {requirements_path}",
        ]
        if contract_path:
            parts.append(f"- If needed for cross-project sync, read/write contract: {contract_path} (<=4KB).")
        parts.append("Return a git-style patch only. No prose, no Markdown fences.")
        return "\n".join(parts) + "\n"

    def apply(self, state: RunState, *, options: dict[str, Any]) -> dict[str, Any]:
        cwd_opt = options.get("cwd")
        if isinstance(cwd_opt, str) and cwd_opt.strip():
            state = self._store.load(state.run_id, cwd=cwd_opt)
        repo_root = Path(state.repo_root)
        layout = StorageLayout.for_repo(repo_root)
        patch_path = layout.run_paths(state.run_id).patch_path
        base = state.public_status(options=options)
        if not patch_path.exists():
            wait_ms = min(state.compute_forced_wait_ms(), 5000)
            summary = [f"patch 未就绪，当前阶段: {state.phase}"]
            return {"run_id": state.run_id, "forced_wait_ms": wait_ms, "summary": summary, "events": [], "applied": False, "dry_run": True, "error": "patch.diff not found"}
        patch_text = patch_path.read_text(encoding="utf-8", errors="replace")
        dry_run = bool(options.get("dry_run", True))
        args = ["apply", "--check"] if dry_run else ["apply"]
        proc = subprocess.run(["git", *args, str(patch_path)], cwd=repo_root, capture_output=True, text=True)
        ok = proc.returncode == 0
        summary = ""
        try:
            touched = touched_files_from_patch(patch_text)
            summary = f"files={len(touched)}"
        except Exception:
            summary = ""
        if not ok:
            err = (proc.stderr or proc.stdout or "").strip()[:2000]
            # Record failure for visibility in follow-up squad_status.
            with self._lock:
                current = self._store.load(state.run_id, cwd=cwd_opt if isinstance(cwd_opt, str) else None)
                current.phase = "error"
                current.next_action = "wait"
                current.wait_reason = "error"
                current.important_event = "git apply 失败"
                current.important_event_at = utc_now_iso()
                current.event_seq += 1
                self._store.save(current)
                self._write_report(layout=StorageLayout.for_repo(Path(current.repo_root)), state=current)
                base = current.public_status()
            return {**base, "applied": False, "dry_run": dry_run, "summary": summary, "error": err or "git apply failed"}
        if not dry_run:
            # Record apply event in state (best-effort).
            with self._lock:
                current = self._store.load(state.run_id, cwd=cwd_opt if isinstance(cwd_opt, str) else None)
                current.important_event = "patch 已应用"
                current.important_event_at = utc_now_iso()
                current.event_seq += 1
                self._store.save(current)
                self._write_report(layout=StorageLayout.for_repo(Path(current.repo_root)), state=current)
                base = current.public_status()
        return {**base, "applied": True, "dry_run": dry_run, "summary": summary}

    def _write_report(self, *, layout: StorageLayout, state: RunState) -> None:
        """
        Write a short Chinese report for users to skim.
        This is an artifact (not returned via MCP tools by default).
        """
        try:
            paths = layout.run_paths(state.run_id)
            paths.artifacts_dir.mkdir(parents=True, exist_ok=True)
            task_lines: list[str] = []
            for t in state.tasks:
                task_lines.append(f"- {t.slug}: {t.status}" + (f"（{t.error}）" if t.error else ""))
            text = "\n".join(
                [
                    "# 执行报告（简版）",
                    "",
                    f"- Run ID: {state.run_id}",
                    f"- 模式: {state.mode}",
                    f"- 阶段: {state.phase}",
                    f"- 下一步: {state.next_action}",
                    f"- 等待原因: {state.wait_reason}",
                    f"- 最近进展: {state.important_event}",
                    f"- 更新时间: {state.updated_at}",
                    "",
                    "## 子任务状态",
                    *(task_lines or ["- （无）"]),
                    "",
                    "## 产物位置",
                    f"- 需求文档（英文）: `{paths.requirements_path.name}` / `{paths.requirements_primary_path.name}` / `{paths.requirements_secondary_path.name}`",
                    f"- Patch: `{paths.patch_path.name}`",
                    "",
                ]
            )
            paths.report_path.write_text(text, encoding="utf-8")
        except Exception:
            return

    def _plan_scan(self, *, repo_root: Path, query: str, layout: StorageLayout, light: bool) -> list[Path]:
        """
        Deterministic scan plan: pick a small set of high-signal files to read, biased by
        primary root and query terms to reduce irrelevant context.
        """
        candidates: list[Path] = []

        def add(rel: str) -> None:
            p = repo_root / rel
            if p.exists() and p.is_file() and p not in candidates:
                candidates.append(p)

        profile = read_json(layout.kb_dir / "repo_profile.json") or {}
        primary_root = profile.get("primary_root") if isinstance(profile.get("primary_root"), str) else "."
        top_dirs = profile.get("top_level_dirs") if isinstance(profile.get("top_level_dirs"), list) else []

        # Always read repo README first.
        add("README.md")

        # Bias toward the primary project root.
        add(f"{primary_root}/README.md")
        add(f"{primary_root}/package.json")
        add(f"{primary_root}/pyproject.toml")

        # Pick README for any top-level dir mentioned in the query.
        q = (query or "").lower()
        for name in top_dirs:
            if not isinstance(name, str):
                continue
            if name.lower() in q:
                add(f"{name}/README.md")

        # Add a few common manifest/config files near the primary root to anchor context.
        for rel in ["next.config.js", "next.config.mjs", "pnpm-workspace.yaml", "package-lock.json", "pnpm-lock.yaml"]:
            add(f"{primary_root}/{rel}")

        # Fallback: scan key files for every discovered root (limited).
        project_roots = profile.get("project_roots") if isinstance(profile.get("project_roots"), list) else []
        for item in project_roots[:12]:
            if not isinstance(item, dict):
                continue
            path = item.get("path")
            if not isinstance(path, str):
                continue
            add(f"{path}/README.md")

        limit = 6 if light else 20
        return candidates[:limit]

    def _exec_scan(
        self,
        *,
        layout: StorageLayout,
        plan_files: list[Path],
        artifacts_dir: Path,
        read_limits: tuple[int, int, int],
    ) -> list[dict[str, Any]]:
        max_files, max_file_bytes, max_total_bytes = read_limits
        evidence: list[dict[str, Any]] = []
        total = 0
        artifacts_dir.mkdir(parents=True, exist_ok=True)
        for path in plan_files[: max(1, max_files)]:
            if not path.exists() or not path.is_file():
                continue
            try:
                data = path.read_bytes()
            except OSError:
                continue
            snippet = data[: max_file_bytes]
            total += len(snippet)
            try:
                rel = str(path.resolve().relative_to(layout.repo_root.resolve())).replace("\\", "/")
            except Exception:
                rel = str(path)
            evidence.append(
                {
                    "path": rel,
                    "size": len(data),
                    "snippet": snippet.decode("utf-8", errors="replace")[:4000],
                    "truncated": len(data) > len(snippet),
                }
            )
            if total >= max_total_bytes:
                break
        try:
            atomic_write_json(
                artifacts_dir / "evidence.json",
                {"generated_at": utc_now_iso(), "files": evidence},
            )
        except Exception:
            pass
        return evidence
