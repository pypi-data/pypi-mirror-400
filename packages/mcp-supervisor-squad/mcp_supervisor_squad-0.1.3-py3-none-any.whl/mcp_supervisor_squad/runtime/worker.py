from __future__ import annotations

from collections.abc import Callable
import json
import subprocess
import threading
from pathlib import Path
from typing import Any
from uuid import uuid4

from .dispatch import run_codex_exec
from ..persistence.contract import write_repo_contract
from ..persistence.kb import archive_and_clear_inbox, read_external_report, write_compact, write_kb_index
from ..utils.patch_utils import (
    detect_patch_conflicts,
    extract_patch_from_stdout_jsonl,
    extract_tagged_b64_json_from_stdout_jsonl,
    touched_b_paths_from_patch,
    touched_files_from_patch,
)
from ..persistence.state import RunState, RunStore, RunTask
from ..planning.config import effective_config
from ..planning.scan import ensure_repo_profile
from ..persistence.storage import StorageLayout, append_jsonl, atomic_write_json, safe_rmtree, utc_now_iso
from ..planning.supervisor import decide_start, prune_on_start


def _run_git(repo_root: Path, args: list[str]) -> tuple[int, str]:
    res = subprocess.run(["git", *args], cwd=repo_root, capture_output=True, text=True)
    out = (res.stdout or "") + (res.stderr or "")
    return res.returncode, out.strip()


class Worker:
    def __init__(self, store: RunStore):
        self._store = store
        self._lock = threading.Lock()

    def start(self, *, cwd: str, query: str, options: dict[str, Any]) -> RunState:
        resolved_cwd = Path(cwd).resolve()
        decision = decide_start(cwd=resolved_cwd, query=query, options=options)
        layout = StorageLayout.for_repo(decision.repo_root)
        retention_days = int(options.get("retention_days") or 10)
        prune_on_start(repo_root=decision.repo_root, retention_days=retention_days)

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
            important = "已创建 run；等待 supervisor 生成需求文档"
        else:
            tasks = [RunTask(slug="single", project_root=str(decision.primary_root), worktree=str(layout.worktrees_dir / run_id / "single"))]
            important = "已创建 run；等待 supervisor 生成需求文档"

        now = utc_now_iso()
        state = RunState(
            run_id=run_id,
            repo_root=str(decision.repo_root),
            cwd=str(resolved_cwd),
            query=query,
            sandbox=cfg.execution.sandbox,
            approval_policy=cfg.execution.approval_policy,
            supervisor_model=cfg.supervisor.model,
            supervisor_reasoning_effort=cfg.supervisor.reasoning_effort,
            supervisor_extra_config=list(cfg.supervisor.extra_config),
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
            mode=decision.mode,
            phase="supervisor_run",
            next_action="wait",
            wait_reason="agent_running",
            created_at=now,
            updated_at=now,
            retention_days=retention_days,
            important_event=important,
            important_event_at=now,
            tasks=tasks,
        )
        self._store.save(state)
        self._write_report(layout=layout, state=state)
        append_jsonl(
            layout.kb_dir / "run_journal.jsonl",
            {
                "ts": now,
                "run_id": run_id,
                "repo_root": str(decision.repo_root),
                "cwd": str(resolved_cwd),
                "mode": decision.mode,
                "query": query,
            },
        )

        thread = threading.Thread(target=self._run, args=(state.run_id,), name=f"supervisor-squad-{run_id}", daemon=True)
        thread.start()
        return state

    def _run(self, run_id: str) -> None:
        try:
            state = self._store.load(run_id)
        except Exception:
            return
        repo_root = Path(state.repo_root)
        layout = StorageLayout.for_repo(repo_root)
        paths = layout.run_paths(run_id)

        def update(*, mutator: Callable[[RunState], None] | None = None, **fields: Any) -> None:
            with self._lock:
                current = self._store.load(run_id)
                if mutator is not None:
                    mutator(current)
                for k, v in fields.items():
                    setattr(current, k, v)
                current.updated_at = utc_now_iso()
                current.brief_cache = None
                current.public_status()  # refresh brief cache
                self._store.save(current)
                self._write_report(layout=layout, state=current)

        update(phase="supervisor_run", important_event="已开始执行 supervisor", important_event_at=utc_now_iso())

        # Ensure shared KB scan cache exists (best-effort).
        try:
            primary_root = Path(state.tasks[0].project_root) if state.tasks else repo_root
            secondary_root = Path(state.tasks[1].project_root) if (state.mode == "dual" and len(state.tasks) > 1) else None
            _ = ensure_repo_profile(layout=layout, primary_root=primary_root, secondary_root=secondary_root)
        except Exception:
            pass

        # Supervisor phase: read external report (if any) and produce requirements/contract/compact.
        report = read_external_report(layout=layout, max_kb=state.kb_inbox_max_kb)
        if getattr(report, "kind", "") == "json" and getattr(report, "payload", None) is None and getattr(report, "path", None):
            # Oversized or invalid JSON report; archive it to avoid repeated failures.
            archive_and_clear_inbox(layout=layout, run_id=run_id, keep=state.kb_archive_keep, max_kb=state.kb_archive_max_kb)
            report = read_external_report(layout=layout, max_kb=state.kb_inbox_max_kb)

        supervisor_worktree = layout.worktrees_dir / run_id / "supervisor"
        supervisor_worktree.parent.mkdir(parents=True, exist_ok=True)
        if not supervisor_worktree.exists():
            code, out = _run_git(repo_root, ["worktree", "add", "--detach", str(supervisor_worktree)])
            if code != 0:
                _ = out
                update(
                    phase="error",
                    next_action="wait",
                    wait_reason="error",
                    important_event="supervisor worktree 创建失败",
                    important_event_at=utc_now_iso(),
                )
                return

        # Best-effort sparse checkout to keep supervisor context small.
        allow_prefixes: list[str] = []
        for t in state.tasks:
            try:
                rel = Path(t.project_root).resolve().relative_to(repo_root.resolve())
                pfx = str(rel).replace("\\", "/").strip("/")
            except Exception:
                pfx = ""
            if pfx and pfx not in allow_prefixes:
                allow_prefixes.append(pfx)
        try:
            _run_git(supervisor_worktree, ["sparse-checkout", "init", "--no-cone"])
            patterns = [f"{p}/**" for p in allow_prefixes if p] + [".codex/**"]
            if patterns:
                _run_git(supervisor_worktree, ["sparse-checkout", "set", "--no-cone", "--skip-checks", *patterns])
        except Exception:
            pass

        supervisor_job_id = f"{run_id}--supervisor"
        supervisor_prompt = self._build_supervisor_prompt(
            run_id=run_id,
            repo_root=repo_root,
            query=state.query,
            mode=state.mode,
            allow_prefixes=allow_prefixes,
            repo_profile_path=layout.kb_dir / "repo_profile.json",
            external_report=report,
            artifacts_dir=paths.artifacts_dir,
            kb_dir=layout.kb_dir,
            read_limits=(state.read_limits_max_files, state.read_limits_max_file_bytes, state.read_limits_max_total_bytes),
            kb_limits=(state.kb_compact_max_kb,),
        )
        sup_res = run_codex_exec(
            job_id=supervisor_job_id,
            jobs_dir=paths.jobs_dir,
            prompt=supervisor_prompt,
            cwd=supervisor_worktree,
            model=state.supervisor_model,
            sandbox=state.sandbox,
            approval_policy=state.approval_policy,
            extra_config=[
                f"model_reasoning_effort=\"{state.supervisor_reasoning_effort}\"",
                *list(state.supervisor_extra_config or []),
            ],
        )
        if sup_res.status != "completed":
            update(
                phase="error",
                next_action="wait",
                wait_reason="error",
                important_event="supervisor 失败",
                important_event_at=utc_now_iso(),
            )
            return

        sup_payload = extract_tagged_b64_json_from_stdout_jsonl(sup_res.artifacts.stdout_jsonl, tag="SUPERVISOR_JSON_B64")
        if not sup_payload:
            update(
                phase="error",
                next_action="wait",
                wait_reason="error",
                important_event="supervisor 未输出结构化结果",
                important_event_at=utc_now_iso(),
            )
            return

        def get_str(key: str) -> str:
            v = sup_payload.get(key)
            return str(v) if isinstance(v, str) else ""

        requirements_single = get_str("requirements")
        requirements_primary = get_str("requirements_primary")
        requirements_secondary = get_str("requirements_secondary")
        compact_md = get_str("compact_md")
        contract_obj = sup_payload.get("contract") if isinstance(sup_payload.get("contract"), dict) else None
        important = get_str("important_event") or "supervisor 已生成需求文档"

        try:
            paths.artifacts_dir.mkdir(parents=True, exist_ok=True)
            if state.mode == "dual":
                if not requirements_primary.strip() or not requirements_secondary.strip():
                    raise ValueError("missing dual requirements")
                paths.requirements_primary_path.write_text(requirements_primary, encoding="utf-8")
                paths.requirements_secondary_path.write_text(requirements_secondary, encoding="utf-8")
                if contract_obj is None:
                    contract_obj = {"version": 1, "notes": "no contract provided"}
                raw_contract = json.dumps(contract_obj, ensure_ascii=False).encode("utf-8", errors="replace")
                if len(raw_contract) > 4096:
                    contract_obj = {"version": 1, "notes": "contract truncated to fit 4KB"}
                atomic_write_json(paths.contract_path, contract_obj)
            else:
                if not requirements_single.strip():
                    raise ValueError("missing requirements")
                paths.requirements_path.write_text(requirements_single, encoding="utf-8")

            if compact_md.strip():
                _ = write_compact(layout=layout, compact_md=compact_md, max_kb=state.kb_compact_max_kb)
            write_kb_index(layout=layout, run_id=run_id, note="supervisor completed")
            archive_and_clear_inbox(layout=layout, run_id=run_id, keep=state.kb_archive_keep, max_kb=state.kb_archive_max_kb)
        except Exception:
            update(
                phase="error",
                next_action="wait",
                wait_reason="error",
                important_event="写入 requirements/KB 失败",
                important_event_at=utc_now_iso(),
            )
            return

        update(phase="coder_run", important_event=important, important_event_at=utc_now_iso())

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
            if allow_prefix:
                for p in touched:
                    if p == allow_prefix or p.startswith(f"{allow_prefix}/"):
                        continue

                    def set_failed_scope(current: RunState) -> None:
                        for t in current.tasks:
                            if t.slug != task_slug:
                                continue
                            t.status = "failed"
                            t.error = f"out of scope: {p}"
                            return

                    update(
                        mutator=set_failed_scope,
                        phase="error",
                        next_action="wait",
                        wait_reason="error",
                        important_event=f"patch 越界: {task_slug}",
                        important_event_at=utc_now_iso(),
                    )
                    return
            for prefix in (forbid or []):
                if not prefix:
                    continue
                for p in touched:
                    if p == prefix or p.startswith(f"{prefix}/"):
                        def set_failed_forbid(current: RunState) -> None:
                            for t in current.tasks:
                                if t.slug != task_slug:
                                    continue
                                t.status = "failed"
                                t.error = f"cross-scope: {p}"
                                return

                        update(
                            mutator=set_failed_forbid,
                            phase="error",
                            next_action="wait",
                            wait_reason="error",
                            important_event=f"patch 跨项目: {task_slug}",
                            important_event_at=utc_now_iso(),
                        )
                        return

            with patches_lock:
                patches[task_slug] = patch

            def set_completed(current: RunState) -> None:
                for t in current.tasks:
                    if t.slug != task_slug:
                        continue
                    t.status = "completed"
                    return

            update(mutator=set_completed, important_event=f"已拿到 patch: {task_slug}", important_event_at=utc_now_iso())

        task_specs = [(t.slug, t.project_root, t.worktree) for t in (state.tasks or [])]
        for slug, project_root_str, worktree_str in task_specs:
            worktree_path = Path(worktree_str)
            worktree_path.parent.mkdir(parents=True, exist_ok=True)
            # Create worktree (detached) if not exists.
            if not worktree_path.exists():
                code, out = _run_git(repo_root, ["worktree", "add", "--detach", str(worktree_path)])
                if code != 0:
                    _ = out
                    update(
                        phase="error",
                        next_action="wait",
                        wait_reason="error",
                        important_event=f"worktree 失败: {slug}",
                        important_event_at=utc_now_iso(),
                    )
                    return

            # Best-effort sparse checkout for scope reduction: restrict to project root prefix.
            project_root = Path(project_root_str)
            try:
                rel = project_root.resolve().relative_to(repo_root.resolve())
                allow_prefix = str(rel).replace("\\", "/").strip("/")
            except Exception:
                allow_prefix = ""
            if allow_prefix:
                _run_git(worktree_path, ["sparse-checkout", "init", "--no-cone"])
                _run_git(worktree_path, ["sparse-checkout", "set", "--no-cone", "--skip-checks", f"{allow_prefix}/**"])
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

        # Cleanup in the background; do not block readiness.
        cleanup_thread = threading.Thread(target=self._cleanup, args=(run_id,), daemon=True)
        cleanup_thread.start()

    def _cleanup(self, run_id: str) -> None:
        try:
            state = self._store.load(run_id)
        except Exception:
            return
        repo_root = Path(state.repo_root)
        layout = StorageLayout.for_repo(repo_root)
        paths = layout.run_paths(run_id)

        # Best-effort: remove worktrees and worktree dir.
        for task in state.tasks:
            try:
                _run_git(repo_root, ["worktree", "remove", "--force", str(task.worktree)])
            except Exception:
                pass
        try:
            _run_git(repo_root, ["worktree", "remove", "--force", str(layout.worktrees_dir / run_id / "supervisor")])
        except Exception:
            pass
        safe_rmtree(layout.worktrees_dir / run_id)
        # Keep run artifacts; do not delete patch.

        with self._lock:
            try:
                current = self._store.load(run_id)
            except Exception:
                return
            if current.phase == "done":
                current.public_status()
                self._store.save(current)
                self._write_report(layout=layout, state=current)

    def _build_supervisor_prompt(
        self,
        *,
        run_id: str,
        repo_root: Path,
        query: str,
        mode: str,
        allow_prefixes: list[str],
        repo_profile_path: Path,
        external_report: Any,
        artifacts_dir: Path,
        kb_dir: Path,
        read_limits: tuple[int, int, int],
        kb_limits: tuple[int],
    ) -> str:
        max_files, max_file_bytes, max_total_bytes = read_limits
        (compact_max_kb,) = kb_limits
        allow = [p for p in allow_prefixes if p]
        scope_lines = [f"- Allowed prefix: `{p}/**`" for p in allow] if allow else ["- Allowed prefix: `./**` (entire repo)"]
        external_path = getattr(external_report, "path", None)
        external_kind = getattr(external_report, "kind", "none")

        contract_rule = "If mode=dual, include a minimal `contract` object (keep JSON <= 4KB)."
        if mode != "dual":
            contract_rule = "If mode=single, omit `contract` or set it to null."

        parts = [
            "You are the SUPERVISOR subagent for a supervisor-squad workflow.",
            "Your job: analyze the request, scan the repo minimally, and generate concise requirements for coder agents.",
            "",
            "Hard rules:",
            "- DO NOT modify repository source code.",
            f"- You MAY write only under: {artifacts_dir} and {kb_dir}",
            "- Keep outputs short and structured; avoid logs.",
            "",
            "User request:",
            query.strip() or "(empty query)",
            "",
            "Inputs to read (on disk):",
            f"- Repo profile (scan cache): {repo_profile_path}",
        ]
        if external_kind != "none" and external_path:
            parts.append(f"- External injected report ({external_kind}): {external_path}")
        else:
            parts.append("- External injected report: (none)")

        parts += [
            "",
            "Repo scan guidance (keep it light):",
            f"- You may use `rg` under allowed prefixes only: {', '.join(allow) if allow else '(no restriction)'}",
            f"- You may read at most {max_files} files.",
            f"- Each file read should be <= {max_file_bytes} bytes; total <= {max_total_bytes} bytes.",
            "",
            "Scope policy to enforce in requirements:",
            *scope_lines,
            "",
            "Produce requirements in English. Requirements must include: goal, scope, acceptance criteria, constraints.",
            contract_rule,
            f"Keep `compact_md` <= {compact_max_kb}KB.",
            "",
            "Output format (MANDATORY):",
            "1) Construct a JSON object with keys:",
            "- important_event (short string, <=80 chars)",
            "- compact_md (string, <=10KB, summarize decisions & scan findings for shared KB)",
            "- requirements (string) for single mode",
            "- requirements_primary (string) + requirements_secondary (string) for dual mode",
            "- contract (object) for dual mode (optional for single)",
            "2) Base64-encode that JSON (UTF-8).",
            "3) Print exactly ONE line:",
            "SUPERVISOR_JSON_B64: <base64>",
            "4) Print nothing else after that line.",
        ]
        return "\n".join(parts) + "\n"

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
            return {**base, "applied": False, "dry_run": True, "summary": "", "error": "patch.diff not found"}
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
                current.brief_cache = None
                current.public_status()
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
                current.brief_cache = None
                current.public_status()
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
