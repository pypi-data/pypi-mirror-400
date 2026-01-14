from __future__ import annotations

import os
import subprocess
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from ..persistence.storage import atomic_write_json, utc_now_iso


@dataclass(frozen=True, slots=True)
class CodexJobArtifacts:
    job_dir: Path
    stdout_jsonl: Path
    stderr_log: Path
    last_message: Path
    meta_path: Path


@dataclass(frozen=True, slots=True)
class CodexJobResult:
    job_id: str
    status: str
    exit_code: int
    artifacts: CodexJobArtifacts


def run_codex_exec(
    *,
    job_id: str,
    jobs_dir: Path,
    prompt: str,
    cwd: Path,
    model: str,
    sandbox: str,
    approval_policy: str,
    extra_config: list[str] | None = None,
    env: dict[str, str] | None = None,
    timeout_s: int | None = None,
) -> CodexJobResult:
    jobs_dir.mkdir(parents=True, exist_ok=True)
    job_dir = jobs_dir / job_id
    job_dir.mkdir(parents=True, exist_ok=True)
    stdout_path = job_dir / "stdout.jsonl"
    stderr_path = job_dir / "stderr.log"
    last_msg_path = job_dir / "last_message.txt"
    meta_path = job_dir / "meta.json"

    cmd: list[str] = ["codex", "-a", approval_policy, "-m", model, "-s", sandbox]
    for cfg in extra_config or []:
        if cfg:
            cmd += ["-c", cfg]
    cmd += [
        "exec",
        "-C",
        str(cwd),
        "--skip-git-repo-check",
        "--json",
        "--color",
        "never",
        "--output-last-message",
        str(last_msg_path),
        "-",
    ]

    meta: dict[str, Any] = {
        "id": job_id,
        "created_at": utc_now_iso(),
        "status": "running",
        "cwd": str(cwd),
        "model": model,
        "sandbox": sandbox,
        "approval_policy": approval_policy,
        "command": cmd,
        "pid": None,
        "timeout_s": int(timeout_s) if isinstance(timeout_s, int) else None,
        "artifacts": {
            "job_dir": str(job_dir),
            "stdout_jsonl": str(stdout_path),
            "stderr_log": str(stderr_path),
            "last_message": str(last_msg_path),
        },
    }
    atomic_write_json(meta_path, meta)

    env_vars = os.environ.copy()
    if env:
        env_vars.update({str(k): str(v) for k, v in env.items()})

    with stdout_path.open("wb") as out, stderr_path.open("wb") as err:
        proc = subprocess.Popen(cmd, stdin=subprocess.PIPE, stdout=out, stderr=err, env=env_vars)
        assert proc.stdin is not None
        meta["pid"] = proc.pid
        atomic_write_json(meta_path, meta)
        proc.stdin.write((prompt or "").encode("utf-8"))
        proc.stdin.close()
        try:
            exit_code = proc.wait(timeout=timeout_s) if timeout_s else proc.wait()
        except subprocess.TimeoutExpired:
            try:
                proc.terminate()
            except Exception:
                pass
            try:
                exit_code = proc.wait(timeout=5)
            except Exception:
                try:
                    proc.kill()
                except Exception:
                    pass
                exit_code = proc.wait()
            meta.update({"status": "timeout", "exit_code": int(exit_code), "finished_at": utc_now_iso()})
            atomic_write_json(meta_path, meta)
            return CodexJobResult(
                job_id=job_id,
                status="failed",
                exit_code=int(exit_code),
                artifacts=CodexJobArtifacts(
                    job_dir=job_dir,
                    stdout_jsonl=stdout_path,
                    stderr_log=stderr_path,
                    last_message=last_msg_path,
                    meta_path=meta_path,
                ),
            )

    status = "completed" if exit_code == 0 else "failed"
    meta.update({"status": status, "exit_code": exit_code, "finished_at": utc_now_iso()})
    atomic_write_json(meta_path, meta)

    return CodexJobResult(
        job_id=job_id,
        status=status,
        exit_code=exit_code,
        artifacts=CodexJobArtifacts(
            job_dir=job_dir,
            stdout_jsonl=stdout_path,
            stderr_log=stderr_path,
            last_message=last_msg_path,
            meta_path=meta_path,
        ),
    )
