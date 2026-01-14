from __future__ import annotations

from collections.abc import Callable
import os
import signal
import threading
from datetime import datetime, timezone
from pathlib import Path
from typing import Any
from uuid import uuid4

from .dispatch import run_codex_exec
from ..planning.decider import decide_start, prune_on_start
from ..persistence.storage import StorageLayout
from ..persistence.state import RunState, RunStore, RunTask
from ..utils.storage import read_json
from ..utils.time import utc_now_iso


class Worker:
    def __init__(self) -> None:
        self._lock = threading.Lock()
        self._store = RunStore()

    def _classify_difficulty(self, query: str) -> str:
        q = (query or "").lower()
        if not q.strip():
            return "simple"
        simple_keys = ["typo", "rename", "doc", "readme", "comment", "log", "tiny", "small"]
        hard_keys = ["multi", "architecture", "refactor", "protocol", "api", "schema"]
        if any(k in q for k in simple_keys) and not any(k in q for k in hard_keys):
            return "simple"
        if any(k in q for k in hard_keys):
            return "hard"
        return "medium"

    def start(self, *, cwd: str, query: str, options: dict[str, Any]) -> RunState:
        resolved_cwd = Path(cwd).resolve()
        decision = decide_start(cwd=resolved_cwd, query=query, options=options)
        layout = StorageLayout.for_repo(decision.repo_root)
        retention_days = int(options.get("retention_days") or 10)
        prune_on_start(repo_root=decision.repo_root, retention_days=retention_days)
        self._kill_orphan_jobs(layout=layout)

        run_id = f"ss-{uuid4().hex}"
        paths = layout.run_paths(run_id)
        paths.run_dir.mkdir(parents=True, exist_ok=True)
        paths.artifacts_dir.mkdir(parents=True, exist_ok=True)
        paths.jobs_dir.mkdir(parents=True, exist_ok=True)

        tasks: list[RunTask] = [RunTask(slug="single", project_root=str(decision.primary_root), worktree=str(decision.repo_root))]

        now = utc_now_iso()
        state = RunState(
            run_id=run_id,
            repo_root=str(decision.repo_root),
            cwd=str(resolved_cwd),
            query=query,
            sandbox=str(options.get("sandbox") or "workspace-write"),
            approval_policy=str(options.get("approval_policy") or "never"),
            planner_model=str(options.get("planner_model") or "gpt-5.2"),
            planner_reasoning_effort=str(options.get("planner_reasoning_effort") or "medium"),
            planner_extra_config=list(options.get("planner_extra_config") or []),
            coder_model=str(options.get("coder_model") or "gpt-5.1-codex-mini"),
            coder_reasoning_effort=str(options.get("coder_reasoning_effort") or "medium"),
            coder_extra_config=list(options.get("coder_extra_config") or []),
            read_limits_max_files=30,
            read_limits_max_file_bytes=65_536,
            read_limits_max_total_bytes=1_000_000,
            polling_max_ms=60_000,
            polling_jitter_ratio=0.1,
            mode="single",
            phase="coder_run",
            next_action="wait",
            wait_reason="agent_running",
            created_at=now,
            updated_at=now,
            phase_started_at=now,
            retention_days=retention_days,
            important_event="已开始执行 coder",
            important_event_at=now,
            forced_wait_ms=8000,
            event_seq=1,
            requirements_brief="",
            canceled=False,
            events=[],
            tasks=tasks,
        )
        state.events = [
            {"phase": "coder_run", "kind": "info", "message": "已创建 run"},
            {"phase": "coder_run", "kind": "info", "message": "已开始执行 coder"},
        ]
        self._store.save(state)

        thread = threading.Thread(target=self._run, args=(state.run_id, state.repo_root), name=f"supervisor-squad-{run_id}", daemon=True)
        thread.start()
        return state

    def cancel(self, *, run_id: str, cwd: str, reason: str | None = None) -> bool:
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
            if isinstance(state.events, list):
                state.events.append({"phase": "canceled", "kind": "info", "message": state.important_event})
            self._store.save(state)
            self._write_report(layout=layout, state=state)

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
                killed += 1
            except Exception:
                continue
        return killed

    def _kill_orphan_jobs(self, *, layout: StorageLayout) -> None:
        jobs_root = layout.runs_dir
        if not jobs_root.exists():
            return
        for run_dir in jobs_root.iterdir():
            if not run_dir.is_dir():
                continue
            state_path = run_dir / "state.json"
            jobs_dir = run_dir / "jobs"
            if not state_path.exists() and jobs_dir.exists():
                for job_dir in jobs_dir.iterdir():
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
        difficulty = self._classify_difficulty(state.query)

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
                    current.events = current.events[-50:]
                current.updated_at = utc_now_iso()
                current.event_seq += 1
                self._store.save(current)
                self._write_report(layout=layout, state=current)

        def build_prompt() -> str:
            guidance = [
                "You are a focused code-writing subagent.",
                "Rules:",
                "- Edit files in the repo directly. Do NOT return a patch/diff.",
                "- Keep changes minimal and directly related to the goal.",
                "- Quick analysis: extract goal/scope/constraints from the user query below; do not invent files/config.",
                "- Self-check acceptance criteria before returning.",
            ]
            if difficulty in {"medium", "hard"}:
                guidance += [
                    "- Before editing, consider existing conventions (naming, styling, toolchain).",
                    "- Avoid new deps/config unless strictly required.",
                ]
            guidance.append(f"- User query: {(state.query or '').strip()[:2000]}")
            return "\n".join(guidance) + "\nApply changes directly. No patch output. No Markdown fences.\n"

        def run_task(task_slug: str, prompt_text: str, cwd_path: Path) -> None:
            job_id = f"{run_id}--{task_slug}"

            def set_running(cur: RunState) -> None:
                for t in cur.tasks:
                    if t.slug != task_slug:
                        continue
                    t.status = "running"
                    t.started_at = utc_now_iso()
                    t.job_id = job_id
                    t.error = None
                    return

            update(mutator=set_running, event={"kind": "info", "message": f"coder 任务开始: {task_slug}"})

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
                timeout_s=90,
            )

            def set_finished(cur: RunState) -> None:
                for t in cur.tasks:
                    if t.slug != task_slug:
                        continue
                    t.finished_at = utc_now_iso()
                    return

            update(mutator=set_finished)
            if res.status != "completed":
                def set_failed(cur: RunState) -> None:
                    for t in cur.tasks:
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
                    event={"kind": "error", "message": f"coder 失败: {task_slug}"},
                )
                return

            def set_completed(cur: RunState) -> None:
                for t in cur.tasks:
                    if t.slug != task_slug:
                        continue
                    t.status = "completed"
                    return

            update(mutator=set_completed, event={"kind": "info", "message": f"coder 完成: {task_slug}"})

        prompt = build_prompt()
        t = threading.Thread(target=run_task, kwargs={"task_slug": "single", "prompt_text": prompt, "cwd_path": repo_root}, daemon=True, name=f"{run_id}--single")
        t.start()
        t.join()

        with self._lock:
            try:
                current = self._store.load(run_id, cwd=str(repo_root))
            except Exception:
                return
            if current.phase == "error":
                return
            current.phase = "done"
            current.next_action = "done"
            current.wait_reason = "completed"
            current.important_event = "coder 已完成并写入代码"
            current.important_event_at = utc_now_iso()
            current.event_seq += 1
            current.forced_wait_ms = 0
            if isinstance(current.events, list):
                current.events.append({"phase": "done", "kind": "info", "message": "coder 已完成并写入代码"})
            self._store.save(current)
            self._write_report(layout=layout, state=current)

    def _write_report(self, *, layout: StorageLayout, state: RunState) -> None:
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
                    "- 代码已直接写入仓库，无 patch/requirements/KB",
                    "",
                ]
            )
            paths.report_path.write_text(text, encoding="utf-8")
        except Exception:
            return


worker = Worker()
